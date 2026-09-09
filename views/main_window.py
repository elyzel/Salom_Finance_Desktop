"""Janela principal da aplicação"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS
from utils.excel_exporter import exportar_excel


class MainWindow(ctk.CTk):
    def __init__(self, db, controllers):
        super().__init__()
        self.db = db
        self.controllers = controllers
        self.ocultar_valores = False
        self._view_atual = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("💰 Ket Finance")
        self.geometry("1100x700")
        self.configure(fg_color=COLORS['bg_primary'])

        try:
            self.wm_iconbitmap("KetFinance_Icone.ico")
        except Exception:
            pass

        self._build_layout()

    def _build_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS['sidebar'], width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(self.sidebar, text="💰 Ket Finance",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(20, 30))

        botoes = [
            ("📊 Dashboard", self.mostrar_dashboard),
            ("➕ Nova Transação", self.mostrar_entrada),
            ("📥 Importar Extrato", self.mostrar_importar),
            ("📋 Registros", self.mostrar_registros),
            ("🏆 Objetivos", self.mostrar_metas),
            ("📈 Investimentos", self.mostrar_investimentos),
            ("🎯 Metas de Orçamento", self.mostrar_metas_orcamento),
        ]
        for texto, cmd in botoes:
            ctk.CTkButton(self.sidebar, text=texto, fg_color=COLORS['sidebar'],
                          hover_color=COLORS['accent'], anchor="w",
                          text_color=COLORS['text'], font=ctk.CTkFont(size=13),
                          command=cmd).pack(fill="x", padx=10, pady=3)

        # Separador
        ctk.CTkFrame(self.sidebar, height=2, fg_color=COLORS['accent']).pack(fill="x", padx=10, pady=10)

        # Botões utilitários
        ctk.CTkButton(self.sidebar, text="👁 Ocultar Valores", fg_color=COLORS['sidebar'],
                      hover_color=COLORS['card'], anchor="w",
                      text_color=COLORS['text'], font=ctk.CTkFont(size=12),
                      command=self._toggle_ocultar).pack(fill="x", padx=10, pady=3)

        ctk.CTkButton(self.sidebar, text="📊 Exportar Excel", fg_color=COLORS['sidebar'],
                      hover_color=COLORS['card'], anchor="w",
                      text_color=COLORS['text'], font=ctk.CTkFont(size=12),
                      command=self._exportar_excel).pack(fill="x", padx=10, pady=3)

        ctk.CTkButton(self.sidebar, text="🔄 Recalcular", fg_color=COLORS['sidebar'],
                      hover_color=COLORS['card'], anchor="w",
                      text_color=COLORS['text'], font=ctk.CTkFont(size=12),
                      command=self._recalcular).pack(fill="x", padx=10, pady=3)

        # Área de conteúdo
        self.content = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'], corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

    def _trocar_view(self, view_class, **kwargs):
        for w in self.content.winfo_children():
            w.destroy()
        view = view_class(self.content, self.db, self.controllers,
                          ocultar_valores=self.ocultar_valores, **kwargs)
        view.pack(fill="both", expand=True)
        self._view_atual = (view_class, kwargs)

    def mostrar_dashboard(self):
        from views.dashboard_view import DashboardView
        self._trocar_view(DashboardView)

    def mostrar_entrada(self):
        from views.entry_view import EntryView
        self._trocar_view(EntryView, callback_atualizar=self.mostrar_dashboard)

    def mostrar_importar(self):
        from views.import_view import ImportView
        self._trocar_view(ImportView, callback_atualizar=self.mostrar_dashboard)

    def mostrar_registros(self):
        from views.records_view import RecordsView
        self._trocar_view(RecordsView, callback_atualizar=self.mostrar_dashboard)

    def mostrar_metas(self):
        from views.goals_view import GoalsView
        self._trocar_view(GoalsView)

    def mostrar_investimentos(self):
        from views.investments_view import InvestmentsView
        self._trocar_view(InvestmentsView)

    def mostrar_metas_orcamento(self):
        from views.budget_goals_view import BudgetGoalsView
        self._trocar_view(BudgetGoalsView)

    def _toggle_ocultar(self):
        self.ocultar_valores = not self.ocultar_valores
        self.mostrar_dashboard()

    def _exportar_excel(self):
        try:
            arquivo = exportar_excel(self.db)
            messagebox.showinfo("Sucesso", f"Relatório exportado:\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _recalcular(self):
        if messagebox.askyesno("Confirmar", "Recalcular todos os saldos?"):
            self.db.recalcular_saldos()
            messagebox.showinfo("Sucesso", "Saldos recalculados!")
            self.mostrar_dashboard()
