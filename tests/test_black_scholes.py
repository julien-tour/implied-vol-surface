import numpy as np
from src.black_scholes import call_price, put_price, vega

def test_call_price():
    price = call_price(
        S=200,
        K=200,
        T=0.5,
        r=0.03,
        sigma=0.25,
        q=0.0
    )

    assert abs(price - 15.520513343818479) < 1e-10


def test_put_price():
    price = put_price(
        S=200,
        K=200,
        T=0.5,
        r=0.03,
        sigma=0.25,
        q=0.0
    )

    assert abs(price - 12.542901264430995) < 1e-10


def test_vega():
    vega_value = vega(
        S=200,
        K=200,
        T=0.5,
        r=0.03,
        sigma=0.25,
        q=0.0
    )

    assert abs(vega_value - 55.578642127658625) < 1e-10


def test_put_call_parity():
    S = 200
    K = 200
    T = 0.5
    r = 0.03
    q = 0.01
    sigma = 0.25

    call = call_price(
        S=S,
        K=K,
        T=T,
        r=r,
        sigma=sigma,
        q=q
    )

    put = put_price(
        S=S,
        K=K,
        T=T,
        r=r,
        sigma=sigma,
        q=q
    )

    left_side = call - put

    right_side = (
        S * np.exp(-q * T)
        - K * np.exp(-r * T)
    )

    assert abs(left_side - right_side) < 1e-10