"""Dashboard unificado — todos os dashboards em scroll vertical"""
import customtkinter as ctk
from config import COLORS, MESES, CATEGORY_COLORS
from utils.formatters import formatar_valor, mes_ano_atual


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db, controllers, ocultar_valores=False):
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        self.db = db
        self.controllers = controllers
        self.ocultar = ocultar_valores
        self.mes, self.ano = mes_ano_atual()
        self.visualizacao_grafico = "📊 Últimos Meses"  # aba selecionada por padrão

        # Frame scrollável
        
        # Frame scrollável
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_primary'])
        self.scroll.pack(fill="both", expand=True)
        
        self._build()

    def _build(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        tc = self.controllers['transaction']
        resumo = tc.get_resumo_mes(self.mes, self.ano)
        historico = tc.get_resumo_ultimos_meses(6)
        despesas_cat = self._calcular_despesas()

        # ── Filtro mês/ano global ─────────────────────────────────
        filtro = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_primary'])
        filtro.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkButton(filtro, text="◀", width=30, fg_color=COLORS['card'],
                      hover_color=COLORS['accent'],
                      command=self._mes_anterior).pack(side="left")

        nome_mes = MESES.get(self.mes, '')
        sinal = "[+]" if resumo['saldo'] >= 0 else "[-]"
        ctk.CTkLabel(filtro,
                     text=f"{sinal}  {nome_mes} {self.ano}",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS['success'] if resumo['saldo'] >= 0 else COLORS['error']
                     ).pack(side="left", expand=True)

        ctk.CTkButton(filtro, text="▶", width=30, fg_color=COLORS['card'],
                      hover_color=COLORS['accent'],
                      command=self._mes_proximo).pack(side="right")

        # ══════════════════════════════════════════════════════════
        # DASHBOARD 1: Receitas vs Despesas
        # ══════════════════════════════════════════════════════════
        self._dashboard_receitas_despesas(resumo, historico)

        # Separador
        ctk.CTkFrame(self.scroll, height=2, fg_color=COLORS['accent']).pack(
            fill="x", padx=40, pady=20)

        # ══════════════════════════════════════════════════════════
        # DASHBOARD 2: Gastos por Categoria
        # ══════════════════════════════════════════════════════════
        self._dashboard_categorias(despesas_cat)

    def _dashboard_receitas_despesas(self, resumo, historico):
        """Dashboard de Receitas vs Despesas"""
        ctk.CTkLabel(self.scroll, text="📊 Receitas vs Despesas",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(0, 10))

        # 3 Cards
        frame_cards = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_primary'])
        frame_cards.pack(fill="x", padx=20, pady=5)

        cards = [
            ("Receitas", resumo['receitas'], COLORS['success']),
            ("Despesas", resumo['despesas'], COLORS['error']),
            ("Saldo", resumo['saldo'], COLORS['info'] if resumo['saldo'] >= 0 else COLORS['error']),
        ]
        for titulo, valor, cor in cards:
            card = ctk.CTkFrame(frame_cards, fg_color=COLORS['card'], corner_radius=12)
            card.pack(side="left", expand=True, fill="both", padx=6)
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12),
                         text_color=COLORS['text']).pack(pady=(12, 2))
            ctk.CTkLabel(card, text=formatar_valor(valor, self.ocultar),
                         font=ctk.CTkFont(size=17, weight="bold"),
                         text_color=cor).pack(pady=(0, 12))

        # Indicador
        msg = "Mes positivo — suas receitas superam as despesas!" if resumo['saldo'] >= 0 else "Mes negativo — suas despesas superam as receitas."
        cor_msg = COLORS['success'] if resumo['saldo'] >= 0 else COLORS['error']
        ctk.CTkLabel(self.scroll, text=msg, font=ctk.CTkFont(size=12),
                     text_color=cor_msg).pack(pady=(5, 10))

        # Gráfico de barras agrupadas
                # Abas para escolher entre visão mensal (barras) e diária (linhas)
        self._historico_cache = historico
        toggle_frame = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_primary'])
        toggle_frame.pack(pady=(0, 8))

        self.seg_grafico = ctk.CTkSegmentedButton(
            toggle_frame,
            values=["📊 Últimos Meses", "📈 Diário do Mês"],
            command=self._trocar_grafico_rd,
            fg_color=COLORS['card'],
            selected_color=COLORS['accent'],
            unselected_color=COLORS['card']
        )
        self.seg_grafico.set(self.visualizacao_grafico)
        self.seg_grafico.pack()

        # Container onde o gráfico ativo é desenhado
        self.frame_grafico_rd = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_primary'])
        self.frame_grafico_rd.pack(fill="x")

        self._desenhar_grafico_rd()

    def _dashboard_categorias(self, despesas_cat):
        """Dashboard de Gastos por Categoria"""
        ctk.CTkLabel(self.scroll, text="🍕 Gastos por Categoria",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(0, 10))

        if not despesas_cat:
            ctk.CTkLabel(self.scroll, text="Nenhuma despesa registrada neste mes.",
                         text_color=COLORS['text'], font=ctk.CTkFont(size=13)).pack(pady=20)
            return

        # Layout: donut à esquerda, lista à direita
        corpo = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_primary'], height=400)
        corpo.pack(fill="x", padx=20, pady=5)
        corpo.pack_propagate(False)

        frame_grafico = ctk.CTkFrame(corpo, fg_color=COLORS['bg_primary'])
        frame_grafico.pack(side="left", fill="both", expand=True)
        self._grafico_donut(frame_grafico, despesas_cat)

        frame_lista = ctk.CTkFrame(corpo, fg_color=COLORS['bg_secondary'], corner_radius=12, width=280)
        frame_lista.pack(side="right", fill="y", padx=(10, 0))
        frame_lista.pack_propagate(False)
        self._lista_categorias(frame_lista, despesas_cat)

    def _calcular_despesas(self):
        tc = self.controllers['transaction']
        transacoes = tc.get_por_mes(self.mes, self.ano)
        totais = {}
        for t in transacoes:
            if t.tipo == 'Despesa':
                totais[t.categoria] = totais.get(t.categoria, 0.0) + t.valor
        return dict(sorted(totais.items(), key=lambda x: x[1], reverse=True))

    def _trocar_grafico_rd(self, valor):
        """Chamado quando o usuário clica numa aba do seletor de gráfico."""
        self.visualizacao_grafico = valor
        self._desenhar_grafico_rd()

    def _desenhar_grafico_rd(self):
        """Limpa o container e desenha o gráfico correspondente à aba ativa."""
        for w in self.frame_grafico_rd.winfo_children():
            w.destroy()

        if self.visualizacao_grafico == "📈 Diário do Mês":
            dados = self.controllers['transaction'].get_movimentacao_diaria(self.mes, self.ano)
            self._grafico_linhas_diario(dados)
        else:
            self._grafico_barras(self._historico_cache)

    def _grafico_linhas_diario(self, dados):
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            dias = dados['dias']
            receitas = dados['receitas']
            despesas = dados['despesas']

            fig, ax = plt.subplots(figsize=(7, 3), facecolor=COLORS['chart_bg'])
            ax.set_facecolor(COLORS['chart_bg'])

            ax.plot(dias, receitas, label='Receitas', color=COLORS['success'],
                    marker='o', markersize=3, linewidth=1.8, zorder=3)
            ax.plot(dias, despesas, label='Despesas', color=COLORS['error'],
                    marker='o', markersize=3, linewidth=1.8, zorder=3)

            ax.set_xticks(dias)
            ax.set_xticklabels(dias, color=COLORS['text'], fontsize=6)
            ax.tick_params(axis='y', colors=COLORS['text'], labelsize=7)
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: f"R${v/1000:.0f}k" if v >= 1000 else f"R${v:.0f}")
            )
            ax.set_xlabel("Dia do mês", color=COLORS['text'], fontsize=8)
            ax.grid(axis='y', color=COLORS['bg_secondary'], linewidth=0.5, zorder=0)
            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.legend(facecolor=COLORS['bg_secondary'], labelcolor=COLORS['text'],
                      fontsize=8, framealpha=0.6)

            fig.subplots_adjust(top=0.9, bottom=0.22, left=0.1, right=0.97)
            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico_rd)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=20, pady=(0, 10))
            plt.close(fig)
        except Exception as e:
            print(f"Erro ao renderizar gráfico de linhas: {e}")

    def _grafico_barras(self, historico):
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            labels = [h['label'] for h in historico]
            receitas = [h['receitas'] for h in historico]
            despesas = [h['despesas'] for h in historico]

            x = np.arange(len(labels))
            largura = 0.35

            fig, ax = plt.subplots(figsize=(7, 3), facecolor=COLORS['chart_bg'])
            ax.set_facecolor(COLORS['chart_bg'])

            b1 = ax.bar(x - largura / 2, receitas, largura, label='Receitas',
                        color=COLORS['success'], zorder=3)
            b2 = ax.bar(x + largura / 2, despesas, largura, label='Despesas',
                        color=COLORS['error'], zorder=3)

            ax.set_xticks(x)
            ax.set_xticklabels(labels, color=COLORS['text'], fontsize=8)
            ax.tick_params(axis='y', colors=COLORS['text'], labelsize=7)
            ax.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda v, _: f"R${v/1000:.0f}k" if v >= 1000 else f"R${v:.0f}")
            )
            ax.grid(axis='y', color=COLORS['bg_secondary'], linewidth=0.5, zorder=0)
            for spine in ax.spines.values():
                spine.set_visible(False)

            for bar in list(b1) + list(b2):
                h = bar.get_height()
                if h > 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, h,
                            f"R${h:,.0f}".replace(',', '.'),
                            ha='center', va='bottom', color=COLORS['text'], fontsize=6)

            ax.legend(facecolor=COLORS['bg_secondary'], labelcolor=COLORS['text'],
                      fontsize=8, framealpha=0.6)

            fig.subplots_adjust(top=0.88, bottom=0.18, left=0.12, right=0.97)
            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico_rd)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=20, pady=(0, 10))
            plt.close(fig)
        except Exception as e:
            print(f"Erro ao renderizar gráfico de barras: {e}")

    def _grafico_donut(self, parent, despesas_cat):
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            categorias = list(despesas_cat.keys())
            valores = list(despesas_cat.values())
            total = sum(valores)
            maior_cat = categorias[0]

            cores = [CATEGORY_COLORS.get(c, '#64748b') for c in categorias]
            explode = [0.06 if c == maior_cat else 0 for c in categorias]

            fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor=COLORS['chart_bg'])
            ax.set_facecolor(COLORS['chart_bg'])

            wedges, _ = ax.pie(valores, colors=cores, explode=explode, startangle=90,
                               wedgeprops=dict(width=0.55, edgecolor=COLORS['chart_bg'], linewidth=2))

            wedges[0].set_linewidth(3)
            wedges[0].set_edgecolor('white')

            ax.text(0, 0.08, "Total", ha='center', va='center',
                    color=COLORS['text'], fontsize=9)
            ax.text(0, -0.18, formatar_valor(total), ha='center', va='center',
                    color='white', fontsize=11, fontweight='bold')

            fig.subplots_adjust(top=0.95, bottom=0.05, left=0.05, right=0.95)
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        except Exception as e:
            print(f"Erro ao renderizar gráfico donut: {e}")

    def _lista_categorias(self, parent, despesas_cat):
        total = sum(despesas_cat.values())
        maior_cat = next(iter(despesas_cat))

        ctk.CTkLabel(parent, text="Detalhamento", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS['text']).pack(pady=(12, 6))

        scroll = ctk.CTkScrollableFrame(parent, fg_color=COLORS['bg_primary'])
        scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        for cat, valor in despesas_cat.items():
            pct = (valor / total * 100) if total > 0 else 0
            cor = CATEGORY_COLORS.get(cat, '#64748b')
            destaque = cat == maior_cat

            row = ctk.CTkFrame(scroll,
                               fg_color=COLORS['card'] if destaque else COLORS['bg_secondary'],
                               corner_radius=8, border_width=2 if destaque else 0,
                               border_color=cor if destaque else COLORS['bg_secondary'])
            row.pack(fill="x", pady=3)

            canvas_cor = ctk.CTkCanvas(row, width=12, height=12,
                                       bg=COLORS['card'] if destaque else COLORS['bg_secondary'],
                                       highlightthickness=0)
            canvas_cor.pack(side="left", padx=(8, 4), pady=8)
            canvas_cor.create_rectangle(0, 0, 12, 12, fill=cor, outline="")

            ctk.CTkLabel(row, text=cat,
                         font=ctk.CTkFont(size=11, weight="bold" if destaque else "normal"),
                         text_color='white' if destaque else COLORS['text'],
                         anchor="w").pack(side="left", expand=True)

            info = ctk.CTkFrame(row, fg_color=COLORS['bg_primary'])
            info.pack(side="right", padx=8)
            ctk.CTkLabel(info, text=f"{pct:.1f}%", font=ctk.CTkFont(size=10),
                         text_color=cor).pack(anchor="e")
            ctk.CTkLabel(info, text=formatar_valor(valor, self.ocultar),
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color='white').pack(anchor="e")

    def _mes_anterior(self):
        if self.mes == 1:
            self.mes, self.ano = 12, self.ano - 1
        else:
            self.mes -= 1
        self._build()

    def _mes_proximo(self):
        if self.mes == 12:
            self.mes, self.ano = 1, self.ano + 1
        else:
            self.mes += 1
        self._build()
