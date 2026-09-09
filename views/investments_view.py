"""View de investimentos"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS
from utils.formatters import formatar_valor
from utils.validators import validar_valor, campos_obrigatorios


class InvestmentsView(ctk.CTkFrame):
    def __init__(self, parent, db, controllers, ocultar_valores=False):
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        self.db = db
        self.controllers = controllers
        self.ocultar = ocultar_valores
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📈 Investimentos",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(20, 5))

        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_primary'])
        scroll.pack(fill="both", expand=True, padx=20, pady=5)

        self._secao_cdb(scroll)
        self._secao_acoes(scroll)

    def _secao_cdb(self, parent):
        ic = self.controllers['investment']
        cdb = ic.get_cdb()

        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], corner_radius=10)
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text="🏦 CDB / Reserva de Emergência",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(10, 5))

        pct = (cdb['valor'] / cdb['meta']) if cdb['meta'] > 0 else 0
        ctk.CTkLabel(frame, text=f"Valor: {formatar_valor(cdb['valor'], self.ocultar)}  |  Meta: {formatar_valor(cdb['meta'], self.ocultar)}",
                     text_color=COLORS['text']).pack()
        bar = ctk.CTkProgressBar(frame, progress_color=COLORS['success'])
        bar.pack(fill="x", padx=15, pady=5)
        bar.set(min(pct, 1.0))
        ctk.CTkLabel(frame, text=f"{pct*100:.1f}% da meta",
                     text_color=COLORS['text'], font=ctk.CTkFont(size=10)).pack()

        row = ctk.CTkFrame(frame, fg_color=COLORS['bg_primary'])
        row.pack(pady=(5, 10))
        self.cdb_entry = ctk.CTkEntry(row, placeholder_text="Valor", width=120)
        self.cdb_entry.pack(side="left", padx=3)
        ctk.CTkButton(row, text="Aportar", fg_color=COLORS['success'], width=80,
                      command=self._aportar_cdb).pack(side="left", padx=3)
        ctk.CTkButton(row, text="Resgatar", fg_color=COLORS['error'], width=80,
                      command=self._resgatar_cdb).pack(side="left", padx=3)

        row2 = ctk.CTkFrame(frame, fg_color=COLORS['bg_primary'])
        row2.pack(pady=(0, 10))
        self.meta_cdb_entry = ctk.CTkEntry(row2, placeholder_text="Nova meta CDB", width=150)
        self.meta_cdb_entry.pack(side="left", padx=3)
        ctk.CTkButton(row2, text="Definir Meta", fg_color=COLORS['accent'], width=100,
                      command=self._set_meta_cdb).pack(side="left", padx=3)

    def _secao_acoes(self, parent):
        ic = self.controllers['investment']
        acoes = ic.get_acoes()
        total = ic.get_total_acoes()
        meta = ic.get_meta_investimentos()

        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_secondary'], corner_radius=10)
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text="📊 Bolsa de Valores",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(10, 5))

        ctk.CTkLabel(frame, text=f"Total investido: {formatar_valor(total, self.ocultar)}  |  Meta: {formatar_valor(meta, self.ocultar)}",
                     text_color=COLORS['text']).pack()

        # Formulário nova ação
        row = ctk.CTkFrame(frame, fg_color=COLORS['bg_primary'])
        row.pack(pady=5)
        self.ticker_entry = ctk.CTkEntry(row, placeholder_text="Ticker", width=80)
        self.ticker_entry.pack(side="left", padx=3)
        self.qtd_entry = ctk.CTkEntry(row, placeholder_text="Qtd", width=60)
        self.qtd_entry.pack(side="left", padx=3)
        self.preco_entry = ctk.CTkEntry(row, placeholder_text="Preço médio", width=100)
        self.preco_entry.pack(side="left", padx=3)
        ctk.CTkButton(row, text="➕", width=40, fg_color=COLORS['accent'],
                      command=self._adicionar_acao).pack(side="left", padx=3)

        # Lista de ações
        self.acoes_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_primary'])
        self.acoes_frame.pack(fill="x", padx=10, pady=5)
        self._listar_acoes(acoes)

        # Meta investimentos
        row2 = ctk.CTkFrame(frame, fg_color=COLORS['bg_primary'])
        row2.pack(pady=(0, 10))
        self.meta_inv_entry = ctk.CTkEntry(row2, placeholder_text="Meta total investimentos", width=180)
        self.meta_inv_entry.pack(side="left", padx=3)
        ctk.CTkButton(row2, text="Definir Meta", fg_color=COLORS['accent'], width=100,
                      command=self._set_meta_inv).pack(side="left", padx=3)
        ctk.CTkButton(row2, text="Editar Meta", fg_color=COLORS['warning'], width=100,
                      command=self._edit_meta_inv).pack(side="left", padx=3)

    def _listar_acoes(self, acoes):
        for w in self.acoes_frame.winfo_children():
            w.destroy()
        if not acoes:
            ctk.CTkLabel(self.acoes_frame, text="Nenhuma ação cadastrada.",
                         text_color=COLORS['text']).pack()
            return
        for a in acoes:
            row = ctk.CTkFrame(self.acoes_frame, fg_color=COLORS['card'], corner_radius=8)
            row.pack(fill="x", pady=2)
            total = a.quantidade * a.preco_medio
            ctk.CTkLabel(row, text=f"{a.ticker}  |  {a.quantidade} un  |  PM: {formatar_valor(a.preco_medio, self.ocultar)}  |  Total: {formatar_valor(total, self.ocultar)}",
                         text_color=COLORS['text'], font=ctk.CTkFont(size=11)).pack(side="left", padx=8)
            ctk.CTkButton(row, text="🗑", width=30, fg_color=COLORS['error'],
                          command=lambda aid=a.id: self._remover_acao(aid)).pack(side="right", padx=5)

    def _aportar_cdb(self):
        v = validar_valor(self.cdb_entry.get().strip())
        if v is None:
            messagebox.showerror("Erro", "Valor inválido.")
            return
        self.controllers['investment'].aportar_cdb(v)
        self.cdb_entry.delete(0, "end")
        self._rebuild()

    def _resgatar_cdb(self):
        v = validar_valor(self.cdb_entry.get().strip())
        if v is None:
            messagebox.showerror("Erro", "Valor inválido.")
            return
        self.controllers['investment'].resgatar_cdb(v)
        self.cdb_entry.delete(0, "end")
        self._rebuild()

    def _set_meta_cdb(self):
        v = validar_valor(self.meta_cdb_entry.get().strip())
        if v is None:
            messagebox.showerror("Erro", "Valor inválido.")
            return
        self.controllers['investment'].set_meta_cdb(v)
        self.meta_cdb_entry.delete(0, "end")
        self._rebuild()

    def _adicionar_acao(self):
        ticker = self.ticker_entry.get().strip()
        qtd_str = self.qtd_entry.get().strip()
        preco_str = self.preco_entry.get().strip()
        if not campos_obrigatorios(ticker, qtd_str, preco_str):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        try:
            qtd = int(qtd_str)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return
        preco = validar_valor(preco_str)
        if preco is None:
            messagebox.showerror("Erro", "Preço inválido.")
            return
        self.controllers['investment'].adicionar_acao(ticker, qtd, preco)
        self.ticker_entry.delete(0, "end")
        self.qtd_entry.delete(0, "end")
        self.preco_entry.delete(0, "end")
        self._rebuild()

    def _remover_acao(self, aid):
        if messagebox.askyesno("Confirmar", "Remover esta ação?"):
            self.controllers['investment'].remover_acao(aid)
            self._rebuild()

    def _set_meta_inv(self):
        v = validar_valor(self.meta_inv_entry.get().strip())
        if v is None:
            messagebox.showerror("Erro", "Valor inválido.")
            return
        self.controllers['investment'].set_meta_investimentos(v)
        self.meta_inv_entry.delete(0, "end")
        self._rebuild()

    def _edit_meta_inv(self):
        """Abre dialog para editar o valor da meta de investimentos"""
        current_meta = self.controllers['investment'].get_meta_investimentos()
        
        # Criar janela de edição
        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Editar Meta de Investimentos")
        edit_window.geometry("300x150")
        edit_window.configure(fg_color=COLORS['bg_primary'])
        
        # Tornar modal
        edit_window.transient(self)
        edit_window.grab_set()
        
        ctk.CTkLabel(
            edit_window, 
            text="Editar Meta de Investimentos",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS['text']
        ).pack(pady=(15, 10))
        
        ctk.CTkLabel(
            edit_window,
            text=f"Valor atual: {formatar_valor(current_meta, self.ocultar)}",
            text_color=COLORS['text']
        ).pack(pady=(0, 10))
        
        entry_frame = ctk.CTkFrame(edit_window, fg_color=COLORS['bg_primary'])
        entry_frame.pack(pady=10)
        
        meta_entry = ctk.CTkEntry(
            entry_frame, 
            placeholder_text="Novo valor da meta",
            width=200
        )
        meta_entry.pack(side="left", padx=10)
        
        def save_edit():
            v = validar_valor(meta_entry.get().strip())
            if v is None:
                messagebox.showerror("Erro", "Valor inválido.", parent=edit_window)
                return
            self.controllers['investment'].set_meta_investimentos(v)
            edit_window.destroy()
            self._rebuild()
        
        ctk.CTkButton(
            edit_window,
            text="Salvar",
            fg_color=COLORS['success'],
            command=save_edit
        ).pack(pady=(0, 15))

    def _rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
