
import pandas as pd
import numpy as np


def get_expenses(df):
    
    return df[df["tipo"] == "egreso"].copy()


def get_income(df):
    
    return df[df["tipo"] == "ingreso"].copy()


def get_kpis(df, salary):
    """Calcula los KPIs principales."""
    expenses = get_expenses(df)
    income = get_income(df)
    total_income = income["monto"].sum() if len(income) > 0 else salary
    total_expenses = expenses["monto"].sum()
    balance = total_income - total_expenses
    n_months = max(1, df["fecha"].dt.to_period("M").nunique())
    avg_monthly_expense = total_expenses / n_months
    savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0

    return {
        "total_ingresos": total_income,
        "total_gastos": total_expenses,
        "balance": balance,
        "gasto_mensual_promedio": avg_monthly_expense,
        "tasa_ahorro": round(savings_rate, 1),
        "n_transacciones": len(expenses),
        "n_meses": n_months,
    }


def spending_by_category(df):
    """Gasto total por categoría, ordenado de mayor a menor."""
    expenses = get_expenses(df)
    result = expenses.groupby("categoria")["monto"].sum().sort_values(ascending=False)
    return result


def spending_by_day_of_week(df):
    expenses = get_expenses(df)
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    expenses = expenses.copy()
    expenses["dia_semana"] = expenses["fecha"].dt.dayofweek
    result = expenses.groupby("dia_semana")["monto"].mean().reindex(range(7), fill_value=0)
    result.index = dias
    return result


def weekend_emotional_spending(df):
    expenses = get_expenses(df)
    expenses = expenses.copy()
    expenses["es_finsemana"] = expenses["fecha"].dt.dayofweek >= 5

    weekday = expenses[~expenses["es_finsemana"]]
    weekend = expenses[expenses["es_finsemana"]]

    # Número de días de semana vs fin de semana en el dataset
    all_dates = pd.date_range(df["fecha"].min(), df["fecha"].max())
    n_weekdays = sum(1 for d in all_dates if d.dayofweek < 5) or 1
    n_weekends = sum(1 for d in all_dates if d.dayofweek >= 5) or 1

    avg_weekday = weekday["monto"].sum() / n_weekdays
    avg_weekend = weekend["monto"].sum() / n_weekends

    pct_increase = ((avg_weekend - avg_weekday) / avg_weekday * 100) if avg_weekday > 0 else 0

    # Categorías que más suben en fin de semana
    cat_weekday = weekday.groupby("categoria")["monto"].sum() / n_weekdays
    cat_weekend = weekend.groupby("categoria")["monto"].sum() / n_weekends
    cat_diff = ((cat_weekend - cat_weekday) / cat_weekday * 100).dropna().sort_values(ascending=False)

    return {
        "promedio_entre_semana": round(avg_weekday),
        "promedio_fin_semana": round(avg_weekend),
        "pct_aumento": round(pct_increase, 1),
        "categorias_emocionales": cat_diff.head(3).to_dict(),
    }


def ant_expenses(df, threshold_pct=0.005):
    """Detecta gastos hormiga: transacciones pequeñas y frecuentes
    que individualmente parecen insignificantes pero suman mucho.
    """
    expenses = get_expenses(df)
    if len(expenses) == 0:
        return {"gastos_hormiga": [], "total_hormiga": 0, "pct_del_total": 0}

    total = expenses["monto"].sum()
    threshold = total * threshold_pct  # Menos del 0.5% del total cada una

    small = expenses[expenses["monto"] <= threshold].copy()
    if len(small) == 0:
        # Use median-based threshold
        median = expenses["monto"].median()
        small = expenses[expenses["monto"] <= median * 0.3].copy()

    total_hormiga = small["monto"].sum()
    pct = (total_hormiga / total * 100) if total > 0 else 0

    # Agrupar por descripción
    top = (
        small.groupby("descripcion")
        .agg(veces=("monto", "count"), total=("monto", "sum"), promedio=("monto", "mean"))
        .sort_values("total", ascending=False)
        .head(5)
    )

    return {
        "gastos_hormiga": top.reset_index().to_dict("records"),
        "total_hormiga": round(total_hormiga),
        "pct_del_total": round(pct, 1),
    }


def silent_category(df):
    expenses = get_expenses(df)
    if len(expenses) == 0:
        return None

    cat_stats = expenses.groupby("categoria").agg(
        total=("monto", "sum"),
        promedio=("monto", "mean"),
        count=("monto", "count"),
    )
    # Score: alto total * bajo promedio * alto count = gasto silencioso
    cat_stats["score"] = cat_stats["total"] * cat_stats["count"] / (cat_stats["promedio"] + 1)
    winner = cat_stats.sort_values("score", ascending=False).iloc[0]
    winner_name = cat_stats.sort_values("score", ascending=False).index[0]

    return {
        "categoria": winner_name,
        "total": round(winner["total"]),
        "n_transacciones": int(winner["count"]),
        "promedio_por_transaccion": round(winner["promedio"]),
    }


def monthly_trend(df):
    expenses = get_expenses(df)
    expenses = expenses.copy()
    expenses["mes"] = expenses["fecha"].dt.to_period("M").astype(str)
    monthly = expenses.groupby("mes")["monto"].sum().sort_index()
    return monthly


def daily_spending(df):
    expenses = get_expenses(df)
    daily = expenses.groupby(expenses["fecha"].dt.date)["monto"].sum()
    daily.index = pd.to_datetime(daily.index)
    return daily


def necessity_breakdown(df):
    expenses = get_expenses(df)
    if "tipo_gasto" not in expenses.columns:
        return {}
    return expenses.groupby("tipo_gasto")["monto"].sum().to_dict()
