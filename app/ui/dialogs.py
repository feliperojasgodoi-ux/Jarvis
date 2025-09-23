from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
    QDateEdit,
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator
from datetime import date
from ..models import Transacao, TipoTransacao


class TransacaoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Transação")
        layout = QFormLayout(self)

        # Campos
        self.tipo = QComboBox()
        self.tipo.addItems([t.value for t in TipoTransacao])

        self.categoria = QLineEdit()
        self.categoria.setPlaceholderText("Ex.: Alimentação")

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Ex.: Almoço no trabalho")

        self.banco = QLineEdit()
        self.banco.setPlaceholderText("Ex.: Banco do Brasil")

        self.valor = QLineEdit()
        self.valor.setPlaceholderText("Ex.: 45.90")
        # Validador numérico simples (2 casas)
        validator = QDoubleValidator(0.0, 10**9, 2, self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.valor.setValidator(validator)

        self.data = QDateEdit(QDate.currentDate())
        self.data.setCalendarPopup(True)

        layout.addRow("Tipo:", self.tipo)
        layout.addRow("Categoria:", self.categoria)
        layout.addRow("Descrição:", self.descricao)
        layout.addRow("Banco:", self.banco)
        layout.addRow("Valor:", self.valor)
        layout.addRow("Data:", self.data)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # >>> ESTE MÉTODO PRECISA ESTAR DENTRO DA CLASSE <<<
    def get_transacao(self) -> Transacao:
        if not self.categoria.text().strip():
            raise ValueError("Categoria vazia.")
        if not self.descricao.text().strip():
            raise ValueError("Descrição vazia.")
        if not self.valor.text().strip():
            raise ValueError("Valor vazio.")

        # aceita vírgula ou ponto
        valor = float(self.valor.text().replace(",", "."))

        d = self.data.date()
        return Transacao(
            id=None,
            tipo=TipoTransacao(self.tipo.currentText()),
            categoria=self.categoria.text().strip(),
            descricao=self.descricao.text().strip(),
            valor=valor,
            data=date(d.year(), d.month(), d.day()),
            banco=self.banco.text().strip(),
        )
