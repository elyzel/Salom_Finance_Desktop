"""Controller de investimentos"""
from models.entities import Acao


class InvestmentController:
    def __init__(self, db):
        self.db = db

    # --- Ações ---
    def adicionar_acao(self, ticker, quantidade, preco_medio):
        ticker = ticker.strip().upper()
        existente = next((a for a in self.db.get_acoes() if a.ticker.upper() == ticker), None)
        if existente:
            # Recalcula o preço médio ponderado e grava direto no SQLite
            total_qtd = existente.quantidade + quantidade
            novo_preco = ((existente.preco_medio * existente.quantidade) +
                          (preco_medio * quantidade)) / total_qtd
            with self.db.conn:
                self.db.conn.execute(
                    "UPDATE acoes SET quantidade = ?, preco_medio = ? WHERE id = ?",
                    (total_qtd, novo_preco, existente.id))
        else:
            self.db.adicionar_acao(Acao(ticker=ticker, quantidade=quantidade, preco_medio=preco_medio))

    def remover_acao(self, aid: str):
        self.db.remover_acao(aid)

    def get_acoes(self):
        return self.db.get_acoes()

    def get_total_acoes(self):
        return sum(a.quantidade * a.preco_medio for a in self.db.get_acoes())

    def get_meta_investimentos(self):
        return self.db.get_meta_investimentos()

    def set_meta_investimentos(self, valor):
        self.db.set_meta_investimentos(valor)

    def get_aportes_pendentes(self):
        return self.db.get_aportes_investimento_pendentes()

    def get_movimentacoes(self):
        return self.db.get_movimentacoes_investimentos()

    def get_total_aportes_bolsa(self):
        return self.db.get_total_aportes_investimento('Bolsa de Valores')

    def confirmar_aportes(self, ids, investimento):
        if investimento not in ('CDB', 'Bolsa de Valores', 'Fundos Imobiliários'):
            raise ValueError('Tipo de investimento inválido.')
        return self.db.confirmar_aportes_investimento(ids, investimento)

    # --- CDB ---
    def get_cdb(self):
        return self.db.get_cdb()

    def aportar_cdb(self, valor):
        cdb = self.db.get_cdb()
        self.db.set_cdb(valor=cdb['valor'] + valor)

    def resgatar_cdb(self, valor):
        cdb = self.db.get_cdb()
        self.db.set_cdb(valor=max(0.0, cdb['valor'] - valor))

    def set_meta_cdb(self, meta):
        self.db.set_cdb(meta=meta)
