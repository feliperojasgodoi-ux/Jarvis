from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class PieChartWidget(QWidget):
    def __init__(self, data_pairs, title: str = "Gastos por Categoria", parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.figure.patch.set_facecolor("#121212")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#121212")
        self.plot(data_pairs, title)

    def plot(self, data_pairs, title):
        self.ax.clear()
        self.ax.set_facecolor("#121212")

        labels = [c for c, _ in data_pairs]
        sizes = [v for _, v in data_pairs]
        if sizes:
            self.ax.pie(sizes, labels=labels, autopct="%1.1f%%", textprops={"color": "white"}, startangle = 90)


        self.ax.axis('equal')
        self.ax.set_axis_off()    
        self.ax.set_title(title)
        self.figure.subplots_adjust(left=0, right=1, top=0.9, bottom=0)
        self.canvas.draw()


class BarChartWidget(QWidget):
    def __init__(
        self, meses, receitas, despesas, title: str = "Receitas x Despesas", parent=None
    ):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.plot(meses, receitas, despesas, title)

    def plot(self, meses, receitas, despesas, title):
        ax = self.figure.add_subplot(111)
        ax.clear()
        x = range(len(meses))
        self.ax.bar(x, receitas, label="Receitas")
        self.ax.bar(x, despesas, label="Despesas", alpha=0.6)
        self.ax.set_xticks(list(x))
        self.ax.set_xticklabels(meses, rotation=45, ha="right")
        self.ax.legend()
        self.ax.set_title(title)

        self.figue.tight_layout()
        self.canvas.draw()
