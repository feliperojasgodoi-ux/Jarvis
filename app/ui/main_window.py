from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLabel,
    QHeaderView,
    QFrame,
    QSplitter,
    QStyledItemDelegate,
    QSizePolicy,
    QComboBox,
    QDateEdit,
    QTableView,

)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSettings, QDate
from ..repository import TransacaoRepository
from ..models import TipoTransacao, Categorias
from .dialogs import TransacaoDialog
from ..charts import DonutChartWidget, CategoryBarChartWidget
from matplotlib import cm
from datetime import date, timedelta
from typing import Optional
from .calendar_style import beautify_calendar, TodayRingDelegate
# from ..charts import BarChartWidget  # se precisar do gráfico de barras mensal

class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter 

class MainWindow(QMainWindow):
    def __init__(self, repo: TransacaoRepository):
        super().__init__()
        self.repo = repo
        self.setWindowTitle("Gerenciador Financeiro")
        self.resize(900, 600)
        # Paleta e dicionário de cores por categoria
        self._palette = list(cm.get_cmap("tab20").colors)  # 20 cores harmonizadas
        self._color_idx = 0
        self._cat_colors = {}  # {"Categoria": (r,g,b)}


        # Root widget
        root = QWidget()
        self.setCentralWidget(root)
        root.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #e0e0e0;
            font-family: Arial, sans-serif;
        }
        """)
        layout = QVBoxLayout(root)
        
        # Toolbar
        tb = QHBoxLayout()
        self.btn_add = QPushButton("Adicionar")
        self.btn_del = QPushButton("Remover Selecionada")
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems([
            "Mês",
            "Sempre",
            "Últimos 12 meses"
        ])
        
        self.mes_ref = QDateEdit(QDate.currentDate())
        self.mes_ref.setDisplayFormat("MM/yyyy")
        self.mes_ref.setCalendarPopup(True)
        # tornar "Mês" seleção padrão e mostrar o seletor já ao iniciar
        cal = self.mes_ref.calendarWidget()
        beautify_calendar(cal)
        table_view = cal.findChild(QTableView)
        table_view.setItemDelegate(TodayRingDelegate(table_view))
        self.mes_ref.setVisible(True)
        self.combo_periodo.setCurrentIndex(0)

        # não chamar o handler ainda — a UI (tabela) será construída abaixo

        tb.insertWidget(0, QLabel("Período: "))
        tb.insertWidget(1, self.combo_periodo)
        tb.insertWidget(2, self.mes_ref)


        self.combo_periodo.currentIndexChanged.connect(self._on_periodo_changed)
        self.mes_ref.dateChanged.connect(self._aplicar_filtro)
        self._inicio: Optional[date] = None
        self._fim: Optional[date] = None

        self.combo_cat = QComboBox()
        self.combo_cat.addItem("Todas as categorias")
        self.combo_cat.addItems(Categorias.Categorias_PADRAO)
        self.combo_cat.currentIndexChanged.connect(self._aplicar_filtro)

        tb.insertWidget(3, QLabel("Categoria: "))
        tb.insertWidget(4, self.combo_cat)

                # ===== Estilo dark para botões e label de saldo =====
        btn_qss = """
        QPushButton {
            background: #2b2d31;         /* fundo escuro */
            color: #eaeaea;              /* texto claro */
            border: 1px solid #3a3d42;
            border-radius: 8px;
            padding: 6px 12px;
            font-family: Segue UI, sans-serif;
            font-weight: 600;
        }
        QPushButton:hover { border-color: #3a86ff; }
        QPushButton:pressed { background: #1e1f22; }
        """
        self.btn_add.setStyleSheet(btn_qss)
        self.btn_del.setStyleSheet(btn_qss)

        self.lbl_saldo = QLabel("Saldo: R$ 0,00")
        self.lbl_saldo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # Saldo mais visível no tema escuro
        self.lbl_saldo.setStyleSheet("color: #eaeaea; font-weight: 700;font: Segoe UI, sans-serif;")

        tb.addWidget(self.btn_add)
        tb.addWidget(self.btn_del)
        tb.addStretch()
        tb.addWidget(self.lbl_saldo)

        layout.addLayout(tb)

        # Tabela

        self.table = QTableWidget(0, 6)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(36)       # altura das linhas
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setFrameShape(QFrame.NoFrame)      
        self.table.setHorizontalHeaderLabels(
            [ "Data","Tipo", "Categoria", "Banco", "Valor (R$)", "Descrição"]
        )
        self.table.setItemDelegate(AlignDelegate(self.table))  # centraliza todo o conteúdo
        self.settings = QSettings("Felipe", "JarvisFinance")
        state = self.settings.value("table/header_state") 
        
        if state is not None:
            self.table.horizontalHeader().restoreState(state)
        header = self.table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.Interactive)

        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.viewport().update()
        self.table.update()

       # >>> Stylesheet ÚNICO (sem dark_style + sem palette)
        self.table.setStyleSheet("""
        /* Tabela como 'card' */
        QTableWidget {
            background-color: #1e1f22;
            color: #eaeaea;
            border: 1px solid #2b2d31;
            border-radius: 14px;
            gridline-color: #2b2d31;
            font-family: Segoe UI, sans-serif;

            /* Alternância de linhas no tema dark */
            alternate-background-color: #24272c;  /* ímpares */
        }

        /* Itens */
        QTableWidget::item { background-color: transparent; }
        QTableWidget::item:selected { background: #2a2d33; }
        QTableWidget::item:hover:!selected { background: rgba(255,255,255,0.04); }

        /* Cabeçalho (mesma cor do 'canto' e cantos arredondados) */
        QHeaderView::section {
            background-color: #2b2d31;
            color: #eaeaea;
            padding: 8px 10px;
            border: none;
            border-right: 1px solid #3a3d42;
            font: Segoe UI, sans-serif;
        }
        QHeaderView::section:first { 
            border-top-left-radius: 14px; 
        }
        QHeaderView::section:last { 
            border-right: none; 
            border-top-right-radius: 14px; 
        }

        /* Botão do canto e corner da área de scroll (elimina rebarba) */
        QTableCornerButton::section {
            background-color: #2b2d31;
            border: none;
            border-top-left-radius: 14px;
        }
        QAbstractScrollArea::corner { background: #1e1f22; }

        /* Scrollbars (opcional) */
        QScrollBar:vertical, QScrollBar:horizontal { background: transparent; }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #3a3d42; border-radius: 6px;
        }
        QScrollBar::add-line, QScrollBar::sub-line { background: transparent; }
        """)
        

        # Área de gráficos
        self.chart_pie = DonutChartWidget([])
        self.chart_bars  = CategoryBarChartWidget([], [], title="")


        # container horizontal para os 2 gráficos (sem barra divisória)
        charts_container = QWidget()
        charts_layout = QHBoxLayout(charts_container)
        charts_layout.setContentsMargins(0, 16, 0, 0)   # top margin p/ respirar da tabela
        charts_layout.setSpacing(16)

        # faz cada gráfico expandir igualmente
        for w in (self.chart_pie, self.chart_bars):
            w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            charts_layout.addWidget(w, 1)  # peso 1 para cada
    
        self.charts_title = QLabel("Gráficos por Categoria")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.charts_title.setFont(font)
        self.charts_title.setAlignment(Qt.AlignCenter)
        self.charts_title.setStyleSheet("color: #eaeaea; padding: 8px; font: Segoe UI, sans-serif;")

        charts_block = QWidget()
        block_layout = QVBoxLayout(charts_block)
        block_layout.setContentsMargins(0, 12, 0, 0)
        block_layout.setSpacing(8)
        block_layout.addWidget(self.charts_title)
        block_layout.addWidget(charts_container)

        # >>> Splitter vertical 50/50
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)  # impede colapsar um painel
        splitter.addWidget(self.table)
        splitter.addWidget(charts_block)

        # tamanhos iniciais (metade/metade) — ajusta depois do show
        splitter.setStretchFactor(0, 1)  # tabela
        splitter.setStretchFactor(1, 1)  # gráfico

        # (opcional) estilo do “trilho” no tema dark
        splitter.setStyleSheet("""
        QSplitter::handle {
            background: #2b2d31;
        }
        QSplitter::handle:vertical {
            height: 6px;
            margin: 4px 8px;
            border-radius: 3px;
        }
        """)
        layout.addWidget(splitter)
    

        # Sinais
        self.btn_add.clicked.connect(self._adicionar)
        self.btn_del.clicked.connect(self._remover)

        # Inicializa
        # agora que toda a UI foi criada, aplica o período inicial (isto chama _recarregar internamente)
        self._on_periodo_changed(self.combo_periodo.currentIndex())

    def set_charts_title(self, title: str):
        self.charts_title.setText(title)

    def _recarregar(self):

        cat = None
        if hasattr(self, "combo_cat") and self.combo_cat.currentIndex() > 0:
            cat = self.combo_cat.currentText().strip()

        # tabela (com período e categoria)
        if (self._inicio is not None) and (self._fim is not None):
            transacoes = self.repo.listar_filtrado(self._inicio, self._fim, cat)
        else:
            transacoes = self.repo.listar_filtrado(None, None, cat)

        if (self._inicio is not None) and (self._fim is not None):
            dados = self.repo.soma_por_categoria_periodo(TipoTransacao.DESPESA, self._inicio, self._fim)
        else:
            dados = self.repo.soma_por_categoria(TipoTransacao.DESPESA)

        self.table.setRowCount(0)
        total = 0.0
        
        for t in transacoes:
            r = self.table.rowCount()
            self.table.insertRow(r)
            item_data = QTableWidgetItem(t.data.strftime("%d/%m/%Y"))
            item_data.setData(Qt.UserRole, t.id)  # <— ID guardado aqui
            self.table.setItem(r, 0, item_data)
            self.table.setItem(r, 1, QTableWidgetItem(t.tipo.value))
            self.table.setItem(r, 2, QTableWidgetItem(t.categoria))
            self.table.setItem(r, 3, QTableWidgetItem(t.banco))
            self.table.setItem(r, 4, QTableWidgetItem(f"{t.valor:,.2f}"))
            self.table.setItem(r, 5, QTableWidgetItem(t.descricao))
            total += t.valor if t.tipo == TipoTransacao.RECEITA else -t.valor
            

        self.lbl_saldo.setText(f"Saldo: R$ {total:,.2f}")

        # Rosca de despesas por categoria
        dados = self.repo.soma_por_categoria_periodo(TipoTransacao.DESPESA, self._inicio, self._fim)
        pairs = [(d["categoria"], float(d["total"])) for d in dados]

        # atualiza barras (labels e valores)
        labels =[c for c, _ in pairs]
        values = [v for _, v in pairs]

        # lista de cores consistente
        colors = [self._color_for(cat) for cat in labels] if hasattr(self, "_color_for") else None

        # atualiza gráficos com as MESMAS cores
        self.chart_pie.plot(pairs, title="", colors=colors, show_legend=True)
        self.chart_bars.plot(labels, values, title="", colors=colors)  
        
        

    def _adicionar(self):
        dlg = TransacaoDialog(self)
        if dlg.exec_():
            try:
                t = dlg.get_transacao()
                self.repo.adicionar(t)
                self._recarregar()

            except ValueError:
                QMessageBox.warning(
                    self, "Entrada Inválida", "Verifique os dados informados."
                )

    def _remover(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()})
        if not rows:
            QMessageBox.information(
                self,
                "Nenhuma Seleção",
                "Selecione ao menos uma transação para remover.",
            )
            return

        transacao_id = int(self.table.item(rows[0], 0).data(Qt.UserRole))
        self.repo.remover(transacao_id)
        self._recarregar()
    
    def closeEvent(self, event):
        # Salva estado do header da tabela
        self.settings.setValue("table/header_state", self.table.horizontalHeader().saveState())
        super().closeEvent(event)
    
    def _color_for(self, categoria: str):
        if categoria not in self._cat_colors:
            self._cat_colors[categoria] = self._palette[self._color_idx % len(self._palette)]
            self._color_idx += 1
        return self._cat_colors[categoria]

    def _on_periodo_changed(self, idx: int):
        # mostra/oculta o seletor de mês quando necessário
        self.mes_ref.setVisible(self.combo_periodo.currentText().startswith("Mês"))
        self._aplicar_filtro()

    def _aplicar_filtro(self):
        hoje = date.today()
        escolha = self.combo_periodo.currentText()

        if escolha == "Sempre":
            self._inicio, self._fim = None, None

        elif escolha.startswith("Mês"):
            qd = self.mes_ref.date()
            ano, mes = qd.year(), qd.month()
            # 1º dia do mês
            inicio = date(ano, mes, 1)
            # último dia do mês:
            if mes == 12:
                fim = date(ano, 12, 31)
            else:
                fim = date(ano, mes + 1, 1) - timedelta(days=1)
            self._inicio, self._fim = inicio, fim

        elif escolha == "Últimos 12 meses":
            # inclui o dia de hoje e volta 365 dias (simples e efetivo)
            self._fim = hoje
            self._inicio = hoje - timedelta(days=365)

        self._recarregar()
    
    def _atualizar_titulo_charts(self):
        if self._inicio and self._fim:
            if self._inicio.day == 1 and (self._fim.month != self._inicio.month or self._fim.day >= 28):
                # formato "Set/2025" quando for mês cheio
                texto = self._inicio.strftime("%b/%Y").capitalize()
            else:
                texto = f"{self._inicio.strftime('%d/%m/%Y')} – {self._fim.strftime('%d/%m/%Y')}"
        else:
            texto = "Todos os tempos"

        self.charts_title.setText(f"Gráficos por Categoria • {texto}")

