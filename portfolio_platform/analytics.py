import numpy as np
import pandas as pd

from .data import get_returns_data


def weighted_average(series: pd.Series, weights: pd.Series):
    valid = series.notna() & np.isfinite(series)
    if not valid.any():
        return np.nan
    s = series[valid].astype(float)
    w = weights[valid].astype(float)
    if w.sum() == 0:
        return np.nan
    return float(np.average(s, weights=w))


def valuation_summary(holdings: pd.DataFrame) -> dict:
    w = holdings["Value"] / holdings["Value"].sum()
    return {
        "Weighted Trailing P/E": weighted_average(holdings["trailingPE"], w),
        "Weighted Forward P/E": weighted_average(holdings["forwardPE"], w),
        "Weighted P/B": weighted_average(holdings["priceToBook"], w),
        "Weighted ROE %": weighted_average(holdings["returnOnEquity"] * 100, w),
        "Weighted Gross Margin %": weighted_average(holdings["grossMargins"] * 100, w),
        "Weighted Op Margin %": weighted_average(holdings["operatingMargins"] * 100, w),
        "Weighted Profit Margin %": weighted_average(holdings["profitMargins"] * 100, w),
        "Weighted Dividend Yield %": weighted_average(holdings["dividendYield"] * 100, w),
        "Weighted Beta (Ticker-level)": weighted_average(holdings["beta"], w),
    }


def concentration_metrics(holdings: pd.DataFrame) -> dict:
    w = holdings["Weight %"] / 100
    hhi = float((w.pow(2)).sum())
    effective_n = float(1 / hhi) if hhi > 0 else np.nan
    return {
        "Top 1 %": float(holdings["Weight %"].head(1).sum()),
        "Top 3 %": float(holdings["Weight %"].head(3).sum()),
        "Top 5 %": float(holdings["Weight %"].head(5).sum()),
        "HHI": hhi,
        "Effective N": effective_n,
    }


def portfolio_return_series(holdings: pd.DataFrame, lookback: str) -> pd.Series:
    returns_df = get_returns_data(tuple(holdings["Ticker"].tolist()), period=lookback)
    if returns_df.empty:
        return pd.Series(dtype=float)

    weights = holdings.set_index("Ticker")["Value"] / holdings["Value"].sum()
    cols = [c for c in returns_df.columns if c in weights.index]
    if not cols:
        return pd.Series(dtype=float)

    weighted = returns_df[cols].mul(weights[cols], axis=1).sum(axis=1)
    return weighted.dropna()


def compute_risk_metrics(port: pd.Series, bench: pd.Series, rf: float) -> dict | None:
    if port.empty:
        return None

    ann_factor = 252
    ann_ret = port.mean() * ann_factor
    ann_vol = port.std() * np.sqrt(ann_factor)

    downside = port[port < 0]
    downside_vol = downside.std() * np.sqrt(ann_factor) if not downside.empty else np.nan

    sharpe = (ann_ret - rf) / ann_vol if ann_vol > 0 else np.nan
    sortino = (ann_ret - rf) / downside_vol if pd.notna(downside_vol) and downside_vol > 0 else np.nan

    eq = (1 + port).cumprod()
    cum_ret = float(eq.iloc[-1] - 1) if not eq.empty else np.nan
    dd = eq / eq.cummax() - 1
    max_dd = float(dd.min()) if not dd.empty else np.nan
    calmar = ann_ret / abs(max_dd) if pd.notna(max_dd) and max_dd < 0 else np.nan

    var95 = float(port.quantile(0.05))
    var99 = float(port.quantile(0.01))
    cvar95 = float(port[port <= var95].mean()) if (port <= var95).any() else np.nan
    cvar99 = float(port[port <= var99].mean()) if (port <= var99).any() else np.nan

    skew = float(port.skew())
    kurt = float(port.kurt())

    beta = np.nan
    alpha = np.nan
    tracking_error = np.nan
    info_ratio = np.nan

    if not bench.empty:
        aligned = pd.concat([port, bench], axis=1).dropna()
        if len(aligned) > 2:
            p = aligned.iloc[:, 0]
            b = aligned.iloc[:, 1]
            b_var = b.var()
            if b_var > 0:
                beta = p.cov(b) / b_var
                bench_ann = b.mean() * ann_factor
                alpha = ann_ret - (rf + beta * (bench_ann - rf))
            active = p - b
            tracking_error = active.std() * np.sqrt(ann_factor) if active.std() > 0 else np.nan
            info_ratio = (active.mean() * ann_factor) / tracking_error if pd.notna(tracking_error) and tracking_error > 0 else np.nan

    return {
        "Cumulative Return %": cum_ret * 100,
        "Annual Return %": ann_ret * 100,
        "Annual Volatility %": ann_vol * 100,
        "Downside Volatility %": downside_vol * 100 if pd.notna(downside_vol) else np.nan,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Calmar Ratio": calmar,
        "Max Drawdown %": max_dd * 100,
        "Daily VaR 95% %": var95 * 100,
        "Daily CVaR 95% %": cvar95 * 100,
        "Daily VaR 99% %": var99 * 100,
        "Daily CVaR 99% %": cvar99 * 100,
        "Skewness": skew,
        "Excess Kurtosis": kurt,
        "Beta vs Benchmark": beta,
        "Jensen Alpha %": alpha * 100 if pd.notna(alpha) else np.nan,
        "Tracking Error %": tracking_error * 100 if pd.notna(tracking_error) else np.nan,
        "Information Ratio": info_ratio,
        "Drawdown Series": dd,
        "Equity Curve": eq,
    }


def optimize_random_frontier(returns_df: pd.DataFrame, n_portfolios: int = 4000, rf: float = 0.04):
    if returns_df.empty or returns_df.shape[1] < 2:
        return pd.DataFrame(), None, None

    mu = returns_df.mean().values * 252
    cov = returns_df.cov().values * 252
    n = returns_df.shape[1]

    results = []
    for _ in range(n_portfolios):
        w = np.random.random(n)
        w = w / w.sum()
        r = float(np.dot(w, mu))
        v = float(np.sqrt(np.dot(w.T, np.dot(cov, w))))
        s = (r - rf) / v if v > 0 else np.nan
        results.append({"Return": r, "Volatility": v, "Sharpe": s, "Weights": w})

    df = pd.DataFrame(results)
    if df.empty:
        return df, None, None

    max_sharpe = df.loc[df["Sharpe"].idxmax()]
    min_vol = df.loc[df["Volatility"].idxmin()]
    return df, max_sharpe, min_vol


def rolling_sharpe(series: pd.Series, window: int, rf: float) -> pd.Series:
    ann = 252
    roll_mean = series.rolling(window).mean() * ann
    roll_vol = series.rolling(window).std() * np.sqrt(ann)
    return (roll_mean - rf) / roll_vol


def compute_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(window).mean()
    ma_down = down.rolling(window).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))
