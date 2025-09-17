from PyQt5.QtWidgets import QApplication
import sys
from app.ui.main_window import MainWindow
from app.db import Database
from app.repository import TransacaoRepository




def main():
    app = QApplication(sys.argv)


    # Inicializa DB e repo
    db = Database(db_path="finance.db")
    repo = TransacaoRepository(db)


    # Janela principal
    window = MainWindow(repo)
    window.show()


    sys.exit(app.exec_())




if __name__ == "__main__":
    main()