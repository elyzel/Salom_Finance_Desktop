"""Formatação de valores e datas"""
from datetime import datetime


def formatar_valor(valor, ocultar=False):
    if ocultar:
        return "R$ ••••••"
    try:
        return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"


def formatar_data(data_str):
    """Converte data de qualquer formato para DD/MM/AAAA"""
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(data_str, fmt).strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            pass
    return data_str


def data_para_datetime(data_str):
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(data_str, fmt)
        except (ValueError, TypeError):
            pass
    return None


def mes_ano_atual():
    now = datetime.now()
    return now.month, now.year
