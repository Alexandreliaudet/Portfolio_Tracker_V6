# Portfolio Dashboard - Quick Start (Friend Setup)

## What you need
- Python 3.10+ installed
- Internet connection (first run only, to install packages)

## Files required
- `dashboard.py`
- `requirements-dashboard.txt`
- `portfolio_data.json`
- `run_dashboard.sh`

## Mac / Linux (fastest)
Open Terminal in this folder and run:

```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

This script will:
1. Create a local virtual environment (`.venv`) if missing
2. Install all required packages
3. Launch the dashboard

## Windows (PowerShell)
In the project folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dashboard.txt
python -m streamlit run dashboard.py
```

## Troubleshooting
- If you see "streamlit: command not found", use:
  - `python -m streamlit run dashboard.py`
- If package install fails, check internet and Python version.
- If the page does not open automatically, go to:
  - `http://localhost:8501`
