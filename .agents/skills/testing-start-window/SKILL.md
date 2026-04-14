# Testing the Jarvis Start Window

## Overview
Jarvis is a PyQt5 desktop financial management app. The start window is the landing dashboard after login, containing a title, a FinanceCard with a donut chart, and placeholder tiles.

## Devin Secrets Needed
None — the login password is hardcoded in `app/ui/login_dialog.py`.

## Prerequisites
- `wmctrl` must be installed (`sudo apt-get install -y wmctrl`)
- Python dependencies: `pip install PyQt5>=5.15 matplotlib>=3.7 pandas>=2.0`
- Display server must be running (`DISPLAY=:0`)

## How to Launch
```bash
cd /home/ubuntu/repos/Jarvis
DISPLAY=:0 python main.py &
```

## How to Log In
- A login dialog appears on launch
- Password is in `app/ui/login_dialog.py` (look for the hardcoded string)
- After login, the Start Window ("Início") opens

## Key UI Elements to Verify
1. **Title**: "J.A.R.V.I.S." — large bold white text, centered
2. **FinanceCard** (center column): "Controle Financeiro" title + donut chart + "Total gasto: R$ X,XXX.XX" footer
3. **Placeholder tiles** (left and right columns): "EM DESENVOLVIMENTO" text
4. **Donut chart**: Colored wedges, center text ("R$ X.X mil"), percentage labels with leader lines

## Layout Structure
- 3-column QGridLayout with stretch ratio 1:2:1
- Title spans all 3 columns (row 0, columns 0-2)
- Cards in row 1: left tile (col 0), FinanceCard (col 1), right tile (col 2)
- Minimum window size: 800×600

## Resizing for Responsiveness Testing
The window title contains an accent character ("Início"). Use wmctrl carefully:
```bash
# List windows to find the exact title
wmctrl -l

# Maximize
wmctrl -r "Início" -b add,maximized_vert,maximized_horz

# Resize to 800×600
wmctrl -r "Início" -b remove,maximized_vert,maximized_horz
sleep 0.5
wmctrl -r "Início" -e 0,100,100,800,600
```

## Common Issues
- **wmctrl title mismatch**: The window title has an accent ("Início" not "Inicio"). Always use `wmctrl -l` first to get the exact title.
- **Pre-existing CI failures**: The repo has flake8 lint errors across the entire codebase on `main`. These are not introduced by PRs — check if errors are in files you changed before investigating.
- **Database data**: Transaction data in `finance.db` may be in a specific month (e.g., September 2025). The FinanceCard loads data for the current month by default. If the donut appears empty, the data might be from a different period.
- **Donut percentage labels**: Controlled by `show_percent` parameter in `start_window.py` FinanceCard.refresh(). The `if show_percent:` guard in `charts.py` controls whether annotations are drawn.
- **Title clipping**: The title uses a 56pt bold font. At very narrow widths (<800px) it may still clip. The fix (spanning all 3 columns) ensures it fits within the 800px minimum.
