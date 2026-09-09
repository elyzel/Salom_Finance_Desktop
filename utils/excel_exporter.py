"""Exportação de relatórios para Excel"""
import os
import sqlite3
from datetime import datetime
from config import MESES, DB_PATH


def exportar_excel(db):
    try:
        import pandas as pd
        from openpyxl import load_workbook
        from openpyxl.styles import PatternFill, Font, Alignment

        now = datetime.now()
        mes_nome = MESES.get(now.month, str(now.month))
        pasta = f"Relatorios_{now.year}"
        os.makedirs(pasta, exist_ok=True)
        arquivo = os.path.join(pasta, f"{now.month:02d}_{mes_nome}_{now.year}.xlsx")

        # Conectar ao SQLite
        conn = sqlite3.connect(DB_PATH)

        with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
            # Contas
            df_contas = pd.read_sql_query("SELECT nome AS Conta, saldo AS Saldo FROM contas", conn)
            df_contas.to_excel(writer, sheet_name='Contas', index=False)

            # Transações
            df_trans = pd.read_sql_query("""
                SELECT data, tipo, categoria, descricao, valor, conta
                FROM transacoes
                WHERE agendada = 0
                ORDER BY data
            """, conn)
            if not df_trans.empty:
                df_trans.to_excel(writer, sheet_name='Transações', index=False)

            # Metas
            df_metas = pd.read_sql_query("""
                SELECT nome, emoji, valor_atual, valor_alvo, 
                       CASE WHEN prioritaria = 1 THEN 'Sim' ELSE 'Não' END AS prioritaria
                FROM metas
            """, conn)
            if not df_metas.empty:
                df_metas.to_excel(writer, sheet_name='Metas', index=False)

            # Ações
            df_acoes = pd.read_sql_query("SELECT ticker, quantidade, preco_medio FROM acoes", conn)
            if not df_acoes.empty:
                df_acoes.to_excel(writer, sheet_name='Ações', index=False)

        conn.close()
        return arquivo
    except Exception as e:
        raise RuntimeError(f"Erro ao exportar Excel: {e}")
