# Testing Jarvis PyQt5 UI

This skill covers how to set up and test the Jarvis desktop application, a PyQt5-based personal finance manager.

## Prerequisites

- Python 3.12+
- X11 display (DISPLAY=:0 on VM)
- `wmctrl` for window management during testing

## Setup

```bash
pip install PyQt5>=5.15 matplotlib>=3.7 pandas>=2.0
sudo apt-get install -y wmctrl
```

## Running the App

```bash
cd /home/ubuntu/repos/Jarvis
DISPLAY=:0 python main.py &
```

The app launches a login dialog first. After successful login, the Start Window appears maximized.

## Login

The login dialog requires a password. The password is hardcoded in `app/ui/login_dialog.py`. Check the `check_password` method for the current value.

## Devin Secrets Needed

No external secrets required. The app uses a local SQLite database (`finance.db`) and has a hardcoded login.

## App Architecture

- **Entry point**: `main.py` — creates QApplication, applies dark theme, shows login then StartWindow
- **Start Window** (`app/ui/start_window.py`): Grid layout with title + 3 cards (FinanceCard + 2 placeholder tiles)
- **FinanceCard**: Custom QWidget with donut chart showing expense breakdown, clickable to open MainWindow
- **Main Window** (`app/ui/main_window.py`): Financial transaction manager with table, filters, and charts
- **Charts** (`app/charts.py`): DonutChartWidget, PieChartWidget, CategoryBarChartWidget using matplotlib
- **Database**: SQLite `finance.db` with `transacoes` table

## Testing the Start Window

1. Launch the app with `DISPLAY=:0 python main.py &`
2. Enter the password in the login dialog
3. The Start Window should appear maximized with:
   - "J.A.R.V.I.S." title (centered, large bold font) in the top area
   - Three cards in the bottom row: left/right "EM DESENVOLVIMENTO" placeholders, center FinanceCard with donut
   - The donut chart should show expense data from the database with center text showing total in compact BRL format
   - Footer showing "Total gasto: R$ X,XXX.XX"
4. Use `wmctrl` to resize: `DISPLAY=:0 wmctrl -r "Início" -e 0,x,y,width,height`
5. Use `DISPLAY=:0 wmctrl -r "Início" -b add,maximized_vert,maximized_horz` to maximize

## Window Management Tips

- The window title is "Início" (with accent) — use this for wmctrl commands
- List windows: `DISPLAY=:0 wmctrl -l`
- Remove maximize: `DISPLAY=:0 wmctrl -r "Início" -b remove,maximized_vert,maximized_horz`

## Known Issues to Watch For

- The `show_percent` parameter in `DonutChartWidget.plot()` might not be properly respected — check `charts.py` lines 125-146 for whether there's a guard on the `show_percent` flag
- The minimum window size (800×600) might be too small for the combined minimum heights of the title label and donut chart — test responsiveness at smaller sizes
- The title label has a large `minimumSize` that may cause clipping at smaller window sizes
