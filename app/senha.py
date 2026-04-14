from PyQt5.QtWidgets import (
    QLineEdit, QDialog, QVBoxLayout, QPushButton, QLabel,
)
from app.security import verify_password, is_password_configured


class Senha(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Protection")
        self.setFixedSize(300, 150)

        self.layout = QVBoxLayout()

        self.label = QLabel("Enter Password:")
        self.layout.addWidget(self.label)

        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.senha_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_password)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

        if not is_password_configured():
            self.label.setText(
                "JARVIS_PASSWORD_HASH not set. See README."
            )

    def check_password(self):
        if verify_password(self.senha_input.text()):
            self.accept()
        else:
            self.label.setText("Incorrect Password. Try Again.")

    def get_senha(self) -> str:
        return self.senha_input.text()
