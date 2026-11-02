"""Regras iniciais usadas somente na primeira criação do banco.

Depois de inseridas no SQLite, a tabela regras passa a ser a única fonte de
verdade. Estes dados não são consultados durante o uso normal da aplicação.
"""

DEFAULT_RULES = [
    # Ignorar saldos antes das demais regras.
    {"campo": "descricao", "operador": "começa com", "valor": "SALDO", "acao": "ignorar", "categoria": "", "tipo": "Todos", "descricao": "Ignorar saldos", "ordem": 10},
    {"campo": "descricao", "operador": "começa com", "valor": "SDO ", "acao": "ignorar", "categoria": "", "tipo": "Todos", "descricao": "Ignorar saldo abreviado", "ordem": 20},
    {"campo": "descricao", "operador": "contém", "valor": "SALDO DO DIA", "acao": "ignorar", "categoria": "", "tipo": "Todos", "descricao": "Ignorar saldo do dia", "ordem": 30},

    {"campo": "descricao", "operador": "contém qualquer", "valor": "MERCADO,UNISSUL,SUPERMERCADO,ATACAD,HORTIFRUTI,CARREFOUR,PAO DE ACUCAR,EXTRA,ASSAI,DIA SUPERMERCADO", "acao": "categorizar", "categoria": "🛒 Mercado", "tipo": "Todos", "descricao": "Mercados e supermercados", "ordem": 100},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "IFOOD,RAPPI,RESTAURANTE,LANCHONETE,PIZZARIA,BAR,MC DONALD,BURGER,HABIBS", "acao": "categorizar", "categoria": "🍔 Restaurante", "tipo": "Todos", "descricao": "Restaurantes e delivery", "ordem": 110},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "RSCSS SANTA CLARA,PADARIA,PANIFICADORA", "acao": "categorizar", "categoria": "🥐 Padaria", "tipo": "Todos", "descricao": "Padarias", "ordem": 120},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "THE BEST,LUIGI", "acao": "categorizar", "categoria": "🍦 Sorveteria", "tipo": "Todos", "descricao": "Sorveterias", "ordem": 130},
    {"campo": "descricao", "operador": "contém", "valor": "FATURA PAGA ITAU PLATINA", "acao": "categorizar", "categoria": "💳 Cartão de Crédito", "tipo": "Todos", "descricao": "Fatura cartão Itaú", "ordem": 140},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "UBER,99APP,99POP,TAXI,METRO,ONIBUS,BILHETE UNICO,POSTO,COMBUSTIVEL,ESTACIONAMENTO,PEDAGIO,IPVA", "acao": "categorizar", "categoria": "🚌 Transporte", "tipo": "Todos", "descricao": "Transporte e combustível", "ordem": 150},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "ALUGUEL,TRIBUTO,VOLUY,CEMIG,CONDOMINIO,IPTU,IMOBILIARIA", "acao": "categorizar", "categoria": "🏠 Moradia", "tipo": "Todos", "descricao": "Moradia", "ordem": 160},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "ENERGIA,ROYAL,ELETROPAULO,CEMIG,COPEL,CPFL,SABESP,COMPANHIA DE AGUA,GAS ENCANADO", "acao": "categorizar", "categoria": "💡 Utilidades", "tipo": "Todos", "descricao": "Utilidades", "ordem": 170},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "VIVO,INT PRE-PAGO,CLARO,TIM,OI,NET SERVICOS,INTERNET,TELEFONIA", "acao": "categorizar", "categoria": "📶 Internet", "tipo": "Todos", "descricao": "Internet e telefonia", "ordem": 180},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "NETFLIX,SPOTIFY,DISNEY,HBO,PRIME VIDEO,CINEMA,STEAM,PLAYSTATION,XBOX,INGRESSO", "acao": "categorizar", "categoria": "🎮 Lazer", "tipo": "Todos", "descricao": "Lazer e streaming", "ordem": 190},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "RENNER,RIACHUELO,C&A,ZARA,CALCADOS,MODA", "acao": "categorizar", "categoria": "👕 Vestuário", "tipo": "Todos", "descricao": "Vestuário", "ordem": 200},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "FARMACIA,NATUS FARMA,DROGA,DROGARIA,HOSPITAL,CLINICA,LABORATORIO,PLANO DE SAUDE,UNIMED,AMIL", "acao": "categorizar", "categoria": "💊 Saúde", "tipo": "Todos", "descricao": "Saúde", "ordem": 210},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "ESCOLA,PAG BOLETO FUNDACAO INSTITUTO NACIONAL,FACULDADE,UNIVERSIDADE,CURSO,MENSALIDADE,UDEMY,ALURA", "acao": "categorizar", "categoria": "📚 Educação", "tipo": "Todos", "descricao": "Educação", "ordem": 220},
    {"campo": "descricao", "operador": "contém qualquer", "valor": "SALARIO,PROVENTOS,PAGAMENTO SALARIAL,HONORARIOS,PIX RECEBIDO,TED,DOC RECEBID", "acao": "categorizar", "categoria": "💼 Trabalho", "tipo": "Receita", "descricao": "Receitas de trabalho", "ordem": 230},
]
