# 💰 Salom Finance

> **Controle financeiro pessoal moderno, bonito e 100% local.**  
> Feito para quem quer organizar as finanças sem depender de apps na nuvem ou assinaturas.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![CustomTkinter](https://img.shields.io/badge/Interface-CustomTkinter-7c3aed?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Em%20desenvolvimento-f59e0b?style=flat-square)

---

## 🧭 O que é o Salom Finance?

O **Salom Finance** é um sistema desktop de controle financeiro pessoal desenvolvido em Python. Ele foi criado para ser simples de usar, visualmente agradável e completamente offline — seus dados ficam salvos no seu próprio computador, sem nenhuma conta ou servidor externo.

Com ele você registra receitas e despesas, acompanha metas de economia, controla investimentos e visualiza tudo em gráficos claros — tudo em uma única tela.

---

## 🎯 Objetivo

Oferecer uma alternativa **gratuita, privada e personalizável** aos aplicativos financeiros comerciais, com uma interface moderna e funcionalidades pensadas para o dia a dia brasileiro — incluindo parcelamento, agendamento de contas fixas e controle de CDB e bolsa de valores.

---

## 🖥️ Tecnologias Utilizadas

| Tecnologia | Função |
|---|---|
| **Python 3.8+** | Linguagem principal |
| **CustomTkinter** | Interface gráfica moderna com tema escuro |
| **Matplotlib** | Gráficos do dashboard |
| **Pandas** | Geração de relatórios Excel |
| **OpenPyXL** | Leitura e escrita de arquivos `.xlsx` |
| **PyTZ** | Fuso horário (Brasília) |
| **Python-DateUtil** | Cálculo de parcelas mensais |
| **JSON** | Persistência local dos dados |

---

## ✨ Funcionalidades

### 📊 Dashboard
- Cards com resumo de receitas, despesas e saldo do mês
- Saldos de todas as contas em tempo real
- Gráfico de barras comparando receitas e despesas

### ➕ Nova Transação
- Registro de **Receitas**, **Despesas** e **Transferências**
- **Parcelamento automático** — gera uma transação por mês automaticamente
- **Agendamento** — registre contas futuras sem afetar o saldo atual
- Categorias com emojis: 🛒 Mercado, 🏠 Moradia, 💊 Saúde, 📚 Educação e mais

### 📋 Registros
- Listagem de transações por mês com navegação ◀ ▶
- Seção separada de agendamentos futuros
- Exclusão com reversão automática do saldo

### 🎯 Metas Financeiras
- Crie metas com nome, emoji e valor alvo
- Barra de progresso visual em cada meta
- Marque metas como **prioritárias** para destaque
- Adicione valores incrementalmente conforme vai economizando

### 📈 Investimentos
- **Bolsa de Valores** — cadastre ações com ticker, quantidade e preço médio
- **CDB / Reserva de Emergência** — controle aportes e resgates com barra de progresso
- Metas de investimento com acompanhamento percentual

### 🔧 Ferramentas
- **👁 Ocultar Valores** — esconde todos os números para privacidade
- **📊 Exportar Excel** — gera relatório `.xlsx` organizado por mês em `Relatorios_YYYY/`
- **🔄 Recalcular Saldos** — reprocessa todo o histórico do zero para corrigir inconsistências

---

## 🚀 Como Instalar e Rodar

### Pré-requisito
Instale o Python em **https://www.python.org/downloads/**  
⚠️ Marque a opção **"Add Python to PATH"** durante a instalação.

### Opção 1 — Automático (recomendado)
Dê duplo clique em `setup_e_iniciar.bat`.  
Ele localiza o Python, cria o ambiente virtual, instala as dependências e abre o programa.

### Opção 2 — Manual
```bash
pip install -r requirements.txt
python main.py
```

---

## 📁 Estrutura do Projeto

```
Salom_Finance/
├── main.py                  # Ponto de entrada
├── config.py                # Constantes, cores e categorias
├── requirements.txt         # Dependências
├── setup_e_iniciar.bat      # Instalação e execução automática
├── dados_financeiros.json   # Banco de dados local (gerado automaticamente)
│
├── models/                  # Camada de dados
│   ├── database.py          # Leitura/escrita do JSON
│   └── entities.py          # Dataclasses: Transacao, Meta, Acao
│
├── controllers/             # Lógica de negócio
│   ├── transaction_controller.py
│   ├── goal_controller.py
│   └── investment_controller.py
│
├── views/                   # Interface gráfica
│   ├── main_window.py       # Janela principal e sidebar
│   ├── dashboard_view.py
│   ├── entry_view.py
│   ├── records_view.py
│   ├── goals_view.py
│   └── investments_view.py
│
└── utils/                   # Utilitários
    ├── formatters.py
    ├── validators.py
    └── excel_exporter.py
```

---

## 🔒 Privacidade

Todos os seus dados ficam **exclusivamente no seu computador** dentro do arquivo `dados_financeiros.json`.  
O Salom Finance não faz nenhuma conexão com a internet.

> 💡 Faça backup desse arquivo regularmente para não perder seus dados.

---

## 🗺️ Roadmap

- [ ] Fundos Imobiliários (FIIs)
- [ ] Gráfico de linha para fluxo de caixa mensal
- [ ] Importação de extratos OFX/CSV
- [ ] Criptografia do arquivo de dados
- [ ] Tema claro
- [ ] Instalador executável `.exe`

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Faça um fork do projeto
2. Crie uma branch: `git checkout -b feature/MinhaFuncionalidade`
3. Commit: `git commit -m '✨ Adiciona MinhaFuncionalidade'`
4. Push: `git push origin feature/MinhaFuncionalidade`
5. Abra um Pull Request

---

<div align="center">

Feito com 💜 para organizar as finanças do jeito certo.

</div>
