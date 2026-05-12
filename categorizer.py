"""
Categorizador automático de transacciones bancarias.
Clasifica gastos por categoría y necesidad usando palabras clave
en las descripciones de los movimientos.
"""

CATEGORIES = {
    "Alimentacion": {
        "keywords": [
            "supermercado", "exito", "jumbo", "d1", "ara", "olimpica", "carulla",
            "restaurante", "comida", "almuerzo", "desayuno", "cena", "rappi",
            "ifood", "domicilio", "panaderia", "fruver", "carniceria", "tienda",
            "mercado", "pollo", "pizza", "hamburguesa", "sushi", "cafe", "cafeteria",
            "corral", "mcdonalds", "subway", "crepes", "wok", "juan valdez",
        ],
        "emoji": "🍽️",
        "necesario": True,
    },
    "Vivienda": {
        "keywords": [
            "arriendo", "alquiler", "administracion", "agua", "acueducto", "luz",
            "energia", "gas natural", "internet", "telefono", "celular", "claro",
            "movistar", "tigo", "etb", "epm", "codensa", "servicio publico",
        ],
        "emoji": "🏠",
        "necesario": True,
    },
    "Transporte": {
        "keywords": [
            "uber", "didi", "beat", "indriver", "gasolina", "tanqueo", "peaje",
            "parqueadero", "bus", "transmilenio", "mio", "sitp", "taxi", "metro",
            "soat", "tecnicomecanica", "vehiculo",
        ],
        "emoji": "🚗",
        "necesario": True,
    },
    "Entretenimiento": {
        "keywords": [
            "netflix", "spotify", "disney", "hbo", "amazon prime", "youtube premium",
            "cine", "bar", "discoteca", "fiesta", "cerveza", "licor", "juego",
            "videojuego", "playstation", "xbox", "steam", "concierto", "evento",
            "bolos", "karaoke", "billar",
        ],
        "emoji": "🎉",
        "necesario": False,
    },
    "Ropa y Accesorios": {
        "keywords": [
            "zara", "h&m", "falabella", "ropa", "zapatos", "tenis", "chaqueta",
            "camisa", "pantalon", "vestido", "accesorios", "reloj", "gafas",
            "maquillaje", "perfume", "centro comercial", "koaj", "arturo calle",
            "tennis", "adidas", "nike",
        ],
        "emoji": "👕",
        "necesario": False,
    },
    "Salud": {
        "keywords": [
            "farmacia", "drogueria", "eps", "medicina", "medico", "doctor",
            "consulta", "laboratorio", "hospital", "clinica", "odontologia",
            "dentista", "lentes", "optica", "gym", "gimnasio", "vitamina",
        ],
        "emoji": "💊",
        "necesario": True,
    },
    "Educacion": {
        "keywords": [
            "universidad", "colegio", "curso", "libro", "udemy", "coursera",
            "platzi", "educacion", "matricula", "pension", "seminario",
            "capacitacion", "papeleria", "copias", "impresion",
        ],
        "emoji": "📚",
        "necesario": True,
    },
    "Ahorro e Inversion": {
        "keywords": ["ahorro", "cdt", "inversion", "fondo", "fiducuenta", "aporte"],
        "emoji": "💰",
        "necesario": True,
    },
}


def categorize_transaction(description: str):
    """Clasifica una transacción por su descripción.
    Returns: (categoria, emoji, es_necesario)
    """
    desc_lower = description.lower()
    for cat_name, cat_info in CATEGORIES.items():
        for keyword in cat_info["keywords"]:
            if keyword in desc_lower:
                return cat_name, cat_info["emoji"], cat_info["necesario"]
    return "Otros", "❓", None


def categorize_dataframe(df):
    """Agrega columnas de categoría a todo el DataFrame."""
    cats, emojis, types = [], [], []
    for _, row in df.iterrows():
        desc = str(row.get("descripcion", ""))
        cat, emoji, nec = categorize_transaction(desc)
        cats.append(cat)
        emojis.append(emoji)
        if nec is True:
            types.append("Necesario")
        elif nec is False:
            types.append("Innecesario")
        else:
            types.append("Otros")
    df = df.copy()
    df["categoria"] = cats
    df["emoji_cat"] = emojis
    df["tipo_gasto"] = types
    return df
