"""View de registros de transações"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config import COLORS, MESES
from utils.formatters import formatar_valor, mes_ano_atual


class RecordsView(ctk.CTkFrame):
    def __init__(self, parent, db, controllers, ocultar_valores=False, callback_atualizar=None):
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        self.db = db
        self.controllers = controllers
        self.ocultar = ocultar_valores
        self.callback = callback_atualizar
        self.mes, self.ano = mes_ano_atual()
        self._build()

    def _build(self):
        # Cabeçalho com navegação de mês
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
        header.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkButton(header, text="◀", width=30, fg_color=COLORS['card'],
                      command=self._mes_anterior).pack(side="left")
        self.titulo_label = ctk.CTkLabel(header, text="",
                                          font=ctk.CTkFont(size=18, weight="bold"),
                                          text_color=COLORS['text'])
        self.titulo_label.pack(side="left", expand=True)
        ctk.CTkButton(header, text="▶", width=30, fg_color=COLORS['card'],
                      command=self._mes_proximo).pack(side="right")
        ctk.CTkButton(header, text="🗑 Excluir Mês", width=110, fg_color=COLORS['error'],
                      command=self._excluir_mes).pack(side="right", padx=(0, 10))

        # Frame scrollável para transações
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=10)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Agendamentos
        ctk.CTkLabel(self, text="📅 Agendamentos Futuros",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS['warning']).pack(pady=(5, 2))
        self.scroll_ag = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_secondary'],
                                                 corner_radius=10, height=120)
        self.scroll_ag.pack(fill="x", padx=20, pady=(0, 10))

        self._atualizar()

    def _atualizar(self):
        nome_mes = MESES.get(self.mes, '')
        self.titulo_label.configure(text=f"📋 {nome_mes} {self.ano}")

        # Limpar
        for w in self.scroll.winfo_children():
            w.destroy()
        for w in self.scroll_ag.winfo_children():
            w.destroy()

        tc = self.controllers['transaction']
        transacoes = tc.get_por_mes(self.mes, self.ano)
        transacoes.sort(key=lambda t: t.data, reverse=True)

        if not transacoes:
            ctk.CTkLabel(self.scroll, text="Nenhuma transação neste mês.",
                         text_color=COLORS['text']).pack(pady=20)
        else:
            for t in transacoes:
                self._row_transacao(self.scroll, t)

        agendados = tc.get_agendados()
        if not agendados:
            ctk.CTkLabel(self.scroll_ag, text="Nenhum agendamento.",
                         text_color=COLORS['text']).pack(pady=5)
        else:
            for t in agendados:
                self._row_transacao(self.scroll_ag, t, agendado=True)

    def _row_transacao(self, parent, t, agendado=False):
        cor = COLORS['success'] if t.tipo == 'Receita' else (
            COLORS['warning'] if t.tipo == 'Transferência' else COLORS['error'])
        row = ctk.CTkFrame(parent, fg_color=COLORS['card'], corner_radius=8)
        row.pack(fill="x", padx=5, pady=2)

        info = f"{t.data} | {t.tipo} | {t.conta} | {t.categoria}"
        ctk.CTkLabel(row, text=info, text_color=COLORS['text'],
                     font=ctk.CTkFont(size=10)).pack(side="left", padx=8)
        ctk.CTkLabel(row, text=t.descricao, text_color=COLORS['text'],
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
        ctk.CTkLabel(row, text=formatar_valor(t.valor, self.ocultar),
                     text_color=cor, font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=8)
        ctk.CTkButton(row, text="🗑", width=30, fg_color=COLORS['error'],
                      command=lambda tid=t.id: self._excluir(tid)).pack(side="right", padx=4)

    def _excluir(self, tid):
        if messagebox.askyesno("Confirmar", "Excluir esta transação?"):
            self.controllers['transaction'].remover(tid)
            self._atualizar()
        if self.callback:
            self.callback()

    def _excluir_mes(self):
        nome_mes = MESES.get(self.mes, '')
        confirmar = messagebox.askyesno(
            "Excluir mês inteiro",
            f"Isso vai excluir TODAS as transações de {nome_mes} {self.ano} "
            f"(incluindo agendamentos daquele mês) e reverter o saldo das contas. "
            f"Essa ação não pode ser desfeita.\n\nDeseja continuar?"
        )
        if not confirmar:
            return

        qtd = self.controllers['transaction'].remover_por_mes(self.mes, self.ano)
        messagebox.showinfo("Concluído", f"{qtd} registro(s) de {nome_mes} {self.ano} excluído(s).")
        self._atualizar()
        if self.callback:
            self.callback()

    def _mes_anterior(self):
        if self.mes == 1:
            self.mes, self.ano = 12, self.ano - 1
        else:
            self.mes -= 1
        self._atualizar()

    def _mes_proximo(self):
        if self.mes == 12:
            self.mes, self.ano = 1, self.ano + 1
        else:
            self.mes += 1
        self._atualizar()
