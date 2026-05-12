import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from .config import SM3_TO_BBL


def exp_decline(t, qi, Di):
    return qi * np.exp(-Di * t)


def harm_decline(t, qi, Di):
    return qi / (1.0 + Di * t)


def hyp_decline(t, qi, Di, b):
    return qi / (1.0 + b * Di * t) ** (1.0 / b)


def _r2_rmse(q_actual, q_pred):
    ss_res = float(np.sum((q_actual - q_pred) ** 2))
    ss_tot = float(np.sum((q_actual - q_actual.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    rmse = float(np.sqrt(ss_res / len(q_actual)))
    return round(r2, 4), round(rmse, 2)


def fit_arps_models(df, phase="Oil_bbl", resample="ME") -> dict:
    if phase not in df.columns or len(df) < 6:
        return {}
    monthly = (df.set_index("Date")[phase]
               .resample(resample).mean()
               .dropna()
               .reset_index())
    monthly.columns = ["Date", "q"]
    monthly = monthly[monthly["q"] > 10].copy()
    if len(monthly) < 4:
        return {}
    peak_i = monthly["q"].idxmax()
    fit_df = monthly.iloc[peak_i:].copy()
    t0 = fit_df["Date"].iloc[0]
    t = (fit_df["Date"] - t0).dt.days.values.astype(float)
    q = fit_df["q"].values.astype(float)
    qi0 = float(q[0])
    Di0 = 0.001
    results = {}
    n = len(q)
    try:
        popt, _ = curve_fit(exp_decline, t, q,
                            p0=[qi0, Di0],
                            bounds=([qi0 * 0.3, 1e-7], [qi0 * 3, 10 / 365]),
                            maxfev=20000)
        q_fit = exp_decline(t, *popt)
        r2, rmse = _r2_rmse(q, q_fit)
        k = 2
        aic = n * np.log(np.sum((q - q_fit) ** 2) / n) + 2 * k
        results["Exponential"] = dict(
            qi=popt[0], Di_day=popt[1], Di_year=popt[1] * 365, b=0.0,
            r2=r2, rmse=rmse, AIC=round(aic, 1),
            t=t, q_actual=q, q_fitted=q_fit,
            dates=fit_df["Date"].values, peak_date=t0,
        )
    except Exception:
        pass
    try:
        popt, _ = curve_fit(harm_decline, t, q,
                            p0=[qi0, Di0],
                            bounds=([qi0 * 0.3, 1e-7], [qi0 * 3, 10 / 365]),
                            maxfev=20000)
        q_fit = harm_decline(t, *popt)
        r2, rmse = _r2_rmse(q, q_fit)
        k = 2
        aic = n * np.log(np.sum((q - q_fit) ** 2) / n) + 2 * k
        results["Harmonic"] = dict(
            qi=popt[0], Di_day=popt[1], Di_year=popt[1] * 365, b=1.0,
            r2=r2, rmse=rmse, AIC=round(aic, 1),
            t=t, q_actual=q, q_fitted=q_fit,
            dates=fit_df["Date"].values, peak_date=t0,
        )
    except Exception:
        pass
    try:
        popt, _ = curve_fit(hyp_decline, t, q,
                            p0=[qi0, Di0, 0.8],
                            bounds=([qi0 * 0.3, 1e-7, 0.01], [qi0 * 3, 10 / 365, 1.99]),
                            maxfev=50000)
        q_fit = hyp_decline(t, *popt)
        r2, rmse = _r2_rmse(q, q_fit)
        k = 3
        aic = n * np.log(np.sum((q - q_fit) ** 2) / n) + 2 * k
        results["Hyperbolic"] = dict(
            qi=popt[0], Di_day=popt[1], Di_year=popt[1] * 365, b=popt[2],
            r2=r2, rmse=rmse, AIC=round(aic, 1),
            t=t, q_actual=q, q_fitted=q_fit,
            dates=fit_df["Date"].values, peak_date=t0,
        )
    except Exception:
        pass
    return results


def best_model(results: dict) -> str:
    if not results:
        return "Hyperbolic"
    return max(results, key=lambda k: results[k]["r2"])


def calculate_eur(qi, Di_day, b, model, econ_limit_bbl,
                  horizon_years=10, peak_date=None, cum_to_date_bbl=0.0) -> dict:
    t_max = horizon_years * 365
    t_f = np.arange(0.0, float(t_max), 1.0)
    if model == "Exponential" or b < 0.01:
        q_f = exp_decline(t_f, qi, Di_day)
    elif model == "Harmonic" or abs(b - 1.0) < 0.01:
        q_f = harm_decline(t_f, qi, Di_day)
    else:
        q_f = hyp_decline(t_f, qi, Di_day, b)
    econ_idx = np.where(q_f <= econ_limit_bbl)[0]
    if len(econ_idx):
        cut = econ_idx[0]
        t_econ = float(t_f[cut])
        q_f[cut:] = econ_limit_bbl
    else:
        t_econ = float(t_max)
    cum_f = np.cumsum(q_f)
    eur_from_peak = float(cum_f[-1])
    eur_total = eur_from_peak + cum_to_date_bbl
    remaining = max(0.0, eur_from_peak)
    if peak_date is not None:
        peak_dt = pd.Timestamp(peak_date)
        dates_fore = [peak_dt + pd.Timedelta(days=int(tt)) for tt in t_f]
    else:
        dates_fore = list(t_f)
    return dict(
        eur_bbl=eur_total, eur_mmbbl=eur_total / 1e6,
        remaining_bbl=remaining, remaining_mmbbl=remaining / 1e6,
        cum_to_date_mmbbl=cum_to_date_bbl / 1e6,
        t_econ_days=t_econ, t_econ_years=round(t_econ / 365, 1),
        peak_rate=qi, t_forecast=t_f, q_forecast=q_f,
        cum_forecast=cum_f, dates_forecast=dates_fore,
        econ_limit=econ_limit_bbl,
    )
