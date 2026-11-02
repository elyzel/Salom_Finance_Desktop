"""Motor de regras do Ket Finance.

As regras são lidas do SQLite e avaliadas de cima para baixo.
A primeira regra ativa que casar é a regra aplicada.
"""

import re
import unicodedata


CAMPOS = {
    "descricao": "Descrição",
    "valor": "Valor",
    "tipo": "Tipo",
    "conta": "Conta",
}

CONDICOES_TEXTO = [
    "contém",
    "não contém",
    "começa com",
    "termina com",
    "igual a",
    "contém qualquer um de",
    "contém qualquer",
]

CONDICOES_NUMERICAS = [
    "igual a",
    "maior que",
    "maior ou igual a",
    "menor que",
    "menor ou igual a",
    "entre",
]

CONDICOES_TIPO = ["é", "não é"]


def normalizar_texto(valor):
    texto = "" if valor is None else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.upper().strip()


def converter_numero(valor):
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except (ValueError, TypeError):
        return None


def condicao_texto(atual, alvo, operador):
    atual = normalizar_texto(atual)
    alvo = normalizar_texto(alvo)

    if operador == "contém":
        return alvo in atual
    if operador == "não contém":
        return alvo not in atual
    if operador == "começa com":
        return atual.startswith(alvo)
    if operador == "termina com":
        return atual.endswith(alvo)
    if operador == "igual a":
        return atual == alvo
    if operador in ("contém qualquer um de", "contém qualquer"):
        valores = [
            normalizar_texto(v)
            for v in re.split(r"[,;|]", alvo)
            if normalizar_texto(v)
        ]
        return any(v in atual for v in valores)

    return False


def condicao_numerica(atual, alvo, alvo2, operador):
    atual = converter_numero(atual)
    alvo = converter_numero(alvo)
    if atual is None or alvo is None:
        return False

    if operador == "igual a":
        return abs(atual - alvo) < 0.005
    if operador == "maior que":
        return atual > alvo
    if operador == "maior ou igual a":
        return atual >= alvo
    if operador == "menor que":
        return atual < alvo
    if operador == "menor ou igual a":
        return atual <= alvo
    if operador == "entre":
        alvo2 = converter_numero(alvo2)
        if alvo2 is None:
            return False
        return min(alvo, alvo2) <= atual <= max(alvo, alvo2)

    return False


def regra_casa(regra, transacao):
    if not regra.get("ativa", True):
        return False

    campo = regra.get("campo", "descricao")
    if regra.get("tipo", "Todos") not in (None, "", "Todos"):
        if normalizar_texto(transacao.get("tipo")) != normalizar_texto(regra["tipo"]):
            return False
    operador = regra.get("operador", "contém")
    atual = transacao.get(campo, "")
    alvo = regra.get("valor", "")
    alvo2 = regra.get("valor2", "")

    if campo in ("descricao", "conta"):
        return condicao_texto(atual, alvo, operador)

    if campo == "tipo":
        atual = normalizar_texto(atual)
        alvo = normalizar_texto(alvo)
        if operador in ("é", "igual a"):
            return atual == alvo
        if operador == "não é":
            return atual != alvo
        return False

    if campo == "valor":
        return condicao_numerica(atual, alvo, alvo2, operador)

    return False


def aplicar_regras(regras, transacao):
    resultado = dict(transacao)
    resultado.update({
        "categoria_sugerida": "📦 Outros",
        "acao_regra": "categorizar",
        "regra_id": None,
        "regra_numero": None,
        "regra_aplicada": None,
        "selecionada": True,
        "investimento_pendente": False,
        "ignorar": False,
    })

    for regra in regras:
        if not regra_casa(regra, transacao):
            continue

        resultado["regra_id"] = regra.get("id")
        resultado["regra_numero"] = regra.get("ordem")
        resultado["regra_aplicada"] = (
            regra.get("descricao") or f"Regra #{regra.get('ordem', '')}"
        )

        acao = regra.get("acao", "categorizar")
        resultado["acao_regra"] = acao

        if acao == "ignorar":
            resultado["selecionada"] = False
            resultado["ignorar"] = True
        elif acao == "desmarcar":
            resultado["selecionada"] = False
        elif acao == "categorizar":
            resultado["categoria_sugerida"] = regra.get("categoria") or "📦 Outros"
            if resultado["categoria_sugerida"] in ("💰 Investimentos", "📈 Investimentos"):
                resultado["investimento_pendente"] = True

        return resultado

    return resultado


def descricao_regra(regra):
    campo = CAMPOS.get(regra.get("campo"), regra.get("campo", "Descrição"))
    operador = regra.get("operador", "contém")
    valor = regra.get("valor", "")

    if operador == "entre":
        condicao = f"entre {valor} e {regra.get('valor2', '')}"
    else:
        condicao = f"{operador} {valor}"

    acao = regra.get("acao", "categorizar")
    if acao == "categorizar":
        destino = regra.get("categoria") or "📦 Outros"
    elif acao == "desmarcar":
        destino = "Desmarcar"
    else:
        destino = "Ignorar"

    return f"Se {campo} {condicao} → {destino}"
