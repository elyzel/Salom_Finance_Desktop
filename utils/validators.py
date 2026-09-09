"""Validações de entrada"""


def validar_valor(valor_str):
    """Retorna float ou None se inválido"""
    if not valor_str:
        return None
    try:
        v = str(valor_str).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        f = float(v)
        return f if f > 0 else None
    except (ValueError, AttributeError):
        return None


def validar_data(data_str):
    from utils.formatters import data_para_datetime
    return data_para_datetime(data_str) is not None


def campos_obrigatorios(*campos):
    return all(c and str(c).strip() for c in campos)
