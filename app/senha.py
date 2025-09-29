from PyQt5.QtWidgets import QApplication, QLineEdit, QDialog, QVBoxLayout, QPushButton, QLabel

class Senha(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def check_password(self):
        predefined_password = "Tonto2402"
        if self.senha_input.text() == predefined_password:
            self.accept()  # Close the dialog and return success
        else:
            self.label.setText("Incorrect Password. Try Again.")

    def get_senha(self) -> str:
        return self.senha_input.text()