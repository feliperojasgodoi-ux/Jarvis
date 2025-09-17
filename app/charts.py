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
        self.plot(data_pairs, title)


    def plot(self, data_pairs, title):
        ax = self.figure.add_subplot(111)
        ax.clear()
        labels = [c for c, _ in data_pairs]
        sizes = [v for _, v in data_pairs]
        if sizes:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title(title)
        self.canvas.draw()




class BarChartWidget(QWidget):
    def __init__(self, meses, receitas, despesas, title: str = "Receitas x Despesas", parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.plot(meses, receitas, despesas, title)


    def plot(self, meses, receitas, despesas, title):
        ax = self.figure.add_subplot(111)
        ax.clear()
        x = range(len(meses))
        ax.bar(x, receitas, label="Receitas")
        ax.bar(x, despesas, bottom=None, label="Despesas", alpha=0.6)
        ax.set_xticks(list(x))
        ax.set_xticklabels(meses, rotation=45, ha='right')
        ax.legend()
        ax.set_title(title)
        self.canvas.draw()