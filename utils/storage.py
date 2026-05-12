"""
Módulo de persistencia de datos.
Guarda perfil de usuario y transacciones en JSON para que el usuario
solo tenga que cargar datos una vez por mes.
"""
import json
import os
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_data")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def save_user_profile(profile: dict):
    """Guarda el perfil del usuario (nombre, salario, fecha)."""
    ensure_data_dir()
    path = os.path.join(DATA_DIR, "profile.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2, default=str)


def load_user_profile():
    """Carga el perfil del usuario guardado."""
    path = os.path.join(DATA_DIR, "profile.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_transactions(df: pd.DataFrame):
    """Guarda las transacciones del mes actual."""
    ensure_data_dir()
    path = os.path.join(DATA_DIR, "transactions.json")
    records = df.to_dict(orient="records")
    for r in records:
        for k, v in r.items():
            if isinstance(v, (pd.Timestamp, datetime)):
                r[k] = v.isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)


def load_transactions():
    """Carga las transacciones guardadas."""
    path = os.path.join(DATA_DIR, "transactions.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            records = json.load(f)
        if not records:
            return None
        df = pd.DataFrame(records)
        if "fecha" in df.columns:
            df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    return None


def data_exists():
    return os.path.exists(os.path.join(DATA_DIR, "transactions.json"))


def clear_all_data():
    """Elimina todos los datos guardados."""
    import shutil
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
