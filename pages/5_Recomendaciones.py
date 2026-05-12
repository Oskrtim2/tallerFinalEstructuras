"""Página 5: Recomendaciones Personalizadas para Ahorrar."""
import streamlit as st
from utils.styles import inject_css, format_cop
from utils.analyzer import (
    get_kpis, spending_by_category, weekend_emotional_spending,
    ant_expenses, necessity_breakdown,
)
from utils.storage import load_user_profile, load_transactions

st.set_page_config(page_title="Recomendaciones", page_icon="💡", layout="wide")
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

st.markdown("# 💡 Recomendaciones Personalizadas")
st.markdown("Consejos basados en **tus datos reales** para mejorar tu salud financiera.")

kpis = get_kpis(df, salario)

# ─── Regla 50/30/20 ──────────────────────────────────────────────────────
st.markdown("### 📐 Regla 50/30/20 vs Tu Realidad")
st.markdown("La regla sugiere: **50%** necesidades, **30%** deseos, **20%** ahorro.")

nec = necessity_breakdown(df)
necesario = nec.get("Necesario", 0)
innecesario = nec.get("Innecesario", 0)
ahorro_real = max(0, kpis["total_ingresos"] - kpis["total_gastos"])
total_ing = kpis["total_ingresos"] if kpis["total_ingresos"] > 0 else 1

pct_nec = necesario / total_ing * 100
pct_inn = innecesario / total_ing * 100
pct_ahorro = ahorro_real / total_ing * 100

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("🏠 Necesidades", f"{pct_nec:.0f}%", delta=f"Meta: 50%")
    st.caption(format_cop(necesario))
    if pct_nec > 55:
        st.error("Estás gastando demasiado en necesidades.")
    else:
        st.success("¡Bien! Dentro del rango.")

with c2:
    st.metric("🎉 Deseos", f"{pct_inn:.0f}%", delta=f"Meta: 30%")
    st.caption(format_cop(innecesario))
    if pct_inn > 35:
        st.error("Reduce gastos innecesarios.")
    else:
        st.success("¡Controlado!")

with c3:
    st.metric("💰 Ahorro", f"{pct_ahorro:.0f}%", delta=f"Meta: 20%")
    st.caption(format_cop(ahorro_real))
    if pct_ahorro < 15:
        st.error("Intenta ahorrar más.")
    else:
        st.success("¡Excelente hábito de ahorro!")

st.markdown("---")

# ─── Tips personalizados ─────────────────────────────────────────────────
st.markdown("### 🎯 Tips Basados en tus Patrones")
tips = []

# Tip de fin de semana
we = weekend_emotional_spending(df)
if we["pct_aumento"] > 15:
    ahorro_potencial = (we["promedio_fin_semana"] - we["promedio_entre_semana"]) * 8
    tips.append({
        "emoji": "🎭",
        "titulo": "Controla los gastos de fin de semana",
        "desc": (
            f"Gastas un {we['pct_aumento']:.0f}% más los fines de semana. "
            f"Si lo reduces al nivel de entre semana, podrías ahorrar "
            f"**{format_cop(ahorro_potencial)}** al mes."
        ),
        "type": "alert",
    })

# Tip de gastos hormiga
ants = ant_expenses(df)
if ants["pct_del_total"] > 5:
    tips.append({
        "emoji": "🐜",
        "titulo": "Elimina los gastos hormiga",
        "desc": (
            f"Tus gastos pequeños representan el {ants['pct_del_total']}% "
            f"de tu gasto total ({format_cop(ants['total_hormiga'])}). "
            "Lleva un café de casa o evita snacks innecesarios."
        ),
        "type": "alert",
    })

# Tip por categoría más alta
cats = spending_by_category(df)
if len(cats) > 0:
    top_cat = cats.index[0]
    top_val = cats.iloc[0]
    n_months = kpis["n_meses"]
    monthly_top = top_val / n_months
    reduction = monthly_top * 0.2
    tips.append({
        "emoji": "📊",
        "titulo": f"Reduce {top_cat} un 20%",
        "desc": (
            f"Tu mayor gasto es **{top_cat}** con "
            f"{format_cop(monthly_top)}/mes. Si lo reduces un 20%, "
            f"ahorras **{format_cop(reduction)}** cada mes."
        ),
        "type": "info",
    })

# Tip de tasa de ahorro
if kpis["tasa_ahorro"] < 10:
    tips.append({
        "emoji": "🚨",
        "titulo": "Tu tasa de ahorro es muy baja",
        "desc": (
            f"Solo ahorras el {kpis['tasa_ahorro']}% de tus ingresos. "
            "Intenta automatizar un ahorro del 10% al recibir tu salario."
        ),
        "type": "alert",
    })
elif kpis["tasa_ahorro"] >= 20:
    tips.append({
        "emoji": "🏆",
        "titulo": "¡Excelente tasa de ahorro!",
        "desc": (
            f"Ahorras el {kpis['tasa_ahorro']}% de tus ingresos. "
            "Considera invertir parte en un CDT o fondo de inversión."
        ),
        "type": "success",
    })

for tip in tips:
    css_class = "alert-card" if tip["type"] == "alert" else (
        "success-card" if tip["type"] == "success" else "info-card"
    )
    st.markdown(
        f"""<div class="{css_class}">
        <span class="emoji">{tip['emoji']}</span>
        <strong>{tip['titulo']}</strong><br>
        {tip['desc']}
        </div>""", unsafe_allow_html=True,
    )

st.markdown("---")

# ─── Simulador de ahorro ─────────────────────────────────────────────────
st.markdown("### 🧮 Simulador: ¿Cuánto puedes ahorrar?")
st.markdown("Ajusta los porcentajes de reducción por categoría.")

if len(cats) > 0:
    total_ahorro = 0
    n_months = max(1, kpis["n_meses"])
    for cat in cats.index[:5]:
        monthly = cats[cat] / n_months
        pct = st.slider(f"Reducir **{cat}** ({format_cop(monthly)}/mes)",
                        0, 50, 10, key=f"slider_{cat}")
        saved = monthly * pct / 100
        total_ahorro += saved

    if total_ahorro > 0:
        st.markdown(
            f"""<div class="success-card">
            <span class="emoji">💰</span>
            <strong>Ahorro potencial mensual: {format_cop(total_ahorro)}</strong><br>
            Eso es <strong>{format_cop(total_ahorro * 12)}</strong> al año.
            ¡Podrías darte unas vacaciones!
            </div>""", unsafe_allow_html=True,
        )
