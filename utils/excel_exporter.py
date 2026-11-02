"""Exportação de relatórios para Excel (somente openpyxl, sem pandas)"""
import io
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment

from config import MESES
from utils.formatters import data_para_datetime

MOEDA = 'R$ #,##0.00'
CABECALHO_FILL = PatternFill("solid", fgColor="7C3AED")
CABECALHO_FONT = Font(bold=True, color="FFFFFF")


def _aba(wb, titulo, cabecalho, linhas, colunas_moeda=()):
    ws = wb.create_sheet(titulo)
    ws.append(cabecalho)
    for c in ws[1]:
        c.fill, c.font = CABECALHO_FILL, CABECALHO_FONT
        c.alignment = Alignment(horizontal="center")
    for linha in linhas:
        ws.append(linha)
    for col in colunas_moeda:
        for cel in ws[col][1:]:
            cel.number_format = MOEDA
    for i, nome in enumerate(cabecalho):
        maior = max([len(str(nome))] + [len(str(l[i])) for l in linhas if i < len(l)] or [10])
        ws.column_dimensions[chr(65 + i)].width = min(maior + 3, 50)
    ws.freeze_panes = "A2"
    return ws


def gerar_excel(db, mes=None, ano=None):
    """Gera o relatório em memória e devolve (BytesIO, nome_do_arquivo).
    Com mes/ano, exporta só as transações daquele mês; sem eles, exporta tudo."""
    wb = Workbook()
    wb.remove(wb.active)

    _aba(wb, "Contas", ["Conta", "Saldo"],
         [[n, s] for n, s in db.get_contas().items()], colunas_moeda=("B",))

    trans = [t for t in db.get_transacoes() if not t.agendado]
    if mes and ano:
        trans = [t for t in trans
                 if (d := data_para_datetime(t.data)) and (d.month, d.year) == (mes, ano)]
    trans.sort(key=lambda t: data_para_datetime(t.data) or datetime.min)
    _aba(wb, "Transações", ["Data", "Tipo", "Categoria", "Descrição", "Valor", "Conta"],
         [[t.data, t.tipo, t.categoria, t.descricao, t.valor, t.conta] for t in trans],
         colunas_moeda=("E",))

    _aba(wb, "Metas", ["Nome", "Emoji", "Valor atual", "Valor alvo", "Prioritária"],
         [[m.nome, m.emoji, m.valor_atual, m.valor_alvo, "Sim" if m.prioritaria else "Não"]
          for m in db.get_metas()], colunas_moeda=("C", "D"))

    _aba(wb, "Ações", ["Ticker", "Quantidade", "Preço médio", "Total"],
         [[a.ticker, a.quantidade, a.preco_medio, a.quantidade * a.preco_medio]
          for a in db.get_acoes()], colunas_moeda=("C", "D"))

    cdb = db.get_cdb()
    _aba(wb, "CDB", ["Saldo", "Meta"], [[cdb["valor"], cdb["meta"]]], colunas_moeda=("A", "B"))

    cur = db.conn.execute("SELECT categoria, percentual FROM metas_orcamento")
    _aba(wb, "Orçamento", ["Categoria", "Percentual (%)"], [[r[0], r[1]] for r in cur])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    nome = (f"KetFinance_{ano}-{mes:02d}_{MESES[mes]}.xlsx" if mes and ano
            else f"KetFinance_completo_{datetime.now():%Y-%m-%d}.xlsx")
    return buf, nome


def exportar_excel(db):
    """Compatibilidade com a versão desktop: grava o relatório completo em disco."""
    buf, nome = gerar_excel(db)
    with open(nome, "wb") as f:
        f.write(buf.getvalue())
    return nome