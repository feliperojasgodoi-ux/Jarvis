from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QGridLayout, QSizePolicy, QLabel
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from ..repository import TransacaoRepository
from .main_window import MainWindow


TILE_QSS = """
QPushButton {
    background: #1e1f22;           /* fundo do card */
    color: #eaeaea;                 /* texto */
    border-radius: 18px;
    padding: 12px;
    border: 2px solid #2b2d31;
    text-align: center;
}
QPushButton:hover {
    border-color: #3a86ff;          /* destaque no hover */
}
QPushButton:pressed {
    background: #2b2d31;
}
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
        self.setWindowTitle("Início")
        self.resize(900, 600)

        root = QWidget(); self.setCentralWidget(root)
        grid = QGridLayout(root)
        grid.setSpacing(16)
        grid.setContentsMargins(16,16,16,16)

        # ---- Título "JARVIS" (não-clicável) ----
        title = QLabel("J.A.R.V.I.S.")
        f = QFont()
        f.setPointSize(36)
        f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(TITLE_QSS)
        title.setMinimumSize(QSize(300, 180))

        # helper para criar cards grandes
        def make_tile(text: str) -> QPushButton:
            btn = QPushButton(text)
            btn.setMinimumSize(QSize(300, 180))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setStyleSheet(TILE_QSS)
            f = QFont()
            f.setPointSize(18)
            f.setBold(True)
            btn.setFont(f)
            return btn

        # cards 
        self.btn_financas = make_tile("CONTROLE\nFINANCEIRO")
        self.btn_dev1 = make_tile("EM\nDESENVOLVIMENTO")
        self.btn_dev2 = make_tile("EM\nDESENVOLVIMENTO")

        grid.addWidget(title,             0, 0)
        grid.addWidget(self.btn_financas, 0, 1)
        grid.addWidget(self.btn_dev1,     1, 0)
        grid.addWidget(self.btn_dev2,     1, 1)

        # ações
        self.btn_financas.clicked.connect(self._abrir_financas)
        self.btn_dev1.clicked.connect(self._placeholder)
        self.btn_dev2.clicked.connect(self._placeholder)

        self._fin_win = None  # manter referência

    def _abrir_financas(self):
        if self._fin_win is None:
            self._fin_win = MainWindow(self.repo)
        self._fin_win.show()
        self._fin_win.raise_()
        self._fin_win.activateWindow()

    def _placeholder(self):
        # no futuro, substitua pelo módulo real
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Em desenvolvimento",
                                "Módulo ainda em desenvolvimento.")
