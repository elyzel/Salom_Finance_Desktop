"""View de entrada de transações"""
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from config import COLORS, ACCOUNTS, CATEGORIES, TRANSACTION_TYPES
from utils.validators import validar_valor, validar_data, campos_obrigatorios
from utils.formatters import formatar_valor


class EntryView(ctk.CTkFrame):
    def __init__(self, parent, db, controllers, ocultar_valores=False, callback_atualizar=None):
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        self.db = db
        self.controllers = controllers
        self.callback = callback_atualizar
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="➕ Nova Transação",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(20, 10))

        form = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=10)
        form.pack(fill="x", padx=20, pady=5)

        # Tipo
        self._label(form, "Tipo:")
        self.tipo_var = ctk.StringVar(value=TRANSACTION_TYPES[0])
        ctk.CTkOptionMenu(form, variable=self.tipo_var, values=TRANSACTION_TYPES,
                          fg_color=COLORS['card'], button_color=COLORS['accent'],
                          command=self._on_tipo_change).pack(fill="x", padx=15, pady=3)

        # Data
        self._label(form, "Data (DD/MM/AAAA):")
        self.data_entry = ctk.CTkEntry(form, placeholder_text=datetime.now().strftime('%d/%m/%Y'))
        self.data_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.data_entry.pack(fill="x", padx=15, pady=3)

        # Conta
        self._label(form, "Conta:")
        self.conta_var = ctk.StringVar(value=ACCOUNTS[0])
        self.conta_menu = ctk.CTkOptionMenu(form, variable=self.conta_var, values=ACCOUNTS,
                                             fg_color=COLORS['card'], button_color=COLORS['accent'])
        self.conta_menu.pack(fill="x", padx=15, pady=3)

        # Conta destino (transferência)
        self._label(form, "Conta Destino:")
        self.destino_var = ctk.StringVar(value=ACCOUNTS[1])
        self.destino_menu = ctk.CTkOptionMenu(form, variable=self.destino_var, values=ACCOUNTS,
                                               fg_color=COLORS['card'], button_color=COLORS['accent'])
        self.destino_menu.pack(fill="x", padx=15, pady=3)
        self.destino_menu.pack_forget()

        # Categoria
        self._label(form, "Categoria:")
        cats = list(CATEGORIES.keys())
        self.cat_var = ctk.StringVar(value=cats[0])
        ctk.CTkOptionMenu(form, variable=self.cat_var, values=cats,
                          fg_color=COLORS['card'], button_color=COLORS['accent']).pack(fill="x", padx=15, pady=3)

        # Valor
        self._label(form, "Valor (R$):")
        self.valor_entry = ctk.CTkEntry(form, placeholder_text="0,00")
        self.valor_entry.pack(fill="x", padx=15, pady=3)

        # Descrição
        self._label(form, "Descrição:")
        self.desc_entry = ctk.CTkEntry(form, placeholder_text="Descrição da transação")
        self.desc_entry.pack(fill="x", padx=15, pady=3)

        # Parcelamento
        frame_parc = ctk.CTkFrame(form, fg_color=COLORS['bg_secondary'])
        frame_parc.pack(fill="x", padx=15, pady=3)
        self.parcelado_var = ctk.BooleanVar()
        ctk.CTkCheckBox(frame_parc, text="Parcelado", variable=self.parcelado_var,
                        text_color=COLORS['text'],
                        command=self._on_parcelado).pack(side="left")
        self.parcelas_entry = ctk.CTkEntry(frame_parc, placeholder_text="Nº parcelas", width=100)
        self.parcelas_entry.pack(side="left", padx=10)
        self.parcelas_entry.configure(state="disabled")

        # Agendado
        self.agendado_var = ctk.BooleanVar()
        ctk.CTkCheckBox(form, text="Agendar (não afeta saldo agora)",
                        variable=self.agendado_var,
                        text_color=COLORS['warning']).pack(padx=15, pady=3, anchor="w")

        # Botão salvar
        ctk.CTkButton(self, text="💾 Salvar Transação",
                      fg_color=COLORS['accent'], hover_color=COLORS['card'],
                      command=self._salvar).pack(pady=15)

    def _label(self, parent, texto):
        ctk.CTkLabel(parent, text=texto, text_color=COLORS['text'],
                     font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(5, 0))

    def _on_tipo_change(self, valor):
        if valor == 'Transferência':
            self.destino_menu.pack(fill="x", padx=15, pady=3)
        else:
            self.destino_menu.pack_forget()

    def _on_parcelado(self):
        state = "normal" if self.parcelado_var.get() else "disabled"
        self.parcelas_entry.configure(state=state)

    def _salvar(self):
        tipo = self.tipo_var.get()
        data = self.data_entry.get().strip()
        conta = self.conta_var.get()
        categoria = self.cat_var.get()
        valor_str = self.valor_entry.get().strip()
        descricao = self.desc_entry.get().strip()
        agendado = 1 if self.agendado_var.get() else 0
        conta_destino = self.destino_var.get() if tipo == 'Transferência' else None

        if not campos_obrigatorios(data, conta, valor_str, descricao):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return
        if not validar_data(data):
            messagebox.showerror("Erro", "Data inválida. Use DD/MM/AAAA.")
            return
        valor = validar_valor(valor_str)
        if valor is None:
            messagebox.showerror("Erro", "Valor inválido.")
            return

        parcelado = self.parcelado_var.get()
        total_parcelas = 1
        if parcelado:
            try:
                total_parcelas = int(self.parcelas_entry.get())
                if total_parcelas < 2:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro", "Número de parcelas inválido.")
                return

        try:
            self.controllers['transaction'].adicionar(
                tipo=tipo, data_str=data, conta=conta, categoria=categoria,
                valor=valor, descricao=descricao, parcelado=parcelado,
                total_parcelas=total_parcelas, agendado=agendado,
                conta_destino=conta_destino
            )
            messagebox.showinfo("Sucesso", "Transação salva com sucesso!")
            self._limpar()
            if self.callback:
                self.callback()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _limpar(self):
        self.data_entry.delete(0, "end")
        self.data_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.valor_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.parcelado_var.set(False)
        self.agendado_var.set(False)
        self.parcelas_entry.configure(state="disabled")
        self.parcelas_entry.delete(0, "end")
