from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox,
)
from ..security import verify_password, is_password_configured


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setFixedSize(300, 150)

        self.layout = QVBoxLayout()

        self.label = QLabel("Enter Password:")
        self.layout.addWidget(self.label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_password)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

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

    def get_password(self) -> str:
        return self.password_input.text()
