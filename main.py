"""
Kate Finance - Sistema de Controle Financeiro Pessoal
Arquivo principal de inicialização
"""
import sys
from tkinter import messagebox

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias = [
        ('customtkinter', 'customtkinter'),
        ('matplotlib', 'matplotlib'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('pytz', 'pytz'),
        ('dateutil', 'python-dateutil'),
        ('tkcalendar', 'tkcalendar')
    ]
    
    faltando = []
    for modulo, nome_pacote in dependencias:
        try:
            __import__(modulo)
        except ImportError:
            faltando.append(nome_pacote)
    
    if faltando:
        mensagem = f"Dependências faltando: {', '.join(faltando)}\n\n"
        mensagem += "Execute: pip install -r requirements.txt"
        messagebox.showerror("Erro de Dependências", mensagem)
        return False
    
    return True

def main():
    """Função principal"""
    try:
        # Verificar dependências
        if not verificar_dependencias():
            sys.exit(1)
        
        # Importar módulos
        from models import Database
        from controllers import TransactionController, GoalController, InvestmentController
        from controllers.budget_controller import BudgetController
        from controllers.import_controller import ImportController
        from views import MainWindow
        
        # Inicializar banco de dados
        db = Database()
        
        # Inicializar controllers
        transaction_controller = TransactionController(db)
        controllers = {
            'transaction': transaction_controller,
            'goal': GoalController(db),
            'investment': InvestmentController(db),
            'budget': BudgetController(db),
            'import': ImportController(db, transaction_controller)
        }
        
        # Criar e executar janela principal
        app = MainWindow(db, controllers)
        
        # Mostrar dashboard inicial
        app.mostrar_dashboard()
        
        # Iniciar loop principal
        app.mainloop()
        
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro ao iniciar aplicação:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
