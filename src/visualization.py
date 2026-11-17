import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from src.data_loader import load_surface_snapshot

def plot_volatility_smiles(surface_data):
    for expiration, group in surface_data.groupby("expiration"):
        group = group.sort_values("strike")

        plt.plot(
            group["strike"],
            group["implied_vol"] * 100,
            marker="o",
            label=expiration
        )

    plt.xlabel("Strike")
    plt.ylabel("Implied Volatility (%)")
    plt.title("AAPL Implied Volatility Smiles")
    plt.legend()
    plt.grid(True)

    plt.show()

def interpolate_vol_surface(surface_data):
    strikes = surface_data["strike"].to_numpy()
    maturities = surface_data["T"].to_numpy()
    implied_vols = surface_data["implied_vol"].to_numpy()

    strike_grid = np.linspace(
        strikes.min(),
        strikes.max(),
        50
    )

    maturity_grid = np.linspace(
        maturities.min(),
        maturities.max(),
        50
    )

    K_grid, T_grid = np.meshgrid(
        strike_grid,
        maturity_grid
    )

    IV_grid = griddata(
        points=(strikes, maturities),
        values=implied_vols,
        xi=(K_grid, T_grid),
        method="linear"
    )

    return K_grid, T_grid, IV_grid
def plot_volatility_surface(surface_data):
    K_grid, T_grid, IV_grid = interpolate_vol_surface(
        surface_data
    )

    fig = plt.figure(figsize=(10, 7))

    ax = fig.add_subplot(
        111,
        projection="3d"
    )

    ax.plot_surface(
        K_grid,
        T_grid,
        IV_grid * 100,
        cmap="viridis",
        alpha=0.85
    )

    ax.scatter(
        surface_data["strike"],
        surface_data["T"],
        surface_data["implied_vol"] * 100,
        color="black",
        s=25,
        label="Observed market points"
    )

    ax.set_xlabel("Strike")
    ax.set_ylabel("Time to Maturity (Years)")
    ax.set_zlabel("Implied Volatility (%)")

    ax.set_title(
        "AAPL Implied Volatility Surface"
    )

    ax.legend()

    plt.show()

def plot_log_moneyness_smiles(surface_data):
    for expiration, group in surface_data.groupby("expiration"):
        group = group.copy()

        spot = group["spot"].iloc[0]
        T = group["T"].iloc[0]
        r = group["r"].iloc[0]
        q = group["q"].iloc[0]

        forward = spot * np.exp(
            (r - q) * T
        )

        group["log_moneyness"] = np.log(
            group["strike"] / forward
        )

        group = group.sort_values(
            "log_moneyness"
        )

        plt.plot(
            group["log_moneyness"],
            group["implied_vol"] * 100,
            marker="o",
            label=expiration
        )

    plt.axvline(
        x=0,
        linestyle="--",
        linewidth=1
    )

    plt.xlabel("Log-Moneyness log(K/F)")
    plt.ylabel("Implied Volatility (%)")

    plt.title(
        "AAPL Implied Volatility Skew by Log-Moneyness"
    )

    plt.legend()
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    surface_data = load_surface_snapshot(
        "data/aapl_surface_snapshot.csv"
    )

    plot_log_moneyness_smiles(
        surface_data
    )
