"""Estilos CSS premium para el dashboard."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* KPI Cards glassmorphism */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(59,130,246,0.10) 100%);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 16px;
    padding: 16px 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(124,58,237,0.3);
}
div[data-testid="metric-container"] label {
    color: #a78bfa !important;
    font-weight: 500;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-weight: 700;
    font-size: 1.8rem;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.85rem;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117 0%, #1A1F2E 100%);
    border-right: 1px solid rgba(124,58,237,0.15);
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem;
}

/* Headers */
h1 {
    background: linear-gradient(90deg, #7C3AED, #3B82F6, #06B6D4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}
h2, h3 { color: #c4b5fd !important; font-weight: 600 !important; }

/* Alert boxes */
div.stAlert {
    border-radius: 12px;
    border: 1px solid rgba(124,58,237,0.2);
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(124,58,237,0.15);
}

/* Upload widget */
div[data-testid="stFileUploader"] {
    border-radius: 16px;
}

/* Buttons */
button[kind="primary"] {
    background: linear-gradient(90deg, #7C3AED, #3B82F6) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
button[kind="primary"]:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
}

/* Custom info card */
.info-card {
    background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(59,130,246,0.08));
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    backdrop-filter: blur(10px);
}
.info-card h4 {
    color: #a78bfa;
    margin-top: 0;
}
.info-card .big-number {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #7C3AED, #3B82F6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Alert card */
.alert-card {
    background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(220,38,38,0.05));
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
}
.alert-card .emoji { font-size: 1.5rem; }

/* Success card */
.success-card {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(5,150,105,0.05));
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
}
</style>
"""


def inject_css():
    """Inyecta CSS personalizado en la página."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def format_cop(value):
    """Formatea un número como pesos colombianos."""
    if value >= 0:
        return f"${value:,.0f}".replace(",", ".")
    return f"-${abs(value):,.0f}".replace(",", ".")
