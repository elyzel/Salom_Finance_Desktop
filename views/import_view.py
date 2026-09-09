"""View de importação de extratos bancários (OFX/CSV)"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from config import COLORS, ACCOUNTS, CATEGORIES
from utils.formatters import formatar_valor


class ImportView(ctk.CTkFrame):
    """
    Tela de importação de extrato.

    Fluxo:
      1. Usuário escolhe o arquivo .ofx/.csv exportado do banco
      2. O sistema lê e monta uma pré-visualização, linha a linha, já com
         categoria sugerida e marcando possíveis duplicatas
      3. Usuário revisa (pode desmarcar linhas, trocar categoria/conta)
      4. Usuário confirma e só então as transações são gravadas
    """

    def __init__(self, parent, db, controllers, ocultar_valores=False, callback_atualizar=None):
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        self.db = db
        self.controllers = controllers
        self.callback = callback_atualizar
        self.ocultar = ocultar_valores

        self.transacoes_lidas = []  # lista de dicts vindos do parser
        self.linhas_widgets = []    # (dados, var_incluir, var_categoria, var_conta)

        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📥 Importar Extrato Bancário",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(20, 5))

        ctk.CTkLabel(
            self,
            text="Selecione um arquivo .OFX ou .CSV exportado do internet banking do seu banco.",
            font=ctk.CTkFont(size=12), text_color=COLORS['text']
        ).pack(pady=(0, 10))

        # Barra de seleção de arquivo + conta padrão
        topo = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=10)
        topo.pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(topo, text="📂 Selecionar Arquivo", fg_color=COLORS['accent'],
                      command=self._selecionar_arquivo).pack(side="left", padx=15, pady=12)

        self.arquivo_label = ctk.CTkLabel(topo, text="Nenhum arquivo selecionado",
                                           text_color=COLORS['text'])
        self.arquivo_label.pack(side="left", padx=10)

        ctk.CTkLabel(topo, text="Conta padrão:", text_color=COLORS['text']).pack(side="left", padx=(30, 5))
        self.conta_padrao_var = ctk.StringVar(value=ACCOUNTS[0])
        ctk.CTkOptionMenu(topo, variable=self.conta_padrao_var, values=ACCOUNTS,
                          fg_color=COLORS['card'], button_color=COLORS['accent'],
                          width=160).pack(side="left", padx=(0, 15))

        # Cabeçalho da tabela de revisão
        self.info_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12, weight="bold"),
                                        text_color=COLORS['warning'])
        self.info_label.pack(pady=(10, 0))

        # Área scrollável com as linhas para revisão
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_secondary'], corner_radius=10)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Botões de ação (aparecem só depois de carregar um arquivo)
        self.acoes_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
        self.acoes_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_marcar_todas = ctk.CTkButton(
            self.acoes_frame, text="Marcar/Desmarcar Todas", fg_color=COLORS['card'],
            command=self._alternar_todas)
        self.btn_confirmar = ctk.CTkButton(
            self.acoes_frame, text="✅ Confirmar Importação", fg_color=COLORS['success'],
            command=self._confirmar_importacao)

    # -----------------------------------------------------------------
    def _selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o extrato bancário",
            filetypes=[("Extratos", "*.ofx *.qfx *.csv"), ("Todos os arquivos", "*.*")]
        )
        if not caminho:
            return

        try:
            self.transacoes_lidas = self.controllers['import'].ler_arquivo(caminho)
        except Exception as e:
            messagebox.showerror("Erro ao ler arquivo", str(e))
            return

        if not self.transacoes_lidas:
            messagebox.showinfo("Nada encontrado",
                                 "Não foi possível encontrar transações nesse arquivo.")
            return

        nome_arquivo = caminho.split('/')[-1].split('\\')[-1]
        self.arquivo_label.configure(text=nome_arquivo)
        self._montar_preview()

    def _montar_preview(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self.linhas_widgets = []

        duplicadas = sum(1 for t in self.transacoes_lidas if t['duplicada'])
        total = len(self.transacoes_lidas)
        self.info_label.configure(
            text=f"{total} lançamento(s) encontrado(s) — {duplicadas} possível(is) duplicata(s) "
                 f"(já desmarcada(s) abaixo, mas você pode incluir se quiser)."
        )

        cats = list(CATEGORIES.keys())

        # Cabeçalho da grade
        cab = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_primary'])
        cab.pack(fill="x", pady=(0, 5))
        for texto, largura in [("Incluir", 60), ("Data", 90), ("Descrição", 260),
                                ("Valor", 110), ("Tipo", 90), ("Categoria", 180), ("Conta", 150)]:
            ctk.CTkLabel(cab, text=texto, width=largura, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COLORS['warning']).pack(side="left", padx=2)

        for t in self.transacoes_lidas:
            linha = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_primary'])
            linha.pack(fill="x", pady=1)

            # Duplicata vem desmarcada por padrão; nova transação vem marcada
            var_incluir = ctk.BooleanVar(value=not t['duplicada'])
            ctk.CTkCheckBox(linha, text="", variable=var_incluir, width=60,
                            fg_color=COLORS['accent']).pack(side="left", padx=2)

            cor_texto = COLORS['warning'] if t['duplicada'] else COLORS['text']
            ctk.CTkLabel(linha, text=t['data'], width=90, text_color=cor_texto).pack(side="left", padx=2)

            desc_exibida = t['descricao'][:38] + ('…' if len(t['descricao']) > 38 else '')
            texto_desc = desc_exibida + (" (duplicata?)" if t['duplicada'] else "")
            ctk.CTkLabel(linha, text=texto_desc, width=260, text_color=cor_texto,
                         anchor="w").pack(side="left", padx=2)

            valor_fmt = formatar_valor(t['valor'], self.ocultar)
            cor_valor = COLORS['success'] if t['tipo'] == 'Receita' else COLORS['error']
            ctk.CTkLabel(linha, text=valor_fmt, width=110, text_color=cor_valor).pack(side="left", padx=2)

            ctk.CTkLabel(linha, text=t['tipo'], width=90, text_color=cor_texto).pack(side="left", padx=2)

            var_categoria = ctk.StringVar(value=t['categoria_sugerida'])
            ctk.CTkOptionMenu(linha, variable=var_categoria, values=cats, width=180,
                              fg_color=COLORS['card'], button_color=COLORS['accent']).pack(side="left", padx=2)

            var_conta = ctk.StringVar(value=self.conta_padrao_var.get())
            ctk.CTkOptionMenu(linha, variable=var_conta, values=ACCOUNTS, width=150,
                              fg_color=COLORS['card'], button_color=COLORS['accent']).pack(side="left", padx=2)

            self.linhas_widgets.append((t, var_incluir, var_categoria, var_conta))

        self.btn_marcar_todas.pack(side="left", padx=(0, 10))
        self.btn_confirmar.pack(side="left")

    def _alternar_todas(self):
        if not self.linhas_widgets:
            return
        novo_estado = not self.linhas_widgets[0][1].get()
        for _, var_incluir, _, _ in self.linhas_widgets:
            var_incluir.set(novo_estado)

    def _confirmar_importacao(self):
        selecionadas = []
        for t, var_incluir, var_categoria, var_conta in self.linhas_widgets:
            if var_incluir.get():
                selecionadas.append({
                    'data': t['data'],
                    'descricao': t['descricao'],
                    'valor': t['valor'],
                    'tipo': t['tipo'],
                    'categoria': var_categoria.get(),
                    'conta': var_conta.get(),
                })

        if not selecionadas:
            messagebox.showinfo("Nada selecionado", "Marque ao menos uma transação para importar.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar importação",
            f"Deseja importar {len(selecionadas)} transação(ões) para o Ket Finance?"
        )
        if not confirmar:
            return

        qtd = self.controllers['import'].confirmar_importacao(
            selecionadas, self.conta_padrao_var.get()
        )
        messagebox.showinfo("Importação concluída", f"{qtd} transação(ões) importada(s) com sucesso!")

        # Limpa a tela para uma nova importação
        self.transacoes_lidas = []
        self.linhas_widgets = []
        self.arquivo_label.configure(text="Nenhum arquivo selecionado")
        self.info_label.configure(text="")
        for w in self.scroll.winfo_children():
            w.destroy()
        self.btn_marcar_todas.pack_forget()
        self.btn_confirmar.pack_forget()

        if self.callback:
            self.callback()
