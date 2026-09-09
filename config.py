"""Configurações e constantes do sistema"""

# Cores do Tema Escuro
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'sidebar': '#0f3460',
    'card': '#533483',
    'accent': '#7c3aed',
    'success': '#10b981',
    'error': '#ef4444',
    'warning': '#f59e0b',
    'info': '#3b82f6',
    'text': '#f5f3ff',
    'text_white': 'white',
    'chart_bg': '#0a0a0a'
}

# Contas do Sistema
ACCOUNTS = [
    'Conta Corrente',
    'Receita Fixa',
    'Despesa Fixa',
    'Reserva Emergência',
    'Investimentos'
]

# Categorias com Emojis
CATEGORIES = {
    '🛒 Mercado': '🛒',
    '🍔 Restaurante': '🍔',
    '🚌 Transporte': '🚌',
    '🏠 Moradia': '🏠',
    '💡 Utilidades': '💡',
    '📶 Internet': '📶',
    '🎮 Lazer': '🎮',
    '👕 Vestuário': '👕',
    '💊 Saúde': '💊',
    '📚 Educação': '📚',
    '👨‍👩‍👧 Família': '👨‍👩‍👧',
    '💼 Trabalho': '💼',
    '🔧 Correção': '🔧',
    '📦 Outros': '📦'
}

# Emojis para Metas
META_EMOJIS = [
    '🎯', '✈️', '🚗', '🏠', '💻', '📱', '🎮', '👗', 
    '💍', '🎓', '🏊', '🎸', '📷', '🎁', '🏋️', '🛒',
    '💰', '🏦', '📈', '🎪', '🌴', '🏖️', '⛷️', '🚴'
]

# Cores fixas por categoria para gráficos
CATEGORY_COLORS = {
    '🛒 Mercado':      '#f59e0b',
    '🍔 Restaurante':  '#ef4444',
    '🚌 Transporte':   '#3b82f6',
    '🏠 Moradia':      '#8b5cf6',
    '💡 Utilidades':   '#06b6d4',
    '📶 Internet':     '#6366f1',
    '🎮 Lazer':        '#ec4899',
    '👕 Vestuário':    '#f97316',
    '💊 Saúde':        '#10b981',
    '📚 Educação':     '#14b8a6',
    '👨‍👩‍👧 Família':    '#a855f7',
    '💼 Trabalho':     '#84cc16',
    '🔧 Correção':     '#94a3b8',
    '📦 Outros':       '#64748b',
}
TRANSACTION_TYPES = ['Receita', 'Despesa', 'Transferência']

# Tipos de Investimento
INVESTMENT_TYPES = ['Bolsa de Valores', 'CDB', 'Fundos Imobiliários']

# Arquivo de Dados
DATA_FILE = 'dados_financeiros.json'  # Mantido para compatibilidade com backup/migração
DB_PATH = 'ket_finance.db'  # Banco SQLite principal

# Estrutura Inicial de Dados
INITIAL_DATA = {
    'contas': {
        'Conta Corrente': 0.0,
        'Receita Fixa': 0.0,
        'Despesa Fixa': 0.0,
        'Reserva Emergência': 0.0,
        'Investimentos': 0.0
    },
    'transacoes': [],
    'metas': [],
    'acoes': [],
    'cdb': {
        'valor': 0.0,
        'meta': 0.0
    },
    'meta_investimentos': 0.0,
    'metas_orcamento': {
        'Moradia': 30,
        'Educação': 10,
        'Reserva de Emergência': 20,
        'Investimentos': 20,
        'Lazer': 10,
        'Viagem': 10
    }
}

# Meses em Português
MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}
