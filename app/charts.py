from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class PieChartWidget(QWidget):
    def __init__(self, data_pairs, title: str = "", parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.figure.patch.set_facecolor("#121212")
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left = 0.06, right = 0.98, top = 0.90, bottom = 0.15)
        self.ax.set_facecolor("#121212")
        self.plot(data_pairs, title)

    def plot(self, data_pairs, title):
        self.ax.clear()
        self.ax.set_facecolor("#121212")

        labels = [c for c, _ in data_pairs]
        sizes = [v for _, v in data_pairs]
        if sizes:
            wedges, texts, autotexts = self.ax.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                textprops={"color": "white"},
                startangle=90,
            )
            # garantir que os labels (texts) também fiquem na cor clara
            for t in texts:
                t.set_color("#eaeaea")
            for at in autotexts:
                at.set_color("#ffffff")

        self.ax.axis("equal")
        # título com cor explícita para override do rcParams
        self.ax.set_title(title, color="#da2424", fontsize=14, fontweight="bold", pad=10)
        # opcional: esconder eixos (não remove o título)
        self.ax.set_axis_off()
        self.figure.subplots_adjust(left=0, right=1, top=0.88, bottom=0)
        self.canvas.draw()


class BarChartWidget(QWidget):
    def __init__(
        self, meses, receitas, despesas, title: str = "Receitas x Despesas", parent=None
    ):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3))
        self.figure.patch.set_facecolor("#121212")
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#121212")
        self.ax.tick_params(colors="#eaeaea")
        self.plot(meses, receitas, despesas, title)

    def plot(self, meses, receitas, despesas, title):
        # sempre usar self.ax (o mesmo eixo) para desenhar
        self.ax.clear()
        x = range(len(meses))
        self.ax.bar(x, receitas, label="Receitas")
        self.ax.bar(x, despesas, label="Despesas", alpha=0.6)
        self.ax.set_xticks(list(x))
        self.ax.set_xticklabels(meses, rotation=45, ha="right", color="#da2a2a")
        self.ax.legend()
        # título com cor aplicada diretamente eaeaea
        self.ax.set_title(title)

        self.figure.tight_layout()
        self.canvas.draw()

# app/charts.py (adicione abaixo do PieChartWidget)
class CategoryBarChartWidget(QWidget):
    def __init__(self, labels=None, values=None, title="", parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        # Dark theme
        self.figure.patch.set_facecolor("#121212")
        self.ax.set_facecolor("#121212")
        self.plot(labels or [], values or [], title)

    def plot(self, labels, values, title):
        self.ax.clear()
        self.ax.set_facecolor("#121212")

        x = range(len(labels))
        self.ax.bar(x, values)

        self.ax.set_xticks(list(x))
        self.ax.set_xticklabels(labels, rotation=45, ha="right", color="white")

        self.ax.tick_params(colors="white")
        for spine in self.ax.spines.values():
            spine.set_color("#eaeaea")

        self.ax.set_title(title, color="#eaeaea", fontweight="bold", fontsize=14, pad=10)
        self.figure.subplots_adjust(left = 0.06, right = 0.98, top = 0.90, bottom = 0.15)
        self.canvas.draw()
