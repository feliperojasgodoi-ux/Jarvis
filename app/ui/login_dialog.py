from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

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

    def check_password(self):
        if self.password_input.text() == "Tonto2402":
            self.accept()  # Close the dialog and return success
        else:
            QMessageBox.warning(self, "Error", "Incorrect password. Please try again.")

    def get_password(self) -> str:
        return self.password_input.text()