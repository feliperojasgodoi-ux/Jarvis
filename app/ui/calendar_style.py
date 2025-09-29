from PyQt5.QtCore import Qt, QLocale, QDate
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtWidgets import QCalendarWidget, QToolButton
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QPainter, QPen, QColor


def beautify_calendar(cal: QCalendarWidget):
    """Aplica tema dark elegante ao QCalendarWidget."""
    # QSS
    cal.setStyleSheet("""
    QCalendarWidget {
        background: #1e1f22;
        color: #eaeaea;
        border: 1px solid #2b2d31;
        border-radius: 12px;
    }
    /* barra de navegação (mês/ano + botões) */
    QCalendarWidget QWidget#qt_calendar_navigationbar {
        background: #1e1f22;
        border-bottom: 1px solid #2b2d31;
    }
    QCalendarWidget QToolButton {
        background: #2b2d31;
        color: #eaeaea;
        border: 1px solid #3a3d42;
        border-radius: 8px;
        padding: 4px 10px;
        font-weight: 600;
    }
    QCalendarWidget QToolButton:hover { border-color: #3a86ff; }
    QCalendarWidget QToolButton:pressed { background: #1e1f22; }

    /* botões prev/next */
    QCalendarWidget QToolButton#qt_calendar_prevmonth,
    QCalendarWidget QToolButton#qt_calendar_nextmonth {
        width: 28px; height: 28px; padding: 0; margin: 4px;
    }

    /* tabela de dias */
    QCalendarWidget QTableView {
        outline: 0;
        border: none;
        background: #1e1f22;
        gridline-color: #2b2d31;
    }
    QCalendarWidget QTableView::item {
        padding: 6px;
        border-radius: 8px;
    }
    QCalendarWidget QTableView::item:hover {
        background: rgba(255,255,255,0.06);
    }
    QCalendarWidget QTableView::item:selected {
        background: #2a2d33;
        color: #ffffff;
        border: 1px solid #3a86ff;
    }

    /* cabeçalho dos dias (dom, seg, ...) */
    QCalendarWidget QTableView QHeaderView::section {
        background: #2b2d31;
        color: #eaeaea;
        border: none;
        padding: 6px 0;
        font-weight: 700;
        text-transform: lowercase;       /* "dom, seg..." */
    }
    """)

    # Locale e layout
    cal.setLocale(QLocale(QLocale.Portuguese, QLocale.Brazil))
    cal.setFirstDayOfWeek(Qt.Monday)
    cal.setGridVisible(False)

    # Formatos de texto
    base = QTextCharFormat(); base.setForeground(Qt.white)
    for wd in (Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday, Qt.Friday):
        cal.setWeekdayTextFormat(wd, base)

    we = QTextCharFormat(); we.setForeground(Qt.red)  # finais de semana
    cal.setWeekdayTextFormat(Qt.Saturday, we)
    cal.setWeekdayTextFormat(Qt.Sunday, we)

    # “Hoje” em negrito (o anel bonito vem no delegate opcional abaixo)
    today_fmt = QTextCharFormat(); today_fmt.setFontWeight(QFont.Bold)
    cal.setDateTextFormat(QDate.currentDate(), today_fmt)

    # Deixa os botões prev/next com setas
    prev_btn = cal.findChild(QToolButton, "qt_calendar_prevmonth")
    next_btn = cal.findChild(QToolButton, "qt_calendar_nextmonth")
    if prev_btn and next_btn:
        prev_btn.setText("❮"); next_btn.setText("❯")
        prev_btn.setIconSize(prev_btn.size()); next_btn.setIconSize(next_btn.size())

class TodayRingDelegate(QStyledItemDelegate):
    """Desenha um anel discreto na célula de 'hoje'."""
    def paint(self, painter: QPainter, option, index):
        super().paint(painter, option, index)  # pinta padrão do Qt
        # data desta célula
        model = index.model()
        date = model.index(index.row(), index.column()).data(Qt.UserRole)
        # o QCalendarWidget não fornece direto; usamos o texto + mês visível
        text = index.data()
        if not text or not text.isdigit():
            return
        # heurística: “hoje” = número do dia e mês do calendário
        cal = index.model().parent()  # QTableView -> QCalendarWidget
        if hasattr(cal, "parentWidget"):
            cw = cal.parentWidget()
        # com segurança:
        current = QDate.currentDate()
        nav = cal.parent().parent() if hasattr(cal, "parent") else None

        # se a célula é o dia de hoje (mês/ano visíveis)
        monthShown = cal.monthShown() if hasattr(cal, "monthShown") else current.month()
        yearShown  = cal.yearShown()  if hasattr(cal, "yearShown")  else current.year()
        if int(text) == current.day() and monthShown == current.month() and yearShown == current.year():
            r = option.rect.adjusted(4, 4, -4, -4)
            painter.save()
            pen = QPen(QColor("#eaeaea"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(r, 8, 8)
            painter.restore()
