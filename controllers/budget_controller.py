"""Controller para gerenciar metas de orçamento"""
import os
from openpyxl import Workbook, load_workbook


class BudgetController:
    def __init__(self, db):
        self.db = db
        self.excel_file = "metas_orcamento.xlsx"
        
        # Valores padrão das categorias
        self.valores_padrao = {
            "Moradia": 30,
            "Educação": 10,
            "Reserva de Emergência": 20,
            "Investimentos": 20,
            "Lazer": 10,
            "Viagem": 10
        }
    
    def carregar_metas_orcamento(self):
        """
        Carrega as metas de orçamento do SQLite.
        Se não existir, retorna valores padrão.
        """
        try:
            cursor = self.db.conn.execute("SELECT categoria, percentual FROM metas_orcamento")
            metas = {row[0]: row[1] for row in cursor}
            return metas if metas else self.valores_padrao.copy()
        except Exception:
            return self.valores_padrao.copy()
    
    def salvar_metas_orcamento(self, metas):
        """
        Salva as metas de orçamento no SQLite e no Excel.
        
        Args:
            metas (dict): Dicionário com categoria: percentual
        """
        # Salvar no SQLite usando a conexão do Database
        with self.db.conn:
            for categoria, percentual in metas.items():
                self.db.conn.execute("""
                    INSERT OR REPLACE INTO metas_orcamento (categoria, percentual)
                    VALUES (?, ?)
                """, (categoria, percentual))
        
        # Salvar no Excel
        self._salvar_excel(metas)
    
    def _salvar_excel(self, metas):
        """
        Salva os dados no arquivo Excel.
        Cria ou sobrescreve a aba 'metas'.
        """
        # Verificar se o arquivo existe
        if os.path.exists(self.excel_file):
            wb = load_workbook(self.excel_file)
            # Remover aba 'metas' se já existir
            if 'metas' in wb.sheetnames:
                del wb['metas']
        else:
            wb = Workbook()
            # Remover a aba padrão
            if 'Sheet' in wb.sheetnames:
                del wb['Sheet']
        
        # Criar nova aba 'metas'
        ws = wb.create_sheet('metas')
        
        # Cabeçalhos
        ws['A1'] = 'Categoria'
        ws['B1'] = 'Percentual'
        
        # Dados
        linha = 2
        for categoria, percentual in metas.items():
            ws[f'A{linha}'] = categoria
            ws[f'B{linha}'] = percentual
            linha += 1
        
        # Salvar arquivo
        wb.save(self.excel_file)
    
    def carregar_do_excel(self):
        """
        Carrega as metas do arquivo Excel.
        Se não existir, retorna None.
        """
        if not os.path.exists(self.excel_file):
            return None
        
        try:
            wb = load_workbook(self.excel_file)
            if 'metas' not in wb.sheetnames:
                return None
            
            ws = wb['metas']
            metas = {}
            
            # Ler dados (pular cabeçalho)
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] and row[1] is not None:
                    categoria = row[0]
                    percentual = float(row[1])
                    metas[categoria] = percentual
            
            return metas if metas else None
        except Exception:
            return None
    
    def resetar_valores(self):
        """
        Reseta todos os valores para o padrão.
        """
        self.salvar_metas_orcamento(self.valores_padrao.copy())
        return self.valores_padrao.copy()
    
    def validar_total(self, metas):
        """
        Valida se a soma dos percentuais não ultrapassa 100%.
        
        Args:
            metas (dict): Dicionário com categoria: percentual
            
        Returns:
            tuple: (bool, float) - (é válido?, total)
        """
        total = sum(metas.values())
        return (total <= 100, total)
