# 📝 Changelog de Correções - Ket Finance

> Registro detalhado de todas as correções e melhorias aplicadas

---

## 🗓️ Data: 09/05/2026

### 🔴 Correções Críticas (Prioridade Alta)

#### 1. Padronização de Tipos Booleanos nas Entidades
**Arquivo:** `models/entities.py`

**Problema:** Os campos `agendado` (Transacao) e `prioritaria` (Meta) estavam definidos como `int` mas deveriam ser `bool`.

**Antes:**
```python
@dataclass
class Transacao:
    agendado: int = 0

@dataclass
class Meta:
    prioritaria: int = 0
```

**Depois:**
```python
@dataclass
class Transacao:
    agendado: bool = False

@dataclass
class Meta:
    prioritaria: bool = False
```

**Impacto:** Elimina confusão e bugs sutis ao comparar valores booleanos.

---

#### 2. Prevenção de SQL Injection
**Arquivo:** `models/database.py`

**Problema:** O método `atualizar_meta` usava f-string para construir queries SQL dinâmicas sem validação.

**Antes:**
```python
def atualizar_meta(self, mid: str, **kwargs):
    with self.conn:
        for campo, valor in kwargs.items():
            if campo == 'prioritaria':
                valor = int(valor)
            self.conn.execute(
                f"UPDATE metas SET {campo} = ? WHERE id = ?",
                (valor, mid)
            )
```

**Depois:**
```python
def atualizar_meta(self, mid: str, **kwargs):
    # Whitelist de campos permitidos para evitar SQL injection
    CAMPOS_PERMITIDOS = ['nome', 'emoji', 'valor_alvo', 'valor_atual', 
                         'prioritaria', 'categoria', 'ordem']
    with self.conn:
        for campo, valor in kwargs.items():
            if campo not in CAMPOS_PERMITIDOS:
                raise ValueError(f"Campo inválido: {campo}")
            if campo == 'prioritaria':
                valor = int(valor)
            self.conn.execute(
                f"UPDATE metas SET {campo} = ? WHERE id = ?",
                (valor, mid)
            )
```

**Impacto:** Previne ataques de SQL injection através de campos maliciosos.

---

#### 3. Refatoração do BudgetController para Usar Conexão Compartilhada
**Arquivo:** `controllers/budget_controller.py`

**Problema:** O controller criava novas conexões SQLite em vez de reutilizar a conexão do Database, causando possíveis vazamentos e inconsistências.

**Antes:**
```python
def carregar_metas_orcamento(self):
    try:
        import sqlite3
        conn = sqlite3.connect('ket_finance.db')
        cursor = conn.execute("SELECT categoria, percentual FROM metas_orcamento")
        metas = {row[0]: row[1] for row in cursor}
        conn.close()
        return metas if metas else self.valores_padrao.copy()
    except Exception:
        return self.valores_padrao.copy()

def salvar_metas_orcamento(self, metas):
    import sqlite3
    conn = sqlite3.connect('ket_finance.db')
    with conn:
        for categoria, percentual in metas.items():
            conn.execute("""
                INSERT OR REPLACE INTO metas_orcamento (categoria, percentual)
                VALUES (?, ?)
            """, (categoria, percentual))
    conn.close()
    self._salvar_excel(metas)
```

**Depois:**
```python
def carregar_metas_orcamento(self):
    try:
        cursor = self.db.conn.execute("SELECT categoria, percentual FROM metas_orcamento")
        metas = {row[0]: row[1] for row in cursor}
        return metas if metas else self.valores_padrao.copy()
    except Exception:
        return self.valores_padrao.copy()

def salvar_metas_orcamento(self, metas):
    # Salvar no SQLite usando a conexão do Database
    with self.db.conn:
        for categoria, percentual in metas.items():
            self.db.conn.execute("""
                INSERT OR REPLACE INTO metas_orcamento (categoria, percentual)
                VALUES (?, ?)
            """, (categoria, percentual))
    self._salvar_excel(metas)
```

**Impacto:** Elimina vazamento de conexões e melhora a consistência dos dados.

---

### 🟡 Correções Médias (Prioridade Média)

#### 4. Validação de None em validar_valor
**Arquivo:** `utils/validators.py`

**Problema:** A função `validar_valor` não validava se o parâmetro era `None` antes de chamar métodos de string.

**Antes:**
```python
def validar_valor(valor_str):
    """Retorna float ou None se inválido"""
    try:
        v = valor_str.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        f = float(v)
        return f if f > 0 else None
    except (ValueError, AttributeError):
        return None
```

**Depois:**
```python
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
```

**Impacto:** Previne exceções `AttributeError` quando `None` é passado como parâmetro.

---

#### 5. Melhoria no Tratamento de Exceções nos Gráficos
**Arquivo:** `views/dashboard_view.py`

**Problema:** Blocos `try/except` vazios silenciavam erros nos gráficos, dificultando o debugging.

**Antes:**
```python
except Exception:
    pass
```

**Depois:**
```python
except Exception as e:
    print(f"Erro ao renderizar gráfico de barras: {e}")
```

e

```python
except Exception as e:
    print(f"Erro ao renderizar gráfico donut: {e}")
```

**Impacto:** Facilita a identificação e correção de problemas nos gráficos.

---

### 📚 Atualizações de Documentação

#### 6. Correção da Documentação do Banco de Dados
**Arquivo:** `ARCHITECTURE.md`

**Problema:** A documentação mencionava `dados_financeiros.json` como banco de dados principal, mas o código usa SQLite (`ket_finance.db`).

**Alteração:**
- Adicionada seção explicando que o SQLite é o banco de dados principal
- Listadas todas as tabelas do SQLite
- Marcado o JSON como "Legado/Backup"

**Impacto:** Elimina confusão para desenvolvedores que leem a documentação técnica.

---

## 📊 Resumo das Correções

| Categoria | Quantidade | Status |
|-----------|------------|--------|
| 🔴 Críticas | 3 | ✅ Concluídas |
| 🟡 Médias | 2 | ✅ Concluídas |
| 📚 Documentação | 1 | ✅ Concluída |
| **Total** | **6** | **✅ Todas Concluídas** |

---

## 🔍 Arquivos Modificados

1. `models/entities.py` - Tipos booleanos padronizados
2. `models/database.py` - Prevenção de SQL injection adicionada
3. `controllers/budget_controller.py` - Refatorado para usar conexão compartilhada
4. `utils/validators.py` - Validação de None adicionada
5. `views/dashboard_view.py` - Tratamento de exceções melhorado
6. `ARCHITECTURE.md` - Documentação corrigida

---

## ✅ Testes Recomendados

Após estas correções, recomenda-se testar:

1. **Transações:**
   - [ ] Criar transação normal
   - [ ] Criar transação agendada
   - [ ] Criar transação parcelada
   - [ ] Excluir transação

2. **Metas:**
   - [ ] Criar nova meta
   - [ ] Atualizar meta (incluindo prioritária)
   - [ ] Excluir meta

3. **Orçamento:**
   - [ ] Carregar metas de orçamento
   - [ ] Salvar metas de orçamento
   - [ ] Resetar valores padrão

4. **Investimentos:**
   - [ ] Adicionar ação
   - [ ] Aportar/resgatar CDB
   - [ ] Definir metas

5. **Dashboard:**
   - [ ] Verificar se gráficos carregam corretamente
   - [ ] Navegar entre meses

---

## 🚀 Próximos Passos Sugeridos

1. **Adicionar Type Hints** - Melhorar a tipagem em todo o código
2. **Implementar Logging** - Substituir prints por sistema de logging
3. **Adicionar Tests Unitários** - Criar suite de tests para validadores e controllers
4. **Melhorar Validações** - Adicionar mais validações de entrada
5. **Otimizar Banco de Dados** - Adicionar índices nas tabelas principais

---

### 🆕 Nova Funcionalidade Adicionada

#### Botão "Editar Meta" no Menu Investimentos
**Arquivo:** `views/investments_view.py`

**Descrição:** Adicionado botão "Editar Meta" na seção de Bolsa de Valores que abre um dialog modal para editar o valor da meta de investimentos.

**Funcionalidades:**
- Exibe o valor atual da meta
- Permite inserir novo valor
- Valida o valor informado
- Atualiza a meta no banco de dados
- Atualiza a interface automaticamente

**Impacto:** Usuários agora podem alterar o valor da meta de investimentos sem precisar redefinir do zero.

---

<div align="center">

**Correções aplicadas em:** 09/05/2026  
**Versão após correções:** 1.0.2  
**Status:** ✅ Todas as correções prioritárias concluídas + nova funcionalidade

</div>
