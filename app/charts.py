import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QFont
import numpy as np

# Preferir a fonte do Qt (no Windows costuma ser Segoe UI). Se não der, usa DejaVu Sans.
try:
    qt_font = QFont()
    mpl.rcParams["font.family"] = qt_font.family()
except Exception:
    mpl.rcParams["font.family"] = "DejaVu Sans"

# Ajustes globais de tamanho/peso para ficar consistente no tema escuro
mpl.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})

def _fmt_brl_compacto(v: float) -> str:
    # R$ 8,3 mil | R$ 1,2 mi | R$ 3,4 bi ...
    abs_v = abs(v)
    if abs_v >= 1_000_000_000:
        return f"R$ {v/1_000_000_000:.1f} bi"
    if abs_v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f} mi"
    if abs_v >= 1_000:
        return f"R$ {v/1_000:.1f} mil"
    return f"R$ {v:,.0f}".replace(",", ".")  # 1.234

class DonutChartWidget(QWidget):
    def __init__(self, data_pairs=None, title="Gastos por Categoria", parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self); layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.figure.patch.set_facecolor("#121212")
        self.ax.set_facecolor("#121212")
        
        self._center_text = None
        self._resize_cid = None
        
        self.plot(data_pairs or [], title)

        # >>> novo: calcula fontsize proporcional ao tamanho do eixo
    def _fit_center_text(self, min_px=12, max_px=40, k=0.12):
        if not self._center_text:
            return
        # tamanho do eixo em pixels
        fig_w, fig_h = (self.figure.get_size_inches() * self.figure.dpi)
        l, b, w, h = self.ax.get_position().bounds  # fração da figura
        ax_w, ax_h = w * fig_w, h * fig_h
        target = k * min(ax_w, ax_h)                # proporcional ao menor lado
        fs = max(min_px, min(max_px, target))
        self._center_text.set_fontsize(fs)
        self.canvas.draw_idle()

    def plot(self, data_pairs, title, colors=None, show_legend=True, min_pct = 3.0):
        self.ax.clear()
        self.ax.set_facecolor("#121212")

        labels = [c for c, _ in data_pairs]
        sizes  = [float(v) for _, v in data_pairs]
        total  = sum(sizes)
        
        if sizes:
            # fonte específica para o texto central
            center_fp = FontProperties(family=mpl.rcParams["font.family"], weight="bold")
             # DONUT: rosca com "width"
            wedges, _ = self.ax.pie(
                sizes,                            # rótulos fora
                startangle=90,
                colors=colors,
                wedgeprops=dict(width=0.4, edgecolor="#121212"),
                   
            )

            # Texto central: total + subtítulo
            self.ax.text(
                0, 0,
                f"{_fmt_brl_compacto(total)}",
                ha="center", va="center",
                color="#ffffff", fontproperties=center_fp, fontsize = 18
            )
            self.ax.text(
                0, -0.12, 
                "Total Gasto",
                ha="center", va="center",
                color="#e0e0e0",fontproperties=center_fp, fontsize=8
            )
            for i, w in enumerate(wedges):
                pct = 100.0 * sizes[i] / total if total else 0.0
                if pct < min_pct:
                    continue  # pula as menores

                # ângulo médio da fatia
                ang = (w.theta2 + w.theta1) / 2.0
                ang_rad = np.deg2rad(ang)
                x, y = np.cos(ang_rad), np.sin(ang_rad)

                # ponto na borda externa da rosca
                r_outer = 1.0   # raio externo do pie
                xy = (r_outer * x, r_outer * y)

                # posição do texto (um pouco para fora)
                OFFSET = 1.20
                xytext = (OFFSET * np.sign(x), OFFSET * y)

                # alinhamento do texto: esquerda/direita conforme lado
                ha = "left" if x >= 0 else "right"

                self.ax.annotate(
                    f"{pct:.1f}%",
                    xy=xy, xycoords="data",
                    xytext=xytext, textcoords="data",
                    ha=ha, va="center",
                    color="#e0e0e0", fontsize=11,
                    arrowprops=dict(
                        arrowstyle="-",
                        color="#5f5e5e",
                        lw=1.0,
                        shrinkA=0, shrinkB=0,
                          # curva leve
                    ),
                )

        self.ax.axis("equal")
        self.ax.set_title(title, color="#eaeaea", fontweight="bold", fontsize=16, pad=10)

        # Legenda opcional (linhas, mesma ordem das fatias)
        if show_legend and labels:
            self.ax.legend(
                loc="upper center", bbox_to_anchor=(0.5, -0.08),
                ncol=min(5, len(labels)), frameon=False,
                labels=labels
            )
            # legenda clara no dark
            for t in self.ax.get_legend().get_texts():
                t.set_color("#eaeaea")

        # margens iguais às do gráfico de barras para alinhamento
        self.figure.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.20)
        self.canvas.draw()

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

    def plot(self, data_pairs, title, colors=None, show_labels=True):
        self.ax.clear()
        self.ax.set_facecolor("#121212")

        labels = [c for c, _ in data_pairs]
        sizes = [v for _, v in data_pairs]
        if sizes:
            wedges, texts, autotexts = self.ax.pie(
                sizes,
                labels=(labels if show_labels else[]),
                autopct="%1.1f%%",
                textprops={"color": "white"},
                startangle=90,
                colors=colors
            )
            # garantir que os labels (texts) também fiquem na cor clara
            for t in texts:
                t.set_color("#eaeaea")
            for at in autotexts:
                at.set_color("#ffffff")

        self.ax.axis("equal")
        # título com cor explícita para override do rcParams
        self.ax.set_title(title, color="#eaeaea", fontsize=14, fontweight="bold", pad=10)
        # opcional: esconder eixos (não remove o título)
        self.ax.set_axis_off()
        self.figure.subplots_adjust(left=0.06, right=0.98, top=0.90, bottom=0.15)
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

    def plot(self, labels, values, title, colors = None):
        self.ax.clear()
        self.ax.set_facecolor("#121212")

        x = range(len(labels))
        self.ax.bar(list(x), values, color=colors)

        self.ax.set_xticks(list(x))
        self.ax.set_xticklabels(labels, rotation=45, ha="right", color="white")

        self.ax.tick_params(colors="white")
        for spine in self.ax.spines.values():
            spine.set_color("#eaeaea")

        self.ax.set_title(title, color="#eaeaea", fontweight="bold", fontsize=14, pad=10)
        self.figure.subplots_adjust(left = 0.06, right = 0.98, top = 0.90, bottom = 0.15)
        self.canvas.draw()
