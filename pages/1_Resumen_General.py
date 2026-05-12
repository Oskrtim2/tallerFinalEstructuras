"""Página 1: Resumen General con KPIs y gráficos principales."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.styles import inject_css, format_cop
from utils.analyzer import get_kpis, spending_by_category, daily_spending, necessity_breakdown
from utils.storage import load_user_profile, load_transactions

st.set_page_config(page_title="Resumen General", page_icon="📊", layout="wide")
inject_css()

# Cargar datos
if "profile" not in st.session_state:
    p = load_user_profile()
    if p:
        st.session_state["profile"] = p
if "transactions" not in st.session_state:
    tx = load_transactions()
    if tx is not None:
        st.session_state["transactions"] = tx

if "transactions" not in st.session_state or st.session_state["transactions"] is None:
    st.warning("⚠️ No hay datos cargados. Ve a la página principal para subir tu extracto.")
    st.stop()

df = st.session_state["transactions"]
profile = st.session_state.get("profile", {})
salario = profile.get("salario", 0)

st.markdown("# 📊 Resumen General")

# ─── KPIs ─────────────────────────────────────────────────────────────────
kpis = get_kpis(df, salario)
c1, c2, c3, c4 = st.columns(4)
c1.metric("💵 Ingresos Totales", format_cop(kpis["total_ingresos"]))
c2.metric("🔴 Gastos Totales", format_cop(kpis["total_gastos"]))
c3.metric("📊 Balance", format_cop(kpis["balance"]),
          delta=f"{kpis['tasa_ahorro']}% ahorro")
c4.metric("📅 Gasto Mensual Prom.", format_cop(kpis["gasto_mensual_promedio"]),
          delta=f"{kpis['n_transacciones']} transacciones")

st.markdown("---")

# ─── Gráficos ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### 🍩 Gastos por Categoría")
    cat_data = spending_by_category(df)
    if len(cat_data) > 0:
        fig = px.pie(
            names=cat_data.index,
            values=cat_data.values,
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Purp_r,
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", size=13),
            legend=dict(font=dict(size=11)),
            margin=dict(t=20, b=20),
            height=380,
        )
        fig.update_traces(textinfo="label+percent", textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### ⚖️ Necesario vs Innecesario")
    nec = necessity_breakdown(df)
    if nec:
        labels = list(nec.keys())
        values = list(nec.values())
        colors = {"Necesario": "#7C3AED", "Innecesario": "#EF4444", "Otros": "#6B7280"}
        fig2 = go.Figure(go.Bar(
            x=labels, y=values,
            marker_color=[colors.get(l, "#6B7280") for l in labels],
            text=[format_cop(v) for v in values],
            textposition="outside",
        ))
        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            showlegend=False,
            margin=dict(t=20, b=20),
            height=380,
            yaxis=dict(showgrid=False, showticklabels=False),
        )
        st.plotly_chart(fig2, use_container_width=True)

# ─── Timeline diario ──────────────────────────────────────────────────────
st.markdown("### 📈 Gastos Diarios")
daily = daily_spending(df)
if len(daily) > 0:
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=daily.index, y=daily.values,
        fill="tozeroy",
        fillcolor="rgba(124,58,237,0.15)",
        line=dict(color="#7C3AED", width=2),
        mode="lines",
    ))
    # Línea promedio
    avg = daily.mean()
    fig3.add_hline(y=avg, line_dash="dash", line_color="#3B82F6",
                   annotation_text=f"Promedio: {format_cop(avg)}",
                   annotation_font_color="#3B82F6")
    fig3.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        margin=dict(t=20, b=20, l=40, r=20),
        height=320,
        xaxis_title="Fecha",
        yaxis_title="Gasto (COP)",
    )
    st.plotly_chart(fig3, use_container_width=True)

# ─── Top gastos ───────────────────────────────────────────────────────────
st.markdown("### 🔝 Top 10 Gastos (Mayor a Menor)")
expenses = df[df["tipo"] == "egreso"].sort_values("monto", ascending=False).head(10)
st.dataframe(
    expenses[["fecha", "descripcion", "monto", "categoria", "tipo_gasto"]].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    column_config={
        "fecha": st.column_config.DateColumn("Fecha"),
        "monto": st.column_config.NumberColumn("Monto", format="$%d"),
        "descripcion": "Descripción",
        "categoria": "Categoría",
        "tipo_gasto": "Tipo",
    },
)