import numpy as np

from src.black_scholes import call_price, put_price, vega


def is_valid_call_price(market_price, S, K, T, r, q=0.0):
    lower_bound = max(
        0.0,
        S * np.exp(-q * T) - K * np.exp(-r * T)
    )

    upper_bound = S * np.exp(-q * T)

    return lower_bound <= market_price <= upper_bound


def is_valid_put_price(market_price, S, K, T, r, q=0.0):
    lower_bound = max(
        0.0,
        K * np.exp(-r * T) - S * np.exp(-q * T)
    )

    upper_bound = K * np.exp(-r * T)

    return lower_bound <= market_price <= upper_bound


def implied_vol_call(
    market_price,
    S,
    K,
    T,
    r,
    q=0.0,
    initial_sigma=0.20,
    tol=1e-6,
    max_iter=100
):
    if not is_valid_call_price(
        market_price, S, K, T, r, q
    ):
        return None

    sigma = initial_sigma

    for _ in range(max_iter):
        price = call_price(S, K, T, r, sigma, q)

        error = price - market_price

        if abs(error) < tol:
            return sigma

        vega_value = vega(S, K, T, r, sigma, q)

        if abs(vega_value) < 1e-8:
            return None

        sigma = sigma - error / vega_value

        if sigma <= 0 or sigma > 5.0:
            return None

    return None


def implied_vol_put(
    market_price,
    S,
    K,
    T,
    r,
    q=0.0,
    initial_sigma=0.20,
    tol=1e-6,
    max_iter=100
):
    if not is_valid_put_price(
        market_price, S, K, T, r, q
    ):
        return None

    sigma = initial_sigma

    for _ in range(max_iter):
        price = put_price(S, K, T, r, sigma, q)

        error = price - market_price

        if abs(error) < tol:
            return sigma

        vega_value = vega(S, K, T, r, sigma, q)

        if abs(vega_value) < 1e-8:
            return None

        sigma = sigma - error / vega_value

        if sigma <= 0 or sigma > 5.0:
            return None

    return None