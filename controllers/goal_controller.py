"""Controller de metas financeiras"""
from models.entities import Meta


class GoalController:
    def __init__(self, db):
        self.db = db

    def adicionar(self, nome, emoji, valor_alvo, categoria, prioritaria=0):
        metas = self.db.get_metas()
        ordem = len(metas)
        m = Meta(nome=nome, emoji=emoji, valor_atual=0.0, valor_alvo=valor_alvo,
                 categoria=categoria, prioritaria=prioritaria, ordem=ordem)
        self.db.adicionar_meta(m)
        return m

    def adicionar_valor(self, mid: str, valor: float):
        metas = self.db.get_metas()
        m = next((x for x in metas if x.id == mid), None)
        if m:
            novo = min(m.valor_atual + valor, m.valor_alvo)
            self.db.atualizar_meta(mid, valor_atual=novo)

    def remover(self, mid: str):
        self.db.remover_meta(mid)

    def get_todas(self):
        return sorted(self.db.get_metas(), key=lambda m: (not m.prioritaria, m.ordem))
