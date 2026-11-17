from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

from src.cleaning import build_otm_smile
from src.implied_vol import implied_vol


def get_expirations(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    return ticker.options


def get_option_chain(ticker_symbol, expiration):
    ticker = yf.Ticker(ticker_symbol)
    chain = ticker.option_chain(expiration)

    return chain.calls, chain.puts


def get_spot_price(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    return ticker.fast_info["last_price"]


def time_to_expiry(expiration):
    today = datetime.now(timezone.utc).date()

    expiry_date = datetime.strptime(
        expiration,
        "%Y-%m-%d"
    ).date()

    days_to_expiry = (expiry_date - today).days

    return days_to_expiry / 365.0


def build_smile_for_expiration(
    ticker_symbol,
    expiration,
    spot,
    r,
    q
):
    calls, puts = get_option_chain(
        ticker_symbol,
        expiration
    )

    smile = build_otm_smile(
        calls,
        puts,
        spot
    )

    T = time_to_expiry(expiration)

    smile["implied_vol"] = smile.apply(
        lambda row: implied_vol(
            option_type=row["option_type"],
            market_price=row["mid"],
            S=spot,
            K=row["strike"],
            T=T,
            r=r,
            q=q,
            initial_sigma=0.20
        ),
        axis=1
    )

    smile["expiration"] = expiration
    smile["T"] = T
    smile["spot"] = spot
    smile["r"] = r
    smile["q"] = q

    return smile


def load_surface_data():
    ticker_symbol = "AAPL"

    expirations = [
        "2026-12-18",
        "2027-01-15",
        "2027-03-19",
        "2027-06-17"
    ]

    rates = {
        "2026-12-18": 0.0410,
        "2027-01-15": 0.0426,
        "2027-03-19": 0.0434,
        "2027-06-17": 0.0445
    }

    q = 0.00306

    spot = get_spot_price(ticker_symbol)

    all_smiles = []

    for expiration in expirations:
        smile = build_smile_for_expiration(
            ticker_symbol=ticker_symbol,
            expiration=expiration,
            spot=spot,
            r=rates[expiration],
            q=q
        )

        all_smiles.append(smile)

    surface_data = pd.concat(
        all_smiles,
        ignore_index=True
    )

    surface_data["retrieved_at_utc"] = datetime.now(
        timezone.utc
    ).isoformat()

    return surface_data

def save_surface_snapshot(surface_data, filepath):
    surface_data.to_csv(
        filepath,
        index=False
    )
def load_surface_snapshot(filepath):
    return pd.read_csv(filepath) 


if __name__ == "__main__":
    surface_data = load_surface_data()

    save_surface_snapshot(
        surface_data,
        "data/aapl_surface_snapshot.csv"
    )

    print(
        surface_data[
            [
                "expiration",
                "T",
                "strike",
                "option_type",
                "mid",
                "implied_vol"
            ]
        ]
    )