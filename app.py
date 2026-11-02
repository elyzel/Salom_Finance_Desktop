"""Ket Finance - versão web (Flask). Reaproveita models/ e controllers/."""
import io
import os
import tempfile
import threading
import uuid
import math
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session

from config import MESES, ACCOUNTS, CATEGORIES, CATEGORY_COLORS, TRANSACTION_TYPES, META_EMOJIS
from models import Database
from controllers import TransactionController, GoalController, InvestmentController
from controllers.budget_controller import BudgetController
from controllers.import_controller import ImportController
from utils.formatters import formatar_valor, formatar_data
from utils.validators import validar_valor, validar_data, campos_obrigatorios
from utils.excel_exporter import gerar_excel
from utils.rule_engine import aplicar_regras, CAMPOS, CONDICOES_TEXTO, CONDICOES_NUMERICAS, CONDICOES_TIPO

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-troque-em-producao")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # extratos de até 10 MB

# O caminho do banco vem de variável de ambiente (no Docker aponta para um volume)
DB_PATH = os.environ.get("KET_DB_PATH", "ket_finance.db")
db = Database(DB_PATH)
transacoes = TransactionController(db)
metas = GoalController(db)
investimentos = InvestmentController(db)
orcamento = BudgetController(db)
importador = ImportController(db, transacoes)
_lock = threading.Lock()  # SQLite compartilhado entre threads: serializa escritas

app.jinja_env.filters["brl"] = formatar_valor

ACOES_REGRA = ["categorizar", "ignorar", "desmarcar"]
TIPOS_REGRA = ["Todos", "Receita", "Despesa"]


def _validar_regra(dados):
    regra = dict(dados or {})
    regra["descricao"] = str(regra.get("descricao", "")).strip() or "Regra sem nome"
    regra["campo"] = str(regra.get("campo", "descricao"))
    regra["operador"] = str(regra.get("operador", "contém"))
    regra["valor"] = str(regra.get("valor", "")).strip()
    regra["valor2"] = str(regra.get("valor2", "")).strip()
    regra["acao"] = str(regra.get("acao", "categorizar"))
    regra["categoria"] = str(regra.get("categoria", ""))
    regra["tipo"] = str(regra.get("tipo", "Todos"))
    if regra["campo"] not in CAMPOS:
        raise ValueError("Campo de regra inválido.")
    permitidos = CONDICOES_TEXTO if regra["campo"] in ("descricao", "conta") else (CONDICOES_TIPO if regra["campo"] == "tipo" else CONDICOES_NUMERICAS)
    if regra["operador"] not in permitidos:
        raise ValueError("Condição incompatível com o campo escolhido.")
    if not regra["valor"]:
        raise ValueError("Informe o valor que a regra deve procurar.")
    if regra["acao"] not in ACOES_REGRA or regra["tipo"] not in TIPOS_REGRA:
        raise ValueError("Ação ou tipo de transação inválido.")
    if regra["acao"] == "categorizar" and regra["categoria"] not in CATEGORIES:
        raise ValueError("Escolha uma categoria válida.")
    regra["ativa"] = int(str(regra.get("ativa", True)).lower() not in ("0", "false", "off", "no", ""))
    try:
        regra["ordem"] = int(regra.get("numero", regra.get("ordem", 0)) or 0)
    except (TypeError, ValueError):
        raise ValueError("O número da regra precisa ser um inteiro.")
    if regra["ordem"] < 1:
        raise ValueError("O número da regra precisa ser maior que zero.")
    return regra


def _mes_ano():
    hoje = date.today()
    try:
        mes = int(request.args.get("mes", hoje.month))
        ano = int(request.args.get("ano", hoje.year))
        if not (1 <= mes <= 12):
            raise ValueError
    except ValueError:
        mes, ano = hoje.month, hoje.year
    return mes, ano


def _navegacao(mes, ano):
    ant = (12, ano - 1) if mes == 1 else (mes - 1, ano)
    prox = (1, ano + 1) if mes == 12 else (mes + 1, ano)
    return {"ant": ant, "prox": prox, "titulo": f"{MESES[mes]} {ano}"}


def _valor_orcamento(valor, vazio_zero=False):
    texto = str(valor or "").strip().replace("R$", "").replace(" ", "")
    if not texto:
        return 0.0 if vazio_zero else None
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(",", ".")
    elif "." in texto:
        partes = texto.split(".")
        if len(partes) > 1 and all(len(parte) == 3 for parte in partes[1:]):
            texto = "".join(partes)
    try:
        numero = float(texto)
        return numero if math.isfinite(numero) and numero >= 0 else None
    except ValueError:
        return None


def _render_orcamento(mes, ano, plano, erro=None, limpar_rascunho=False):
    itens_plano = plano.get("itens", [])
    fixas = plano.get("fixas", []) or [
        {"categoria": categoria, "descricao": "", "valor": ""}
        for categoria in ("Moradia", "Educação", "Saúde")
        if categoria in orcamento.categorias_despesas
    ]
    destinacoes = plano.get("destinacoes", []) or [
        {"categoria": categoria, "descricao": "", "valor": ""}
        for categoria in orcamento.categorias_destinacoes
    ]
    receita = float(plano.get("receita", 0) or 0)
    total_fixas = sum(_valor_orcamento(item.get("valor", 0), vazio_zero=True) or 0 for item in fixas)
    total_destinacoes = sum(_valor_orcamento(item.get("valor", 0), vazio_zero=True) or 0 for item in destinacoes)
    liquido_apos_fixas = receita - total_fixas
    disponivel = liquido_apos_fixas - total_destinacoes
    totais_categoria = {}
    for item in fixas + destinacoes:
        categoria = item.get("categoria", "")
        totais_categoria[categoria] = totais_categoria.get(categoria, 0.0) + (_valor_orcamento(item.get("valor", 0), vazio_zero=True) or 0)
    return render_template(
        "orcamento.html", pagina="orcamento", nav=_navegacao(mes, ano), mes=mes, ano=ano,
        receita=receita, receita_input=plano.get("receita_input", f"{receita:.2f}"),
        fixas=fixas, destinacoes=destinacoes,
        itens_plano=itens_plano,
        categorias_despesas=orcamento.categorias_despesas,
        categorias_destinacoes=orcamento.categorias_destinacoes,
        total_fixas=total_fixas, total_destinacoes=total_destinacoes,
        liquido_apos_fixas=liquido_apos_fixas, disponivel=disponivel,
        totais_categoria=totais_categoria, erro=erro, limpar_rascunho=limpar_rascunho,
        planejamento_salvo=bool(plano.get("existe", False)),
    )


@app.route("/")
def dashboard():
    mes, ano = _mes_ano()
    do_mes = transacoes.get_por_mes(mes, ano)

    por_categoria = {}
    for t in do_mes:
        if t.tipo == "Despesa":
            por_categoria[t.categoria] = por_categoria.get(t.categoria, 0) + t.valor
    por_categoria = dict(sorted(por_categoria.items(), key=lambda x: -x[1]))
    resumo_mes = transacoes.get_resumo_mes(mes, ano)

    seis = transacoes.get_resumo_ultimos_meses(6)
    diaria = transacoes.get_movimentacao_diaria(mes, ano)
    contas = db.get_contas()
    lista_metas = metas.get_todas()

    graficos = {
        "meses": {"labels": [m["label"] for m in seis],
                  "receitas": [m["receitas"] for m in seis],
                  "despesas": [m["despesas"] for m in seis]},
        "diaria": diaria,
        "categorias": {"labels": list(por_categoria.keys()),
                       "valores": list(por_categoria.values()),
                       "cores": [CATEGORY_COLORS.get(c, "#64748b") for c in por_categoria]},
    }
    return render_template(
        "dashboard.html", pagina="dashboard", nav=_navegacao(mes, ano), mes=mes, ano=ano,
        resumo=resumo_mes, contas=contas,
        patrimonio=sum(contas.values()), metas=lista_metas,
        total_acoes=investimentos.get_total_acoes(), cdb=investimentos.get_cdb(),
        agendados=len(transacoes.get_agendados()), graficos=graficos,
    )


@app.route("/lancamentos", methods=["GET", "POST"])
def lancamentos():
    if request.method == "POST":
        f = request.form
        tipo, conta, categoria = f.get("tipo"), f.get("conta"), f.get("categoria")
        valor = validar_valor(f.get("valor"))
        data_str = formatar_data(f.get("data", ""))
        destino = f.get("conta_destino") or None
        try:
            parcelas = max(1, int(f.get("parcelas", 1) or 1))
        except ValueError:
            parcelas = 1

        if tipo not in TRANSACTION_TYPES or not campos_obrigatorios(conta, categoria, f.get("descricao")):
            flash("Preencha todos os campos obrigatórios.", "erro")
        elif valor is None:
            flash("Valor inválido. Use um número maior que zero.", "erro")
        elif not validar_data(data_str):
            flash("Data inválida.", "erro")
        elif tipo == "Transferência" and (not destino or destino == conta):
            flash("Escolha uma conta de destino diferente da origem.", "erro")
        else:
            with _lock:
                transacoes.adicionar(
                    tipo, data_str, conta, categoria, valor, f["descricao"].strip(),
                    parcelado=parcelas > 1, total_parcelas=parcelas,
                    agendado=1 if f.get("agendado") else 0,
                    conta_destino=destino if tipo == "Transferência" else None)
            flash("Lançamento salvo com sucesso!", "ok")
        return redirect(url_for("lancamentos", mes=f.get("mes_ref"), ano=f.get("ano_ref")))

    mes, ano = _mes_ano()
    lista = sorted(transacoes.get_por_mes(mes, ano), key=lambda t: t.data[6:] + t.data[3:5] + t.data[:2], reverse=True)
    return render_template(
        "lancamentos.html", pagina="lancamentos", nav=_navegacao(mes, ano), mes=mes, ano=ano,
        lista=lista, resumo=transacoes.get_resumo_mes(mes, ano), contas=ACCOUNTS,
        categorias=list(CATEGORIES.keys()), tipos=TRANSACTION_TYPES,
        agendados=transacoes.get_agendados(), hoje=date.today().isoformat())


@app.post("/lancamentos/<tid>/excluir")
def excluir(tid):
    with _lock:
        transacoes.remover(tid)
    flash("Lançamento excluído (saldo revertido).", "ok")
    return redirect(url_for("lancamentos", mes=request.form.get("mes"), ano=request.form.get("ano")))


# ---------------------------------------------------------------------------
# Metas financeiras
# ---------------------------------------------------------------------------
def _voltar(rota, **kw):
    return redirect(url_for(rota, **kw))


@app.route("/metas")
def pagina_metas():
    return render_template("metas.html", pagina="metas", nav=None,
                           metas=metas.get_todas(), emojis=META_EMOJIS)


@app.post("/metas/nova")
def meta_nova():
    f = request.form
    alvo = validar_valor(f.get("alvo"))
    if not campos_obrigatorios(f.get("nome")) or alvo is None:
        flash("Informe o nome e um valor alvo válido.", "erro")
    else:
        with _lock:
            metas.adicionar(f["nome"].strip(), f.get("emoji", "🎯"), alvo,
                            (f.get("categoria") or "").strip(), int(bool(f.get("prioritaria"))))
        flash("Meta criada!", "ok")
    return _voltar("pagina_metas")


@app.post("/metas/<mid>/aportar")
def meta_aportar(mid):
    valor = validar_valor(request.form.get("valor"))
    if valor is None:
        flash("Valor inválido.", "erro")
    else:
        with _lock:
            metas.adicionar_valor(mid, valor)
        flash("Valor adicionado à meta.", "ok")
    return _voltar("pagina_metas")


@app.post("/metas/<mid>/excluir")
def meta_excluir(mid):
    with _lock:
        metas.remover(mid)
    flash("Meta removida.", "ok")
    return _voltar("pagina_metas")


# ---------------------------------------------------------------------------
# Investimentos (CDB + Bolsa)
# ---------------------------------------------------------------------------
@app.route("/investimentos")
def pagina_investimentos():
    return render_template("investimentos.html", pagina="investimentos", nav=None,
                           cdb=investimentos.get_cdb(), acoes=investimentos.get_acoes(),
                           total_acoes=investimentos.get_total_acoes(),
                           meta_inv=investimentos.get_meta_investimentos(),
                           aportes_bolsa=investimentos.get_total_aportes_bolsa(),
                           movimentacoes=investimentos.get_movimentacoes())


@app.post("/investimentos/cdb/<op>")
def cdb_operacao(op):
    valor = validar_valor(request.form.get("valor"))
    if valor is None or op not in ("aportar", "resgatar", "meta"):
        flash("Valor inválido.", "erro")
    else:
        with _lock:
            {"aportar": investimentos.aportar_cdb, "resgatar": investimentos.resgatar_cdb,
             "meta": investimentos.set_meta_cdb}[op](valor)
        flash("CDB atualizado.", "ok")
    return _voltar("pagina_investimentos")


@app.post("/investimentos/acoes/nova")
def acao_nova():
    f = request.form
    preco = validar_valor(f.get("preco"))
    try:
        qtd = int(f.get("quantidade", 0))
    except ValueError:
        qtd = 0
    if not campos_obrigatorios(f.get("ticker")) or qtd <= 0 or preco is None:
        flash("Informe ticker, quantidade e preço médio válidos.", "erro")
    else:
        with _lock:
            investimentos.adicionar_acao(f["ticker"], qtd, preco)
        flash("Ação registrada (preço médio recalculado se o ticker já existia).", "ok")
    return _voltar("pagina_investimentos")


@app.post("/investimentos/acoes/<aid>/excluir")
def acao_excluir(aid):
    with _lock:
        investimentos.remover_acao(aid)
    flash("Ação removida.", "ok")
    return _voltar("pagina_investimentos")


@app.post("/investimentos/meta")
def meta_investimentos():
    valor = validar_valor(request.form.get("valor"))
    if valor is None:
        flash("Valor inválido.", "erro")
    else:
        with _lock:
            investimentos.set_meta_investimentos(valor)
        flash("Meta de investimentos atualizada.", "ok")
    return _voltar("pagina_investimentos")


# ---------------------------------------------------------------------------
# Metas de orçamento (percentuais por categoria)
# ---------------------------------------------------------------------------
CORES_ORCAMENTO = ["#7c3aed", "#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#06b6d4", "#ef4444", "#84cc16"]


@app.route("/orcamento", methods=["GET", "POST"])
def pagina_orcamento():
    if request.method == "POST":
        try:
            mes = int(request.form.get("mes_ref", date.today().month))
            ano = int(request.form.get("ano_ref", date.today().year))
            if not 1 <= mes <= 12:
                raise ValueError
        except ValueError:
            mes, ano = date.today().month, date.today().year

        receita_raw = request.form.get("receita", "")
        receita = _valor_orcamento(receita_raw)
        fixas = []
        destinacoes = []
        erro = None
        if receita is None:
            erro = "Informe uma receita total válida, igual ou maior que zero."
        for grupo, categorias_validas, chave_prefixo, destino in (
            ("fixa", set(orcamento.categorias_despesas), "fixa_", fixas),
            ("destinacao", set(orcamento.categorias_destinacoes), "dest_", destinacoes),
        ):
            categorias = request.form.getlist(f"{chave_prefixo}categoria")
            descricoes = request.form.getlist(f"{chave_prefixo}descricao")
            valores = request.form.getlist(f"{chave_prefixo}valor")
            for ordem, (categoria, descricao, valor_raw) in enumerate(zip(categorias, descricoes, valores)):
                descricao = (descricao or "").strip()
                valor = _valor_orcamento(valor_raw, vazio_zero=True)
                if categoria not in categorias_validas:
                    erro = "Uma das categorias escolhidas não é válida."
                    break
                if valor is None:
                    erro = f"Informe um valor válido para “{descricao or categoria}”."
                    break
                if not descricao and valor == 0:
                    continue
                if not descricao and grupo == "fixa":
                    erro = f"Informe a descrição do item em {categoria}."
                    break
                destino.append({"grupo": grupo, "categoria": categoria,
                                "descricao": descricao, "valor": valor, "ordem": ordem})
            if erro:
                break

        if erro:
            plano = {"receita": receita or 0, "receita_input": receita_raw,
                     "fixas": [{"categoria": c, "descricao": d, "valor": v}
                               for c, d, v in zip(request.form.getlist("fixa_categoria"), request.form.getlist("fixa_descricao"), request.form.getlist("fixa_valor"))],
                     "destinacoes": [{"categoria": c, "descricao": d, "valor": v}
                                     for c, d, v in zip(request.form.getlist("dest_categoria"), request.form.getlist("dest_descricao"), request.form.getlist("dest_valor"))]}
            return _render_orcamento(mes, ano, plano, erro)

        periodo = f"{ano:04d}-{mes:02d}"
        with _lock:
            orcamento.salvar_planejamento(periodo, receita, fixas + destinacoes)
        flash("Planejamento mensal salvo.", "ok")
        return _voltar("pagina_orcamento", mes=mes, ano=ano, salvo=1)

    mes, ano = _mes_ano()
    periodo = f"{ano:04d}-{mes:02d}"
    return _render_orcamento(mes, ano, orcamento.carregar_planejamento(periodo),
                             limpar_rascunho=request.args.get("salvo") == "1" or request.args.get("apagado") == "1")


@app.post("/orcamento/resetar")
def orcamento_resetar():
    try:
        mes = int(request.form.get("mes_ref", date.today().month))
        ano = int(request.form.get("ano_ref", date.today().year))
        if not 1 <= mes <= 12:
            raise ValueError
    except ValueError:
        mes, ano = date.today().month, date.today().year
    with _lock:
        orcamento.limpar_planejamento(f"{ano:04d}-{mes:02d}")
    flash("Planejamento desse mês apagado.", "ok")
    return _voltar("pagina_orcamento", mes=mes, ano=ano, apagado=1)


# ---------------------------------------------------------------------------
# Regras de categorização
# ---------------------------------------------------------------------------
@app.get("/regras")
def pagina_regras():
    prefill = {k: request.args.get(k, "") for k in ("descricao", "valor", "tipo")}
    return render_template("regras.html", pagina="regras", nav=None,
                           categorias=list(CATEGORIES), campos=CAMPOS,
                           operadores=list(dict.fromkeys(CONDICOES_TEXTO + CONDICOES_NUMERICAS + CONDICOES_TIPO)),
                           acoes=ACOES_REGRA, tipos=TIPOS_REGRA, prefill=prefill)


@app.get("/api/regras")
def api_regras():
    return jsonify(db.get_regras())


@app.post("/api/regras")
def api_regra_nova():
    try:
        regra = _validar_regra(request.get_json(silent=True))
        if any(int(r["ordem"]) == regra["ordem"] for r in db.get_regras()):
            raise ValueError(f"Já existe uma regra com o número {regra['ordem']}.")
        with _lock:
            regra["id"] = db.adicionar_regra(regra)
        return jsonify(regra), 201
    except (ValueError, TypeError) as e:
        return jsonify(erro=str(e)), 400


@app.route("/api/regras/<int:rid>", methods=["PUT", "DELETE"])
def api_regra_item(rid):
    if request.method == "DELETE":
        with _lock:
            db.remover_regra(rid)
        return jsonify(ok=True)
    try:
        regra = _validar_regra(request.get_json(silent=True))
        if any(int(r["ordem"]) == regra["ordem"] and int(r["id"]) != rid for r in db.get_regras()):
            raise ValueError(f"Já existe uma regra com o número {regra['ordem']}.")
        with _lock:
            if not db.atualizar_regra(rid, regra):
                return jsonify(erro="Regra não encontrada."), 404
        regra["id"] = rid
        return jsonify(regra)
    except (ValueError, TypeError) as e:
        return jsonify(erro=str(e)), 400


@app.post("/api/regras/reordenar")
def api_reordenar_regras():
    dados = request.get_json(silent=True) or {}
    ids = dados.get("ids", [])
    existentes = {int(r["id"]) for r in db.get_regras()}
    try:
        ids = [int(i) for i in ids]
        if len(ids) != len(set(ids)) or set(ids) != existentes:
            raise ValueError("A lista de prioridades não corresponde às regras existentes.")
        with _lock:
            db.reordenar_regras(ids)
        return jsonify(ok=True)
    except (ValueError, TypeError) as e:
        return jsonify(ok=False, erro=str(e)), 400


@app.post("/api/regras/testar")
def api_testar_regra():
    try:
        regra = _validar_regra(request.get_json(silent=True))
        return jsonify(total=importador.testar_regras(regra))
    except (ValueError, TypeError) as e:
        return jsonify(erro=str(e)), 400


@app.post("/api/regras/aplicar-historico")
def api_aplicar_regras_historico():
    alteradas = 0
    regras = db.get_regras(apenas_ativas=True)
    with _lock:
        for t in db.get_transacoes():
            resultado = aplicar_regras(regras, {"descricao": t.descricao, "valor": t.valor,
                                                 "tipo": t.tipo, "conta": t.conta})
            if resultado.get("regra_id") and resultado.get("acao_regra") == "categorizar":
                categoria = resultado["categoria_sugerida"]
                if categoria != t.categoria:
                    db.atualizar_categoria_transacao(t.id, categoria)
                    alteradas += 1
    return jsonify(alteradas=alteradas)


@app.get("/regras/exportar")
def exportar_regras():
    from openpyxl import Workbook
    from io import BytesIO
    wb = Workbook(); ws = wb.active; ws.title = "Regras"
    campos = ["ordem", "ativa", "descricao", "campo", "operador", "valor", "valor2", "acao", "categoria", "tipo"]
    ws.append(campos)
    for regra in db.get_regras():
        ws.append([regra.get(k) for k in campos])
    buf = BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="regras_ket_finance.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.post("/regras/importar")
def importar_regras_xlsx():
    from openpyxl import load_workbook
    arq = request.files.get("arquivo")
    if not arq or not arq.filename.lower().endswith(".xlsx"):
        flash("Selecione um arquivo .xlsx de regras.", "erro")
        return _voltar("pagina_regras")
    try:
        ws = load_workbook(arq, read_only=True, data_only=True).active
        cabecalho = [str(c or "").strip() for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
        count = 0
        for linha in ws.iter_rows(min_row=2, values_only=True):
            dados = dict(zip(cabecalho, linha))
            if not any(v is not None for v in linha):
                continue
            regra = _validar_regra(dados)
            with _lock:
                db.adicionar_regra(regra)
            count += 1
        flash(f"{count} regra(s) importada(s).", "ok")
    except Exception as e:
        flash(f"Não foi possível importar as regras: {e}", "erro")
    return _voltar("pagina_regras")


# ---------------------------------------------------------------------------
# Importação de extrato (PDF / OFX / CSV) com tela de revisão
# ---------------------------------------------------------------------------
EXTENSOES_OK = ("pdf", "ofx", "qfx", "csv")


@app.route("/importar", methods=["GET", "POST"])
def importar():
    if request.method == "GET":
        rascunho_id = session.get("importacao_rascunho_id")
        rascunho = db.get_rascunho_importacao(rascunho_id) if rascunho_id else None
        if rascunho:
            linhas = rascunho.get("linhas", [])
            return render_template("importar.html", pagina="importar", nav=None, contas=ACCOUNTS,
                                   linhas=linhas, conta_padrao=rascunho.get("conta_padrao", ACCOUNTS[0]),
                                   arquivo=rascunho.get("arquivo", "Extrato"), categorias=list(CATEGORIES.keys()),
                                   duplicadas=sum(1 for l in linhas if l.get("duplicada")), rascunho_restaurado=True)
        return render_template("importar.html", pagina="importar", nav=None, contas=ACCOUNTS, linhas=None)

    arq = request.files.get("arquivo")
    conta = request.form.get("conta")
    if not arq or not arq.filename:
        flash("Selecione um arquivo de extrato.", "erro")
        return redirect(url_for("importar"))
    ext = arq.filename.rsplit(".", 1)[-1].lower()
    if ext not in EXTENSOES_OK or conta not in ACCOUNTS:
        flash("Formato não suportado. Use PDF, OFX ou CSV.", "erro")
        return redirect(url_for("importar"))

    # O parser trabalha com caminho de arquivo: salva num temporário e apaga em seguida
    with tempfile.NamedTemporaryFile(suffix="." + ext, delete=False) as tmp:
        arq.save(tmp.name)
    try:
        linhas = importador.ler_arquivo(tmp.name)
    except Exception as e:
        flash(f"Não foi possível ler o arquivo: {e}", "erro")
        return redirect(url_for("importar"))
    finally:
        os.remove(tmp.name)

    if not linhas:
        flash("Nenhum lançamento encontrado. Se for PDF, o layout do seu banco pode não ser reconhecido.", "erro")
        return redirect(url_for("importar"))
    rascunho_id = session.get("importacao_rascunho_id") or str(uuid.uuid4())
    session["importacao_rascunho_id"] = rascunho_id
    db.salvar_rascunho_importacao(rascunho_id, {
        "linhas": linhas, "conta_padrao": conta, "arquivo": arq.filename,
    })
    return render_template("importar.html", pagina="importar", nav=None, contas=ACCOUNTS, linhas=linhas,
                           conta_padrao=conta, arquivo=arq.filename, categorias=list(CATEGORIES.keys()),
                           duplicadas=sum(1 for l in linhas if l["duplicada"]), rascunho_restaurado=False)


@app.post("/api/importar/rascunho")
def salvar_rascunho_importacao():
    rascunho_id = session.get("importacao_rascunho_id")
    atual = db.get_rascunho_importacao(rascunho_id) if rascunho_id else None
    dados = request.get_json(silent=True)
    if not atual or not isinstance(dados, dict):
        return jsonify(ok=False, erro="Rascunho de importação não encontrado."), 404
    linhas = dados.get("linhas")
    if not isinstance(linhas, list) or len(linhas) != len(atual.get("linhas", [])):
        return jsonify(ok=False, erro="A lista de lançamentos do rascunho é inválida."), 400
    if any(not isinstance(l, dict) for l in linhas):
        return jsonify(ok=False, erro="Há um lançamento inválido no rascunho."), 400
    conta_padrao = dados.get("conta_padrao", atual.get("conta_padrao"))
    if conta_padrao not in ACCOUNTS:
        conta_padrao = atual.get("conta_padrao", ACCOUNTS[0])
    db.salvar_rascunho_importacao(rascunho_id, {
        "linhas": linhas, "conta_padrao": conta_padrao,
        "arquivo": atual.get("arquivo", "Extrato"),
    })
    return jsonify(ok=True)


@app.post("/importar/rascunho/descartar")
def descartar_rascunho_importacao():
    rascunho_id = session.pop("importacao_rascunho_id", None)
    if rascunho_id:
        db.remover_rascunho_importacao(rascunho_id)
    flash("Rascunho da importação descartado.", "ok")
    return redirect(url_for("importar"))


@app.post("/importar/confirmar")
def importar_confirmar():
    f = request.form
    aprovadas, ignoradas = [], 0
    for i in range(int(f.get("total", 0) or 0)):
        if not f.get(f"inc_{i}"):
            continue
        try:
            item = {"data": f[f"data_{i}"], "descricao": f[f"desc_{i}"].strip() or "Lançamento importado",
                    "valor": float(f[f"valor_{i}"]), "tipo": f[f"tipo_{i}"],
                    "categoria": f[f"cat_{i}"], "conta": f.get(f"conta_{i}") or f.get("conta_padrao"),
                    "investimento": f.get(f"investimento_{i}", "")}
        except (KeyError, ValueError):
            ignoradas += 1
            continue
        if (item["tipo"] not in ("Receita", "Despesa") or item["categoria"] not in CATEGORIES
                or item["conta"] not in ACCOUNTS or item["valor"] <= 0 or not validar_data(item["data"])):
            ignoradas += 1
            continue
        if item["categoria"] == "💰 Investimentos" and item["investimento"] not in ("CDB", "Bolsa de Valores"):
            ignoradas += 1
            continue
        aprovadas.append(item)

    if not aprovadas:
        flash("Nenhum lançamento válido foi selecionado.", "erro")
        return redirect(url_for("importar"))
    with _lock:
        resultado = importador.confirmar_importacao(aprovadas, f.get("conta_padrao"))
        qtd = resultado["importadas"]
    rascunho_id = session.pop("importacao_rascunho_id", None)
    if rascunho_id:
        db.remover_rascunho_importacao(rascunho_id)
    aviso = f" ({ignoradas} ignorado(s) por dados inválidos)" if ignoradas else ""
    flash(f"{qtd} lançamento(s) importado(s) com sucesso!{aviso}", "ok")
    d = aprovadas[-1]["data"]
    return redirect(url_for("lancamentos", mes=int(d[3:5]), ano=int(d[6:10])))


# ---------------------------------------------------------------------------
# Exportar Excel e recalcular saldos
# ---------------------------------------------------------------------------
@app.route("/exportar")
def exportar():
    mes = request.args.get("mes", type=int)
    ano = request.args.get("ano", type=int)
    if mes and not (1 <= mes <= 12):
        mes = ano = None
    buf, nome = gerar_excel(db, mes if ano else None, ano if mes else None)
    return send_file(buf, as_attachment=True, download_name=nome,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.post("/recalcular")
def recalcular():
    with _lock:
        db.recalcular_saldos()
    flash("Saldos recalculados a partir das transações.", "ok")
    return redirect(request.referrer or url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
