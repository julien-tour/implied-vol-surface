import numpy as np
import pandas as pd

from src.data_loader import load_surface_snapshot


# ============================================================
# ATM TERM STRUCTURE
# ============================================================

def get_atm_vols(surface_data):
    atm_rows = []

    for expiration, group in surface_data.groupby("expiration"):
        spot = group["spot"].iloc[0]

        group = group.copy()

        group["distance_to_spot"] = abs(
            group["strike"] - spot
        )

        atm_row = group.loc[
            group["distance_to_spot"].idxmin()
        ]

        atm_rows.append(
            {
                "expiration": expiration,
                "T": atm_row["T"],
                "strike": atm_row["strike"],
                "spot": spot,
                "implied_vol": atm_row["implied_vol"]
            }
        )

    return pd.DataFrame(atm_rows)


# ============================================================
# SIMPLE SKEW BETWEEN TWO STRIKES
# ============================================================

def get_skew_by_maturity(
    surface_data,
    low_strike=320,
    high_strike=380
):
    skew_rows = []

    for expiration, group in surface_data.groupby("expiration"):
        low_row = group[
            group["strike"] == low_strike
        ]

        high_row = group[
            group["strike"] == high_strike
        ]

        if low_row.empty or high_row.empty:
            continue

        low_vol = low_row[
            "implied_vol"
        ].iloc[0]

        high_vol = high_row[
            "implied_vol"
        ].iloc[0]

        skew = (
            low_vol - high_vol
        )

        skew_slope = (
            high_vol - low_vol
        ) / (
            high_strike - low_strike
        )

        skew_rows.append(
            {
                "expiration": expiration,
                "low_strike_vol": low_vol,
                "high_strike_vol": high_vol,
                "skew": skew,
                "skew_slope": skew_slope
            }
        )

    return pd.DataFrame(skew_rows)


# ============================================================
# LINEAR REGRESSION USING STRIKE
# ============================================================

def get_regression_skew(surface_data):
    regression_rows = []

    for expiration, group in surface_data.groupby("expiration"):
        strikes = group[
            "strike"
        ].to_numpy()

        implied_vols = group[
            "implied_vol"
        ].to_numpy()

        slope, intercept = np.polyfit(
            strikes,
            implied_vols,
            1
        )

        fitted_vols = (
            slope * strikes
            + intercept
        )

        residuals = (
            implied_vols
            - fitted_vols
        )

        ss_res = np.sum(
            residuals ** 2
        )

        ss_tot = np.sum(
            (
                implied_vols
                - implied_vols.mean()
            ) ** 2
        )

        r_squared = (
            1 - ss_res / ss_tot
        )

        regression_rows.append(
            {
                "expiration": expiration,
                "slope": slope,
                "slope_per_10_strike": slope * 10,
                "r_squared": r_squared
            }
        )

    return pd.DataFrame(regression_rows)


# ============================================================
# LINEAR REGRESSION USING MONEYNESS K / S
# ============================================================

def get_moneyness_regression_skew(surface_data):
    regression_rows = []

    for expiration, group in surface_data.groupby("expiration"):
        group = group.copy()

        spot = group[
            "spot"
        ].iloc[0]

        group["moneyness"] = (
            group["strike"] / spot
        )

        moneyness = group[
            "moneyness"
        ].to_numpy()

        implied_vols = group[
            "implied_vol"
        ].to_numpy()

        slope, intercept = np.polyfit(
            moneyness,
            implied_vols,
            1
        )

        fitted_vols = (
            slope * moneyness
            + intercept
        )

        residuals = (
            implied_vols
            - fitted_vols
        )

        ss_res = np.sum(
            residuals ** 2
        )

        ss_tot = np.sum(
            (
                implied_vols
                - implied_vols.mean()
            ) ** 2
        )

        r_squared = (
            1 - ss_res / ss_tot
        )

        regression_rows.append(
            {
                "expiration": expiration,
                "moneyness_slope": slope,
                "r_squared": r_squared
            }
        )

    return pd.DataFrame(regression_rows)


# ============================================================
# LINEAR REGRESSION USING LOG-MONEYNESS log(K / F)
# ============================================================

def get_log_moneyness_regression_skew(surface_data):
    regression_rows = []

    for expiration, group in surface_data.groupby("expiration"):
        group = group.copy()

        spot = group[
            "spot"
        ].iloc[0]

        T = group[
            "T"
        ].iloc[0]

        r = group[
            "r"
        ].iloc[0]

        q = group[
            "q"
        ].iloc[0]

        forward = spot * np.exp(
            (r - q) * T
        )

        group["log_moneyness"] = np.log(
            group["strike"] / forward
        )

        log_moneyness = group[
            "log_moneyness"
        ].to_numpy()

        implied_vols = group[
            "implied_vol"
        ].to_numpy()

        slope, intercept = np.polyfit(
            log_moneyness,
            implied_vols,
            1
        )

        fitted_vols = (
            slope * log_moneyness
            + intercept
        )

        residuals = (
            implied_vols
            - fitted_vols
        )

        ss_res = np.sum(
            residuals ** 2
        )

        ss_tot = np.sum(
            (
                implied_vols
                - implied_vols.mean()
            ) ** 2
        )

        r_squared = (
            1 - ss_res / ss_tot
        )

        regression_rows.append(
            {
                "expiration": expiration,
                "forward": forward,
                "log_moneyness_slope": slope,
                "r_squared": r_squared
            }
        )

    return pd.DataFrame(regression_rows)


# ============================================================
# ATM-FORWARD TOTAL VARIANCE
# ============================================================

def get_atm_forward_total_variance(surface_data):
    rows = []

    for expiration, group in surface_data.groupby("expiration"):
        group = group.copy()

        spot = group[
            "spot"
        ].iloc[0]

        T = group[
            "T"
        ].iloc[0]

        r = group[
            "r"
        ].iloc[0]

        q = group[
            "q"
        ].iloc[0]

        forward = spot * np.exp(
            (r - q) * T
        )

        group["log_moneyness"] = np.log(
            group["strike"] / forward
        )

        group = group.sort_values(
            "log_moneyness"
        )

        x = group[
            "log_moneyness"
        ].to_numpy()

        vols = group[
            "implied_vol"
        ].to_numpy()

        if x.min() > 0 or x.max() < 0:
            continue

        atm_forward_vol = np.interp(
            0.0,
            x,
            vols
        )

        total_variance = (
            atm_forward_vol ** 2
        ) * T

        rows.append(
            {
                "expiration": expiration,
                "T": T,
                "forward": forward,
                "atm_forward_vol": atm_forward_vol,
                "total_variance": total_variance
            }
        )

    result = pd.DataFrame(rows)

    result = result.sort_values(
        "T"
    ).reset_index(drop=True)

    result["variance_change"] = (
        result["total_variance"].diff()
    )

    return result


# ============================================================
# CALENDAR ARBITRAGE CHECK
# ============================================================

def check_calendar_total_variance(
    surface_data,
    grid_size=15
):
    maturity_data = []

    for expiration, group in surface_data.groupby("expiration"):
        group = group.copy()

        spot = group[
            "spot"
        ].iloc[0]

        T = group[
            "T"
        ].iloc[0]

        r = group[
            "r"
        ].iloc[0]

        q = group[
            "q"
        ].iloc[0]

        forward = spot * np.exp(
            (r - q) * T
        )

        group["log_moneyness"] = np.log(
            group["strike"] / forward
        )

        group = group.sort_values(
            "log_moneyness"
        )

        maturity_data.append(
            {
                "expiration": expiration,
                "T": T,
                "group": group,
                "min_log_moneyness": group[
                    "log_moneyness"
                ].min(),
                "max_log_moneyness": group[
                    "log_moneyness"
                ].max()
            }
        )

    common_min = max(
        item["min_log_moneyness"]
        for item in maturity_data
    )

    common_max = min(
        item["max_log_moneyness"]
        for item in maturity_data
    )

    log_moneyness_grid = np.linspace(
        common_min,
        common_max,
        grid_size
    )

    rows = []

    for item in maturity_data:
        group = item["group"]

        x = group[
            "log_moneyness"
        ].to_numpy()

        vols = group[
            "implied_vol"
        ].to_numpy()

        interpolated_vols = np.interp(
            log_moneyness_grid,
            x,
            vols
        )

        total_variances = (
            interpolated_vols ** 2
        ) * item["T"]

        for k, vol, variance in zip(
            log_moneyness_grid,
            interpolated_vols,
            total_variances
        ):
            rows.append(
                {
                    "expiration": item["expiration"],
                    "T": item["T"],
                    "log_moneyness": k,
                    "implied_vol": vol,
                    "total_variance": variance
                }
            )

    result = pd.DataFrame(rows)

    result = result.sort_values(
        [
            "log_moneyness",
            "T"
        ]
    )

    result["variance_change"] = (
        result.groupby(
            "log_moneyness"
        )["total_variance"].diff()
    )

    result["calendar_violation"] = (
        result["variance_change"] < 0
    )

    print(
        "Common log-moneyness range:",
        common_min,
        "to",
        common_max
    )

    return result


# ============================================================
# CALL-EQUIVALENT QUOTES
# ============================================================

def build_call_equivalent_quotes(group):
    group = group.copy()

    spot = group[
        "spot"
    ].iloc[0]

    T = group[
        "T"
    ].iloc[0]

    r = group[
        "r"
    ].iloc[0]

    q = group[
        "q"
    ].iloc[0]

    parity_adjustment = (
        spot * np.exp(-q * T)
        - group["strike"] * np.exp(-r * T)
    )

    group["call_mid"] = np.where(
        group["option_type"] == "call",
        group["mid"],
        group["mid"] + parity_adjustment
    )

    group["call_bid"] = np.where(
        group["option_type"] == "call",
        group["bid"],
        group["bid"] + parity_adjustment
    )

    group["call_ask"] = np.where(
        group["option_type"] == "call",
        group["ask"],
        group["ask"] + parity_adjustment
    )

    return group


# ============================================================
# BUTTERFLY / CONVEXITY CHECK WITH BID-ASK
# ============================================================

def check_butterfly_convexity(
    surface_data,
    tolerance=1e-10
):
    rows = []

    for expiration, group in surface_data.groupby("expiration"):
        group = build_call_equivalent_quotes(
            group
        )

        group = group.sort_values(
            "strike"
        ).reset_index(drop=True)

        for i in range(
            1,
            len(group) - 1
        ):
            K1 = group.loc[
                i - 1,
                "strike"
            ]

            K2 = group.loc[
                i,
                "strike"
            ]

            K3 = group.loc[
                i + 1,
                "strike"
            ]

            C1_mid = group.loc[
                i - 1,
                "call_mid"
            ]

            C2_mid = group.loc[
                i,
                "call_mid"
            ]

            C3_mid = group.loc[
                i + 1,
                "call_mid"
            ]

            C1_ask = group.loc[
                i - 1,
                "call_ask"
            ]

            C2_bid = group.loc[
                i,
                "call_bid"
            ]

            C3_ask = group.loc[
                i + 1,
                "call_ask"
            ]

            # ------------------------------------------------
            # Generalised butterfly weights
            #
            # For equally spaced strikes:
            #
            # left_weight  = 1
            # center       = -2
            # right_weight = 1
            #
            # For unequal spacing the weights are adjusted so
            # that the strategy still represents a convexity
            # test.
            # ------------------------------------------------

            left_weight = (
                2
                * (K3 - K2)
                / (K3 - K1)
            )

            right_weight = (
                2
                * (K2 - K1)
                / (K3 - K1)
            )

            # Mid-price butterfly value
            mid_butterfly = (
                left_weight * C1_mid
                - 2 * C2_mid
                + right_weight * C3_mid
            )

            midpoint_violation = (
                mid_butterfly < -tolerance
            )

            # ------------------------------------------------
            # Executable butterfly
            #
            # Long wings -> buy at ask
            # Short centre -> sell at bid
            #
            # A negative cost would indicate an executable
            # arbitrage under the simplified assumptions used.
            # ------------------------------------------------

            executable_cost = (
                left_weight * C1_ask
                - 2 * C2_bid
                + right_weight * C3_ask
            )

            executable_violation = (
                executable_cost < -tolerance
            )

            rows.append(
                {
                    "expiration": expiration,
                    "K1": K1,
                    "K2": K2,
                    "K3": K3,
                    "left_weight": left_weight,
                    "right_weight": right_weight,
                    "mid_butterfly": mid_butterfly,
                    "midpoint_violation": midpoint_violation,
                    "executable_cost": executable_cost,
                    "executable_violation": executable_violation
                }
            )

    return pd.DataFrame(rows)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    surface_data = load_surface_snapshot(
        "data/aapl_surface_snapshot.csv"
    )

    # --------------------------------------------------------
    # ATM term structure
    # --------------------------------------------------------

    atm_vols = get_atm_vols(
        surface_data
    )

    print(
        "ATM term structure:"
    )

    print(
        atm_vols
    )

    # --------------------------------------------------------
    # Simple skew
    # --------------------------------------------------------

    skew_data = get_skew_by_maturity(
        surface_data
    )

    print(
        "\nSkew by maturity:"
    )

    print(
        skew_data
    )

    # --------------------------------------------------------
    # Strike regression
    # --------------------------------------------------------

    regression_skew = get_regression_skew(
        surface_data
    )

    print(
        "\nRegression skew:"
    )

    print(
        regression_skew
    )

    # --------------------------------------------------------
    # Moneyness regression
    # --------------------------------------------------------

    moneyness_skew = (
        get_moneyness_regression_skew(
            surface_data
        )
    )

    print(
        "\nMoneyness regression skew:"
    )

    print(
        moneyness_skew
    )

    # --------------------------------------------------------
    # Log-moneyness regression
    # --------------------------------------------------------

    log_moneyness_skew = (
        get_log_moneyness_regression_skew(
            surface_data
        )
    )

    print(
        "\nLog-moneyness regression skew:"
    )

    print(
        log_moneyness_skew
    )

    # --------------------------------------------------------
    # ATM-forward total variance
    # --------------------------------------------------------

    atm_forward_variance = (
        get_atm_forward_total_variance(
            surface_data
        )
    )

    print(
        "\nATM-forward total variance:"
    )

    print(
        atm_forward_variance
    )

    # --------------------------------------------------------
    # Calendar consistency
    # --------------------------------------------------------

    print(
        "\nCalendar total variance check:"
    )

    calendar_check = (
        check_calendar_total_variance(
            surface_data
        )
    )

    print(
        calendar_check[
            [
                "expiration",
                "log_moneyness",
                "total_variance",
                "variance_change",
                "calendar_violation"
            ]
        ]
    )

    print(
        "\nNumber of detected calendar violations:",
        calendar_check[
            "calendar_violation"
        ].sum()
    )

    # --------------------------------------------------------
    # Butterfly consistency
    # --------------------------------------------------------

    butterfly_check = (
        check_butterfly_convexity(
            surface_data
        )
    )

    print(
        "\nButterfly convexity check:"
    )

    print(
        butterfly_check[
            [
                "expiration",
                "K1",
                "K2",
                "K3",
                "mid_butterfly",
                "midpoint_violation",
                "executable_cost",
                "executable_violation"
            ]
        ]
    )

    print(
        "\nNumber of midpoint butterfly violations:",
        butterfly_check[
            "midpoint_violation"
        ].sum()
    )

    print(
        "Number of executable butterfly violations:",
        butterfly_check[
            "executable_violation"
        ].sum()
    )

    # --------------------------------------------------------
    # Display midpoint violations only
    # --------------------------------------------------------

    midpoint_violations = butterfly_check[
        butterfly_check[
            "midpoint_violation"
        ]
    ]

    if not midpoint_violations.empty:
        print(
            "\nMidpoint butterfly violations:"
        )

        print(
            midpoint_violations[
                [
                    "expiration",
                    "K1",
                    "K2",
                    "K3",
                    "mid_butterfly",
                    "executable_cost",
                    "executable_violation"
                ]
            ]
        )