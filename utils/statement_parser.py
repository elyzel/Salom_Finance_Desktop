"""
Leitura de extratos bancários (OFX e CSV) e categorização automática.

Este módulo só INTERPRETA arquivos e devolve uma lista de dicionários.
Ele não grava nada no banco — quem decide o que salvar é o
ImportController, depois que o usuário confirma na tela de revisão.

Cada transação interpretada tem o formato:
{
    'data': '15/01/2024',
    'descricao': 'SUPERMERCADO ABC',
    'valor': 150.00,           # sempre positivo
    'tipo': 'Despesa',         # 'Receita' ou 'Despesa'
    'categoria_sugerida': '🛒 Mercado',
    'fitid': '202401150001'    # identificador único do banco (se houver, senão None)
}
"""
import csv
import io
import re
from datetime import datetime

from config import CATEGORIES


# ---------------------------------------------------------------------------
# Categorização automática por palavras-chave
# ---------------------------------------------------------------------------
# Cada chave de CATEGORIES recebe uma lista de palavras/trechos que, se
# encontrados na descrição do lançamento (sem acento, maiúsculo), indicam
# aquela categoria. A ordem importa: a primeira que bater, vence.
PALAVRAS_CHAVE_CATEGORIA = {
    '🛒 Mercado': ['MERCADO', 'SUPERMERCADO', 'ATACAD', 'HORTIFRUTI', 'CARREFOUR',
                   'PAO DE ACUCAR', 'EXTRA ', 'ASSAI', 'DIA SUPERMERCADO'],
    '🍔 Restaurante': ['IFOOD', 'RAPPI', 'RESTAURANTE', 'LANCHONETE', 'PIZZARIA',
                       'PADARIA', 'BAR ', 'MC DONALD', 'BURGER', 'HABIBS'],
    '🚌 Transporte': ['UBER', '99APP', '99POP', 'TAXI', 'METRO', 'ONIBUS',
                      'BILHETE UNICO', 'POSTO ', 'COMBUSTIVEL', 'ESTACIONAMENTO',
                      'PEDAGIO', 'IPVA'],
    '🏠 Moradia': ['ALUGUEL', 'CONDOMINIO', 'IPTU', 'IMOBILIARIA'],
    '💡 Utilidades': ['ENERGIA', 'ELETROPAULO', 'CEMIG', 'COPEL', 'CPFL',
                      'SABESP', 'COMPANHIA DE AGUA', 'GAS ENCANADO'],
    '📶 Internet': ['VIVO', 'CLARO', 'TIM ', 'OI ', 'NET SERVICOS', 'INTERNET',
                    'TELEFONIA'],
    '🎮 Lazer': ['NETFLIX', 'SPOTIFY', 'DISNEY', 'HBO', 'PRIME VIDEO', 'CINEMA',
                 'STEAM', 'PLAYSTATION', 'XBOX', 'INGRESSO'],
    '👕 Vestuário': ['RENNER', 'RIACHUELO', 'C&A', 'ZARA', 'CALCADOS', 'MODA'],
    '💊 Saúde': ['FARMACIA', 'DROGA', 'DROGARIA', 'HOSPITAL', 'CLINICA',
                 'LABORATORIO', 'PLANO DE SAUDE', 'UNIMED', 'AMIL'],
    '📚 Educação': ['ESCOLA', 'FACULDADE', 'UNIVERSIDADE', 'CURSO', 'MENSALIDADE',
                    'UDEMY', 'ALURA'],
    '💼 Trabalho': ['SALARIO', 'PROVENTOS', 'PAGAMENTO SALARIAL', 'HONORARIOS',
                    'PIX RECEBIDO', 'TED RECEBID', 'DOC RECEBID'],
}


def _sem_acento_maiusculo(texto):
    """Normaliza texto para comparação (maiúsculo, sem acentos)."""
    if not texto:
        return ''
    substituicoes = str.maketrans(
        'áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ',
        'aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN'
    )
    return texto.translate(substituicoes).upper()


def sugerir_categoria(descricao, tipo):
    """Sugere uma categoria de config.CATEGORIES com base em palavras-chave.
    Se nada bater, cai em '📦 Outros'."""
    desc_norm = _sem_acento_maiusculo(descricao)
    for categoria, palavras in PALAVRAS_CHAVE_CATEGORIA.items():
        if categoria not in CATEGORIES:
            continue
        for palavra in palavras:
            if palavra in desc_norm:
                return categoria
    return '📦 Outros'


# ---------------------------------------------------------------------------
# Parser OFX
# ---------------------------------------------------------------------------
def _parse_data_ofx(valor_data):
    """Converte data no formato OFX (AAAAMMDDHHMMSS[-3:BRT] ou AAAAMMDD)
    para DD/MM/AAAA."""
    if not valor_data:
        return None
    apenas_numeros = re.match(r'(\d{8})', valor_data.strip())
    if not apenas_numeros:
        return None
    bruta = apenas_numeros.group(1)
    try:
        return datetime.strptime(bruta, '%Y%m%d').strftime('%d/%m/%Y')
    except ValueError:
        return None


def parse_ofx(conteudo):
    """Extrai transações de um arquivo OFX (texto SGML, sem fechamento de
    tags folha — formato padrão dos bancos brasileiros).

    Retorna uma lista de dicts no formato descrito no topo do arquivo.
    """
    transacoes = []

    # Cada lançamento fica dentro de <STMTTRN>...</STMTTRN>
    blocos = re.findall(r'<STMTTRN>(.*?)</STMTTRN>', conteudo, re.DOTALL | re.IGNORECASE)

    for bloco in blocos:
        def campo(tag):
            m = re.search(rf'<{tag}>([^\r\n<]*)', bloco, re.IGNORECASE)
            return m.group(1).strip() if m else None

        data_raw = campo('DTPOSTED')
        valor_raw = campo('TRNAMT')
        memo = campo('MEMO') or campo('NAME') or 'Lançamento sem descrição'
        fitid = campo('FITID')

        data_fmt = _parse_data_ofx(data_raw)
        if data_fmt is None or valor_raw is None:
            continue  # bloco malformado, ignora esse lançamento

        try:
            valor = float(valor_raw.replace(',', '.'))
        except ValueError:
            continue

        tipo = 'Receita' if valor >= 0 else 'Despesa'
        valor_abs = abs(valor)

        transacoes.append({
            'data': data_fmt,
            'descricao': memo,
            'valor': valor_abs,
            'tipo': tipo,
            'categoria_sugerida': sugerir_categoria(memo, tipo),
            'fitid': fitid,
        })

    return transacoes


# ---------------------------------------------------------------------------
# Parser CSV
# ---------------------------------------------------------------------------
# Nomes de coluna aceitos (case-insensitive, sem acento) para cada campo.
# A maioria dos bancos/apps exporta com nomes parecidos com esses.
COLUNAS_DATA = ['DATA', 'DATE', 'DT LANCAMENTO', 'DATA LANCAMENTO']
COLUNAS_DESCRICAO = ['DESCRICAO', 'HISTORICO', 'DESCRIPTION', 'MEMO', 'LANCAMENTO', 'DETALHES']
COLUNAS_VALOR = ['VALOR', 'AMOUNT', 'VALOR (R$)', 'VALOR R$']


def _encontrar_coluna(cabecalho_norm, candidatos):
    for i, col in enumerate(cabecalho_norm):
        if col in candidatos:
            return i
    return None


def _parse_data_csv(valor_data):
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(valor_data.strip(), fmt).strftime('%d/%m/%Y')
        except (ValueError, AttributeError):
            continue
    return None


def parse_csv(conteudo):
    """Extrai transações de um CSV exportado de internet banking.
    Detecta automaticamente o separador (`,` ou `;`) e as colunas de
    data, descrição e valor pelo nome do cabeçalho.
    """
    transacoes = []

    try:
        dialect = csv.Sniffer().sniff(conteudo[:2048], delimiters=';,')
        delimitador = dialect.delimiter
    except csv.Error:
        delimitador = ';' if conteudo[:2048].count(';') > conteudo[:2048].count(',') else ','

    leitor = csv.reader(io.StringIO(conteudo), delimiter=delimitador)
    linhas = list(leitor)
    if not linhas:
        return transacoes

    cabecalho_norm = [_sem_acento_maiusculo(c).strip() for c in linhas[0]]
    idx_data = _encontrar_coluna(cabecalho_norm, COLUNAS_DATA)
    idx_desc = _encontrar_coluna(cabecalho_norm, COLUNAS_DESCRICAO)
    idx_valor = _encontrar_coluna(cabecalho_norm, COLUNAS_VALOR)

    if idx_data is None or idx_valor is None:
        raise ValueError(
            "Não foi possível identificar as colunas de Data e Valor no CSV. "
            "Verifique se o arquivo tem um cabeçalho com esses nomes."
        )

    for linha in linhas[1:]:
        if len(linha) <= max(idx_data, idx_valor):
            continue

        data_fmt = _parse_data_csv(linha[idx_data])
        if data_fmt is None:
            continue

        valor_texto = linha[idx_valor].strip().replace('R$', '').strip()
        # Trata formato brasileiro "1.234,56" e internacional "1234.56"
        if ',' in valor_texto and valor_texto.rfind(',') > valor_texto.rfind('.'):
            valor_texto = valor_texto.replace('.', '').replace(',', '.')
        try:
            valor = float(valor_texto)
        except ValueError:
            continue

        descricao = linha[idx_desc].strip() if idx_desc is not None and idx_desc < len(linha) else 'Lançamento sem descrição'
        tipo = 'Receita' if valor >= 0 else 'Despesa'
        valor_abs = abs(valor)

        transacoes.append({
            'data': data_fmt,
            'descricao': descricao,
            'valor': valor_abs,
            'tipo': tipo,
            'categoria_sugerida': sugerir_categoria(descricao, tipo),
            'fitid': None,
        })

    return transacoes


def parse_extrato(caminho_arquivo):
    """Ponto de entrada único: detecta o formato pela extensão e delega
    para o parser correto. Retorna a lista de transações interpretadas."""
    with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
        conteudo = f.read()

    extensao = caminho_arquivo.lower().rsplit('.', 1)[-1]
    if extensao in ('ofx', 'qfx'):
        return parse_ofx(conteudo)
    elif extensao == 'csv':
        return parse_csv(conteudo)
    else:
        raise ValueError(f"Formato de arquivo não suportado: .{extensao}. Use .ofx ou .csv.")
