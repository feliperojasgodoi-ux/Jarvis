from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox,
)
from app.security import verify_password, is_password_configured


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Enter Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_password)

        layout.addWidget(self.label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        if not is_password_configured():
            QMessageBox.critical(
                self,
                "Configuration Error",
                "JARVIS_PASSWORD_HASH is not set.\n\n"
                "Generate a hash with:\n"
                '  python -c "from app.security import hash_password; '
                "print(hash_password('YOUR_PASSWORD'))\"  \n\n"
                "Then export JARVIS_PASSWORD_HASH=<hash> before starting.",
            )

    def check_password(self):
        if verify_password(self.password_input.text()):
            self.accept()
        else:
            QMessageBox.warning(
                self, "Error",
                "Incorrect password. Please try again.",
            )
            self.password_input.clear()


def show_login_dialog():
    dialog = LoginDialog()
    if dialog.exec_() == QDialog.Accepted:
        return True
    return False
