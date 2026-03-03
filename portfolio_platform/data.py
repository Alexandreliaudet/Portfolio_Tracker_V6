import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=60)
def get_info(ticker: str) -> dict:
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


@st.cache_data(ttl=90)
def get_latest_price(ticker: str):
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        if hist.empty:
            return None
        return float(hist["Close"].iloc[-1])
    except Exception:
        return None


@st.cache_data(ttl=180)
def get_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        hist = yf.Ticker(ticker).history(period=period, interval=interval)
        return hist if isinstance(hist, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_returns_data(tickers: tuple, period: str = "1y") -> pd.DataFrame:
    if not tickers:
        return pd.DataFrame()
    try:
        close = yf.download(
            tickers=list(tickers),
            period=period,
            auto_adjust=True,
            progress=False,
            group_by="column",
        )["Close"]
        if isinstance(close, pd.Series):
            close = close.to_frame(list(tickers)[0])
        returns = close.pct_change().replace([np.inf, -np.inf], np.nan).dropna(how="all")
        return returns.dropna(axis=1, how="all")
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=180)
def get_market_snapshot(symbols: tuple) -> pd.DataFrame:
    rows = []
    for s in symbols:
        try:
            hist = yf.Ticker(s).history(period="5d")
            if hist.empty:
                continue
            last = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last
            d1 = ((last / prev) - 1) * 100 if prev else 0.0
            rows.append({"Symbol": s, "Last": last, "1D %": d1})
        except Exception:
            continue
    return pd.DataFrame(rows)


@st.cache_data(ttl=240)
def get_news(symbol: str):
    try:
        return yf.Ticker(symbol).news or []
    except Exception:
        return []
