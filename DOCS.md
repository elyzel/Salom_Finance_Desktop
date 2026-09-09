# Ket Finance — Documentação

## Instalação

1. Instale o Python em https://www.python.org/downloads/ marcando **"Add Python to PATH"**
2. Abra o terminal na pasta do projeto e execute:
```bash
pip install -r requirements.txt
python main.py
```
Ou dê duplo clique em `setup_e_iniciar.bat` — ele instala tudo automaticamente.

> Se der erro no pandas com Python 3.13+, veja a seção **Problemas Comuns**.

---

## Estrutura do Projeto

```
Ket_Finance/
├── main.py                          # Ponto de entrada
├── config.py                        # Cores, contas, categorias, constantes
├── requirements.txt                 # Dependências
├── setup_e_iniciar.bat              # Instala dependências e inicia o programa
├── dados_financeiros.json           # Banco de dados (criado automaticamente)
│
├── models/
│   ├── database.py                  # Leitura/escrita do JSON, recalcular saldos
│   └── entities.py                  # Dataclasses: Transacao, Meta, Acao
│
├── controllers/
│   ├── transaction_controller.py    # Criar/remover transações, parcelamento, resumos
│   ├── goal_controller.py           # CRUD de metas, adicionar valores
│   └── investment_controller.py     # Ações, CDB, metas de investimento
│
├── views/
│   ├── main_window.py               # Janela principal, sidebar, navegação
│   ├── dashboard_view.py            # Cards de resumo, saldos, gráfico de barras
│   ├── entry_view.py                # Formulário de nova transação
│   ├── records_view.py              # Listagem por mês, agendamentos, exclusão
│   ├── goals_view.py                # Cards de metas com barra de progresso
│   └── investments_view.py          # CDB e bolsa de valores
│
└── utils/
    ├── formatters.py                # formatar_valor, formatar_data, mes_ano_atual
    ├── validators.py                # validar_valor, validar_data, campos_obrigatorios
    └── excel_exporter.py            # Exporta relatório .xlsx em Relatorios_YYYY/
```

---

## Arquitetura MVC

```
Views  →  Controllers  →  Models (Database)  →  dados_financeiros.json
```

- **Views** só exibem dados e capturam input do usuário
- **Controllers** contêm toda a lógica de negócio
- **Database** abstrai toda leitura/escrita do JSON
- **Utils** são funções puras sem estado, usadas por qualquer camada

---

## Regras de Negócio

- Transações **agendadas** (`agendado=1`) não afetam o saldo no momento da criação
- **Parcelamento** gera N transações independentes, cada uma com data +1 mês
- **Excluir** uma transação reverte automaticamente o saldo da conta
- **Recalcular** zera todas as contas e reprocessa o histórico completo do JSON
- **Transferência** debita a conta de origem e credita a conta destino simultaneamente

---

## Como Estender

**Adicionar categoria:**
```python
# config.py → CATEGORIES
'🆕 Nova Categoria': '🆕'
```

**Adicionar conta:**
```python
# config.py → ACCOUNTS
ACCOUNTS.append('Nova Conta')

# config.py → INITIAL_DATA['contas']
'Nova Conta': 0.0
```

**Adicionar nova view:**
1. Crie `views/nova_view.py` com classe herdando `ctk.CTkFrame`
2. Assinatura obrigatória: `__init__(self, parent, db, controllers, ocultar_valores=False)`
3. Adicione botão na sidebar em `views/main_window.py`
4. Chame `self._trocar_view(NovaView)` no método correspondente

---

## Problemas Comuns

| Problema | Solução |
|---|---|
| `pandas` falha ao instalar (Python 3.13+) | As versões no `requirements.txt` já estão corrigidas com `>=` em vez de `==`. Rode `pip install -r requirements.txt` novamente |
| `Python não reconhecido` | Reinstale o Python marcando "Add Python to PATH" |
| `ModuleNotFoundError` | Execute `pip install -r requirements.txt` |
| Saldo incorreto | Clique em "🔄 Recalcular" na sidebar |
| Tela em branco | Clique em qualquer item do menu lateral |
| Erro ao salvar JSON | Execute como administrador ou verifique permissões da pasta |

---

## Backup

O único arquivo que contém seus dados é `dados_financeiros.json`.  
Copie-o regularmente para não perder informações.  
Os relatórios Excel ficam em `Relatorios_YYYY/MM_NomeMes_YYYY.xlsx`.
