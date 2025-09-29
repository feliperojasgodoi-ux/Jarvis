from PyQt5.QtWidgets import QApplication
import sys
from app.ui.main_window import MainWindow
from app.db import Database
from app.repository import TransacaoRepository
from app.ui.start_window import StartWindow


def main():
    app = QApplication(sys.argv)
    dark_style = """
    QWidget {
        background-color: #121212;
        color: #e0e0e0;
    }
    """

    # Inicializa DB e repo
    db = Database(db_path="finance.db")
    repo = TransacaoRepository(db)
    app.setStyleSheet(dark_style)

    # Janela principal
    window = StartWindow(repo)
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()