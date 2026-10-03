from src.black_scholes import call_price, put_price


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