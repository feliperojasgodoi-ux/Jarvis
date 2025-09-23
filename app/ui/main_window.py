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
    QSizePolicy

)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSettings
from ..repository import TransacaoRepository
from ..models import TipoTransacao
from .dialogs import TransacaoDialog
from ..charts import PieChartWidget, CategoryBarChartWidget
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

        # Root widget
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        
        # Toolbar
        tb = QHBoxLayout()
        self.btn_add = QPushButton("Adicionar")
        self.btn_del = QPushButton("Remover Selecionada")
        # ===== Estilo dark para botões e label de saldo =====
        btn_qss = """
        QPushButton {
            background: #2b2d31;         /* fundo escuro */
            color: #eaeaea;              /* texto claro */
            border: 1px solid #3a3d42;
            border-radius: 8px;
            padding: 6px 12px;
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
        self.lbl_saldo.setStyleSheet("color: #eaeaea; font-weight: 700;")

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
        self.chart_pie = PieChartWidget([])
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
        self.charts_title.setStyleSheet("color: #eaeaea; padding: 8px;")

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
        self._recarregar()

    def set_charts_title(self, title: str):
        self.charts_title.setText(title)

    def _recarregar(self):
        # Tabela
        transacoes = self.repo.listar()
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

        # Pizza de despesas por categoria
        dados = self.repo.soma_por_categoria(TipoTransacao.DESPESA)
        pairs = [(d["categoria"], float(d["total"])) for d in dados]

        # atualiza pizza
        self.chart_pie.plot(pairs, title="")

        # atualiza barras (labels e valores)
        labels =[c for c, _ in pairs]
        values = [v for _, v in pairs]
        self.chart_bars.plot(labels, values, title="")
        
        

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
