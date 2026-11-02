"""Controller de transações"""
from datetime import datetime
import calendar
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

        ids_criados = []

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
                ids_criados.append(t.id)
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
            ids_criados.append(t.id)
            if not agendado:
                self._ajustar_saldo(t)

        return ids_criados

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

    def remover_por_mes(self, mes, ano):

        """Exclui TODAS as transações de um mês/ano (efetivadas e
        agendadas), revertendo o saldo normalmente para cada uma —
        mesmo comportamento de remover() aplicado em lote."""

        todas = self.db.get_transacoes()
        alvo = [t for t in todas if self._mes_ano(t.data) == (mes, ano)]
        for t in alvo:
            self.remover(t.id)
        return len(alvo)

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

    def get_resumo_ultimos_meses(self, quantidade=6):
        """Retorna receitas e despesas mensais em ordem cronológica."""
        hoje = datetime.today()
        primeiro_mes = hoje.replace(day=1) - relativedelta(months=max(0, quantidade - 1))
        resultado = []
        for i in range(quantidade):
            mes_dt = primeiro_mes + relativedelta(months=i)
            resumo = self.get_resumo_mes(mes_dt.month, mes_dt.year)
            resultado.append({
                'label': mes_dt.strftime('%m/%Y'),
                'receitas': resumo['receitas'],
                'despesas': resumo['despesas'],
            })
        return resultado

    def get_movimentacao_diaria(self, mes, ano):
        """Soma receitas e despesas por dia do mês selecionado."""
        quantidade_dias = calendar.monthrange(ano, mes)[1]
        dias = list(range(1, quantidade_dias + 1))
        receitas = [0.0] * quantidade_dias
        despesas = [0.0] * quantidade_dias
        for transacao in self.get_por_mes(mes, ano):
            try:
                dia = int(transacao.data[:2])
            except (TypeError, ValueError):
                continue
            if not 1 <= dia <= quantidade_dias:
                continue
            if transacao.tipo == 'Receita':
                receitas[dia - 1] += transacao.valor
            elif transacao.tipo == 'Despesa':
                despesas[dia - 1] += transacao.valor
        return {'dias': dias, 'receitas': receitas, 'despesas': despesas}
