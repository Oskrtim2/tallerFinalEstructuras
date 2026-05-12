"""Página 3: Proyección de Gastos del Próximo Mes."""
import streamlit as st
import plotly.graph_objects as go
from utils.styles import inject_css, format_cop
from utils.projector import project_next_month
from utils.storage import load_user_profile, load_transactions

st.set_page_config(page_title="Proyecciones", page_icon="📈", layout="wide")
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
profile = st.session_state.get("profile", {})
salario = profile.get("salario", 0)

st.markdown("# 📈 Proyección de Gastos")
st.markdown("¿Cuánto vas a gastar el próximo mes? Aquí te lo decimos.")

proj = project_next_month(df)
if proj is None:
    st.info("No hay suficientes datos para proyectar.")
    st.stop()

# ─── KPIs de proyección ──────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("🔮 Proyección próximo mes", format_cop(proj["proyeccion_total"]))

trend_emoji = {"subiendo": "📈", "bajando": "📉", "estable": "➡️"}
c2.metric("📊 Tendencia", f"{trend_emoji.get(proj['tendencia'], '')} {proj['tendencia'].title()}",
          delta=f"{proj['pct_cambio']}%")

if salario > 0:
    pct_salario = proj["proyeccion_total"] / salario * 100
    c3.metric("💰 % del salario", f"{pct_salario:.0f}%",
              delta=f"Sobran {format_cop(max(0, salario - proj['proyeccion_total']))}")

# ─── Mensaje principal ───────────────────────────────────────────────────
st.markdown("---")
if proj["pct_cambio"] > 10:
    st.markdown(
        f"""<div class="alert-card">
        <span class="emoji">⚠️</span> <strong>¡Cuidado!</strong><br>
        Se proyecta que el próximo mes gastarás <strong>{format_cop(proj['proyeccion_total'])}</strong>,
        un <strong>{proj['pct_cambio']}% más</strong> que el mes pasado.
        Revisa tus patrones de gasto para evitar sorpresas.
        </div>""", unsafe_allow_html=True,
    )
elif proj["pct_cambio"] < -5:
    st.markdown(
        f"""<div class="success-card">
        <span class="emoji">🎉</span> <strong>¡Vas bien!</strong><br>
        Se proyecta que gastarás <strong>{format_cop(proj['proyeccion_total'])}</strong>,
        un <strong>{abs(proj['pct_cambio'])}% menos</strong> que el mes pasado. ¡Sigue así!
        </div>""", unsafe_allow_html=True,
    )
else:
    st.info(f"Se proyecta un gasto de **{format_cop(proj['proyeccion_total'])}**, similar al mes anterior.")

# ─── Gráfico histórico + proyección ──────────────────────────────────────
st.markdown("### 📊 Histórico + Proyección")
hist = proj["historico"]
months = list(hist.keys())
values = list(hist.values())

# Agregar proyección
proj_month = "Próximo mes"
all_months = months + [proj_month]
all_values = values + [proj["proyeccion_total"]]

fig = go.Figure()
# Histórico
fig.add_trace(go.Scatter(
    x=months, y=values, mode="lines+markers",
    name="Histórico", line=dict(color="#7C3AED", width=3),
    marker=dict(size=10, color="#7C3AED"),
))
# Proyección (línea punteada)
fig.add_trace(go.Scatter(
    x=[months[-1], proj_month], y=[values[-1], proj["proyeccion_total"]],
    mode="lines+markers", name="Proyección",
    line=dict(color="#3B82F6", width=3, dash="dash"),
    marker=dict(size=12, color="#3B82F6", symbol="diamond"),
))
# Banda de confianza
fig.add_trace(go.Scatter(
    x=[proj_month, proj_month], y=[proj["confianza_baja"], proj["confianza_alta"]],
    mode="lines", name="Rango confianza",
    line=dict(color="rgba(59,130,246,0.3)", width=15),
))

fig.update_layout(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"),
    margin=dict(t=20, b=20), height=400,
    xaxis_title="Mes", yaxis_title="Gasto Total (COP)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig, use_container_width=True)

# ─── Proyección por categoría ────────────────────────────────────────────
st.markdown("### 🏷️ Proyección por Categoría")
cat_proj = proj["por_categoria"]
if cat_proj:
    sorted_cats = sorted(cat_proj.items(), key=lambda x: x[1], reverse=True)
    cats = [c[0] for c in sorted_cats]
    vals = [c[1] for c in sorted_cats]

    fig2 = go.Figure(go.Bar(
        x=cats, y=vals,
        marker=dict(
            color=vals,
            colorscale=[[0, "#3B82F6"], [0.5, "#7C3AED"], [1, "#EF4444"]],
        ),
        text=[format_cop(v) for v in vals],
        textposition="outside",
    ))
    fig2.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"),
        margin=dict(t=20, b=20), height=400,
        yaxis=dict(showgrid=False, showticklabels=False),
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig2, use_container_width=True)