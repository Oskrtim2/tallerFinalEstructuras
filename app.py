"""
Dashboard de Salud Financiera Personal con Patrones de Comportamiento
Página principal: Onboarding + carga de datos.
"""
import streamlit as st
from utils.styles import inject_css, format_cop
from utils.storage import (
    save_user_profile, load_user_profile,
    save_transactions, load_transactions, clear_all_data,
)
from utils.parser import parse_csv, parse_pdf, generate_sample_data

st.set_page_config(
    page_title="Salud Financiera - Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ─── Cargar datos persistidos ────────────────────────────────────────────────
if "profile" not in st.session_state:
    saved = load_user_profile()
    if saved:
        st.session_state["profile"] = saved

if "transactions" not in st.session_state:
    saved_tx = load_transactions()
    if saved_tx is not None:
        st.session_state["transactions"] = saved_tx

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💰 Salud Financiera")
    st.markdown("---")
    if "profile" in st.session_state:
        p = st.session_state["profile"]
        st.markdown(f"👤 **{p.get('nombre', 'Usuario')}**")
        st.markdown(f"💵 Salario: **{format_cop(p.get('salario', 0))}**")
        st.markdown("---")
    if st.button("🗑️ Reiniciar todo", use_container_width=True):
        clear_all_data()
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ─── Si no hay perfil → Onboarding ──────────────────────────────────────────
if "profile" not in st.session_state:
    st.markdown("# 🏦 Bienvenido a tu Dashboard Financiero")
    st.markdown(
        """
        <div class="info-card">
        <h4>¿Qué hace esta app?</h4>
        <p>Analiza tus gastos, detecta patrones de comportamiento, organiza
        tus transacciones de mayor a menor, y te dice cuánto vas a gastar
        el próximo mes. ¡Todo automático!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## 📝 Configuración inicial")
    st.markdown("Solo necesitas hacer esto **una vez**. Tus datos se guardarán automáticamente.")

    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input(
                "👤 Tu nombre",
                placeholder="Ej: Carlos Martínez",
            )
        with col2:
            salario = st.number_input(
                "💵 Tu salario mensual (COP)",
                min_value=0,
                max_value=100_000_000,
                value=2_500_000,
                step=100_000,
                format="%d",
            )
        submitted = st.form_submit_button("✅ Guardar y continuar", use_container_width=True)

    if submitted and nombre and salario > 0:
        profile = {
            "nombre": nombre,
            "salario": salario,
        }
        save_user_profile(profile)
        st.session_state["profile"] = profile
        st.rerun()
    elif submitted:
        st.error("Por favor ingresa tu nombre y un salario válido.")

    st.stop()

# ─── Perfil existe → Carga de datos ─────────────────────────────────────────
profile = st.session_state["profile"]
salario = profile.get("salario", 0)

st.markdown(f"# 👋 ¡Hola, {profile.get('nombre', 'Usuario')}!")

if "transactions" in st.session_state and st.session_state["transactions"] is not None:
    df = st.session_state["transactions"]
    n = len(df)
    gastos = df[df["tipo"] == "egreso"]["monto"].sum()

    st.markdown(
        f"""
        <div class="success-card">
        <span class="emoji">✅</span> <strong>Datos cargados correctamente</strong><br>
        Tienes <strong>{n} transacciones</strong> registradas con un total de
        gastos de <strong>{format_cop(gastos)}</strong>.<br><br>
        👈 Usa el menú lateral para explorar tu dashboard.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📋 Vista rápida de transacciones")
    st.dataframe(
        df[["fecha", "descripcion", "monto", "tipo", "categoria", "tipo_gasto"]]
        .sort_values("monto", ascending=False)
        .head(10),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.markdown("### 🔄 ¿Quieres actualizar tus datos?")

# ─── Sección de carga / generación de datos ──────────────────────────────────
tab1, tab2 = st.tabs(["📄 Subir extracto (CSV/PDF)", "🎲 Generar datos de ejemplo"])

with tab1:
    st.markdown("Sube tu extracto bancario. Solo necesitas hacerlo **una vez por mes**.")
    uploaded = st.file_uploader(
        "Arrastra tu archivo aquí",
        type=["csv", "pdf"],
        help="Formatos soportados: CSV, PDF de extractos bancarios.",
    )
    if uploaded:
        with st.spinner("Procesando archivo..."):
            if uploaded.name.lower().endswith(".csv"):
                df = parse_csv(uploaded)
            else:
                df = parse_pdf(uploaded)

        if df is not None and len(df) > 0:
            save_transactions(df)
            st.session_state["transactions"] = df
            st.success(f"✅ Se cargaron {len(df)} transacciones correctamente.")
            st.rerun()
        else:
            st.error("No se pudieron extraer datos del archivo. Verifica el formato.")

with tab2:
    st.markdown(
        f"Genera datos realistas basados en tu salario de **{format_cop(salario)}** "
        "para probar todas las funciones del dashboard."
    )
    meses = st.slider("¿Cuántos meses de historial generar?", 1, 6, 3)
    if st.button("🎲 Generar datos de ejemplo", type="primary", use_container_width=True):
        with st.spinner("Generando transacciones realistas..."):
            df = generate_sample_data(salario, months=meses)
            save_transactions(df)
            st.session_state["transactions"] = df
        st.success(f"✅ Se generaron {len(df)} transacciones para {meses} meses.")
        st.rerun()
