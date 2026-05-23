import re
import pandas as pd
import streamlit as st
from scipy.optimize import linear_sum_assignment
from supabase import create_client

def cargar_apartamentos_iniciales():
    apartamentos_existentes = cargar_tabla("apartamentos")

    if not apartamentos_existentes.empty:
        return
    apartamentos = [
    {"nombre": "Apt101", "price": 1800000, "zona": "Chapinero", "distancia": 1.2, "pet_friendly": True, "amenities": "gym,ascensor,parqueadero", "size": 52, "bedrooms": 2},
    {"nombre": "Apt102", "price": 2200000, "zona": "Chapinero", "distancia": 2.0, "pet_friendly": True, "amenities": "gym,piscina,coworking", "size": 60, "bedrooms": 2},
    {"nombre": "Apt103", "price": 1600000, "zona": "Chapinero", "distancia": 3.5, "pet_friendly": False, "amenities": "ascensor,seguridad", "size": 45, "bedrooms": 1},
    {"nombre": "Apt104", "price": 2500000, "zona": "Chapinero", "distancia": 1.0, "pet_friendly": True, "amenities": "gym,terraza,piscina", "size": 70, "bedrooms": 3},
    {"nombre": "Apt105", "price": 2000000, "zona": "Chapinero", "distancia": 2.8, "pet_friendly": True, "amenities": "coworking,ascensor", "size": 58, "bedrooms": 2},

    {"nombre": "Apt201", "price": 1500000, "zona": "Suba", "distancia": 2.0, "pet_friendly": False, "amenities": "ascensor,seguridad", "size": 42, "bedrooms": 1},
    {"nombre": "Apt202", "price": 1700000, "zona": "Suba", "distancia": 3.2, "pet_friendly": True, "amenities": "parqueadero,seguridad", "size": 50, "bedrooms": 2},
    {"nombre": "Apt203", "price": 1900000, "zona": "Suba", "distancia": 1.8, "pet_friendly": True, "amenities": "gym,ascensor", "size": 55, "bedrooms": 2},
    {"nombre": "Apt204", "price": 2100000, "zona": "Suba", "distancia": 4.0, "pet_friendly": False, "amenities": "piscina,seguridad", "size": 65, "bedrooms": 3},
    {"nombre": "Apt205", "price": 1300000, "zona": "Suba", "distancia": 2.7, "pet_friendly": True, "amenities": "ascensor", "size": 38, "bedrooms": 1},

    {"nombre": "Apt301", "price": 2300000, "zona": "Usaquén", "distancia": 1.5, "pet_friendly": True, "amenities": "gym,parqueadero,seguridad", "size": 62, "bedrooms": 2},
    {"nombre": "Apt302", "price": 2700000, "zona": "Usaquén", "distancia": 2.2, "pet_friendly": True, "amenities": "gym,piscina,terraza", "size": 75, "bedrooms": 3},
    {"nombre": "Apt303", "price": 1900000, "zona": "Usaquén", "distancia": 3.0, "pet_friendly": False, "amenities": "ascensor,coworking", "size": 50, "bedrooms": 2},
    {"nombre": "Apt304", "price": 3100000, "zona": "Usaquén", "distancia": 1.1, "pet_friendly": True, "amenities": "gym,piscina,parqueadero,seguridad", "size": 85, "bedrooms": 3},
    {"nombre": "Apt305", "price": 1600000, "zona": "Usaquén", "distancia": 4.5, "pet_friendly": False, "amenities": "seguridad", "size": 44, "bedrooms": 1},

    {"nombre": "Apt401", "price": 1700000, "zona": "Teusaquillo", "distancia": 1.4, "pet_friendly": True, "amenities": "ascensor,coworking", "size": 48, "bedrooms": 1},
    {"nombre": "Apt402", "price": 2100000, "zona": "Teusaquillo", "distancia": 2.1, "pet_friendly": True, "amenities": "gym,terraza", "size": 56, "bedrooms": 2},
    {"nombre": "Apt403", "price": 2400000, "zona": "Teusaquillo", "distancia": 1.9, "pet_friendly": False, "amenities": "parqueadero,seguridad", "size": 65, "bedrooms": 3},
    {"nombre": "Apt404", "price": 1450000, "zona": "Teusaquillo", "distancia": 3.5, "pet_friendly": True, "amenities": "ascensor", "size": 40, "bedrooms": 1},
    {"nombre": "Apt405", "price": 2800000, "zona": "Teusaquillo", "distancia": 0.9, "pet_friendly": True, "amenities": "gym,piscina,coworking,terraza", "size": 78, "bedrooms": 3},

    {"nombre": "Apt501", "price": 1200000, "zona": "Centro", "distancia": 1.0, "pet_friendly": False, "amenities": "seguridad", "size": 35, "bedrooms": 1},
    {"nombre": "Apt502", "price": 1550000, "zona": "Centro", "distancia": 2.5, "pet_friendly": True, "amenities": "ascensor,coworking", "size": 45, "bedrooms": 1},
    {"nombre": "Apt503", "price": 1850000, "zona": "Centro", "distancia": 1.7, "pet_friendly": True, "amenities": "gym,ascensor", "size": 52, "bedrooms": 2},
    {"nombre": "Apt504", "price": 2250000, "zona": "Centro", "distancia": 3.0, "pet_friendly": False, "amenities": "parqueadero,seguridad", "size": 60, "bedrooms": 2},
    {"nombre": "Apt505", "price": 2600000, "zona": "Centro", "distancia": 1.3, "pet_friendly": True, "amenities": "terraza,piscina,gym", "size": 72, "bedrooms": 3},

    {"nombre": "Apt601", "price": 1100000, "zona": "Kennedy", "distancia": 2.2, "pet_friendly": False, "amenities": "seguridad", "size": 36, "bedrooms": 1},
    {"nombre": "Apt602", "price": 1400000, "zona": "Kennedy", "distancia": 3.1, "pet_friendly": True, "amenities": "ascensor,parqueadero", "size": 43, "bedrooms": 1},
    {"nombre": "Apt603", "price": 1750000, "zona": "Kennedy", "distancia": 2.6, "pet_friendly": True, "amenities": "gym,seguridad", "size": 55, "bedrooms": 2},
    {"nombre": "Apt604", "price": 2000000, "zona": "Kennedy", "distancia": 4.2, "pet_friendly": False, "amenities": "piscina,parqueadero", "size": 66, "bedrooms": 3},
    {"nombre": "Apt605", "price": 2300000, "zona": "Kennedy", "distancia": 1.8, "pet_friendly": True, "amenities": "gym,piscina,terraza", "size": 74, "bedrooms": 3},

    {"nombre": "Apt701", "price": 1350000, "zona": "Engativá", "distancia": 2.0, "pet_friendly": True, "amenities": "ascensor,seguridad", "size": 41, "bedrooms": 1},
    {"nombre": "Apt702", "price": 1650000, "zona": "Engativá", "distancia": 2.8, "pet_friendly": False, "amenities": "parqueadero", "size": 49, "bedrooms": 2},
    {"nombre": "Apt703", "price": 1950000, "zona": "Engativá", "distancia": 1.6, "pet_friendly": True, "amenities": "gym,coworking", "size": 57, "bedrooms": 2},
    {"nombre": "Apt704", "price": 2150000, "zona": "Engativá", "distancia": 3.7, "pet_friendly": True, "amenities": "piscina,ascensor", "size": 68, "bedrooms": 3},
    {"nombre": "Apt705", "price": 2450000, "zona": "Engativá", "distancia": 1.2, "pet_friendly": False, "amenities": "gym,terraza,seguridad", "size": 76, "bedrooms": 3},
]
    for apt in apartamentos:
        supabase.table("apartamentos").insert(apt).execute()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def insertar_usuario(nombre, budget, zona, radio, pets, amenities_req, size_deseado, bedrooms_deseado):
    supabase.table("usuarios").insert({
        "nombre": nombre,
        "budget": budget,
        "zona": zona,
        "radio": radio,
        "pets": pets,
        "amenities_req": ",".join(amenities_req),
        "size_deseado": size_deseado,
        "bedrooms_deseado": bedrooms_deseado
    }).execute()


def insertar_apartamento(nombre, price, zona, distancia, pet_friendly, amenities, size, bedrooms):
    supabase.table("apartamentos").insert({
        "nombre": nombre,
        "price": price,
        "zona": zona,
        "distancia": distancia,
        "pet_friendly": pet_friendly,
        "amenities": ",".join(amenities),
        "size": size,
        "bedrooms": bedrooms
    }).execute()


def cargar_tabla(tabla):
    response = supabase.table(tabla).select("*").execute()
    return pd.DataFrame(response.data)


def texto_a_lista(texto):
    if texto is None or texto == "":
        return []
    return [x.strip() for x in texto.split(",")]


# ─── NLP ──────────────────────────────────────────────────────────────────────

_AMENITY_KEYWORDS = {
    "gym":         ["gym", "gimnasio"],
    "parqueadero": ["parqueadero", "parking", "garaje", "garage"],
    "ascensor":    ["ascensor", "elevador"],
    "piscina":     ["piscina"],
    "terraza":     ["terraza", "balcón", "balcon"],
    "coworking":   ["coworking", "zona de trabajo", "trabajo remoto"],
    "seguridad":   ["seguridad", "vigilancia", "portería", "porteria"],
    "zona BBQ":    ["bbq", "barbacoa", "parrilla", "asadero"],
}

# Peso relativo de cada amenity en el cálculo de compatibilidad (PRD §4)
_AMENITY_WEIGHTS = {
    "parqueadero": 0.80,
    "ascensor":    0.70,
    "seguridad":   0.70,
    "gym":         0.50,
    "piscina":     0.50,
    "coworking":   0.50,
    "terraza":     0.40,
    "zona BBQ":    0.40,
}

_ZONA_KEYWORDS = {
    "Chapinero":  ["chapinero"],
    "Suba":       ["suba"],
    "Usaquén":    ["usaquén", "usaquen"],
    "Teusaquillo":["teusaquillo"],
    "Centro":     ["centro"],
    "Kennedy":    ["kennedy"],
    "Engativá":   ["engativá", "engativa"],
}


def extraer_entidades(texto):
    t = texto.lower()

    entidades = {
        "budget":          None,
        "zona":            None,
        "radio":           5.0,
        "pets":            False,
        "amenities_req":   [],
        "size_deseado":    85,
        "bedrooms_deseado": 2,
        "tipo":            None,
    }

    # Presupuesto: "2 millones", "1.8 millones", "$1,800,000"
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:millones?|mll?\.?)', t)
    if m:
        entidades["budget"] = int(float(m.group(1).replace(",", ".")) * 1_000_000)
    else:
        m = re.search(r'\$?\s*(\d{1,3}(?:[.,]\d{3})+)', t)
        if m:
            entidades["budget"] = int(m.group(1).replace(".", "").replace(",", ""))

    # Zona
    for zona, kws in _ZONA_KEYWORDS.items():
        if any(k in t for k in kws):
            entidades["zona"] = zona
            break

    # Radio de búsqueda: "5 km", "3 kilómetros"
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:km|kilómetros?|kilometros?)', t)
    if m:
        entidades["radio"] = float(m.group(1).replace(",", "."))

    # Mascotas
    entidades["pets"] = any(p in t for p in ["gato", "perro", "mascota", "pet", "animal"])

    # Amenities
    for amenity, kws in _AMENITY_KEYWORDS.items():
        if any(k in t for k in kws):
            entidades["amenities_req"].append(amenity)

    # Habitaciones: "2 habitaciones", "3 cuartos", "1 alcoba"
    m = re.search(r'(\d+)\s*(?:habitaciones?|cuartos?|alcobas?|rooms?|dormitorios?)', t)
    if m:
        entidades["bedrooms_deseado"] = int(m.group(1))

    # Tamaño: "60 metros", "80 m2"
    m = re.search(r'(\d+)\s*(?:metros?\s*(?:cuadrados?)?|m2|m²)', t)
    if m:
        entidades["size_deseado"] = int(m.group(1))

    # Tipo de transacción
    if any(p in t for p in ["arriendo", "arrendar", "alquiler", "alquilar", "mensual", "/mes"]):
        entidades["tipo"] = "arriendo"
    elif any(p in t for p in ["compra", "comprar", "venta", "vender"]):
        entidades["tipo"] = "compra"
    elif entidades["budget"]:
        if entidades["budget"] <= 5_000_000:
            entidades["tipo"] = "arriendo"
        elif entidades["budget"] >= 100_000_000:
            entidades["tipo"] = "compra"

    return entidades


def buscar_compatibles(entidades):
    """Devuelve todos los apartamentos compatibles ordenados por peso descendente."""
    apartamentos = cargar_tabla("apartamentos")

    usuario = {
        "budget":           entidades["budget"],
        "radio":            entidades["radio"],
        "pets":             entidades["pets"],
        "amenities_req":    ",".join(entidades["amenities_req"]),
        "size_deseado":     entidades["size_deseado"],
        "bedrooms_deseado": entidades["bedrooms_deseado"],
    }

    resultados = []
    for _, apt in apartamentos.iterrows():
        peso = calcular_peso(usuario, apt)
        if peso > 0:
            resultados.append({
                "nombre":        apt["nombre"],
                "zona":          apt["zona"],
                "precio":        apt["price"],
                "distancia":     apt["distancia"],
                "amenities":     apt["amenities"],
                "size":          apt["size"],
                "bedrooms":      apt["bedrooms"],
                "pet_friendly":  apt["pet_friendly"],
                "url":           apt.get("url", ""),
                "descripcion":   apt.get("descripcion", ""),
                "imagen":        apt.get("imagen", ""),
                "compatibilidad": peso,
            })

    resultados.sort(key=lambda x: x["compatibilidad"], reverse=True)
    return resultados


def visualizar_grafo_bipartito(compatibles, top3, entidades):
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    n = len(compatibles)
    if n == 0:
        return None

    top3_nombres    = [apt["nombre"] for apt in top3]
    colores_ranking = ["#FFD700", "#C0C0C0", "#CD7F32"]

    fig, ax = plt.subplots(figsize=(13, max(6, n * 0.95)))
    ax.set_xlim(-0.3, 2.6)
    ax.set_ylim(-0.8, n + 0.3)
    ax.axis("off")
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    # Posiciones: usuario a la izquierda, apartamentos a la derecha
    ux, uy = 0.1, (n - 1) / 2.0
    posiciones = [(1.9, float(n - 1 - i)) for i in range(n)]

    # Etiquetas de conjunto (notación matemática)
    ax.text(ux, n + 0.15, "U", ha="center", fontsize=13, color="#2E86AB", fontweight="bold")
    ax.text(1.9, n + 0.15, "O", ha="center", fontsize=13, color="#555555", fontweight="bold")

    # ── Aristas ──────────────────────────────────────────────────────────────
    for idx, apt in enumerate(compatibles):
        px, py  = posiciones[idx]
        peso    = apt["compatibilidad"]
        es_top  = apt["nombre"] in top3_nombres

        color  = "#F5A623" if es_top else "#CCCCCC"
        grosor = 2.5 + peso * 3 if es_top else 0.7
        alpha  = 0.9 if es_top else 0.35

        ax.plot([ux, px], [uy, py], color=color, linewidth=grosor, alpha=alpha, zorder=1)

        # Etiqueta de peso solo en aristas TOP 3
        if es_top:
            mx, my = (ux + px) / 2, (uy + py) / 2
            ax.text(mx, my, f"w={peso:.2f}",
                    ha="center", va="center", fontsize=7.5, fontweight="bold",
                    color=color,
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                              edgecolor=color, linewidth=1, alpha=0.95),
                    zorder=3)

    # ── Nodo usuario ─────────────────────────────────────────────────────────
    ax.add_patch(plt.Circle((ux, uy), 0.22, color="#2E86AB", zorder=4, ec="white", lw=2))
    ax.text(ux, uy + 0.06, "Tú", ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", zorder=5)
    ax.text(ux, uy - 0.13, f"${entidades['budget'] / 1e6:.1f}M",
            ha="center", va="center", fontsize=7, color="#cce8ff", zorder=5)

    # ── Nodos apartamento ────────────────────────────────────────────────────
    for idx, apt in enumerate(compatibles):
        px, py  = posiciones[idx]
        es_top  = apt["nombre"] in top3_nombres
        rank    = top3_nombres.index(apt["nombre"]) if es_top else -1

        color_nodo  = colores_ranking[rank] if es_top else "#BBBBBB"
        color_texto = "#333333" if es_top else "white"

        ax.add_patch(plt.Circle((px, py), 0.22, color=color_nodo, zorder=4, ec="white", lw=2))
        ax.text(px, py, apt["nombre"], ha="center", va="center",
                fontsize=6.5, fontweight="bold", color=color_texto, zorder=5)

        # Info a la derecha del nodo
        ax.text(px + 0.32, py + 0.08, apt["zona"],
                ha="left", va="center", fontsize=8.5,
                color="#333333", fontweight="bold" if es_top else "normal")
        ax.text(px + 0.32, py - 0.1, f"${apt['precio'] / 1e6:.1f}M · {apt['bedrooms']} hab",
                ha="left", va="center", fontsize=7.5, color="#666666")

    ax.set_title("G = (U ∪ O, E, w)  —  Grafo Bipartito Ponderado",
                 fontsize=12, fontweight="bold", color="#333333", pad=10)

    leyenda = [
        mpatches.Patch(color="#FFD700", label="🥇 1ra opción"),
        mpatches.Patch(color="#C0C0C0", label="🥈 2da opción"),
        mpatches.Patch(color="#CD7F32", label="🥉 3ra opción"),
        mpatches.Patch(color="#BBBBBB", label="Compatible (no en TOP 3)"),
        mpatches.Patch(color="#F5A623", label="Arista TOP 3"),
        mpatches.Patch(color="#CCCCCC", label="Arista regular"),
    ]
    ax.legend(handles=leyenda, loc="lower left", fontsize=7.5,
              framealpha=0.9, edgecolor="#CCCCCC")

    plt.tight_layout()
    return fig


def calcular_peso(usuario, apt):
    if apt["price"] > usuario["budget"]:
        return 0

    if apt["distancia"] > usuario["radio"]:
        return 0

    if usuario["pets"] and not apt["pet_friendly"]:
        return 0

    requeridos = set(texto_a_lista(usuario["amenities_req"]))
    disponibles = set(texto_a_lista(apt["amenities"]))

    if requeridos:
        peso_total = sum(_AMENITY_WEIGHTS.get(a, 0.50) for a in requeridos)
        peso_match = sum(_AMENITY_WEIGHTS.get(a, 0.50) for a in requeridos & disponibles)
        amenity_match = peso_match / peso_total
    else:
        amenity_match = 1.0

    if amenity_match < 0.50:
        return 0

    price_score = 1 - abs(apt["price"] - usuario["budget"]) / usuario["budget"] * 0.5
    location_score = 1 - apt["distancia"] / usuario["radio"]

    amenity_score = amenity_match
    size_score = 1 - abs(apt["size"] - usuario["size_deseado"]) / usuario["size_deseado"] * 0.5
    bedroom_score = 1 - abs(apt["bedrooms"] - usuario["bedrooms_deseado"]) / usuario["bedrooms_deseado"] * 0.5
    pet_score = 1

    secondary_score = (
        0.35 * amenity_score +
        0.35 * size_score +
        0.20 * bedroom_score +
        0.10 * pet_score
    )

    peso = (
        0.40 * price_score +
        0.30 * location_score +
        0.30 * secondary_score
    )

    return round(max(0, min(1, peso)), 3)


def construir_matriz():
    usuarios = cargar_tabla("usuarios")
    apartamentos = cargar_tabla("apartamentos")

    if usuarios.empty or apartamentos.empty:
        return None, usuarios, apartamentos

    matriz = []

    for _, usuario in usuarios.iterrows():
        fila = []
        for _, apt in apartamentos.iterrows():
            fila.append(calcular_peso(usuario, apt))
        matriz.append(fila)

    W = pd.DataFrame(
        matriz,
        index=usuarios["id"],
        columns=apartamentos["id"]
    )

    return W, usuarios, apartamentos


def limpiar_asignaciones():
    asignaciones = cargar_tabla("asignaciones")

    if asignaciones.empty:
        return

    for asignacion_id in asignaciones["id"]:
        supabase.table("asignaciones").delete().eq("id", int(asignacion_id)).execute()


def guardar_asignacion(usuario_id, apartamento_id, peso):
    supabase.table("asignaciones").insert({
        "usuario_id": int(usuario_id),
        "apartamento_id": int(apartamento_id),
        "peso": float(peso)
    }).execute()


def cargar_asignaciones_detalladas():
    asig = cargar_tabla("asignaciones")
    if asig.empty:
        return asig
    usuarios = cargar_tabla("usuarios")
    apts = cargar_tabla("apartamentos")
    merged = asig.merge(usuarios[["id", "nombre"]], left_on="usuario_id", right_on="id")
    merged = merged.merge(apts[["id", "nombre"]], left_on="apartamento_id", right_on="id", suffixes=("_u", "_a"))
    return merged[["nombre_u", "nombre_a", "peso"]].rename(columns={"nombre_u": "usuario", "nombre_a": "apartamento"})


def ejecutar_matching():
    W, usuarios, apartamentos = construir_matriz()

    if W is None:
        return None, None

    C = W.copy()

    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            if C.iloc[i, j] == 0:
                C.iloc[i, j] = 9999
            else:
                C.iloc[i, j] = 1 - C.iloc[i, j]

    filas, columnas = linear_sum_assignment(C)

    limpiar_asignaciones()

    resultados = []

    for i, j in zip(filas, columnas):
        peso = W.iloc[i, j]

        if peso > 0:
            usuario_id = int(W.index[i])
            apartamento_id = int(W.columns[j])

            guardar_asignacion(usuario_id, apartamento_id, peso)

            usuario_nombre = usuarios.loc[usuarios["id"] == usuario_id, "nombre"].values[0]
            apartamento_nombre = apartamentos.loc[apartamentos["id"] == apartamento_id, "nombre"].values[0]

            resultados.append({
                "usuario": usuario_nombre,
                "apartamento": apartamento_nombre,
                "peso": peso
            })

    return W, pd.DataFrame(resultados)


def ejecutar_matching_maximo():
    """Matching máximo (cardinalidad) — maximiza número de asignaciones sin considerar pesos."""
    W, usuarios, apartamentos = construir_matriz()
    if W is None:
        return None, None

    C = W.copy()
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            C.iloc[i, j] = 9999 if C.iloc[i, j] == 0 else 0

    filas, columnas = linear_sum_assignment(C)

    resultados = []
    for i, j in zip(filas, columnas):
        peso = W.iloc[i, j]
        if peso > 0:
            uid = int(W.index[i])
            aid = int(W.columns[j])
            usuario_nombre = usuarios.loc[usuarios["id"] == uid, "nombre"].values[0]
            apt_nombre = apartamentos.loc[apartamentos["id"] == aid, "nombre"].values[0]
            resultados.append({
                "usuario": usuario_nombre,
                "apartamento": apt_nombre,
                "peso": peso,
            })

    return W, pd.DataFrame(resultados)


cargar_apartamentos_iniciales()
st.title("Sistema de Matching de Apartamentos")
st.write("Base de datos remota en Supabase + algoritmo húngaro.")

menu = st.sidebar.selectbox(
    "Menú",
    [
        "Buscar apartamento",
        "Registrar usuario",
        "Registrar apartamento",
        "Ver base de datos",
        "Ejecutar matching",
    ]
)

amenities_opciones = [
    "gym",
    "parqueadero",
    "ascensor",
    "piscina",
    "terraza",
    "coworking",
    "zona BBQ",
    "seguridad"
]

zonas = [
    "Chapinero",
    "Suba",
    "Usaquén",
    "Teusaquillo",
    "Centro",
    "Kennedy",
    "Engativá"
]


if menu == "Buscar apartamento":
    st.header("Buscar apartamento")
    st.write("Describe en lenguaje natural lo que estás buscando.")

    if "entidades_nlp" not in st.session_state:
        st.session_state["entidades_nlp"] = None
    if "mostrar_resultados" not in st.session_state:
        st.session_state["mostrar_resultados"] = False

    query = st.text_area(
        "¿Qué tipo de apartamento buscas?",
        placeholder='Ej: "Busco apartamento en Chapinero, máximo 2 millones al mes, con parqueadero y ascensor. Tengo un gato."',
        height=120,
    )

    if st.button("Buscar", type="primary"):
        if not query.strip():
            st.warning("Por favor escribe lo que buscas.")
        else:
            st.session_state["entidades_nlp"] = extraer_entidades(query)
            st.session_state["mostrar_resultados"] = False

    entidades = st.session_state["entidades_nlp"]

    if entidades is not None:

        # ── Preferencias detectadas ──────────────────────────────────────────
        st.subheader("Preferencias detectadas")
        col1, col2, col3 = st.columns(3)
        with col1:
            presupuesto_str = f"${entidades['budget']:,.0f}" if entidades["budget"] else "⚠️ No detectado"
            st.write(f"**Presupuesto:** {presupuesto_str}")
            st.write(f"**Zona:** {entidades['zona'] or 'No especificada'}")
            st.write(f"**Tipo:** {entidades['tipo'] or '⚠️ No detectado'}")
        with col2:
            st.write(f"**Mascotas:** {'Sí' if entidades['pets'] else 'No'}")
            st.write(f"**Habitaciones:** {entidades['bedrooms_deseado']}")
            st.write(f"**Tamaño deseado:** {entidades['size_deseado']} m²")
        with col3:
            st.write(f"**Radio de búsqueda:** {entidades['radio']} km")
            if entidades["amenities_req"]:
                st.write("**Amenities requeridos:**")
                for a in entidades["amenities_req"]:
                    st.write(f"  • {a}")
            else:
                st.write("**Amenities:** No especificados")

        st.divider()

        # ── Clarificación interactiva de campos faltantes ────────────────────
        budget_final = entidades["budget"]
        tipo_final   = entidades["tipo"]
        necesita_clarificacion = False

        if not budget_final:
            necesita_clarificacion = True
            st.warning("No detecté tu presupuesto. ¿Cuánto puedes pagar?")
            budget_final = st.number_input(
                "Presupuesto máximo (COP)",
                min_value=400_000,
                max_value=3_000_000_000,
                value=2_000_000,
                step=100_000,
                key="budget_manual",
            )

        if not tipo_final:
            necesita_clarificacion = True
            st.warning("No pude determinar si buscas arriendo o compra.")
            tipo_sel = st.radio(
                "¿Qué tipo de transacción buscas?",
                ["Arriendo", "Compra"],
                horizontal=True,
                key="tipo_manual",
            )
            tipo_final = tipo_sel.lower()

        if necesita_clarificacion:
            if st.button("Confirmar y buscar", type="primary"):
                entidades["budget"] = int(budget_final)
                entidades["tipo"]   = tipo_final
                st.session_state["entidades_nlp"]    = entidades
                st.session_state["mostrar_resultados"] = True
                st.rerun()
        else:
            st.session_state["mostrar_resultados"] = True

        # ── Resultados TOP 3 + Grafo ─────────────────────────────────────────
        if st.session_state["mostrar_resultados"]:
            with st.spinner("Analizando apartamentos..."):
                todos = buscar_compatibles(st.session_state["entidades_nlp"])
            top3 = todos[:3]

            if not todos:
                st.warning(
                    "No encontré apartamentos compatibles. "
                    "Intenta aumentar el presupuesto o el radio de búsqueda."
                )
            else:
                st.subheader(f"Top {len(top3)} opciones para ti")
                medallas = ["🥇", "🥈", "🥉"]

                for i, apt in enumerate(top3):
                    with st.container(border=True):
                        col_info, col_match = st.columns([4, 1])
                        with col_info:
                            st.markdown(f"#### {medallas[i]} {apt['nombre']} — {apt['zona']}")
                            st.write(
                                f"**Precio:** ${apt['precio']:,.0f} &nbsp;|&nbsp; "
                                f"**Tamaño:** {apt['size']} m² &nbsp;|&nbsp; "
                                f"**Habitaciones:** {apt['bedrooms']}"
                            )
                            pet_label = "✅ Pet friendly" if apt["pet_friendly"] else "❌ No pet friendly"
                            st.write(f"**Distancia:** {apt['distancia']} km &nbsp;|&nbsp; {pet_label}")
                            amenities_lista = apt["amenities"].replace(",", " · ")
                            st.write(f"**Amenities:** {amenities_lista}")
                        with col_match:
                            pct = round(apt["compatibilidad"] * 100)
                            st.metric("Match", f"{pct}%")
                            if apt.get("url"):
                                st.link_button("Ver listing", apt["url"], use_container_width=True)

                        fotos = [u for u in apt.get("imagen", "").split(",") if u.startswith("http")]
                        if fotos:
                            st.image(fotos[0], use_container_width=True)
                            if len(fotos) > 1:
                                with st.expander(f"Ver todas las fotos ({len(fotos)})"):
                                    n_cols = min(len(fotos), 3)
                                    cols = st.columns(n_cols)
                                    for k, foto_url in enumerate(fotos):
                                        cols[k % n_cols].image(foto_url, use_container_width=True)

                        if apt.get("descripcion"):
                            with st.expander("Ver descripción"):
                                st.write(apt["descripcion"])

                # ── Grafo bipartito ───────────────────────────────────────────
                st.divider()
                with st.expander(
                    f"Ver grafo bipartito — {len(todos)} apartamento(s) compatible(s) encontrado(s)",
                    expanded=False,
                ):
                    st.write(
                        f"Cada **arista** representa una relación de compatibilidad "
                        f"$w(u_i, o_j) \\in [0, 1]$. Solo existen aristas que cumplen "
                        f"las restricciones duras (presupuesto, distancia, mascotas, amenities ≥ 50%). "
                        f"Las aristas naranjas son las del **TOP 3**."
                    )
                    fig = visualizar_grafo_bipartito(
                        todos, top3, st.session_state["entidades_nlp"]
                    )
                    if fig:
                        st.pyplot(fig, use_container_width=True)


elif menu == "Registrar usuario":
    st.header("Registrar usuario")

    with st.form("form_usuario"):
        nombre = st.text_input("Nombre")
        budget = st.number_input("Presupuesto máximo", min_value=0.0, step=100000.0)
        zona = st.selectbox("Zona preferida", zonas)
        radio = st.number_input("Radio máximo en km", min_value=0.0, step=0.5)
        pets = st.checkbox("Tiene mascota")
        amenities_req = st.multiselect("Amenities requeridos", amenities_opciones)
        size_deseado = st.number_input("Tamaño deseado en m²", min_value=1.0, step=1.0)
        bedrooms_deseado = st.number_input("Habitaciones deseadas", min_value=1, step=1)

        enviar = st.form_submit_button("Guardar usuario")

        if enviar:
            insertar_usuario(
                nombre,
                budget,
                zona,
                radio,
                pets,
                amenities_req,
                size_deseado,
                bedrooms_deseado
            )
            st.success("Usuario guardado en Supabase.")


elif menu == "Registrar apartamento":
    st.header("Registrar apartamento")

    with st.form("form_apartamento"):
        nombre = st.text_input("Nombre o código del apartamento")
        price = st.number_input("Precio", min_value=0.0, step=100000.0)
        zona = st.selectbox("Zona", zonas)
        distancia = st.number_input("Distancia en km", min_value=0.0, step=0.5)
        pet_friendly = st.checkbox("Pet friendly")
        amenities = st.multiselect("Amenities disponibles", amenities_opciones)
        size = st.number_input("Tamaño en m²", min_value=1.0, step=1.0)
        bedrooms = st.number_input("Habitaciones", min_value=1, step=1)

        enviar = st.form_submit_button("Guardar apartamento")

        if enviar:
            insertar_apartamento(
                nombre,
                price,
                zona,
                distancia,
                pet_friendly,
                amenities,
                size,
                bedrooms
            )
            st.success("Apartamento guardado en Supabase.")


elif menu == "Ver base de datos":
    st.header("Base de datos remota")

    st.subheader("Usuarios")
    st.dataframe(cargar_tabla("usuarios"))

    st.subheader("Apartamentos")
    st.dataframe(cargar_tabla("apartamentos"))

    st.subheader("Asignaciones")
    st.dataframe(cargar_asignaciones_detalladas())


elif menu == "Ejecutar matching":
    st.header("Matching óptimo")
    st.write(
        "Compara dos estrategias: **Peso máximo** (Algoritmo Húngaro) maximiza la "
        "compatibilidad total; **Matching máximo** maximiza el número de asignaciones."
    )

    if st.button("Ejecutar y comparar", type="primary"):
        W, res_hungaro = ejecutar_matching()

        if W is None:
            st.warning("Debes registrar al menos un usuario y un apartamento.")
        else:
            _, res_maximo = ejecutar_matching_maximo()
            n_usuarios = len(cargar_tabla("usuarios"))

            tab1, tab2 = st.tabs(["Peso máximo (Húngaro)", "Matching máximo (Cardinalidad)"])

            with tab1:
                st.subheader("Algoritmo Húngaro — maximiza compatibilidad total")
                st.dataframe(W, use_container_width=True)
                st.dataframe(res_hungaro, use_container_width=True)
                if not res_hungaro.empty:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Peso total",    round(res_hungaro["peso"].sum(), 3))
                    c2.metric("Peso promedio", round(res_hungaro["peso"].mean(), 3))
                    c3.metric("Cobertura",     f"{round(len(res_hungaro) / n_usuarios * 100, 1)}%")
                else:
                    st.warning("No hubo asignaciones válidas.")

            with tab2:
                st.subheader("Matching máximo — maximiza número de asignaciones")
                st.write("Trata todas las aristas válidas como equivalentes (peso binario).")
                st.dataframe(res_maximo, use_container_width=True)
                if not res_maximo.empty:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Asignaciones",  len(res_maximo))
                    c2.metric("Peso promedio", round(res_maximo["peso"].mean(), 3))
                    c3.metric("Cobertura",     f"{round(len(res_maximo) / n_usuarios * 100, 1)}%")
                else:
                    st.warning("No hubo asignaciones válidas.")

            st.divider()
            st.subheader("Comparación de estrategias")
            hungaro_asig  = len(res_hungaro)  if res_hungaro  is not None and not res_hungaro.empty  else 0
            maximo_asig   = len(res_maximo)   if res_maximo   is not None and not res_maximo.empty   else 0
            hungaro_peso  = round(res_hungaro["peso"].sum(), 3)  if hungaro_asig  else 0
            maximo_peso   = round(res_maximo["peso"].sum(),  3)  if maximo_asig   else 0
            comp = pd.DataFrame({
                "Estrategia":   ["Peso máximo (Húngaro)", "Matching máximo (Cardinalidad)"],
                "Asignaciones": [hungaro_asig,  maximo_asig],
                "Peso total":   [hungaro_peso,  maximo_peso],
                "Cobertura":    [f"{round(hungaro_asig / n_usuarios * 100, 1)}%",
                                 f"{round(maximo_asig  / n_usuarios * 100, 1)}%"],
            })
            st.dataframe(comp, use_container_width=True, hide_index=True)
            st.info(
                "Si **Matching máximo** asigna más usuarios que el Húngaro, significa que "
                "priorizar calidad dejó a algunos buscadores sin apartamento. "
                "Si son iguales, ambas estrategias cubren los mismos usuarios."
            )