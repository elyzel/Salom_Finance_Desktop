"""Controller de investimentos"""
from models.entities import Acao


class InvestmentController:
    def __init__(self, db):
        self.db = db

    # --- Ações ---
    def adicionar_acao(self, ticker, quantidade, preco_medio):
        acoes = self.db.get_acoes()
        existente = next((a for a in acoes if a.ticker.upper() == ticker.upper()), None)
        if existente:
            total_qtd = existente.quantidade + quantidade
            novo_preco = ((existente.preco_medio * existente.quantidade) +
                          (preco_medio * quantidade)) / total_qtd
            self.db.dados['acoes'] = [
                {**a.to_dict(), 'quantidade': total_qtd, 'preco_medio': novo_preco}
                if a.ticker.upper() == ticker.upper() else a.to_dict()
                for a in acoes
            ]
            self.db.salvar()
        else:
            a = Acao(ticker=ticker.upper(), quantidade=quantidade, preco_medio=preco_medio)
            self.db.adicionar_acao(a)

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

    # --- CDB ---
    def get_cdb(self):
        return self.db.get_cdb()

    def aportar_cdb(self, valor):
        cdb = self.db.get_cdb()
        self.db.set_cdb(valor=cdb['valor'] + valor)

    def resgatar_cdb(self, valor):
        cdb = self.db.get_cdb()
        novo = max(0.0, cdb['valor'] - valor)
        self.db.set_cdb(valor=novo)

    def set_meta_cdb(self, meta):
        self.db.set_cdb(meta=meta)
