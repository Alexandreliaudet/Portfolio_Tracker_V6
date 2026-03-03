import json

import numpy as np
import pandas as pd

from .config import VALUATION_COLUMNS
from .data import get_info, get_latest_price


def load_portfolio(path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text()).get("portfolio", {})
    except Exception:
        return {}


def save_portfolio(path, portfolio: dict) -> None:
    path.write_text(json.dumps({"portfolio": portfolio}, indent=4))


def build_holdings_df(portfolio: dict) -> pd.DataFrame:
    rows = []
    for ticker, pos in portfolio.items():
        shares = float(pos.get("shares", 0))
        avg_cost = float(pos.get("avg_cost", 0))
        if shares <= 0 or avg_cost <= 0:
            continue

        price = get_latest_price(ticker)
        if price is None:
            continue

        info = get_info(ticker)
        value = shares * price
        cost = shares * avg_cost
        pnl = value - cost
        ret = ((price / avg_cost) - 1) * 100 if avg_cost > 0 else 0.0

        row = {
            "Ticker": ticker,
            "Name": info.get("longName") or info.get("shortName") or ticker,
            "Sector": info.get("sector", "Unknown"),
            "Industry": info.get("industry", "Unknown"),
            "Country": info.get("country", "Unknown"),
            "Currency": pos.get("currency") or info.get("currency", "N/A"),
            "Shares": shares,
            "Avg Cost": avg_cost,
            "Price": price,
            "Cost": cost,
            "Value": value,
            "Unrealized P/L": pnl,
            "Return %": ret,
            "Market Cap": info.get("marketCap", np.nan),
        }

        for c in VALUATION_COLUMNS:
            row[c] = info.get(c, np.nan)

        rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    total_value = df["Value"].sum()
    df["Weight %"] = (df["Value"] / total_value * 100).round(3) if total_value > 0 else 0
    return df.sort_values("Value", ascending=False).reset_index(drop=True)
