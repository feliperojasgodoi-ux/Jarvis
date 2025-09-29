from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from app.senha import Senha

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

    def check_password(self):
        senha = Senha("Tonto2402")  # Replace with the actual password check logic
        if self.password_input.text() == senha.get_senha():
            self.accept()  # Close the dialog and return success
        else:
            QMessageBox.warning(self, "Error", "Incorrect password. Please try again.")
            self.password_input.clear()  # Clear the input field

def show_login_dialog():
    dialog = LoginDialog()
    if dialog.exec_() == QDialog.Accepted:
        return True
    return False