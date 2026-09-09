"""Controller de transações"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models.entities import Transacao
from utils.formatters import data_para_datetime


class TransactionController:
    def __init__(self, db):
        self.db = db

    def adicionar(self, tipo, data_str, conta, categoria, valor, descricao,
                  parcelado=False, total_parcelas=1, agendado=0, conta_destino=None):
        data_dt = data_para_datetime(data_str)
        if data_dt is None:
            raise ValueError("Data inválida")

        if parcelado and total_parcelas > 1:
            for i in range(total_parcelas):
                data_parcela = (data_dt + relativedelta(months=i)).strftime('%d/%m/%Y')
                t = Transacao(
                    tipo=tipo, data=data_parcela, conta=conta, categoria=categoria,
                    valor=valor, descricao=f"{descricao} ({i+1}/{total_parcelas})",
                    parcelado=True, parcela_atual=i+1, total_parcelas=total_parcelas,
                    agendado=agendado, conta_destino=conta_destino
                )
                self.db.adicionar_transacao(t)
                if not agendado:
                    self._ajustar_saldo(t)
        else:
            t = Transacao(
                tipo=tipo, data=data_str, conta=conta, categoria=categoria,
                valor=valor, descricao=descricao, parcelado=False,
                parcela_atual=1, total_parcelas=1, agendado=agendado,
                conta_destino=conta_destino
            )
            self.db.adicionar_transacao(t)
            if not agendado:
                self._ajustar_saldo(t)

    def _ajustar_saldo(self, t: Transacao):
        if t.tipo == 'Receita':
            self.db.ajustar_conta(t.conta, t.valor)
        elif t.tipo == 'Despesa':
            self.db.ajustar_conta(t.conta, -t.valor)
        elif t.tipo == 'Transferência':
            self.db.ajustar_conta(t.conta, -t.valor)
            if t.conta_destino:
                self.db.ajustar_conta(t.conta_destino, t.valor)

    def remover(self, tid: str):
        transacoes = self.db.get_transacoes()
        t = next((x for x in transacoes if x.id == tid), None)
        if t and not t.agendado:
            # Reverter saldo
            if t.tipo == 'Receita':
                self.db.ajustar_conta(t.conta, -t.valor)
            elif t.tipo == 'Despesa':
                self.db.ajustar_conta(t.conta, t.valor)
            elif t.tipo == 'Transferência':
                self.db.ajustar_conta(t.conta, t.valor)
                if t.conta_destino:
                    self.db.ajustar_conta(t.conta_destino, -t.valor)
        self.db.remover_transacao(tid)

    def get_por_mes(self, mes, ano):
        return [t for t in self.db.get_transacoes()
                if not t.agendado and self._mes_ano(t.data) == (mes, ano)]

    def get_agendados(self):
        return [t for t in self.db.get_transacoes() if t.agendado]

    def _mes_ano(self, data_str):
        dt = data_para_datetime(data_str)
        return (dt.month, dt.year) if dt else (0, 0)

    def get_resumo_mes(self, mes, ano):
        transacoes = self.get_por_mes(mes, ano)
        receitas = sum(t.valor for t in transacoes if t.tipo == 'Receita')
        despesas = sum(t.valor for t in transacoes if t.tipo == 'Despesa')
        return {'receitas': receitas, 'despesas': despesas, 'saldo': receitas - despesas}

    def get_resumo_ultimos_meses(self, n=6):
        from dateutil.relativedelta import relativedelta
        from datetime import date
        hoje = date.today()
        resultado = []
        for i in range(n - 1, -1, -1):
            ref = hoje - relativedelta(months=i)
            resumo = self.get_resumo_mes(ref.month, ref.year)
            from config import MESES
            resultado.append({
                'label': f"{MESES[ref.month][:3]}/{str(ref.year)[2:]}",
                'mes': ref.month,
                'ano': ref.year,
                **resumo
            })
        return resultado
