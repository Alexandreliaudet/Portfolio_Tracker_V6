from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "portfolio_data.json"

MARKET_GROUPS = {
    "Global Equity Indices": ["^GSPC", "^IXIC", "^DJI", "^RUT", "^FTSE", "^N225"],
    "Rates": ["^TNX", "^FVX", "^IRX"],
    "Commodities": ["GC=F", "SI=F", "CL=F", "NG=F"],
    "FX": ["EURUSD=X", "JPY=X", "GBPUSD=X", "BRL=X", "CNY=X"],
    "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
}

REPORT_TOPICS = {
    "US Broad Market": "SPY",
    "Nasdaq Growth": "QQQ",
    "Semiconductors": "SOXX",
    "Energy": "XLE",
    "Financials": "XLF",
    "Emerging Markets": "EEM",
    "Commodities": "DBC",
    "Crypto": "BTC-USD",
}

TIMEFRAME_MAP = {
    "1w": ("5d", "1h"),
    "1m": ("1mo", "1d"),
    "3m": ("3mo", "1d"),
    "6m": ("6mo", "1d"),
    "ytd": ("ytd", "1d"),
    "1y": ("1y", "1d"),
    "2y": ("2y", "1wk"),
    "5y": ("5y", "1wk"),
    "10y": ("10y", "1mo"),
    "all": ("max", "1mo"),
}

VALUATION_COLUMNS = [
    "trailingPE",
    "forwardPE",
    "priceToBook",
    "returnOnEquity",
    "grossMargins",
    "operatingMargins",
    "profitMargins",
    "dividendYield",
    "beta",
]
