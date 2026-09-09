"""Gerenciador de dados SQLite"""
import sqlite3
from config import INITIAL_DATA
from models.entities import Transacao, Meta, Acao


class Database:
    def __init__(self, caminho_db="ket_finance.db"):
        self.caminho_db = caminho_db
        self.conn = sqlite3.connect(caminho_db, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA encoding = 'UTF-8'")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._criar_tabelas()
        self._popular_dados_iniciais()
        # Manter compatibilidade com código que acessa self.dados
        self.dados = {}

    def _criar_tabelas(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS contas (
                    nome TEXT PRIMARY KEY,
                    saldo REAL NOT NULL DEFAULT 0.0
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transacoes (
                    id TEXT PRIMARY KEY,
                    tipo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    descricao TEXT,
                    conta TEXT NOT NULL,
                    data TEXT NOT NULL,
                    agendada INTEGER NOT NULL DEFAULT 0,
                    total_parcelas INTEGER DEFAULT NULL,
                    parcela_atual INTEGER DEFAULT NULL,
                    id_grupo TEXT DEFAULT NULL,
                    conta_destino TEXT DEFAULT NULL,
                    FOREIGN KEY (conta) REFERENCES contas(nome)
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metas (
                    id TEXT PRIMARY KEY,
                    nome TEXT NOT NULL,
                    emoji TEXT DEFAULT '',
                    valor_alvo REAL NOT NULL,
                    valor_atual REAL NOT NULL DEFAULT 0.0,
                    prioritaria INTEGER NOT NULL DEFAULT 0,
                    categoria TEXT DEFAULT '',
                    ordem INTEGER DEFAULT 0
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS acoes (
                    id TEXT PRIMARY KEY,
                    ticker TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_medio REAL NOT NULL
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS cdb (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    saldo REAL NOT NULL DEFAULT 0.0,
                    meta REAL NOT NULL DEFAULT 0.0
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metas_orcamento (
                    categoria TEXT PRIMARY KEY,
                    percentual INTEGER NOT NULL DEFAULT 0
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS meta_investimentos (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    valor REAL NOT NULL DEFAULT 0.0
                )
            """)

    def _popular_dados_iniciais(self):
        with self.conn:
            # Contas padrão
            for conta in INITIAL_DATA['contas'].keys():
                self.conn.execute(
                    "INSERT OR IGNORE INTO contas (nome, saldo) VALUES (?, ?)",
                    (conta, 0.0)
                )
            
            # CDB padrão
            self.conn.execute(
                "INSERT OR IGNORE INTO cdb (id, saldo, meta) VALUES (1, 0.0, 0.0)"
            )
            
            # Meta investimentos padrão
            self.conn.execute(
                "INSERT OR IGNORE INTO meta_investimentos (id, valor) VALUES (1, 0.0)"
            )
            
            # Metas de orçamento padrão
            for cat, perc in INITIAL_DATA['metas_orcamento'].items():
                self.conn.execute(
                    "INSERT OR IGNORE INTO metas_orcamento (categoria, percentual) VALUES (?, ?)",
                    (cat, perc)
                )

    def _carregar(self):
        """Compatibilidade com código antigo"""
        return self.carregar_dados()

    def carregar_dados(self):
        """Retorna dict no formato JSON para compatibilidade"""
        dados = {
            'contas': {},
            'transacoes': [],
            'metas': [],
            'acoes': [],
            'cdb': {'valor': 0.0, 'meta': 0.0},
            'meta_investimentos': 0.0,
            'metas_orcamento': {}
        }
        
        # Contas
        cursor = self.conn.execute("SELECT nome, saldo FROM contas")
        for row in cursor:
            dados['contas'][row['nome']] = row['saldo']
        
        # Transações
        cursor = self.conn.execute("SELECT * FROM transacoes")
        for row in cursor:
            t = dict(row)
            # Converter parcelamento para formato JSON
            if t['total_parcelas'] is not None:
                t['parcelamento'] = {
                    'total_parcelas': t['total_parcelas'],
                    'parcela_atual': t['parcela_atual'],
                    'id_grupo': t['id_grupo']
                }
            t['agendado'] = bool(t['agendada'])
            dados['transacoes'].append(t)
        
        # Metas
        cursor = self.conn.execute("SELECT * FROM metas")
        for row in cursor:
            m = dict(row)
            m['prioritaria'] = bool(m['prioritaria'])
            dados['metas'].append(m)
        
        # Ações
        cursor = self.conn.execute("SELECT * FROM acoes")
        dados['acoes'] = [dict(row) for row in cursor]
        
        # CDB
        cursor = self.conn.execute("SELECT saldo, meta FROM cdb WHERE id = 1")
        row = cursor.fetchone()
        if row:
            dados['cdb'] = {'valor': row['saldo'], 'meta': row['meta']}
        
        # Meta investimentos
        cursor = self.conn.execute("SELECT valor FROM meta_investimentos WHERE id = 1")
        row = cursor.fetchone()
        if row:
            dados['meta_investimentos'] = row['valor']
        
        # Metas orçamento
        cursor = self.conn.execute("SELECT categoria, percentual FROM metas_orcamento")
        for row in cursor:
            dados['metas_orcamento'][row['categoria']] = row['percentual']
        
        return dados

    def salvar(self):
        """No SQLite operações são imediatas - método mantido para compatibilidade"""
        self.conn.commit()

    # --- Contas ---
    def get_contas(self):
        cursor = self.conn.execute("SELECT nome, saldo FROM contas")
        return {row['nome']: row['saldo'] for row in cursor}

    def set_conta(self, nome, valor):
        with self.conn:
            self.conn.execute(
                "UPDATE contas SET saldo = ? WHERE nome = ?",
                (valor, nome)
            )

    def ajustar_conta(self, nome, delta):
        with self.conn:
            self.conn.execute(
                "UPDATE contas SET saldo = saldo + ? WHERE nome = ?",
                (delta, nome)
            )

    # --- Transações ---
    def get_transacoes(self):
        cursor = self.conn.execute("SELECT * FROM transacoes ORDER BY data")
        transacoes = []
        for row in cursor:
            t_dict = {
                'id': row['id'],
                'tipo': row['tipo'],
                'valor': row['valor'],
                'categoria': row['categoria'],
                'descricao': row['descricao'],
                'conta': row['conta'],
                'data': row['data'],
                'agendado': row['agendada'],
                'conta_destino': row['conta_destino'],
                'parcelado': row['total_parcelas'] is not None,
                'parcela_atual': row['parcela_atual'] or 1,
                'total_parcelas': row['total_parcelas'] or 1
            }
            transacoes.append(Transacao.from_dict(t_dict))
        return transacoes

    def adicionar_transacao(self, t: Transacao):
        with self.conn:
            total_parcelas = t.total_parcelas if t.parcelado else None
            parcela_atual = t.parcela_atual if t.parcelado else None
            id_grupo = getattr(t, 'id_grupo', None) if t.parcelado else None
            
            self.conn.execute("""
                INSERT INTO transacoes 
                (id, tipo, valor, categoria, descricao, conta, data, agendada, 
                 total_parcelas, parcela_atual, id_grupo, conta_destino)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t.id, t.tipo, t.valor, t.categoria, t.descricao, t.conta, t.data,
                int(t.agendado), total_parcelas, parcela_atual, id_grupo, t.conta_destino
            ))

    def remover_transacao(self, tid: str):
        with self.conn:
            self.conn.execute("DELETE FROM transacoes WHERE id = ?", (tid,))

    def recalcular_saldos(self):
        """Recalcula saldos do zero com base nas transações"""
        from config import ACCOUNTS
        with self.conn:
            # Zerar saldos
            for conta in ACCOUNTS:
                self.conn.execute("UPDATE contas SET saldo = 0.0 WHERE nome = ?", (conta,))
            
            # Buscar transações não agendadas ordenadas por data
            cursor = self.conn.execute("""
                SELECT * FROM transacoes 
                WHERE agendada = 0 
                ORDER BY data
            """)
            
            for row in cursor:
                tipo = row['tipo']
                conta = row['conta']
                valor = row['valor']
                conta_destino = row['conta_destino']
                
                if tipo == 'Receita':
                    self.conn.execute(
                        "UPDATE contas SET saldo = saldo + ? WHERE nome = ?",
                        (valor, conta)
                    )
                elif tipo == 'Despesa':
                    self.conn.execute(
                        "UPDATE contas SET saldo = saldo - ? WHERE nome = ?",
                        (valor, conta)
                    )
                elif tipo == 'Transferência':
                    self.conn.execute(
                        "UPDATE contas SET saldo = saldo - ? WHERE nome = ?",
                        (valor, conta)
                    )
                    if conta_destino:
                        self.conn.execute(
                            "UPDATE contas SET saldo = saldo + ? WHERE nome = ?",
                            (valor, conta_destino)
                        )

    # --- Metas ---
    def get_metas(self):
        cursor = self.conn.execute("SELECT * FROM metas ORDER BY prioritaria DESC, ordem")
        metas = []
        for row in cursor:
            m_dict = dict(row)
            m_dict['prioritaria'] = row['prioritaria']
            metas.append(Meta.from_dict(m_dict))
        return metas

    def adicionar_meta(self, m: Meta):
        with self.conn:
            self.conn.execute("""
                INSERT INTO metas 
                (id, nome, emoji, valor_alvo, valor_atual, prioritaria, categoria, ordem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                m.id, m.nome, m.emoji, m.valor_alvo, m.valor_atual,
                int(m.prioritaria), m.categoria, m.ordem
            ))

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

    def remover_meta(self, mid: str):
        with self.conn:
            self.conn.execute("DELETE FROM metas WHERE id = ?", (mid,))

    # --- Ações ---
    def get_acoes(self):
        cursor = self.conn.execute("SELECT * FROM acoes")
        return [Acao.from_dict(dict(row)) for row in cursor]

    def adicionar_acao(self, a: Acao):
        with self.conn:
            self.conn.execute("""
                INSERT INTO acoes (id, ticker, quantidade, preco_medio)
                VALUES (?, ?, ?, ?)
            """, (a.id, a.ticker, a.quantidade, a.preco_medio))

    def remover_acao(self, aid: str):
        with self.conn:
            self.conn.execute("DELETE FROM acoes WHERE id = ?", (aid,))

    # --- CDB ---
    def get_cdb(self):
        cursor = self.conn.execute("SELECT saldo, meta FROM cdb WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return {'valor': row['saldo'], 'meta': row['meta']}
        return {'valor': 0.0, 'meta': 0.0}

    def set_cdb(self, valor=None, meta=None):
        with self.conn:
            if valor is not None:
                self.conn.execute("UPDATE cdb SET saldo = ? WHERE id = 1", (valor,))
            if meta is not None:
                self.conn.execute("UPDATE cdb SET meta = ? WHERE id = 1", (meta,))

    # --- Meta Investimentos ---
    def get_meta_investimentos(self):
        cursor = self.conn.execute("SELECT valor FROM meta_investimentos WHERE id = 1")
        row = cursor.fetchone()
        return row['valor'] if row else 0.0

    def set_meta_investimentos(self, valor):
        with self.conn:
            self.conn.execute(
                "UPDATE meta_investimentos SET valor = ? WHERE id = 1",
                (valor,)
            )

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
