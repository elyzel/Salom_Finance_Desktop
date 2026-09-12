# 💰 Ket Finance

Gerenciador financeiro pessoal para desktop, 100% offline e gratuito. Feito em Python para quem quer ter controle das próprias finanças sem dependência de apps pagos, assinaturas ou dados salvos na nuvem.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-7c3aed?style=flat-square)
![License](https://img.shields.io/badge/Licença-MIT-green?style=flat-square)

---

## 📌 Por que o Ket Finance?

Criei o projeto pela necessidade de ter uma ferramenta simples, bonita e totalmente privada. A maioria dos apps atuais exige conta, cobra assinatura ou limita recursos básicos. 

O Ket Finance roda direto no seu computador, salva tudo em um arquivo local e tem recursos focados na realidade brasileira (como compras parceladas, contas fixas, CDB e ações).

---

## ✨ Recursos

* **Dashboard em tempo real:** Visão geral de receitas, despesas, saldo acumulado e gráfico comparativo mensal.
* **Lançamentos flexíveis:** Suporte a receitas, despesas e transferências com parcelamento automático e agendamento de contas futuras.
* **Metas de economia:** Acompanhamento de objetivos com barras de progresso e definição de prioridades.
* **Investimentos:** Controle de carteira de Ações (ticker, preço médio e quantidade) e renda fixa/CDB.
* **Exportação para Excel:** Gera relatórios em `.xlsx` organizados por mês para auditoria ou guarda pessoal.
* **Modo Privacidade:** Botão rápido para ocultar/mostrar os valores na tela.
* **100% Offline:** Seus dados ficam salvos em um arquivo `.json` local. Nada sai da sua máquina.

---

## 🛠️ Tecnologias

* **Linguagem:** Python 3.8+
* **Interface Gráfica:** CustomTkinter (Tema escuro)
* **Gráficos & Dados:** Matplotlib, Pandas, OpenPyXL
* **Persistência:** JSON local

---

## 🚀 Como Rodar o Projeto

### Pré-requisito
Ter o Python instalado (lembre-se de marcar a opção **"Add Python to PATH"** no instalador).

### Forma rápida (Windows)
Apenas dê um duplo clique no arquivo `setup_e_iniciar.bat`. Ele cria o ambiente virtual, instala as dependências e abre a aplicação.

### Forma manual (Terminal)
```bash
# Clone o repositório
git clone [https://github.com/seu-usuario/ket-finance.git](https://github.com/seu-usuario/ket-finance.git)
cd ket-finance

# Instale as dependências
pip install -r requirements.txt

# Execute
python main.py