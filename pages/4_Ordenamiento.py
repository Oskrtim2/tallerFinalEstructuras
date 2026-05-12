"""Página 4: Visualización del Ordenamiento Automático."""
import streamlit as st
import plotly.graph_objects as go
import time
from utils.styles import inject_css, format_cop
from utils.sorting import merge_sort, quick_sort
from utils.storage import load_user_profile, load_transactions

st.set_page_config(page_title="Ordenamiento", page_icon="🔃", layout="wide")
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
expenses = df[df["tipo"] == "egreso"].copy()

st.markdown("# 🔃 Ordenamiento Automático")
st.markdown(
    "Tus gastos organizados **de mayor a menor** usando algoritmos de "
    "ordenamiento implementados desde cero (sin usar `.sort()`)."
)

# ─── Controles ────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    algorithm = st.selectbox("Algoritmo", ["MergeSort", "QuickSort"])
with col2:
    n_items = st.slider("Transacciones a ordenar", 5, min(50, len(expenses)), 15)
with col3:
    order = st.radio("Orden", ["Mayor a menor", "Menor a mayor"], horizontal=True)

reverse = order == "Mayor a menor"
sample = expenses.head(n_items)
items = [{"desc": row["descripcion"], "monto": row["monto"],
          "cat": row.get("categoria", "")}
         for _, row in sample.iterrows()]

# ─── Ejecutar ordenamiento ────────────────────────────────────────────────
if st.button("▶️ Ejecutar Ordenamiento", type="primary", use_container_width=True):
    sort_fn = merge_sort if algorithm == "MergeSort" else quick_sort
    sorted_items, steps = sort_fn(items, key="monto", reverse=reverse)

    st.markdown(f"### 📊 Proceso de {algorithm} ({len(steps)} pasos)")

    # Animación paso a paso
    chart_placeholder = st.empty()
    progress = st.progress(0)
    status = st.empty()

    for i, step_values in enumerate(steps):
        progress.progress((i + 1) / len(steps))
        status.markdown(f"**Paso {i + 1} de {len(steps)}**")

        colors = []
        for v in step_values:
            if v == max(step_values):
                colors.append("#EF4444")
            elif v == min(step_values):
                colors.append("#10B981")
            else:
                colors.append("#7C3AED")

        fig = go.Figure(go.Bar(
            x=list(range(len(step_values))),
            y=step_values,
            marker_color=colors,
            text=[format_cop(v) for v in step_values],
            textposition="outside",
            textfont=dict(size=9),
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            margin=dict(t=30, b=20, l=40, r=20),
            height=350,
            xaxis=dict(showticklabels=False),
            yaxis=dict(showgrid=False),
            title=dict(text=f"Paso {i+1}: {algorithm}", font=dict(size=14)),
        )
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(0.3)

    progress.progress(1.0)
    status.markdown("**✅ Ordenamiento completado**")

    # ─── Resultado final ──────────────────────────────────────────────────
    st.markdown("### ✅ Resultado Final: Gastos Ordenados")
    st.markdown(
        f"""<div class="info-card">
        <h4>Algoritmo: {algorithm}</h4>
        <p>Se ordenaron <strong>{len(sorted_items)}</strong> transacciones en
        <strong>{len(steps)} pasos</strong> de {'mayor a menor' if reverse else 'menor a mayor'}.</p>
        </div>""", unsafe_allow_html=True,
    )

    for rank, item in enumerate(sorted_items, 1):
        color = "#EF4444" if rank <= 3 else "#7C3AED" if rank <= 7 else "#6B7280"
        st.markdown(
            f"**{rank}.** {item['desc']} — "
            f"<span style='color:{color};font-weight:700'>"
            f"{format_cop(item['monto'])}</span> "
            f"({item['cat']})",
            unsafe_allow_html=True,
        )

else:
    # Mostrar datos sin ordenar
    st.markdown("### 📋 Datos actuales (sin ordenar)")
    st.dataframe(
        sample[["fecha", "descripcion", "monto", "categoria"]].reset_index(drop=True),
        use_container_width=True, hide_index=True,
        column_config={
            "monto": st.column_config.NumberColumn("Monto", format="$%d"),
        },
    )
    st.info("👆 Presiona el botón para ver el algoritmo en acción.")
