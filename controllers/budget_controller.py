"""Controller para gerenciar metas de orçamento (somente SQLite)"""
from config import CATEGORIES


class BudgetController:
    def __init__(self, db):
        self.db = db
        self.valores_padrao = {
            "Moradia": 30,
            "Educação": 10,
            "Reserva de Emergência": 20,
            "Investimentos": 20,
            "Saúde": 0,
            "Lazer": 10,
            "Viagem": 10
        }
        self.categorias_destinacoes = [
            "Reserva de Emergência", "Investimentos", "Lazer", "Viagem"
        ]
        nomes = [
            categoria.split(" ", 1)[1] if " " in categoria else categoria
            for categoria in CATEGORIES
        ]
        self.categorias_despesas = list(dict.fromkeys(
            nome for nome in nomes if nome not in self.categorias_destinacoes
        ))

    def carregar_metas_orcamento(self):
        """Carrega as metas do SQLite; se não houver, retorna os valores padrão."""
        try:
            cursor = self.db.conn.execute("SELECT categoria, percentual FROM metas_orcamento")
            metas = {row[0]: row[1] for row in cursor}
            if not metas:
                return self.valores_padrao.copy()
            # Categorias novas aparecem também para bancos que já tinham metas salvas.
            for categoria, percentual in self.valores_padrao.items():
                metas.setdefault(categoria, percentual)
            return metas
        except Exception:
            return self.valores_padrao.copy()

    def salvar_metas_orcamento(self, metas):
        """Salva as metas (categoria -> percentual) no SQLite."""
        with self.db.conn:
            for categoria, percentual in metas.items():
                self.db.conn.execute(
                    "INSERT OR REPLACE INTO metas_orcamento (categoria, percentual) VALUES (?, ?)",
                    (categoria, percentual))

    def resetar_valores(self):
        self.salvar_metas_orcamento(self.valores_padrao.copy())
        return self.valores_padrao.copy()

    def validar_total(self, metas):
        """Retorna (é válido?, total): a soma não pode passar de 100%."""
        total = sum(metas.values())
        return (total <= 100, total)

    def carregar_planejamento(self, periodo):
        plano = self.db.get_orcamento_planejado(periodo)
        plano["fixas"] = [item for item in plano["itens"] if item["grupo"] == "fixa"]
        plano["destinacoes"] = [item for item in plano["itens"] if item["grupo"] == "destinacao"]
        return plano

    def salvar_planejamento(self, periodo, receita, itens):
        self.db.salvar_orcamento_planejado(periodo, receita, itens)

    def limpar_planejamento(self, periodo):
        self.db.limpar_orcamento_planejado(periodo)
