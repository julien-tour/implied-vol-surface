import pandas as pd

def build_otm_smile(calls, puts, spot):
    clean_calls = clean_option_chain(calls, spot)
    clean_puts = clean_option_chain(puts, spot)

    otm_calls = clean_calls[
        clean_calls["strike"] >= spot
    ].copy()

    otm_puts = clean_puts[
        clean_puts["strike"] < spot
    ].copy()

    otm_calls["option_type"] = "call"
    otm_puts["option_type"] = "put"

    smile = pd.concat(
        [otm_puts, otm_calls],
        ignore_index=True
    )

    smile = smile.sort_values("strike").reset_index(drop=True)

    return smile

def clean_option_chain(options, spot, min_moneyness=0.90, max_moneyness=1.10, max_relative_spread=0.10):
    cleaned = options.copy()

    cleaned = cleaned[
        (cleaned["strike"] >= min_moneyness * spot)
        & (cleaned["strike"] <= max_moneyness * spot)
    ]

    cleaned = cleaned[
        (cleaned["bid"] > 0)
        & (cleaned["ask"] > cleaned["bid"])
    ]

    cleaned["mid"] = (
        cleaned["bid"] + cleaned["ask"]
    ) / 2

    cleaned["relative_spread"] = (
        cleaned["ask"] - cleaned["bid"]
    ) / cleaned["mid"]

    cleaned = cleaned[
        cleaned["relative_spread"] <= max_relative_spread
    ]

    return cleaned