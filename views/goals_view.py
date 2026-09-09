"""View de metas financeiras"""
import customtkinter as ctk
from tkinter import messagebox
from config import COLORS, META_EMOJIS
from utils.formatters import formatar_valor
from utils.validators import validar_valor, campos_obrigatorios


class GoalsView(ctk.CTkFrame):
    def __init__(self, parent, db, controllers, ocultar_valores=False):
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        self.db = db
        self.controllers = controllers
        self.ocultar = ocultar_valores
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🎯 Metas Financeiras",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(20, 5))

        # Formulário nova meta
        form = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=10)
        form.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(form, text="Nova Meta", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(8, 2))

        row1 = ctk.CTkFrame(form, fg_color=COLORS['bg_secondary'])
        row1.pack(fill="x", padx=10, pady=3)
        self.nome_entry = ctk.CTkEntry(row1, placeholder_text="Nome da meta")
        self.nome_entry.pack(side="left", expand=True, fill="x", padx=3)
        self.emoji_var = ctk.StringVar(value=META_EMOJIS[0])
        ctk.CTkOptionMenu(row1, variable=self.emoji_var, values=META_EMOJIS,
                          width=70, fg_color=COLORS['card'],
                          button_color=COLORS['accent']).pack(side="left", padx=3)

        row2 = ctk.CTkFrame(form, fg_color=COLORS['bg_secondary'])
        row2.pack(fill="x", padx=10, pady=3)
        self.alvo_entry = ctk.CTkEntry(row2, placeholder_text="Valor alvo (R$)")
        self.alvo_entry.pack(side="left", expand=True, fill="x", padx=3)
        self.cat_entry = ctk.CTkEntry(row2, placeholder_text="Categoria")
        self.cat_entry.pack(side="left", expand=True, fill="x", padx=3)

        self.prior_var = ctk.BooleanVar()
        ctk.CTkCheckBox(form, text="Prioritária", variable=self.prior_var,
                        text_color=COLORS['warning']).pack(padx=10, pady=3, anchor="w")
        ctk.CTkButton(form, text="➕ Adicionar Meta", fg_color=COLORS['accent'],
                      command=self._adicionar).pack(pady=(3, 10))

        # Lista de metas
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_primary'])
        self.scroll.pack(fill="both", expand=True, padx=20, pady=5)
        self._listar()

    def _listar(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        metas = self.controllers['goal'].get_todas()
        if not metas:
            ctk.CTkLabel(self.scroll, text="Nenhuma meta cadastrada.",
                         text_color=COLORS['text']).pack(pady=20)
            return
        for m in metas:
            self._card_meta(m)

    def _card_meta(self, m):
        cor_borda = COLORS['warning'] if m.prioritaria else COLORS['card']
        card = ctk.CTkFrame(self.scroll, fg_color=COLORS['card'], corner_radius=10,
                            border_width=2, border_color=cor_borda)
        card.pack(fill="x", pady=5)

        header = ctk.CTkFrame(card, fg_color=COLORS['bg_primary'])
        header.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(header, text=f"{m.emoji} {m.nome}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS['text']).pack(side="left")
        ctk.CTkButton(header, text="🗑", width=30, fg_color=COLORS['error'],
                      command=lambda mid=m.id: self._remover(mid)).pack(side="right")

        ctk.CTkLabel(card, text=m.categoria, text_color=COLORS['text'],
                     font=ctk.CTkFont(size=10)).pack(anchor="w", padx=10)

        pct = (m.valor_atual / m.valor_alvo) if m.valor_alvo > 0 else 0
        ctk.CTkProgressBar(card, progress_color=COLORS['success']).pack(
            fill="x", padx=10, pady=3)
        card.winfo_children()[-1].set(min(pct, 1.0))

        valores_txt = f"{formatar_valor(m.valor_atual, self.ocultar)} / {formatar_valor(m.valor_alvo, self.ocultar)} ({pct*100:.1f}%)"
        ctk.CTkLabel(card, text=valores_txt, text_color=COLORS['text'],
                     font=ctk.CTkFont(size=11)).pack(padx=10, pady=(0, 5))

        # Adicionar valor
        row = ctk.CTkFrame(card, fg_color=COLORS['bg_primary'])
        row.pack(fill="x", padx=10, pady=(0, 8))
        entry = ctk.CTkEntry(row, placeholder_text="Valor a adicionar", width=150)
        entry.pack(side="left", padx=3)
        ctk.CTkButton(row, text="➕", width=40, fg_color=COLORS['success'],
                      command=lambda mid=m.id, e=entry: self._adicionar_valor(mid, e)).pack(side="left")

    def _adicionar(self):
        nome = self.nome_entry.get().strip()
        alvo_str = self.alvo_entry.get().strip()
        cat = self.cat_entry.get().strip()
        emoji = self.emoji_var.get()
        if not campos_obrigatorios(nome, alvo_str, cat):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        alvo = validar_valor(alvo_str)
        if alvo is None:
            messagebox.showerror("Erro", "Valor alvo inválido.")
            return
        self.controllers['goal'].adicionar(nome, emoji, alvo, cat, int(self.prior_var.get()))
        self.nome_entry.delete(0, "end")
        self.alvo_entry.delete(0, "end")
        self.cat_entry.delete(0, "end")
        self._listar()

    def _adicionar_valor(self, mid, entry):
        v = validar_valor(entry.get().strip())
        if v is None:
            messagebox.showerror("Erro", "Valor inválido.")
            return
        self.controllers['goal'].adicionar_valor(mid, v)
        entry.delete(0, "end")
        self._listar()

    def _remover(self, mid):
        if messagebox.askyesno("Confirmar", "Remover esta meta?"):
            self.controllers['goal'].remover(mid)
            self._listar()
