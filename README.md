# Implied Volatility Surface Construction

A quantitative finance project that builds an implied volatility surface from listed AAPL option quotes.

The project implements the Black-Scholes model and an implied-volatility solver from scratch, cleans market option data, constructs volatility skews across several maturities, interpolates a three-dimensional volatility surface, and performs simplified static-arbitrage consistency checks.

## Project Overview

Option markets do not exhibit a single constant volatility across strikes and maturities.

Instead, the volatility implied by market option prices can be represented as:

\[
\sigma_{\text{impl}} = \sigma(K,T)
\]

where:

- \(K\) is the strike price;
- \(T\) is the time to maturity;
- \(\sigma_{\text{impl}}\) is the implied volatility.

The objective of this project is to recover this volatility structure directly from market option prices and analyze its main characteristics.

The workflow is:

```text
Market option quotes
        ↓
Data cleaning
        ↓
Bid-ask midpoint
        ↓
Black-Scholes pricing
        ↓
Newton-Raphson implied volatility
        ↓
Volatility skew by maturity
        ↓
3D implied volatility surface
        ↓
Log-moneyness analysis
        ↓
Static consistency checks
```

---

## Main Features

The project includes:

- Black-Scholes call and put pricing implemented from scratch;
- analytical Black-Scholes Vega;
- Newton-Raphson implied-volatility inversion;
- theoretical option-price validity checks;
- real listed-option data retrieved with `yfinance`;
- liquidity and bid-ask spread filtering;
- combination of OTM puts and OTM calls;
- multiple option maturities;
- volatility skew visualization;
- three-dimensional implied volatility surface;
- strike, moneyness and log-moneyness analysis;
- ATM-forward volatility term structure;
- total implied variance analysis;
- simplified calendar-arbitrage consistency checks;
- butterfly convexity checks;
- transaction-cost-aware butterfly checks;
- reproducible market-data snapshot;
- automated unit tests with `pytest`.

---

## Data

The analysis uses a fixed AAPL option-market snapshot stored in:

```text
data/aapl_surface_snapshot.csv
```

The snapshot was retrieved on:

```text
2026-11-16T20:54:01 UTC
```

The underlying spot price in the snapshot was approximately:

\[
S = 351.835
\]

Four expirations are used:

| Expiration | Time to maturity |
|---|---:|
| 2026-12-18 | 0.0877 years |
| 2027-01-15 | 0.1644 years |
| 2027-03-19 | 0.3370 years |
| 2027-06-17 | 0.5836 years |

The final cleaned snapshot contains **42 option observations**.

Market data can also be retrieved dynamically using `yfinance`, but the fixed CSV snapshot is used for reproducible analysis.

---

## Data Cleaning

The raw option chain is filtered before implied volatility is calculated.

The current filtering rules retain options satisfying:

```text
90% of spot <= strike <= 110% of spot
bid > 0
ask > bid
relative bid-ask spread <= 10%
```

The option midpoint is defined as:

\[
\text{Mid}=\frac{\text{Bid}+\text{Ask}}{2}
\]

rather than using the last traded price, which may be stale.

The relative spread is:

\[
\text{Relative Spread}
=
\frac{\text{Ask}-\text{Bid}}{\text{Mid}}
\]

To construct each volatility skew, the project uses:

- OTM puts when \(K<S\);
- OTM calls when \(K\geq S\).

This reduces the reliance on less liquid deep in-the-money quotes.

---

## Black-Scholes Model

For a continuously compounded dividend yield \(q\), the European call price is:

\[
C
=
Se^{-qT}N(d_1)
-
Ke^{-rT}N(d_2)
\]

and the put price is:

\[
P
=
Ke^{-rT}N(-d_2)
-
Se^{-qT}N(-d_1)
\]

with:

\[
d_1
=
\frac{
\ln(S/K)
+
(r-q+\frac{1}{2}\sigma^2)T
}{
\sigma\sqrt{T}
}
\]

and:

\[
d_2=d_1-\sigma\sqrt{T}
\]

The implementation is available in:

```text
src/black_scholes.py
```

---

## Vega

The analytical Black-Scholes Vega is:

\[
\text{Vega}
=
Se^{-qT}\phi(d_1)\sqrt{T}
\]

where \(\phi\) is the standard normal probability density function.

Vega is required by the Newton-Raphson implied-volatility solver.

---

## Implied Volatility Solver

Implied volatility is recovered by solving:

\[
BS(\sigma)=P_{\text{market}}
\]

using Newton-Raphson:

\[
\sigma_{n+1}
=
\sigma_n
-
\frac{
BS(\sigma_n)-P_{\text{market}}
}{
\text{Vega}(\sigma_n)
}
\]

The current solver uses:

```text
Initial volatility: 20%
Tolerance:          1e-6
Maximum iterations: 100
Maximum volatility: 500%
Minimum Vega:       1e-8
```

The solver also checks whether the market price satisfies theoretical European option-price bounds before starting the iteration.

Implementation:

```text
src/implied_vol.py
```

---

## Market Assumptions

The snapshot uses the following maturity-specific continuously compounded risk-free rate assumptions:

| Expiration | \(r\) |
|---|---:|
| 2026-12-18 | 4.10% |
| 2027-01-15 | 4.26% |
| 2027-03-19 | 4.34% |
| 2027-06-17 | 4.45% |

The continuous dividend-yield approximation is:

\[
q=0.00306
\]

or approximately:

\[
0.306\%
\]

These values are explicit modelling inputs and are stored alongside each observation in the dataset.

---

## Volatility Skew

The market snapshot displays a clear negative equity volatility skew.

For example, the difference between the implied volatility at strikes 320 and 380 is:

| Expiration | \(\sigma(320)-\sigma(380)\) |
|---|---:|
| 2026-12-18 | 9.01 vol points |
| 2027-01-15 | 6.46 vol points |
| 2027-03-19 | 4.89 vol points |
| 2027-06-17 | 3.54 vol points |

Therefore, in this snapshot:

\[
\frac{\partial \sigma_{\text{impl}}}{\partial K}<0
\]

and the magnitude of the skew decreases with maturity.

---

## Regression Analysis

A simple linear regression of implied volatility against strike gives:

| Expiration | IV change per +$10 strike | \(R^2\) |
|---|---:|---:|
| 2026-12-18 | -1.44 vol points | 0.971 |
| 2027-01-15 | -1.04 vol points | 0.978 |
| 2027-03-19 | -0.78 vol points | 0.987 |
| 2027-06-17 | -0.57 vol points | 0.991 |

The high \(R^2\) values indicate that, over the selected 90%-110% spot range, the dominant feature is a relatively strong negative skew rather than a highly curved symmetric smile.

The linear regression is only used as a descriptive statistic, not as an option-pricing model.

---

## Forward and Log-Moneyness

The theoretical forward is defined as:

\[
F=Se^{(r-q)T}
\]

The project then defines log-moneyness as:

\[
k=\log(K/F)
\]

This provides a more standardized representation of the volatility surface.

The calculated forwards are approximately:

| Expiration | Forward |
|---|---:|
| 2026-12-18 | 353.01 |
| 2027-01-15 | 354.13 |
| 2027-03-19 | 356.65 |
| 2027-06-17 | 360.45 |

The log-moneyness skew remains negative for every maturity.

---

## ATM-Forward Term Structure

ATM-forward implied volatility is obtained by interpolating the volatility skew at:

\[
\log(K/F)=0
\]

The resulting term structure is:

| Expiration | ATM-forward IV |
|---|---:|
| 2026-12-18 | 24.22% |
| 2027-01-15 | 24.05% |
| 2027-03-19 | 26.31% |
| 2027-06-17 | 27.26% |

The term structure is therefore not strictly monotonic in volatility itself.

---

## Total Implied Variance

Total implied variance is defined as:

\[
w(k,T)=\sigma_{\text{impl}}(k,T)^2T
\]

At ATM-forward:

| Expiration | Total variance |
|---|---:|
| 2026-12-18 | 0.00515 |
| 2027-01-15 | 0.00951 |
| 2027-03-19 | 0.02333 |
| 2027-06-17 | 0.04336 |

Total variance increases with maturity over the four expirations.

---

## Calendar Consistency Check

A common log-moneyness interval is constructed across all four expirations:

\[
k\in[-0.0982,\;0.0528]
\]

Fifteen common log-moneyness levels are tested.

For every level, the project checks whether total implied variance decreases between consecutive maturities.

Result:

```text
Detected calendar total-variance violations: 0
```

No violation was detected on the tested grid.

This is a simplified static consistency check and should not be interpreted as a formal proof that the entire interpolated surface is arbitrage-free.

---

## Butterfly Convexity Check

For a fixed maturity, European call prices should be convex with respect to strike.

For three strikes:

\[
K_1<K_2<K_3
\]

the slope should satisfy:

\[
\frac{C(K_2)-C(K_1)}{K_2-K_1}
\leq
\frac{C(K_3)-C(K_2)}{K_3-K_2}
\]

The project converts OTM puts into European call-equivalent prices using put-call parity when necessary.

Using midpoint quotes:

```text
Detected midpoint butterfly violations: 1
```

The single violation is localised around the January 2027 ATM region:

```text
K1 = 350
K2 = 355
K3 = 360
```

Its magnitude is small, approximately $0.10 at midpoint prices.

---

## Bid-Ask-Aware Butterfly Check

A midpoint violation does not necessarily correspond to an executable arbitrage.

The project therefore also evaluates the butterfly using transaction-side quotes:

- long wings are purchased at the ask;
- the centre options are sold at the bid.

Result:

```text
Midpoint butterfly violations:   1
Executable butterfly violations: 0
```

Therefore, the small midpoint convexity anomaly disappears after incorporating the bid-ask spread.

---

## Volatility Surface Interpolation

Observed volatility points do not form a perfectly rectangular strike-maturity grid.

The project therefore uses two-dimensional linear interpolation with:

```python
scipy.interpolate.griddata
```

A \(50\times50\) grid is constructed across strike and maturity.

The three-dimensional surface distinguishes between:

- observed market-implied volatility points;
- interpolated surface values.

The interpolation is intended for visualization and descriptive analysis rather than advanced arbitrage-free calibration.

---

## Visualizations

The project produces:

### Volatility skew by strike

Each maturity is plotted separately with:

\[
x=K,
\qquad
y=\sigma_{\text{impl}}
\]

### Volatility skew by log-moneyness

The horizontal axis becomes:

\[
\log(K/F)
\]

with a reference line at:

\[
\log(K/F)=0
\]

representing ATM-forward.

### 3D implied volatility surface

The surface uses:

- strike on the \(x\)-axis;
- maturity on the \(y\)-axis;
- implied volatility on the \(z\)-axis.

Observed market points are displayed separately from the interpolated surface.

Implementation:

```text
src/visualization.py
```

---

## Project Structure

```text
implied-vol-surface/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── aapl_surface_snapshot.csv
│
├── src/
│   ├── analysis.py
│   ├── black_scholes.py
│   ├── cleaning.py
│   ├── data_loader.py
│   ├── implied_vol.py
│   └── visualization.py
│
└── tests/
    ├── test_black_scholes.py
    └── test_implied_vol.py
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/julien-tour/implied-vol-surface.git
cd implied-vol-surface
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

The project was developed and tested with Python 3.14.7.

---

## Usage

### Retrieve and clean live option data

```bash
python -m src.data_loader
```

This also creates or overwrites:

```text
data/aapl_surface_snapshot.csv
```

### Generate the volatility visualization

```bash
python -m src.visualization
```

### Run the quantitative analysis

```bash
python -m src.analysis
```

### Run the tests

```bash
python -m pytest
```

Current test suite:

```text
11 passed
```

The tests cover:

- Black-Scholes call pricing;
- Black-Scholes put pricing;
- Vega;
- put-call parity;
- call implied-volatility inversion;
- put implied-volatility inversion;
- theoretical price validation;
- generic option-type routing;
- invalid option-type handling.

---

## Main Results

The AAPL snapshot analysed in this project exhibits:

1. a clear negative equity volatility skew;
2. a steeper skew at shorter maturities;
3. a non-flat ATM-forward volatility term structure;
4. increasing ATM-forward total variance with maturity;
5. no calendar total-variance violations on the common tested log-moneyness grid;
6. one small midpoint butterfly convexity violation;
7. zero executable butterfly violations after bid-ask spreads are incorporated.

These results illustrate why the constant-volatility assumption of the Black-Scholes model does not reproduce the structure observed in market option prices.

---

## Limitations

This project is designed as a transparent educational and quantitative-finance implementation rather than a production volatility-surface calibration system.

Important limitations include:

- Black-Scholes assumes European exercise;
- the market quotes are treated under a European pricing approximation;
- dividends are represented using a continuous dividend yield rather than discrete dividend payments;
- risk-free rates are fixed maturity-specific inputs;
- the market snapshot is not perfectly synchronized across all option quotes;
- time to maturity uses calendar days divided by 365;
- market data retrieved through `yfinance` may be delayed;
- the surface uses linear interpolation rather than a calibrated volatility parameterization;
- no SVI, SABR, local-volatility or stochastic-volatility calibration is performed;
- the static-arbitrage tests are simplified discrete checks rather than a formal proof of arbitrage-free interpolation.

These limitations are intentional in order to keep the implementation transparent and interpretable.

---

## Possible Extensions

Possible future improvements include:

- Brent root-finding fallback when Newton-Raphson fails;
- discrete-dividend modelling;
- finer yield-curve interpolation;
- forward-based filtering;
- additional liquidity filters;
- automated snapshot timestamping and versioning;
- SVI calibration;
- explicit arbitrage-free smile interpolation;
- local-volatility extraction;
- comparison with stochastic-volatility models;
- historical analysis of volatility-surface dynamics.

---

## Technologies

- Python
- NumPy
- SciPy
- pandas
- Matplotlib
- yfinance
- pytest

---

## Disclaimer

This project is for educational and research purposes only.

It is not intended to provide investment advice, trading recommendations or production-grade option valuation.