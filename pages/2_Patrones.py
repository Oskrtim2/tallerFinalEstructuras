"""Página 2: Detección de Patrones de Comportamiento."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.styles import inject_css, format_cop
from utils.analyzer import (
    spending_by_day_of_week, weekend_emotional_spending,
    ant_expenses, silent_category, monthly_trend,
)
from utils.storage import load_user_profile, load_transactions

st.set_page_config(page_title="Patrones", page_icon="🔍", layout="wide")
inject_css()

if "profile" not in st.session_state:
    p = load_user_profile()
    if p:
        st.session_state["profile"] = p
if "transactions" not in st.session_state:
    tx = load_transactions()
    if tx is not None:
        st.session_state["transactions"] = tx

if "transactions" not in st.session_state or st.session_state["transactions"] is None:
    st.warning("⚠️ No hay datos. Ve a la página principal.")
    st.stop()

df = st.session_state["transactions"]
st.markdown("# 🔍 Patrones de Comportamiento")
st.markdown("Descubre cómo y cuándo gastas tu dinero sin darte cuenta.")

# ─── Gasto por día de la semana ───────────────────────────────────────────
st.markdown("### 📅 ¿Qué día gastas más?")
dow = spending_by_day_of_week(df)
colors = ["#6366F1"] * 5 + ["#EF4444", "#EF4444"]  # Fines de semana en rojo
fig1 = go.Figure(go.Bar(
    x=dow.index, y=dow.values,
    marker_color=colors,
    text=[format_cop(v) for v in dow.values],
    textposition="outside",
))
max_day = dow.idxmax()
fig1.update_layout(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"),
    margin=dict(t=30, b=20), height=350,
    yaxis=dict(showgrid=False, showticklabels=False),
    annotations=[dict(
        x=max_day, y=dow.max(), text="⬆️ DÍA PICO",
        showarrow=True, arrowhead=2, arrowcolor="#EF4444",
        font=dict(color="#EF4444", size=14, family="Inter"),
    )],
)
st.plotly_chart(fig1, use_container_width=True)

# ─── Gastos emocionales de fin de semana ──────────────────────────────────
st.markdown("### 🎭 Gastos Emocionales de Fin de Semana")
we = weekend_emotional_spending(df)
c1, c2, c3 = st.columns(3)
c1.metric("Lunes-Viernes (prom/día)", format_cop(we["promedio_entre_semana"]))
c2.metric("Sábado-Domingo (prom/día)", format_cop(we["promedio_fin_semana"]))
delta_color = "inverse" if we["pct_aumento"] > 0 else "normal"
c3.metric("Aumento fin de semana", f"{we['pct_aumento']}%", delta_color=delta_color)

if we["pct_aumento"] > 15:
    st.markdown(
        f"""<div class="alert-card">
        <span class="emoji">⚠️</span> <strong>¡Alerta de gasto emocional!</strong><br>
        Gastas un <strong>{we['pct_aumento']}% más</strong> los fines de semana.
        Esto puede indicar compras impulsivas o gastos emocionales.
        </div>""", unsafe_allow_html=True,
    )

if we["categorias_emocionales"]:
    st.markdown("**Categorías que más suben en fin de semana:**")
    for cat, pct in we["categorias_emocionales"].items():
        if pct > 0:
            st.markdown(f"- **{cat}**: +{pct:.0f}% más que entre semana")

st.markdown("---")

# ─── Gastos hormiga ──────────────────────────────────────────────────────
st.markdown("### 🐜 Gastos Hormiga")
st.markdown("Pequeños gastos que parecen nada pero suman mucho.")
ants = ant_expenses(df)

c1, c2 = st.columns(2)
c1.metric("Total gastos hormiga", format_cop(ants["total_hormiga"]))
c2.metric("% del gasto total", f"{ants['pct_del_total']}%")

if ants["gastos_hormiga"]:
    st.markdown("**Top gastos hormiga:**")
    for item in ants["gastos_hormiga"]:
        st.markdown(
            f"- 🐜 **{item['descripcion']}** — "
            f"{int(item['veces'])} veces, total: {format_cop(item['total'])}, "
            f"promedio: {format_cop(item['promedio'])}"
        )

st.markdown("---")

# ─── Categoría silenciosa ────────────────────────────────────────────────
st.markdown("### 🤫 Categoría Silenciosa")
st.markdown("La categoría donde más se te va la plata sin darte cuenta.")
sc = silent_category(df)
if sc:
    st.markdown(
        f"""<div class="info-card">
        <h4>🤫 {sc['categoria']}</h4>
        <p class="big-number">{format_cop(sc['total'])}</p>
        <p>En <strong>{sc['n_transacciones']} transacciones</strong> con un
        promedio de <strong>{format_cop(sc['promedio_por_transaccion'])}</strong> cada una.
        Son tantas transacciones pequeñas que no te das cuenta cuánto suman.</p>
        </div>""", unsafe_allow_html=True,
    )

st.markdown("---")

# ─── Tendencia mensual ──────────────────────────────────────────────────
st.markdown("### 📉 Tendencia Mensual")
mt = monthly_trend(df)
if len(mt) > 0:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=[str(x) for x in mt.index], y=mt.values,
        mode="lines+markers+text",
        line=dict(color="#7C3AED", width=3),
        marker=dict(size=12, color="#7C3AED", line=dict(width=2, color="#fff")),
        text=[format_cop(v) for v in mt.values],
        textposition="top center", textfont=dict(size=12),
    ))
    fig2.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"),
        margin=dict(t=40, b=20), height=350,
        xaxis_title="Mes", yaxis_title="Gasto Total (COP)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    if len(mt) >= 2:
        change = ((mt.iloc[-1] - mt.iloc[-2]) / mt.iloc[-2] * 100)
        if change > 0:
            st.error(f"📈 Tu gasto subió un **{change:.1f}%** respecto al mes anterior.")
        else:
            st.success(f"📉 Tu gasto bajó un **{abs(change):.1f}%** respecto al mes anterior. ¡Bien!")