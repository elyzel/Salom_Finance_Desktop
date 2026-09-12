"""Controller de importação de extratos bancários"""
from utils.statement_parser import parse_extrato


class ImportController:
    """Orquestra a leitura de um extrato e a gravação das transações
    aprovadas pelo usuário, evitando duplicidade.

    Fluxo:
      1. ler_arquivo()      -> interpreta o OFX/CSV e marca duplicatas
      2. (usuário revisa e ajusta na tela)
      3. confirmar_importacao() -> grava só o que foi aprovado
    """

    def __init__(self, db, transaction_controller):
        self.db = db
        self.transaction_controller = transaction_controller

    def ler_arquivo(self, caminho_arquivo):
        """Lê o arquivo e devolve a lista de transações encontradas, cada
        uma já marcada com 'duplicada': True/False."""
        transacoes = parse_extrato(caminho_arquivo)
        existentes = self._assinaturas_existentes()

        for t in transacoes:
            assinatura = self._assinatura(t['data'], t['valor'], t['descricao'])
            t['duplicada'] = assinatura in existentes

        return transacoes

    def confirmar_importacao(self, transacoes_aprovadas, conta_padrao):
        """Grava as transações aprovadas pelo usuário.

        `transacoes_aprovadas` é uma lista de dicts contendo pelo menos:
        data, descricao, valor, tipo, categoria (já revisada pelo usuário),
        e opcionalmente 'conta' (senão usa conta_padrao).

        Retorna a quantidade de transações efetivamente importadas.
        """
        importadas = 0
        for t in transacoes_aprovadas:
            conta = t.get('conta') or conta_padrao
            self.transaction_controller.adicionar(
                tipo=t['tipo'],
                data_str=t['data'],
                conta=conta,
                categoria=t['categoria'],
                valor=t['valor'],
                descricao=t['descricao'],
                parcelado=False,
                total_parcelas=1,
                agendado=0,
                conta_destino=None,
            )
            importadas += 1
        return importadas

    # -- deduplicação ------------------------------------------------------
    def _assinatura(self, data, valor, descricao):
        """Chave usada para detectar se um lançamento do extrato já existe
        no sistema: mesma data + mesmo valor + mesma descrição normalizada."""
        desc_norm = (descricao or '').strip().upper()
        return (data, round(float(valor), 2), desc_norm)

    def _assinaturas_existentes(self):
        existentes = set()
        for t in self.db.get_transacoes():
            existentes.add(self._assinatura(t.data, t.valor, t.descricao))
        return existentes