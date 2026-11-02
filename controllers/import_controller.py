"""Controller de importação de extratos e aplicação das regras do usuário."""
from utils.statement_parser import parse_extrato
from utils.rule_engine import aplicar_regras


class ImportController:
    def __init__(self, db, transaction_controller):
        self.db = db
        self.transaction_controller = transaction_controller

    def ler_arquivo(self, caminho_arquivo):
        transacoes = parse_extrato(caminho_arquivo)
        regras = self.db.get_regras(apenas_ativas=True)
        existentes = self._assinaturas_existentes()
        resultado = []

        for t in transacoes:
            item = aplicar_regras(regras, t)
            assinatura = self._assinatura(item['data'], item['valor'], item['descricao'])
            item['duplicada'] = assinatura in existentes
            if item.get('ignorar'):
                continue
            if item['duplicada']:
                item['selecionada'] = False
            resultado.append(item)

        return resultado

    def testar_regras(self, regra):
        """Conta quantos lançamentos históricos casariam com uma regra."""
        from utils.rule_engine import regra_casa
        total = 0
        for t in self.db.get_transacoes():
            if regra_casa(regra, {
                'descricao': t.descricao,
                'valor': t.valor,
                'tipo': t.tipo,
            }):
                total += 1
        return total

    def confirmar_importacao(self, transacoes_aprovadas, conta_padrao):
        importadas = 0
        investimentos_pendentes = 0

        for t in transacoes_aprovadas:
            conta = t.get('conta') or conta_padrao
            ids = self.transaction_controller.adicionar(
                tipo=t['tipo'], data_str=t['data'], conta=conta,
                categoria=t['categoria'], valor=t['valor'], descricao=t['descricao'],
                parcelado=False, total_parcelas=1, agendado=0, conta_destino=None,
            )

            if t['categoria'] in ('💰 Investimentos', '📈 Investimentos'):
                destino = t.get('investimento')
                for tid in ids:
                    self.db.criar_aporte_investimento_pendente(
                        tid, t['valor'], t['data'], t['descricao']
                    )
                    investimentos_pendentes += 1
                    if destino in ('CDB', 'Bolsa de Valores'):
                        self.db.confirmar_aportes_investimento([self._id_movimento(tid)], destino)

            importadas += 1

        return {
            'importadas': importadas,
            'investimentos_pendentes': investimentos_pendentes,
        }

    def _id_movimento(self, transacao_id):
        row = self.db.conn.execute(
            "SELECT id FROM investimentos_movimentos WHERE transacao_id = ?", (transacao_id,)
        ).fetchone()
        return row[0] if row else -1

    def _assinatura(self, data, valor, descricao):
        desc_norm = (descricao or '').strip().upper()
        return (data, round(float(valor), 2), desc_norm)

    def _assinaturas_existentes(self):
        return {
            self._assinatura(t.data, t.valor, t.descricao)
            for t in self.db.get_transacoes()
        }
