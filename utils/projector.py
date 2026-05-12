"""
Proyeccion de gastos futuros usando regresion lineal simple.
"""
import pandas as pd
import numpy as np


def project_next_month(df):
    expenses = df[df["tipo"] == "egreso"].copy()
    if len(expenses) == 0:
        return None

    expenses["mes"] = expenses["fecha"].dt.to_period("M")
    monthly = expenses.groupby("mes")["monto"].sum().sort_index()

    if len(monthly) < 2:
        return {
            "proyeccion_total": round(monthly.iloc[0]),
            "tendencia": "estable",
            "pct_cambio": 0,
            "historico": {str(k): round(v) for k, v in monthly.items()},
            "por_categoria": _project_by_category(expenses),
            "confianza_baja": round(monthly.iloc[0] * 0.85),
            "confianza_alta": round(monthly.iloc[0] * 1.15),
        }

    X = np.arange(len(monthly)).reshape(-1, 1).astype(float)
    y = monthly.values.astype(float)
    x_mean, y_mean = X.mean(), y.mean()
    num = ((X.flatten() - x_mean) * (y - y_mean)).sum()
    den = ((X.flatten() - x_mean) ** 2).sum()
    slope = num / den if den != 0 else 0
    intercept = y_mean - slope * x_mean

    next_x = len(monthly)
    projection = max(0, intercept + slope * next_x)
    std = y.std() if len(y) > 1 else y[0] * 0.15

    last_month = monthly.iloc[-1]
    pct_change = ((projection - last_month) / last_month * 100) if last_month > 0 else 0
    if pct_change > 5:
        trend = "subiendo"
    elif pct_change < -5:
        trend = "bajando"
    else:
        trend = "estable"

    return {
        "proyeccion_total": round(projection),
        "tendencia": trend,
        "pct_cambio": round(pct_change, 1),
        "historico": {str(k): round(v) for k, v in monthly.items()},
        "por_categoria": _project_by_category(expenses),
        "confianza_baja": round(max(0, projection - std)),
        "confianza_alta": round(projection + std),
    }


def _project_by_category(expenses):
    if "categoria" not in expenses.columns:
        return {}
    expenses = expenses.copy()
    expenses["mes"] = expenses["fecha"].dt.to_period("M")
    cat_monthly = expenses.groupby(["mes", "categoria"])["monto"].sum().unstack(fill_value=0)
    projections = {}
    for cat in cat_monthly.columns:
        vals = cat_monthly[cat].values.astype(float)
        if len(vals) >= 2:
            weights = np.arange(1, len(vals) + 1, dtype=float)
            projections[cat] = round(np.average(vals, weights=weights))
        else:
            projections[cat] = round(vals[0]) if len(vals) > 0 else 0
    return projections
