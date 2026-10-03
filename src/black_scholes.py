import numpy as np
from scipy.stats import norm


def d1_d2(S, K, T, r, sigma, q=0.0):
    d1 = (
        np.log(S / K)
        + (r - q + 0.5 * sigma**2) * T
    ) / (sigma * np.sqrt(T))

    d2 = d1 - sigma * np.sqrt(T)

    return d1, d2

def call_price(S, K, T, r, sigma, q=0.0):
    d1, d2 = d1_d2(S, K, T, r, sigma, q)

    call = (
        S * np.exp(-q * T) * norm.cdf(d1)
        - K * np.exp(-r * T) * norm.cdf(d2)
    )

    return call

def put_price(S, K, T, r, sigma, q=0.0):
    d1, d2 = d1_d2(S, K, T, r, sigma, q)

    put = (
        K * np.exp(-r * T) * norm.cdf(-d2)
        - S * np.exp(-q * T) * norm.cdf(-d1)
    )

    return put

print(put_price(
    S=200,
    K=200,
    T=0.5,
    r=0.03,
    sigma=0.25,
    q=0.0
))