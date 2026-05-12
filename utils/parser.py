"""
Parser de extractos bancarios (CSV/PDF) y generador de datos de ejemplo.
Genera transacciones realistas colombianas proporcionales al salario del usuario.
"""
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from utils.categorizer import categorize_dataframe


# ─── Comercios realistas colombianos ─────────────────────────────────────────
MERCHANTS = {
    "Alimentacion": [
        ("Supermercado Exito - Compra", 0.025, 0.07),
        ("Tienda D1 - Mercado", 0.005, 0.02),
        ("Restaurante El Corral", 0.008, 0.02),
        ("Rappi - Domicilio comida", 0.007, 0.02),
        ("Panaderia La Especial", 0.002, 0.005),
        ("Cafe Juan Valdez", 0.002, 0.006),
        ("Supermercado Ara - Compra", 0.007, 0.025),
        ("Fruver La Cosecha", 0.003, 0.012),
        ("Pizza Dominos - Domicilio", 0.008, 0.018),
        ("Almuerzo corriente cafeteria", 0.003, 0.005),
    ],
    "Vivienda": [
        ("Pago Arriendo Apartamento", 0.28, 0.35),
        ("Servicios Agua - Acueducto", 0.01, 0.02),
        ("Servicios Luz - Codensa", 0.013, 0.03),
        ("Servicios Gas Natural", 0.005, 0.012),
        ("Internet Claro Hogar", 0.02, 0.04),
        ("Plan Celular Movistar", 0.012, 0.025),
    ],
    "Transporte": [
        ("Uber - Viaje", 0.003, 0.01),
        ("Tanqueo Gasolina estacion", 0.02, 0.05),
        ("Recarga SITP Transmilenio", 0.003, 0.008),
        ("Parqueadero centro", 0.002, 0.005),
        ("InDriver - Viaje", 0.003, 0.008),
    ],
    "Entretenimiento": [
        ("Netflix suscripcion mensual", 0.01, 0.015),
        ("Spotify Premium mensual", 0.005, 0.008),
        ("Bar La Villa - Cervezas", 0.008, 0.025),
        ("Cine Colombia - Boletas", 0.006, 0.015),
        ("Steam - Videojuego", 0.01, 0.03),
        ("Disney Plus suscripcion", 0.005, 0.01),
    ],
    "Ropa y Accesorios": [
        ("Falabella - Ropa", 0.02, 0.06),
        ("Koaj - Camisa", 0.01, 0.03),
        ("Tennis - Zapatos tenis", 0.015, 0.04),
        ("Centro Comercial - Accesorios", 0.005, 0.02),
    ],
    "Salud": [
        ("Drogueria Cruz Verde - Farmacia", 0.003, 0.015),
        ("Consulta Medica EPS", 0.005, 0.015),
        ("Gimnasio Smart Fit mensual", 0.015, 0.03),
    ],
    "Educacion": [
        ("Platzi - Suscripcion cursos", 0.008, 0.015),
        ("Papeleria - Copias e impresion", 0.001, 0.004),
        ("Libro Amazon - Educacion", 0.005, 0.02),
    ],
}

# Frecuencia mensual por categoría (min, max transacciones por mes)
FREQUENCY = {
    "Alimentacion": (15, 30),
    "Vivienda": (5, 7),
    "Transporte": (6, 15),
    "Entretenimiento": (3, 8),
    "Ropa y Accesorios": (0, 3),
    "Salud": (1, 3),
    "Educacion": (1, 3),
}


def generate_sample_data(salary: float, months: int = 3):
    """Genera datos de ejemplo realistas basados en el salario."""
    random.seed(42)
    np.random.seed(42)
    transactions = []
    today = datetime.now()
    start_date = today - timedelta(days=30 * months)

    for m in range(months):
        month_start = start_date + timedelta(days=30 * m)

        # Ingreso: salario el día 30 (o último día del mes)
        pay_day = month_start.replace(day=28)
        transactions.append({
            "fecha": pay_day,
            "descripcion": "Nomina - Salario mensual",
            "monto": salary,
            "tipo": "ingreso",
        })

        # Generar gastos por categoría
        for cat, merchants in MERCHANTS.items():
            freq_min, freq_max = FREQUENCY.get(cat, (1, 3))
            n_transactions = random.randint(freq_min, freq_max)

            for _ in range(n_transactions):
                merchant = random.choice(merchants)
                name, pct_min, pct_max = merchant
                amount = round(random.uniform(salary * pct_min, salary * pct_max), -2)
                amount = max(amount, 2000)

                # Día aleatorio del mes, con más peso en fines de semana para entretenimiento
                day = random.randint(1, 28)
                tx_date = month_start.replace(day=day)

                if cat == "Entretenimiento":
                    # 70% de entretenimiento cae en fin de semana
                    if random.random() < 0.7:
                        while tx_date.weekday() < 5:
                            day = random.randint(1, 28)
                            tx_date = month_start.replace(day=day)

                transactions.append({
                    "fecha": tx_date,
                    "descripcion": name,
                    "monto": amount,
                    "tipo": "egreso",
                })

        # Gastos hormiga diarios (café, snacks)
        for day in range(1, 29):
            tx_date = month_start.replace(day=day)
            if random.random() < 0.4:
                transactions.append({
                    "fecha": tx_date,
                    "descripcion": random.choice([
                        "Cafe Juan Valdez", "Tienda - Snack",
                        "Maquina expendedora", "Cafe oficina",
                    ]),
                    "monto": round(random.uniform(salary * 0.001, salary * 0.004), -2),
                    "tipo": "egreso",
                })

    df = pd.DataFrame(transactions)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)
    df = categorize_dataframe(df)
    return df


def parse_csv(uploaded_file):
    """Parsea un archivo CSV de extracto bancario."""
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="latin-1")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Intentar mapear columnas comunes
    col_map = {}
    for col in df.columns:
        cl = col.lower()
        if any(k in cl for k in ["fecha", "date"]):
            col_map["fecha"] = col
        elif any(k in cl for k in ["desc", "concepto", "detalle", "refer"]):
            col_map["descripcion"] = col
        elif any(k in cl for k in ["monto", "valor", "amount", "debito", "total"]):
            col_map["monto"] = col
        elif any(k in cl for k in ["tipo", "type", "naturaleza"]):
            col_map["tipo"] = col

    if col_map:
        df = df.rename(columns={v: k for k, v in col_map.items()})

    # Asegurar columnas mínimas
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True, errors="coerce")
    if "monto" in df.columns:
        df["monto"] = pd.to_numeric(
            df["monto"].astype(str).str.replace(r"[^\d.\-]", "", regex=True),
            errors="coerce",
        )
    if "tipo" not in df.columns:
        if "monto" in df.columns:
            df["tipo"] = df["monto"].apply(lambda x: "ingreso" if x > 0 else "egreso")
            df["monto"] = df["monto"].abs()
    if "descripcion" not in df.columns:
        for col in df.columns:
            if df[col].dtype == object and col != "tipo":
                df["descripcion"] = df[col]
                break

    df = categorize_dataframe(df)
    return df


def parse_pdf(uploaded_file):
    """Parsea un archivo PDF de extracto bancario usando pdfplumber."""
    if pdfplumber is None:
        return None

    all_data = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if len(table) > 1:
                    header = [str(c).strip().lower() if c else f"col_{i}"
                              for i, c in enumerate(table[0])]
                    for row in table[1:]:
                        if row and any(cell for cell in row):
                            record = {}
                            for i, cell in enumerate(row):
                                if i < len(header):
                                    record[header[i]] = cell
                            all_data.append(record)

    if not all_data:
        return None

    df = pd.DataFrame(all_data)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Misma normalización que CSV
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True, errors="coerce")
    if "monto" in df.columns or "valor" in df.columns:
        mcol = "monto" if "monto" in df.columns else "valor"
        df["monto"] = pd.to_numeric(
            df[mcol].astype(str).str.replace(r"[^\d.\-]", "", regex=True),
            errors="coerce",
        )
    if "tipo" not in df.columns and "monto" in df.columns:
        df["tipo"] = df["monto"].apply(lambda x: "ingreso" if x > 0 else "egreso")
        df["monto"] = df["monto"].abs()

    df = categorize_dataframe(df)
    return df
