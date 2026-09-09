"""Tela de Metas de Orçamento"""
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config import COLORS


class BudgetGoalsView(ctk.CTkFrame):
    def __init__(self, parent, db, controllers, **kwargs):
        super().__init__(parent, fg_color=COLORS['bg_primary'])
        self.db = db
        self.budget_controller = controllers['budget']
        
        # Cores das categorias (seguindo o padrão do projeto)
        self.cores_categorias = {
            "Moradia": "#8b5cf6",           # Roxo/violeta
            "Educação": "#3b82f6",          # Azul claro
            "Reserva de Emergência": "#ec4899",  # Rosa
            "Investimentos": "#6366f1",     # Roxo escuro
            "Lazer": "#f97316",             # Laranja
            "Viagem": "#f0c040"             # Amarelo/dourado
        }
        
        # Variáveis para armazenar os sliders e labels
        self.sliders = {}
        self.labels_percentual = {}
        self.label_aviso = None
        
        # Canvas do gráfico
        self.canvas_grafico = None
        self.fig = None
        self.ax = None
        
        # Carregar dados salvos ou usar padrão
        self.metas_atuais = self.budget_controller.carregar_metas_orcamento()
        
        # Construir interface
        self._build_ui()
        
        # Atualizar gráfico inicial
        self.atualizar_grafico()
    
    def _build_ui(self):
        """Constrói a interface completa"""
        # Container principal com dois painéis lado a lado
        container = ctk.CTkFrame(self, fg_color=COLORS['bg_primary'])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configurar grid para dividir em 2 colunas
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # Painel esquerdo - Visualização
        self.criar_painel_esquerdo(container)
        
        # Painel direito - Controles
        self.criar_painel_direito(container)
    
    def criar_painel_esquerdo(self, parent):
        """Cria o painel esquerdo com o gráfico de rosca"""
        painel = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=10)
        painel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Título do painel
        ctk.CTkLabel(
            painel,
            text="Visualização de uso",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 10))
        
        # Frame para o gráfico
        frame_grafico = ctk.CTkFrame(painel, fg_color="#2b2b2b")
        frame_grafico.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Criar figura do matplotlib
        self.fig = Figure(figsize=(6, 5), facecolor='#2b2b2b')
        self.ax = self.fig.add_subplot(111)
        
        # Canvas para embutir o gráfico
        self.canvas_grafico = FigureCanvasTkAgg(self.fig, frame_grafico)
        self.canvas_grafico.get_tk_widget().pack(fill="both", expand=True)
        
        # Frame para a legenda
        frame_legenda = ctk.CTkFrame(painel, fg_color="#2b2b2b")
        frame_legenda.pack(pady=10)
        
        # Criar legenda em duas colunas
        self.criar_legenda(frame_legenda)
        
        # Botão Resetar Valores
        ctk.CTkButton(
            painel,
            text="Resetar Valores",
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            text_color="white",
            font=ctk.CTkFont(size=13),
            command=self.resetar_valores,
            width=200,
            height=35
        ).pack(pady=(10, 20))
    
    def criar_legenda(self, parent):
        """Cria a legenda do gráfico em duas colunas"""
        categorias = list(self.cores_categorias.keys())
        
        # Frame para organizar em grid
        grid_frame = ctk.CTkFrame(parent, fg_color="#2b2b2b")
        grid_frame.pack()
        
        for i, categoria in enumerate(categorias):
            row = i // 2
            col = i % 2
            
            # Frame para cada item da legenda
            item_frame = ctk.CTkFrame(grid_frame, fg_color="#2b2b2b")
            item_frame.grid(row=row, column=col, padx=15, pady=5, sticky="w")
            
            # Quadrado colorido
            cor_frame = ctk.CTkFrame(
                item_frame,
                width=15,
                height=15,
                fg_color=self.cores_categorias[categoria],
                corner_radius=3
            )
            cor_frame.pack(side="left", padx=(0, 8))
            cor_frame.pack_propagate(False)
            
            # Nome da categoria
            ctk.CTkLabel(
                item_frame,
                text=categoria,
                font=ctk.CTkFont(size=12),
                text_color="white"
            ).pack(side="left")
    
    def criar_painel_direito(self, parent):
        """Cria o painel direito com os sliders de controle"""
        painel = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=10)
        painel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Título do painel
        ctk.CTkLabel(
            painel,
            text="Controle de Orçamento",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 20))
        
        # Frame scrollable para os sliders
        scroll_frame = ctk.CTkScrollableFrame(
            painel,
            fg_color="#2b2b2b",
            scrollbar_button_color="#4a4a4a",
            scrollbar_button_hover_color="#5a5a5a"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Criar sliders para cada categoria
        for categoria in self.cores_categorias.keys():
            self.criar_slider_categoria(scroll_frame, categoria)
        
        # Label de aviso (inicialmente invisível)
        self.label_aviso = ctk.CTkLabel(
            painel,
            text="⚠️ Total não pode ultrapassar 100%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ef4444",
            fg_color="#2b2b2b"
        )
        self.label_aviso.pack(pady=(5, 10))
        self.label_aviso.pack_forget()  # Esconder inicialmente
        
        # Botão Salvar
        ctk.CTkButton(
            painel,
            text="Salvar",
            fg_color="#f0c040",
            hover_color="#d4a830",
            text_color="black",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.salvar_dados,
            width=200,
            height=40
        ).pack(pady=(5, 20))
    
    def criar_slider_categoria(self, parent, categoria):
        """Cria um slider para uma categoria específica"""
        # Frame para a categoria
        frame_cat = ctk.CTkFrame(parent, fg_color="#2b2b2b")
        frame_cat.pack(fill="x", pady=10)
        
        # Frame superior: nome e percentual
        frame_top = ctk.CTkFrame(frame_cat, fg_color="#2b2b2b")
        frame_top.pack(fill="x", pady=(0, 5))
        
        # Nome da categoria
        ctk.CTkLabel(
            frame_top,
            text=categoria,
            font=ctk.CTkFont(size=13),
            text_color="white"
        ).pack(side="left")
        
        # Label do percentual
        label_percent = ctk.CTkLabel(
            frame_top,
            text=f"{self.metas_atuais[categoria]}%",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        )
        label_percent.pack(side="right")
        self.labels_percentual[categoria] = label_percent
        
        # Slider
        slider = ctk.CTkSlider(
            frame_cat,
            from_=0,
            to=100,
            number_of_steps=20,  # Passos de 5%
            fg_color="#4a4a4a",
            progress_color=self.cores_categorias[categoria],
            button_color=self.cores_categorias[categoria],
            button_hover_color=self._escurecer_cor(self.cores_categorias[categoria]),
            command=lambda v, c=categoria: self.ao_mover_slider(c, v)
        )
        slider.set(self.metas_atuais[categoria])
        slider.pack(fill="x", pady=(0, 5))
        
        self.sliders[categoria] = slider
    
    def _escurecer_cor(self, hex_color):
        """Escurece uma cor hexadecimal para o efeito hover"""
        # Remove o #
        hex_color = hex_color.lstrip('#')
        # Converte para RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Escurece 20%
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        # Retorna em hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def ao_mover_slider(self, categoria, valor):
        """
        Callback chamado quando um slider é movido.
        Atualiza o percentual e valida o total.
        """
        # Arredondar para múltiplo de 5
        valor = round(valor / 5) * 5
        
        # Atualizar valor temporário
        self.metas_atuais[categoria] = int(valor)
        
        # Validar total
        valido, total = self.budget_controller.validar_total(self.metas_atuais)
        
        if not valido:
            # Reverter para o valor anterior
            diferenca = total - 100
            self.metas_atuais[categoria] = int(valor - diferenca)
            self.sliders[categoria].set(self.metas_atuais[categoria])
            
            # Mostrar aviso
            self.label_aviso.pack(pady=(5, 10))
        else:
            # Esconder aviso
            self.label_aviso.pack_forget()
        
        # Atualizar label do percentual
        self.labels_percentual[categoria].configure(
            text=f"{self.metas_atuais[categoria]}%"
        )
        
        # Atualizar gráfico
        self.atualizar_grafico()
    
    def atualizar_grafico(self):
        """Atualiza o gráfico de rosca com os valores atuais"""
        # Limpar gráfico anterior
        self.ax.clear()
        
        # Preparar dados
        categorias = list(self.metas_atuais.keys())
        valores = list(self.metas_atuais.values())
        cores = [self.cores_categorias[cat] for cat in categorias]
        
        # Calcular total
        total = sum(valores)
        
        # Criar gráfico de rosca
        wedges, texts, autotexts = self.ax.pie(
            valores,
            labels=None,  # Sem labels no gráfico (usamos legenda)
            colors=cores,
            autopct='%1.0f%%',
            startangle=90,
            pctdistance=0.85,
            wedgeprops=dict(width=0.4, edgecolor='#2b2b2b', linewidth=2)
        )
        
        # Estilizar os textos dos percentuais
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_weight('bold')
        
        # Adicionar texto no centro
        self.ax.text(
            0, 0,
            f'{int(total)}%\nTotal',
            ha='center',
            va='center',
            fontsize=16,
            weight='bold',
            color='white'
        )
        
        # Configurar fundo
        self.ax.set_facecolor('#2b2b2b')
        self.fig.patch.set_facecolor('#2b2b2b')
        
        # Ajustar layout
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.05)
        
        # Redesenhar canvas
        self.canvas_grafico.draw()
    
    def salvar_dados(self):
        """Salva os dados no JSON e Excel"""
        try:
            # Validar total
            valido, total = self.budget_controller.validar_total(self.metas_atuais)
            
            if not valido:
                messagebox.showerror(
                    "Erro",
                    f"O total ({int(total)}%) ultrapassa 100%.\nAjuste os valores antes de salvar."
                )
                return
            
            # Salvar
            self.budget_controller.salvar_metas_orcamento(self.metas_atuais)
            
            messagebox.showinfo(
                "Sucesso",
                f"Metas de orçamento salvas com sucesso!\n\n"
                f"📁 JSON: dados_financeiros.json\n"
                f"📊 Excel: metas_orcamento.xlsx"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
    
    def resetar_valores(self):
        """Reseta todos os sliders para os valores padrão"""
        if messagebox.askyesno(
            "Confirmar",
            "Deseja resetar todos os valores para o padrão?\n\n"
            "Moradia: 30%\n"
            "Educação: 10%\n"
            "Reserva de Emergência: 20%\n"
            "Investimentos: 20%\n"
            "Lazer: 10%\n"
            "Viagem: 10%"
        ):
            # Resetar valores
            self.metas_atuais = self.budget_controller.resetar_valores()
            
            # Atualizar sliders e labels
            for categoria, valor in self.metas_atuais.items():
                self.sliders[categoria].set(valor)
                self.labels_percentual[categoria].configure(text=f"{valor}%")
            
            # Esconder aviso
            self.label_aviso.pack_forget()
            
            # Atualizar gráfico
            self.atualizar_grafico()
            
            messagebox.showinfo("Sucesso", "Valores resetados para o padrão!")
