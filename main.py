from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QFont
import sys
from app.ui.main_window import MainWindow
from app.db import Database
from app.repository import TransacaoRepository
from app.ui.start_window import StartWindow
from app.senha import Senha
from app.ui.login_dialog import LoginDialog


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
    app.setFont(QFont("Segoe UI", 10))

    # Janela de login
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        # Janela principal
        window = StartWindow(repo)
        window.showMaximized()
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__ == "__main__":
    main()