# start_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QGridLayout, QSizePolicy,
    QLabel, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont

from ..repository import TransacaoRepository
from .main_window import MainWindow
from ..charts import DonutChartWidget
from ..models import TipoTransacao


TILE_QSS = """
QPushButton {
    background: #1e1f22;
    color: #eaeaea;
    border-radius: 18px;
    padding: 12px;
    border: 2px solid #2b2d31;
    text-align: center;
}
QPushButton:hover { border-color: #3a86ff; }
QPushButton:pressed { background: #2b2d31; }
"""

TITLE_QSS = """
QLabel {
    background: transparent;
    color: #eaeaea;
    padding: 12px;
}
"""


class StartWindow(QMainWindow):
    def __init__(self, repo: TransacaoRepository):
        super().__init__()
        self.repo = repo
        self._fin_win = None  # manter referência da janela financeira

        self.setWindowTitle("Início")
        self.showMaximized()

        root = QWidget()
        self.setCentralWidget(root)

        grid = QGridLayout(root)
        grid.setSpacing(16)
        grid.setContentsMargins(16, 16, 16, 16)

        # layout: dá mais respiro ao título
        grid.setRowStretch(0, 2)
        grid.setRowStretch(1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)

        # --- Título JARVIS (apenas visual) ---
        title = QLabel("J.A.R.V.I.S.")
        f = QFont(); f.setPointSize(56); f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(TITLE_QSS)
        title.setMinimumSize(QSize(400, 260))

        # helper para cards placeholder
        def make_tile(text: str) -> QPushButton:
            btn = QPushButton(text)
            btn.setMinimumSize(QSize(120, 70))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setStyleSheet(TILE_QSS)
            bf = QFont(); bf.setPointSize(14); bf.setBold(True)
            btn.setFont(bf)
            return btn

        # --- Cards ---
        self.card_fin = FinanceCard(self.repo)              # card com donut
        self.btn_dev1 = make_tile("EM\nDESENVOLVIMENTO")
        self.btn_dev2 = make_tile("EM\nDESENVOLVIMENTO")

        grid.addWidget(title,         0, 1)
        grid.addWidget(self.card_fin, 1, 1)
        grid.addWidget(self.btn_dev1, 1, 0)
        grid.addWidget(self.btn_dev2, 1, 2)

        # ações
        self.card_fin.clicked.connect(self._abrir_financas)
        self.btn_dev1.clicked.connect(self._placeholder)
        self.btn_dev2.clicked.connect(self._placeholder)

    def showEvent(self, ev):
        super().showEvent(ev)
        # atualiza o donut quando a Start aparece
        if hasattr(self, "card_fin") and self.card_fin is not None:
            self.card_fin.refresh()

    def _abrir_financas(self):
        if self._fin_win is None:
            self._fin_win = MainWindow(self.repo)
        self._fin_win.showMaximized()
        self._fin_win.raise_()
        self._fin_win.activateWindow()

    def _placeholder(self):
        QMessageBox.information(self, "Em desenvolvimento",
                                "Módulo ainda em desenvolvimento.")


class FinanceCard(QWidget):
    """Card com título + donut e rodapé. Clicável para abrir o módulo financeiro."""
    clicked = pyqtSignal()

    def __init__(self, repo: TransacaoRepository, parent=None):
        super().__init__(parent)
        self.repo = repo

        # visual do card
        self.setObjectName("FinanceCard")
        self.setStyleSheet("""
        QWidget#FinanceCard {
            background: #1e1f22;
            border: 1px solid #2b2d31;
            border-radius: 18px;
        }
        QWidget#FinanceCard:hover { background: #1b1c1f; }
        """)

        # título
        self.title = QLabel("Controle Financeiro")
        tf = QFont(); tf.setPointSize(16); tf.setBold(True)
        self.title.setFont(tf)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color:#eaeaea; padding: 8px 0;")

        # donut compacto (sem legenda para caber no card)
        self.donut = DonutChartWidget([], title="")
        self.donut.setMinimumHeight(220)

        # rodapé
        self.footer = QLabel("")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color:#bdbdbd; padding-bottom: 8px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)
        lay.addWidget(self.title)
        lay.addWidget(self.donut, 1)
        lay.addWidget(self.footer)

    # tornar o card clicável
    def mousePressEvent(self, ev):
        self.clicked.emit()
        super().mousePressEvent(ev)

    # atualizar dados do donut (todos os tempos; você pode trocar para mês atual)
    def refresh(self):
        dados = self.repo.soma_por_categoria(TipoTransacao.DESPESA)
        pairs = [(d["categoria"], float(d["total"])) for d in dados]
        total = sum(v for _, v in pairs)

        # sem cores fixas aqui (o card é compacto); se quiser, injete seu mapa de cores
        self.donut.plot(pairs, title="", colors=None, show_legend=False)
        self.footer.setText(f"Total gasto: R$ {total:,.2f}")
