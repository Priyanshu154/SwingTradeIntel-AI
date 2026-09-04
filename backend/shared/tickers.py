"""Static Nifty 50 universe — no DB needed for a fixed 50-ticker list."""

from __future__ import annotations

# Yahoo Finance NSE suffix. Composition is a portfolio snapshot; update manually if needed.
NIFTY_50: list[str] = [
    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "APOLLOHOSP.NS",
    "ASIANPAINT.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS",
    "BAJAJFINSV.NS",
    "BEL.NS",
    "BHARTIARTL.NS",
    "BPCL.NS",
    "BRITANNIA.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "GRASIM.NS",
    "HCLTECH.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "INDUSINDBK.NS",
    "INFY.NS",
    "ITC.NS",
    "JSWSTEEL.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "M&M.NS",
    "MARUTI.NS",
    "NESTLEIND.NS",
    "NTPC.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "RELIANCE.NS",
    "SBILIFE.NS",
    "SBIN.NS",
    "SUNPHARMA.NS",
    "TCS.NS",
    "TATACONSUM.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "TECHM.NS",
    "TITAN.NS",
    "TRENT.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS",
    "ZOMATO.NS",
]

# Symbol without exchange suffix → full Yahoo ticker
_BY_SYMBOL: dict[str, str] = {
    t.replace(".NS", "").upper(): t for t in NIFTY_50
}


def normalize_ticker(raw: str | None) -> str | None:
    """Accept 'TCS', 'tcs.ns', 'TCS.NS' → 'TCS.NS'. Returns None if not in universe."""
    if not raw:
        return None
    cleaned = raw.strip().upper().replace(".NS", "")
    return _BY_SYMBOL.get(cleaned)


def extract_ticker_from_query(query: str) -> str | None:
    """Best-effort: find a Nifty 50 symbol mentioned in free text."""
    upper = query.upper()
    # Longer symbols first so M&M wins over M, etc.
    for symbol in sorted(_BY_SYMBOL.keys(), key=len, reverse=True):
        if symbol in upper:
            return _BY_SYMBOL[symbol]
    return None
