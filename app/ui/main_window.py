from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLabel,
)
from PyQt5.QtCore import Qt
from ..repository import TransacaoRepository
from ..models import TipoTransacao
from .dialogs import TransacaoDialog
from ..charts import PieChartWidget, BarChartWidget


class MainWindow(QMainWindow):
    def __init__(self, repo: TransacaoRepository):
        super().__init__()
        self.repo = repo
        self.setWindowTitle("Gerenciador Financeiro")
        self.resize(900, 600)

        # Root widget
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        upper_style = """
        QPushButton {
            background: #1e1f22;
            color: #eaeaea;
            border-radius: 6px;
            padding: 6px 12px;
            border: 2px solid #2b2d31;
            }
        QLabel {
                color:
       """       # Toolbar
        tb = QHBoxLayout()
        self.btn_add = QPushButton("Adicionar")
        self.btn_del = QPushButton("Remover Selecionada")
        self.lbl_saldo = QLabel("Saldo: R$ 0,00")
        self.lbl_saldo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        tb.addWidget(self.btn_add)
        tb.addWidget(self.btn_del)
        tb.addStretch()
        tb.addWidget(self.lbl_saldo)
        layout.addLayout(tb)

        # Tabela
        dark_style = """
        QTableWidget {
            background-color: #1e1f22;
            color: #eaeaea;
            gridline-color: #2b2d31;
            text-align: center;
        }
        QHeaderView::section {
            background-color: #2b2d31;
            color: #eaeaea;
            padding: 4px;
            border: 1px solid #3a3c41;
            font-weith: bold;
        }
        """
        self.table = QTableWidget(0, 5)
        self.table.setStyleSheet(dark_style)
        self.table.setHorizontalHeaderLabels(
            [ "Data","Tipo", "Categoria", "Valor (R$)", "Descrição"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        layout.addWidget(self.table)

        # Área de gráficos
        self.chart_pie = PieChartWidget([])
        layout.addWidget(self.chart_pie)

        # Sinais
        self.btn_add.clicked.connect(self._adicionar)
        self.btn_del.clicked.connect(self._remover)

        # Inicializa
        self._recarregar()

    def _recarregar(self):
        # Tabela
        transacoes = self.repo.listar()
        self.table.setRowCount(0)
        total = 0.0

        for t in transacoes:
            r = self.table.rowCount()
            self.table.insertRow(r)
            item_data = QTableWidgetItem(t.data.strftime("%d/%m/%Y"))
            item_data.setData(Qt.UserRole, t.id)  # <— ID guardado aqui
            self.table.setItem(r, 0, item_data)
            self.table.setItem(r, 1, QTableWidgetItem(t.tipo.value))
            self.table.setItem(r, 2, QTableWidgetItem(t.categoria))
            self.table.setItem(r, 3, QTableWidgetItem(f"{t.valor:,.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(t.descricao))
            total += t.valor if t.tipo == TipoTransacao.RECEITA else -t.valor
            

        self.lbl_saldo.setText(f"Saldo: R$ {total:,.2f}")

        # Pizza de despesas por categoria
        dados = self.repo.soma_por_categoria(TipoTransacao.DESPESA)
        pairs = [(d["categoria"], float(d["total"])) for d in dados]
        self.chart_pie.plot(pairs, title="Gastos por Categoria")

    def _adicionar(self):
        dlg = TransacaoDialog(self)
        if dlg.exec_():
            try:
                t = dlg.get_transacao()
                self.repo.adicionar(t)
                self._recarregar()
                self._recarregar()
            except ValueError:
                QMessageBox.warning(
                    self, "Entrada Inválida", "Verifique os dados informados."
                )

    def _remover(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()})
        if not rows:
            QMessageBox.information(
                self,
                "Nenhuma Seleção",
                "Selecione ao menos uma transação para remover.",
            )
            return

        transacao_id = int(self.table.item(rows[0], 0).data(Qt.UserRole))
        self.repo.remover(transacao_id)
        self._recarregar()
