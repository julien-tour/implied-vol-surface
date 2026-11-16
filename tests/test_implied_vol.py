from src.implied_vol import implied_vol_call, implied_vol_put


def test_implied_vol_call():
    sigma = implied_vol_call(
        market_price=15.520513343818479,
        S=200,
        K=200,
        T=0.5,
        r=0.03,
        q=0.0,
        initial_sigma=0.20
    )

    assert abs(sigma - 0.25) < 1e-10


def test_implied_vol_put():
    sigma = implied_vol_put(
        market_price=12.542901264430995,
        S=200,
        K=200,
        T=0.5,
        r=0.03,
        q=0.0,
        initial_sigma=0.20
    )

    assert abs(sigma - 0.25) < 1e-10

def test_invalid_call_price():
    sigma = implied_vol_call(
        market_price=1.0,
        S=200,
        K=200,
        T=0.5,
        r=0.03,
        q=0.0,
        initial_sigma=0.20
    )

    assert sigma is None
def test_invalid_put_price():
    sigma = implied_vol_put(
        market_price=250.0,
        S=200,
        K=200,
        T=0.5,
        r=0.03,
        q=0.0,
        initial_sigma=0.20
    )

    assert sigma is None