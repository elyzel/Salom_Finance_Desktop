# 🏗️ Ket Finance - Arquitetura e Estrutura

> Documentação técnica completa para IA's e desenvolvedores entenderem rapidamente o projeto.

---

## 📐 Arquitetura MVC

```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   VIEWS     │ ───> │ CONTROLLERS  │ ───> │   MODELS     │
│  (Interface)│ <─── │   (Lógica)   │ <─── │   (Dados)    │
└─────────────┘      └──────────────┘      └──────────────┘
       │                                            │
       └────────────────────────────────────────────┘
                    config.py + utils/
```

---

## 📂 Estrutura de Arquivos

```
Ket_Finance/
│
├── main.py                          # Entry point - inicializa MainWindow
├── config.py                        # Constantes globais (cores, categorias, paths)
├── requirements.txt                 # Dependências (pandas>=2.2.0 para Python 3.14)
├── KetFinance.bat                   # Launcher com verificação de dependências
├── KetFinance_Icone.ico             # Ícone da aplicação
├── dados_financeiros.json           # Banco de dados local (auto-gerado)
├── metas_orcamento.xlsx             # Arquivo Excel de metas de orçamento (auto-gerado)
│
├── models/                          # Camada de Dados
│   ├── __init__.py
│   ├── database.py                  # DatabaseManager - CRUD do JSON
│   └── entities.py                  # Dataclasses: Transacao, Meta, Acao
│
├── controllers/                     # Camada de Lógica
│   ├── __init__.py
│   ├── transaction_controller.py    # Lógica de transações e parcelamento
│   ├── goal_controller.py           # Lógica de objetivos financeiros
│   ├── investment_controller.py     # Lógica de investimentos (ações/CDB)
│   └── budget_controller.py         # Lógica de metas de orçamento
│
├── views/                           # Camada de Interface
│   ├── __init__.py
│   ├── main_window.py               # Janela principal + sidebar
│   ├── dashboard_view.py            # Dashboard com gráficos
│   ├── entry_view.py                # Formulário de nova transação
│   ├── records_view.py              # Listagem de transações
│   ├── goals_view.py                # Gerenciamento de objetivos
│   ├── investments_view.py          # Gerenciamento de investimentos
│   └── budget_goals_view.py         # Metas de orçamento com gráfico donut
│
└── utils/                           # Utilitários
    ├── __init__.py
    ├── formatters.py                # Formatação de moeda e datas
    ├── validators.py                # Validação de inputs
    └── excel_exporter.py            # Exportação de relatórios
```

---

## 🗄️ Estrutura de Dados

### Banco de Dados Principal: SQLite (ket_finance.db)

O projeto utiliza **SQLite** como banco de dados principal desde a versão 1.0. O arquivo `dados_financeiros.json` é mantido apenas para compatibilidade com backups/migrações antigas.

**Tabelas do SQLite:**
- `contas` - Saldo de cada conta
- `transacoes` - Todas as transações (receitas, despesas, transferências)
- `metas` - Metas financeiras
- `acoes` - Ações da bolsa de valores
- `cdb` - Saldo e meta do CDB
- `metas_orcamento` - Percentuais de orçamento por categoria
- `meta_investimentos` - Meta total de investimentos

### dados_financeiros.json (Legado/Backup)
```json
{
  "contas": {
    "Carteira": 0.0,
    "Banco": 0.0,
    "Poupança": 0.0
  },
  "transacoes": [
    {
      "id": "uuid-string",
      "tipo": "Receita|Despesa|Transferência",
      "valor": 1500.0,
      "categoria": "💼 Salário",
      "descricao": "Salário Março",
      "conta": "Banco",
      "data": "2024-03-01",
      "agendada": false,
      "parcelamento": {
        "total_parcelas": 12,
        "parcela_atual": 1,
        "id_grupo": "uuid-grupo"
      }
    }
  ],
  "metas": [
    {
      "id": "uuid-string",
      "nome": "Viagem",
      "emoji": "✈️",
      "valor_alvo": 5000.0,
      "valor_atual": 1200.0,
      "prioritaria": true
    }
  ],
  "acoes": [
    {
      "id": "uuid-string",
      "ticker": "PETR4",
      "quantidade": 100,
      "preco_medio": 28.50
    }
  ],
  "cdb": {
    "saldo": 10000.0,
    "meta": 50000.0
  },
  "metas_orcamento": {
    "Moradia": 30,
    "Educação": 10,
    "Reserva de Emergência": 20,
    "Investimentos": 20,
    "Lazer": 10,
    "Viagem": 10
  }
}
```

---

## 🎨 Sistema de Cores (config.py)

### Paleta Principal
```python
COLORS = {
    "bg_primary": "#1a1a2e",      # Fundo principal
    "bg_secondary": "#16213e",    # Fundo secundário
    "bg_card": "#0f3460",         # Cards
    "accent": "#7c3aed",          # Roxo (destaque)
    "text": "#e0e0e0",            # Texto principal
    "text_secondary": "#a0a0a0",  # Texto secundário
    "success": "#10b981",         # Verde (receitas)
    "danger": "#ef4444",          # Vermelho (despesas)
    "warning": "#f59e0b",         # Amarelo (avisos)
    "info": "#3b82f6"             # Azul (informações)
}
```

### Cores por Categoria
```python
CATEGORY_COLORS = {
    "💼 Salário": "#10b981",
    "🛒 Mercado": "#ef4444",
    "🏠 Moradia": "#f59e0b",
    "🚗 Transporte": "#3b82f6",
    # ... 20+ categorias com cores fixas
}
```

---

## 🔄 Fluxo de Dados

### 1. Nova Transação
```
User Input (entry_view.py)
    ↓
TransactionController.adicionar_transacao()
    ↓
DatabaseManager.adicionar_transacao()
    ↓
Atualiza saldo da conta
    ↓
Salva JSON
    ↓
Atualiza Dashboard
```

### 2. Parcelamento Automático
```
User seleciona "Parcelar" + número de parcelas
    ↓
TransactionController gera N transações
    ↓
Cada transação tem mesmo id_grupo
    ↓
Datas incrementadas mensalmente (dateutil.relativedelta)
    ↓
Apenas primeira parcela afeta saldo atual
    ↓
Demais marcadas como "agendada=True"
```

### 3. Recálculo de Saldos
```
DatabaseManager.recalcular_saldos()
    ↓
Zera todos os saldos
    ↓
Ordena transações por data
    ↓
Processa apenas transações não-agendadas
    ↓
Aplica receitas/despesas/transferências
    ↓
Salva estado final
```

---

## 🧩 Componentes Principais

### models/database.py - DatabaseManager
**Responsabilidade**: Persistência e CRUD do JSON

**Métodos Principais**:
- `carregar_dados()` - Lê JSON ou cria estrutura padrão
- `salvar_dados()` - Escreve JSON com indent=2
- `adicionar_transacao(transacao)` - Insere e atualiza saldo
- `remover_transacao(id)` - Remove e reverte saldo
- `recalcular_saldos()` - Reprocessa todo histórico
- `adicionar_meta(meta)` / `atualizar_meta(id, campo, valor)`
- `adicionar_acao(acao)` / `remover_acao(id)`
- `atualizar_cdb(operacao, valor)` - "aporte" ou "resgate"

### controllers/transaction_controller.py - TransactionController
**Responsabilidade**: Lógica de negócio de transações

**Métodos Principais**:
- `adicionar_transacao(tipo, valor, categoria, descricao, conta, data, agendada, parcelamento)`
- `remover_transacao(id)` - Remove transação ou grupo inteiro se parcelada
- `listar_transacoes_mes(ano, mes)` - Filtra por mês
- `listar_agendadas()` - Retorna transações futuras
- `get_resumo_mes(ano, mes)` - Soma receitas/despesas do mês
- `get_resumo_ultimos_meses(n=6)` - Retorna lista de dicts com receitas/despesas dos últimos N meses
- `get_gastos_por_categoria(ano, mes)` - Agrupa despesas por categoria

**Lógica de Parcelamento**:
```python
if parcelamento:
    id_grupo = str(uuid.uuid4())
    for i in range(1, total_parcelas + 1):
        data_parcela = data_base + relativedelta(months=i-1)
        agendada = (i > 1)  # Primeira não é agendada
        transacao = Transacao(
            id=str(uuid.uuid4()),
            tipo=tipo,
            valor=valor,
            # ...
            parcelamento={
                "total_parcelas": total_parcelas,
                "parcela_atual": i,
                "id_grupo": id_grupo
            }
        )
        db.adicionar_transacao(transacao)
```

### controllers/goal_controller.py - GoalController
**Responsabilidade**: Lógica de objetivos financeiros

**Métodos Principais**:
- `adicionar_meta(nome, emoji, valor_alvo, prioritaria)`
- `adicionar_valor_meta(id, valor)` - Incrementa progresso
- `marcar_prioritaria(id, prioritaria)` - Toggle prioridade
- `remover_meta(id)`
- `listar_metas()` - Retorna todas ordenadas (prioritárias primeiro)

### controllers/investment_controller.py - InvestmentController
**Responsabilidade**: Lógica de investimentos

**Métodos Principais**:
- `adicionar_acao(ticker, quantidade, preco_medio)`
- `remover_acao(id)`
- `listar_acoes()` - Retorna todas as ações
- `get_total_investido_acoes()` - Soma quantidade * preco_medio
- `atualizar_cdb(operacao, valor)` - "aporte" ou "resgate"
- `get_cdb_info()` - Retorna {"saldo": float, "meta": float}

### controllers/budget_controller.py - BudgetController
**Responsabilidade**: Lógica de metas de orçamento

**Métodos Principais**:
- `carregar_metas_orcamento()` - Carrega do JSON ou retorna padrão
- `salvar_metas_orcamento(metas)` - Salva no JSON e Excel
- `carregar_do_excel()` - Carrega do arquivo metas_orcamento.xlsx
- `resetar_valores()` - Reseta para valores padrão
- `validar_total(metas)` - Valida se soma <= 100%

**Valores Padrão**:
```python
{
    "Moradia": 30,
    "Educação": 10,
    "Reserva de Emergência": 20,
    "Investimentos": 20,
    "Lazer": 10,
    "Viagem": 10
}
```

### views/main_window.py - MainWindow
**Responsabilidade**: Janela principal e navegação

**Estrutura**:
```python
class MainWindow(ctk.CTk):
    def __init__(self):
        # Configuração da janela
        self.title("Ket Finance")
        self.iconbitmap("KetFinance_Icone.ico")
        
        # Layout: sidebar (esquerda) + content (direita)
        self.sidebar = ctk.CTkFrame(master=self, width=200)
        self.content = ctk.CTkFrame(master=self)
        
        # Botões de navegação
        botoes = [
            ("📊 Dashboard", self.mostrar_dashboard),
            ("➕ Nova Transação", self.mostrar_entrada),
            ("📋 Registros", self.mostrar_registros),
            ("🏆 Objetivos", self.mostrar_metas),
            ("📈 Investimentos", self.mostrar_investimentos),
            ("🎯 Metas de Orçamento", self.mostrar_metas_orcamento)
        ]
```

**Navegação**:
- Cada botão chama método `mostrar_*()` que limpa `self.content` e instancia nova view
- Views recebem `parent=self.content` e `main_window=self` para callbacks

### views/dashboard_view.py - DashboardView
**Responsabilidade**: Visualização de dados financeiros

**Estrutura**:
- **Scrollable Frame** contendo duas seções principais
- **Seção 1: Receitas vs Despesas**
  - 3 cards: Receitas, Despesas, Saldo (com indicador ↑/↓)
  - Gráfico de barras agrupadas dos últimos 6 meses
- **Seção 2: Gastos por Categoria**
  - Gráfico de rosca (donut chart) com categorias
  - Lista detalhada com barras de progresso

**Gráficos Matplotlib**:
```python
# Configuração para evitar warnings
fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
# Não usar plt.tight_layout()

# Cores consistentes via CATEGORY_COLORS
colors = [CATEGORY_COLORS.get(cat, "#666666") for cat in categorias]
```

### views/entry_view.py - EntryView
**Responsabilidade**: Formulário de nova transação

**Campos**:
- Tipo (Receita/Despesa/Transferência)
- Valor (validado como float)
- Categoria (dropdown com emojis)
- Descrição (opcional)
- Conta (dropdown: Carteira/Banco/Poupança)
- Data (DateEntry com formato DD/MM/YYYY)
- Agendar? (checkbox)
- Parcelar? (checkbox + entry de número de parcelas)

**Validação**:
```python
if not valor_str or float(valor_str) <= 0:
    messagebox.showerror("Erro", "Valor inválido")
    return
```

### views/records_view.py - RecordsView
**Responsabilidade**: Listagem de transações

**Funcionalidades**:
- Navegação mensal com botões ◀ ▶
- Seção "Transações do Mês" (não-agendadas)
- Seção "Agendamentos Futuros" (agendadas)
- Botão de exclusão por transação
- Indicador de parcelamento: "Parcela X/Y"

### views/goals_view.py - GoalsView
**Responsabilidade**: Gerenciamento de objetivos

**Funcionalidades**:
- Formulário: nome, emoji, valor alvo, checkbox prioritária
- Lista de metas com:
  - Barra de progresso (valor_atual / valor_alvo)
  - Botão "Adicionar Valor"
  - Botão "Marcar Prioritária" (toggle)
  - Botão "Remover"
- Metas prioritárias aparecem primeiro

### views/investments_view.py - InvestmentsView
**Responsabilidade**: Gerenciamento de investimentos

**Seções**:
1. **Bolsa de Valores**
   - Formulário: ticker, quantidade, preço médio
   - Lista de ações com total investido
   - Botão remover por ação

2. **CDB / Reserva de Emergência**
   - Card com saldo atual e meta
   - Barra de progresso
   - Botões "Aportar" e "Resgatar"

### views/budget_goals_view.py - BudgetGoalsView
**Responsabilidade**: Metas de orçamento com visualização interativa

**Layout**: Dois painéis lado a lado

**Painel Esquerdo - Visualização**:
- Gráfico de rosca (donut) com Matplotlib
- Mostra proporção de cada categoria
- Centro do donut: percentual total alocado
- Legenda em duas colunas com cores
- Botão "Resetar Valores"

**Painel Direito - Controle**:
- 6 sliders (CTkSlider) com cores personalizadas:
  - Moradia (roxo/violeta)
  - Educação (azul claro)
  - Reserva de Emergência (rosa)
  - Investimentos (roxo escuro)
  - Lazer (laranja)
  - Viagem (amarelo/dourado)
- Label de percentual ao lado de cada slider
- Validação em tempo real (total <= 100%)
- Aviso vermelho se ultrapassar 100%
- Botão "Salvar" (amarelo/dourado)

**Funcionalidades**:
- Sliders de 0-100% com passos de 5%
- Gráfico atualiza em tempo real ao mover slider
- Bloqueia valores que ultrapassam 100%
- Salva no JSON e Excel simultaneamente
- Carrega valores salvos ao abrir
- Reset para valores padrão

---

## 🛠️ Utilitários

### utils/formatters.py
```python
def formatar_moeda(valor: float) -> str:
    """Retorna 'R$ 1.234,56'"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data_str: str) -> str:
    """Converte 'YYYY-MM-DD' para 'DD/MM/YYYY'"""
```

### utils/validators.py
```python
def validar_valor(valor_str: str) -> bool:
    """Valida se string é float positivo"""

def validar_data(data_str: str) -> bool:
    """Valida formato DD/MM/YYYY"""
```

### utils/excel_exporter.py
```python
def exportar_relatorio(ano: int, mes: int):
    """
    Gera arquivo Excel em Relatorios_YYYY/relatorio_MM_YYYY.xlsx
    Colunas: Data, Tipo, Categoria, Descrição, Valor, Conta
    """
```

---

## ⚙️ Configurações Importantes

### Python Version
- **Mínimo**: Python 3.8
- **Testado**: Python 3.14
- **Nota**: pandas>=2.2.0 necessário para Python 3.14

### Dependencies (requirements.txt)
```
customtkinter>=5.2.0
matplotlib>=3.7.0
pandas>=2.2.0
openpyxl>=3.1.0
pytz>=2023.3
python-dateutil>=2.8.2
tkcalendar>=1.6.1
```

### Timezone
- **Padrão**: America/Sao_Paulo (pytz)
- **Usado em**: Geração de datas de parcelamento

### Encoding
- **JSON**: UTF-8 com ensure_ascii=False
- **Excel**: UTF-8

---

## 🚀 Inicialização

### Fluxo de Startup
```
1. KetFinance.bat (opcional)
   ↓ Verifica Python instalado
   ↓ Verifica dependências (pip show)
   ↓ Instala faltantes (pip install)
   ↓
2. python main.py
   ↓
3. MainWindow.__init__()
   ↓ Carrega ícone
   ↓ Cria sidebar + content
   ↓ Mostra Dashboard por padrão
   ↓
4. DashboardView carrega dados via controllers
   ↓
5. DatabaseManager.carregar_dados()
   ↓ Se JSON não existe, cria estrutura padrão
   ↓ Se existe, carrega e valida estrutura
```

---

## 🔐 Segurança e Privacidade

- **Armazenamento**: 100% local, sem conexão internet
- **Backup**: Usuário deve copiar `dados_financeiros.json` manualmente
- **Criptografia**: Não implementada (roadmap futuro)
- **Validação**: Inputs validados antes de salvar
- **Integridade**: Função `recalcular_saldos()` corrige inconsistências

---

## 🐛 Debugging

### Logs
- Não há sistema de logs implementado
- Erros aparecem via `messagebox.showerror()`

### Problemas Comuns

**1. Saldos Inconsistentes**
```python
# Solução: Usar ferramenta "Recalcular Saldos"
db.recalcular_saldos()
```

**2. Matplotlib Warnings**
```python
# Evitar: plt.tight_layout()
# Usar: fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
```

**3. Pandas Installation Error (Python 3.14)**
```bash
# Solução: Usar versão >= ao invés de ==
pandas>=2.2.0  # ✅
pandas==2.1.0  # ❌
```

---

## 📊 Performance

### Otimizações Implementadas
- JSON carregado uma vez no início
- Transações filtradas por mês (não carrega tudo)
- Gráficos renderizados sob demanda
- Sem queries complexas (dados em memória)

### Limitações
- Não testado com >10.000 transações
- Gráficos podem ficar lentos com muitos meses
- JSON pode crescer indefinidamente

---

## 🎯 Convenções de Código

### Naming
- **Classes**: PascalCase (TransactionController)
- **Métodos**: snake_case (adicionar_transacao)
- **Constantes**: UPPER_SNAKE_CASE (CATEGORY_COLORS)
- **Privados**: Prefixo _ (_validar_estrutura)

### Imports
```python
# Ordem:
1. Standard library (json, datetime, uuid)
2. Third-party (customtkinter, matplotlib, pandas)
3. Local (from models import, from controllers import)
```

### Docstrings
- Não obrigatórias (código minimalista)
- Usadas apenas em funções complexas

---

## 🔄 Changelog Principais

### v1.0 (Atual)
- ✅ Arquitetura MVC completa
- ✅ Dashboard com 2 seções (Receitas vs Despesas + Gastos por Categoria)
- ✅ Parcelamento automático com relativedelta
- ✅ Agendamento de transações futuras
- ✅ Objetivos financeiros (renomeado de "Metas")
- ✅ Investimentos (Ações + CDB)
- ✅ Metas de Orçamento com gráfico donut interativo
- ✅ Exportação Excel
- ✅ Recálculo de saldos
- ✅ Ícone customizado
- ✅ Launcher batch com verificação de dependências
- ✅ Compatibilidade Python 3.14

### Mudanças Recentes
- **Dashboard**: Unificado em single scroll view (antes era tabbed)
- **Gráficos**: Adicionado grouped bar chart de 6 meses + donut chart
- **Cores**: CATEGORY_COLORS fixas para consistência visual
- **Menu**: "🎯 Metas" → "🏆 Objetivos"
- **Novo Menu**: "🎯 Metas de Orçamento" com sliders interativos e gráfico donut
- **Persistência Dupla**: Metas de orçamento salvas em JSON + Excel
- **Dependencies**: Versões >= para compatibilidade futura

---

## 📝 Notas para IA's

### Ao Modificar Código
1. **Sempre manter minimalismo** - código enxuto e direto
2. **Não remover funcionalidades** - apenas adicionar ou refatorar
3. **Testar compatibilidade** - Python 3.8+ e 3.14
4. **Manter padrão MVC** - não misturar camadas
5. **Usar cores de config.py** - não hardcodar cores
6. **Validar inputs** - sempre antes de salvar
7. **Atualizar este doc** - se arquitetura mudar

### Ao Adicionar Features
1. Criar entidade em `models/entities.py` se necessário
2. Adicionar métodos CRUD em `models/database.py`
3. Criar controller em `controllers/`
4. Criar view em `views/`
5. Adicionar botão em `main_window.py` se for nova tela
6. Atualizar `config.py` se precisar de constantes
7. Documentar aqui em ARCHITECTURE.md

### Padrões de Resposta
- **Leitura de código**: Sempre usar `fsRead` para múltiplos arquivos de uma vez
- **Modificação**: Usar `fsReplace` com múltiplos diffs no mesmo arquivo
- **Criação**: Usar `fsWrite` com código completo
- **Estrutura**: Usar `listDirectory` antes de modificar

---

## 🔗 Referências Rápidas

### Arquivos Críticos
- `main.py` - Entry point
- `config.py` - Todas as constantes
- `models/database.py` - Toda persistência
- `views/main_window.py` - Navegação principal
- `dados_financeiros.json` - Banco de dados

### Métodos Mais Usados
- `DatabaseManager.carregar_dados()`
- `DatabaseManager.salvar_dados()`
- `TransactionController.adicionar_transacao()`
- `TransactionController.get_resumo_mes()`
- `MainWindow.mostrar_dashboard()`

### Cores Principais
- Verde: `#10b981` (receitas/sucesso)
- Vermelho: `#ef4444` (despesas/erro)
- Roxo: `#7c3aed` (accent/destaque)
- Fundo: `#1a1a2e` (background)

---

<div align="center">

**Documentação atualizada em**: 2024  
**Versão do projeto**: 1.0  
**Python**: 3.8+ (testado em 3.14)

</div>
