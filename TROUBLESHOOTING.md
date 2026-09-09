# 🔧 Troubleshooting - Ket Finance

> Documentação de erros comuns e suas soluções

---

## 📋 Índice de Erros

1. [Erro: Dependências Faltando (Múltiplos Pythons)](#erro-1-dependências-faltando-múltiplos-pythons)
2. [Erro: ModuleNotFoundError após instalar bibliotecas](#erro-2-modulenotfounderror-após-instalar-bibliotecas)
3. [Erro: pip não reconhecido](#erro-3-pip-não-reconhecido)
4. [Erro: Matplotlib warnings](#erro-4-matplotlib-warnings)
5. [Erro: Pandas installation error (Python 3.14)](#erro-5-pandas-installation-error-python-314)

---

## Erro 1: Dependências Faltando (Múltiplos Pythons)

### 🔴 Sintomas
```
Dependências faltando: customtkinter, matplotlib, pandas...
Execute: pip install -r requirements.txt
```

Mesmo após executar `pip install -r requirements.txt` e ver:
```
Requirement already satisfied: customtkinter>=5.2.2
Requirement already satisfied: matplotlib>=3.9.0
...
```

O programa continua dizendo que as dependências estão faltando.

---

### 🔍 Causa Raiz

**Você tem MÚLTIPLAS instalações do Python no computador!**

O que acontece:
1. Quando você executa `pip install`, as bibliotecas são instaladas no **Python A**
2. Quando você executa `python main.py`, está usando o **Python B** (que não tem as bibliotecas)

**Como identificar:**

Execute este comando:
```bash
where python
```

Se aparecer mais de um caminho, você tem múltiplos Pythons:
```
C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe
C:\Python39\python.exe
C:\Program Files\Python\python.exe
```

---

### ✅ Solução 1: Usar o caminho completo do Python correto

**Passo 1:** Descubra onde as bibliotecas foram instaladas

Execute:
```bash
pip show customtkinter
```

Procure pela linha `Location:`. Exemplo:
```
Location: C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages
```

Isso significa que o Python correto está em:
```
C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

**Passo 2:** Execute o programa com o caminho completo

```bash
cd C:\Users\Administrador\Documents\Ket_Finance
C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe main.py
```

---

### ✅ Solução 2: Atualizar o KetFinance.bat (PERMANENTE)

O arquivo `KetFinance.bat` foi atualizado para detectar automaticamente o Python correto:

```batch
REM Verificar se existe o Python 3.14 específico
if exist "C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    set PYTHON_EXE=C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe
    echo  [OK] Python 3.14 encontrado!
) else (
    set PYTHON_EXE=python
    echo  [INFO] Usando Python do PATH
)
```

Agora basta dar duplo clique no `KetFinance.bat` que ele usa o Python correto automaticamente!

---

### ✅ Solução 3: Ajustar o PATH do Windows (Avançado)

Se quiser que o comando `python` sempre use o Python correto:

1. Pressione `Windows + R`
2. Digite: `sysdm.cpl`
3. Aba "Avançado" → "Variáveis de Ambiente"
4. Em "Variáveis do sistema", encontre `Path`
5. Clique em "Editar"
6. Mova o caminho do Python 3.14 para o TOPO da lista:
   ```
   C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\
   C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\Scripts\
   ```
7. Clique OK em tudo
8. **IMPORTANTE:** Feche e abra novamente o Prompt de Comando

---

### 📊 Diagrama do Problema

```
┌─────────────────────────────────────────────────────┐
│  COMPUTADOR                                         │
│                                                     │
│  ┌──────────────┐         ┌──────────────┐        │
│  │  Python 3.14 │         │  Python 3.9  │        │
│  │  (correto)   │         │  (antigo)    │        │
│  └──────────────┘         └──────────────┘        │
│         │                         │                │
│         │                         │                │
│  ┌──────▼──────┐           ┌─────▼──────┐        │
│  │ Bibliotecas │           │   Vazio    │        │
│  │ instaladas  │           │            │        │
│  │ ✅          │           │ ❌         │        │
│  └─────────────┘           └────────────┘        │
│                                                     │
│  pip install → Python 3.14 ✅                      │
│  python main.py → Python 3.9 ❌ (ERRO!)           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Erro 2: ModuleNotFoundError após instalar bibliotecas

### 🔴 Sintomas
```python
ModuleNotFoundError: No module named 'customtkinter'
ModuleNotFoundError: No module named 'matplotlib'
```

### 🔍 Causa
Mesmo problema do Erro 1 - múltiplos Pythons.

### ✅ Solução
Siga as soluções do [Erro 1](#erro-1-dependências-faltando-múltiplos-pythons)

---

## Erro 3: pip não reconhecido

### 🔴 Sintomas
```
'pip' não é reconhecido como um comando interno ou externo
```

### 🔍 Causa
O Python não foi adicionado ao PATH durante a instalação.

### ✅ Solução 1: Usar python -m pip

Em vez de:
```bash
pip install -r requirements.txt
```

Use:
```bash
python -m pip install -r requirements.txt
```

Ou com caminho completo:
```bash
C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install -r requirements.txt
```

---

### ✅ Solução 2: Adicionar Python ao PATH

1. Encontre onde o Python está instalado
2. Adicione ao PATH do Windows:
   - `C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\`
   - `C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\Scripts\`

---

## Erro 4: Matplotlib warnings

### 🔴 Sintomas
```
UserWarning: tight_layout: falling back to Agg renderer
```

### 🔍 Causa
Uso de `plt.tight_layout()` com backend TkAgg.

### ✅ Solução
Substituir `plt.tight_layout()` por `fig.subplots_adjust()`:

```python
# ❌ Evitar
plt.tight_layout()

# ✅ Usar
fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
```

**Já corrigido em:** `views/dashboard_view.py`, `views/budget_goals_view.py`

---

## Erro 5: Pandas installation error (Python 3.14)

### 🔴 Sintomas
```
ERROR: Could not build wheels for pandas
Building wheel for pandas (pyproject.toml) ... error
```

### 🔍 Causa
Versões antigas do pandas (como `pandas==2.1.0`) não compilam no Python 3.14.

### ✅ Solução
Usar versões `>=` em vez de `==` no `requirements.txt`:

```txt
# ❌ Evitar (versão fixa)
pandas==2.1.0

# ✅ Usar (versão mínima)
pandas>=2.2.0
```

**Já corrigido em:** `requirements.txt`

---

## 🛠️ Script de Diagnóstico

Criamos um script para testar todas as dependências: `testar_dependencias.py`

### Como usar:

```bash
cd C:\Users\Administrador\Documents\Ket_Finance
python testar_dependencias.py
```

### O que ele faz:

1. ✅ Testa cada biblioteca individualmente
2. ✅ Mostra qual está faltando e por quê
3. ✅ Testa os imports do projeto (models, controllers, views)
4. ✅ Indica se o programa pode ser executado

### Exemplo de saída:

```
==================================================
TESTE DE DEPENDENCIAS - KET FINANCE
==================================================

✅ CustomTkinter                  OK
✅ Matplotlib                     OK
✅ Pandas                         OK
✅ OpenPyXL                       OK
✅ PyTZ                           OK
✅ Python-DateUtil                OK
✅ TkCalendar                     OK
✅ Tkinter (built-in)             OK

==================================================
✅ TODAS AS DEPENDENCIAS ESTAO OK!

Agora testando imports do projeto...

✅ models.Database OK
✅ controllers OK
✅ BudgetController OK
✅ views.MainWindow OK

==================================================
✅ TUDO OK! O PROGRAMA PODE SER EXECUTADO!

Execute: python main.py
==================================================
```

---

## 🔍 Como Diagnosticar Problemas

### Passo 1: Verificar qual Python está sendo usado

```bash
python --version
where python
```

### Passo 2: Verificar onde as bibliotecas estão instaladas

```bash
pip show customtkinter
```

Procure pela linha `Location:`.

### Passo 3: Verificar se o Python e as bibliotecas estão no mesmo lugar

Se o Python está em:
```
C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

As bibliotecas devem estar em:
```
C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages
```

Se estiverem em lugares diferentes = **PROBLEMA DE MÚLTIPLOS PYTHONS**

### Passo 4: Executar o script de diagnóstico

```bash
python testar_dependencias.py
```

---

## 📝 Checklist de Troubleshooting

Quando o programa não iniciar, siga esta ordem:

- [ ] 1. Execute `python testar_dependencias.py`
- [ ] 2. Se falhar, execute `where python` para ver quantos Pythons existem
- [ ] 3. Execute `pip show customtkinter` para ver onde as bibliotecas estão
- [ ] 4. Compare os caminhos - se forem diferentes, use o caminho completo
- [ ] 5. Atualize o `KetFinance.bat` com o caminho correto
- [ ] 6. Teste novamente com duplo clique no `KetFinance.bat`

---

## 🎯 Prevenção de Problemas Futuros

### 1. Sempre use ambientes virtuais (venv)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar programa
python main.py
```

### 2. Use o launcher do Python (py)

Em vez de `python`, use `py`:

```bash
py -3.14 main.py
py -3.14 -m pip install -r requirements.txt
```

### 3. Documente qual Python usar

Crie um arquivo `PYTHON_PATH.txt` com o caminho correto:
```
C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

---

## 📞 Suporte Rápido

### Problema: "Dependências faltando"
**Solução:** Use `KetFinance.bat` ou caminho completo do Python

### Problema: "pip não reconhecido"
**Solução:** Use `python -m pip` em vez de `pip`

### Problema: "ModuleNotFoundError"
**Solução:** Múltiplos Pythons - veja [Erro 1](#erro-1-dependências-faltando-múltiplos-pythons)

### Problema: Matplotlib warnings
**Solução:** Já corrigido - use `fig.subplots_adjust()`

### Problema: Pandas não instala (Python 3.14)
**Solução:** Já corrigido - use `pandas>=2.2.0`

---

## 🔄 Histórico de Correções

### 2024 - Versão 1.0

**Problema Encontrado:**
- Múltiplas instalações do Python causando conflito de dependências
- `pip install` instalava no Python 3.14
- `python main.py` executava com Python diferente (sem bibliotecas)

**Solução Implementada:**
1. Atualizado `KetFinance.bat` para detectar Python 3.14 automaticamente
2. Criado `testar_dependencias.py` para diagnóstico
3. Documentado todas as soluções neste arquivo

**Arquivos Modificados:**
- `KetFinance.bat` - Detecção automática do Python correto
- `TROUBLESHOOTING.md` - Este documento (novo)
- `testar_dependencias.py` - Script de diagnóstico (novo)

---

## 💡 Dicas Importantes

1. **Sempre use o KetFinance.bat** - Ele detecta o Python correto automaticamente
2. **Não instale múltiplos Pythons** - Causa conflitos
3. **Use ambientes virtuais** - Isola as dependências do projeto
4. **Mantenha o Python atualizado** - Mas apenas uma versão principal
5. **Documente o caminho do Python** - Facilita troubleshooting futuro

---

<div align="center">

**Última atualização:** 2024  
**Versão do documento:** 1.0  
**Status:** Todos os erros documentados e corrigidos ✅

</div>
