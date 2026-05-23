import re
import unicodedata
import pandas as pd
import streamlit as st
from scipy.optimize import linear_sum_assignment

from database import (
    crear_tablas,
    insertar_usuario,
    insertar_apartamento,
    cargar_usuarios,
    cargar_apartamentos,
    guardar_asignacion,
    limpiar_asignaciones,
    cargar_asignaciones_detalladas,
    conectar,
)

# ── Adapter ───────────────────────────────────────────────────────────────────

def cargar_tabla(tabla):
    if tabla == "usuarios":
        return cargar_usuarios()
    if tabla == "apartamentos":
        return cargar_apartamentos()
    if tabla == "asignaciones":
        conn = conectar()
        resultado = pd.read_sql_query("SELECT * FROM asignaciones", conn)
        conn.close()
        return resultado
    return pd.DataFrame()


def cargar_apartamentos_iniciales():
    if not cargar_apartamentos().empty:
        return
    apartamentos = [
        {"nombre": "Apt101", "price": 1800000, "zona": "Chapinero",   "distancia": 1.2, "pet_friendly": True,  "amenities": "gym,ascensor,parqueadero",          "size": 52, "bedrooms": 2},
        {"nombre": "Apt102", "price": 2200000, "zona": "Chapinero",   "distancia": 2.0, "pet_friendly": True,  "amenities": "gym,piscina,coworking",             "size": 60, "bedrooms": 2},
        {"nombre": "Apt103", "price": 1600000, "zona": "Chapinero",   "distancia": 3.5, "pet_friendly": False, "amenities": "ascensor,seguridad",                "size": 45, "bedrooms": 1},
        {"nombre": "Apt104", "price": 2500000, "zona": "Chapinero",   "distancia": 1.0, "pet_friendly": True,  "amenities": "gym,terraza,piscina",               "size": 70, "bedrooms": 3},
        {"nombre": "Apt105", "price": 2000000, "zona": "Chapinero",   "distancia": 2.8, "pet_friendly": True,  "amenities": "coworking,ascensor",                "size": 58, "bedrooms": 2},
        {"nombre": "Apt201", "price": 1500000, "zona": "Suba",        "distancia": 2.0, "pet_friendly": False, "amenities": "ascensor,seguridad",                "size": 42, "bedrooms": 1},
        {"nombre": "Apt202", "price": 1700000, "zona": "Suba",        "distancia": 3.2, "pet_friendly": True,  "amenities": "parqueadero,seguridad",             "size": 50, "bedrooms": 2},
        {"nombre": "Apt203", "price": 1900000, "zona": "Suba",        "distancia": 1.8, "pet_friendly": True,  "amenities": "gym,ascensor",                      "size": 55, "bedrooms": 2},
        {"nombre": "Apt204", "price": 2100000, "zona": "Suba",        "distancia": 4.0, "pet_friendly": False, "amenities": "piscina,seguridad",                 "size": 65, "bedrooms": 3},
        {"nombre": "Apt205", "price": 1300000, "zona": "Suba",        "distancia": 2.7, "pet_friendly": True,  "amenities": "ascensor",                          "size": 38, "bedrooms": 1},
        {"nombre": "Apt301", "price": 2300000, "zona": "Usaquén",     "distancia": 1.5, "pet_friendly": True,  "amenities": "gym,parqueadero,seguridad",         "size": 62, "bedrooms": 2},
        {"nombre": "Apt302", "price": 2700000, "zona": "Usaquén",     "distancia": 2.2, "pet_friendly": True,  "amenities": "gym,piscina,terraza",               "size": 75, "bedrooms": 3},
        {"nombre": "Apt303", "price": 1900000, "zona": "Usaquén",     "distancia": 3.0, "pet_friendly": False, "amenities": "ascensor,coworking",                "size": 50, "bedrooms": 2},
        {"nombre": "Apt304", "price": 3100000, "zona": "Usaquén",     "distancia": 1.1, "pet_friendly": True,  "amenities": "gym,piscina,parqueadero,seguridad", "size": 85, "bedrooms": 3},
        {"nombre": "Apt305", "price": 1600000, "zona": "Usaquén",     "distancia": 4.5, "pet_friendly": False, "amenities": "seguridad",                         "size": 44, "bedrooms": 1},
        {"nombre": "Apt401", "price": 1700000, "zona": "Teusaquillo", "distancia": 1.4, "pet_friendly": True,  "amenities": "ascensor,coworking",                "size": 48, "bedrooms": 1},
        {"nombre": "Apt402", "price": 2100000, "zona": "Teusaquillo", "distancia": 2.1, "pet_friendly": True,  "amenities": "gym,terraza",                       "size": 56, "bedrooms": 2},
        {"nombre": "Apt403", "price": 2400000, "zona": "Teusaquillo", "distancia": 1.9, "pet_friendly": False, "amenities": "parqueadero,seguridad",             "size": 65, "bedrooms": 3},
        {"nombre": "Apt404", "price": 1450000, "zona": "Teusaquillo", "distancia": 3.5, "pet_friendly": True,  "amenities": "ascensor",                          "size": 40, "bedrooms": 1},
        {"nombre": "Apt405", "price": 2800000, "zona": "Teusaquillo", "distancia": 0.9, "pet_friendly": True,  "amenities": "gym,piscina,coworking,terraza",     "size": 78, "bedrooms": 3},
        {"nombre": "Apt501", "price": 1200000, "zona": "Centro",      "distancia": 1.0, "pet_friendly": False, "amenities": "seguridad",                         "size": 35, "bedrooms": 1},
        {"nombre": "Apt502", "price": 1550000, "zona": "Centro",      "distancia": 2.5, "pet_friendly": True,  "amenities": "ascensor,coworking",                "size": 45, "bedrooms": 1},
        {"nombre": "Apt503", "price": 1850000, "zona": "Centro",      "distancia": 1.7, "pet_friendly": True,  "amenities": "gym,ascensor",                      "size": 52, "bedrooms": 2},
        {"nombre": "Apt504", "price": 2250000, "zona": "Centro",      "distancia": 3.0, "pet_friendly": False, "amenities": "parqueadero,seguridad",             "size": 60, "bedrooms": 2},
        {"nombre": "Apt505", "price": 2600000, "zona": "Centro",      "distancia": 1.3, "pet_friendly": True,  "amenities": "terraza,piscina,gym",               "size": 72, "bedrooms": 3},
        {"nombre": "Apt601", "price": 1100000, "zona": "Kennedy",     "distancia": 2.2, "pet_friendly": False, "amenities": "seguridad",                         "size": 36, "bedrooms": 1},
        {"nombre": "Apt602", "price": 1400000, "zona": "Kennedy",     "distancia": 3.1, "pet_friendly": True,  "amenities": "ascensor,parqueadero",              "size": 43, "bedrooms": 1},
        {"nombre": "Apt603", "price": 1750000, "zona": "Kennedy",     "distancia": 2.6, "pet_friendly": True,  "amenities": "gym,seguridad",                     "size": 55, "bedrooms": 2},
        {"nombre": "Apt604", "price": 2000000, "zona": "Kennedy",     "distancia": 4.2, "pet_friendly": False, "amenities": "piscina,parqueadero",               "size": 66, "bedrooms": 3},
        {"nombre": "Apt605", "price": 2300000, "zona": "Kennedy",     "distancia": 1.8, "pet_friendly": True,  "amenities": "gym,piscina,terraza",               "size": 74, "bedrooms": 3},
        {"nombre": "Apt701", "price": 1350000, "zona": "Engativá",    "distancia": 2.0, "pet_friendly": True,  "amenities": "ascensor,seguridad",                "size": 41, "bedrooms": 1},
        {"nombre": "Apt702", "price": 1650000, "zona": "Engativá",    "distancia": 2.8, "pet_friendly": False, "amenities": "parqueadero",                       "size": 49, "bedrooms": 2},
        {"nombre": "Apt703", "price": 1950000, "zona": "Engativá",    "distancia": 1.6, "pet_friendly": True,  "amenities": "gym,coworking",                     "size": 57, "bedrooms": 2},
        {"nombre": "Apt704", "price": 2150000, "zona": "Engativá",    "distancia": 3.7, "pet_friendly": True,  "amenities": "piscina,ascensor",                  "size": 68, "bedrooms": 3},
        {"nombre": "Apt705", "price": 2450000, "zona": "Engativá",    "distancia": 1.2, "pet_friendly": False, "amenities": "gym,terraza,seguridad",             "size": 76, "bedrooms": 3},
    ]
    for apt in apartamentos:
        insertar_apartamento(
            apt["nombre"], apt["price"], apt["zona"], apt["distancia"],
            apt["pet_friendly"], apt["amenities"].split(","), apt["size"], apt["bedrooms"],
        )


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
    "Chapinero":   ["chapinero", "chico reservado", "chico norte", "chico", "rosales", "cabrera", "antiguo country"],
    "Suba":        ["suba", "niza", "alhambra", "prado veraniego", "rincón"],
    "Usaquén":     ["usaquén", "usaquen", "santa bárbara", "santa barbara", "cedritos", "country club", "unicentro"],
    "Teusaquillo": ["teusaquillo", "palermo", "la soledad", "armenia"],
    "Centro":      ["centro", "candelaria", "santa fe", "mártires", "martires", "la concordia"],
    "Kennedy":     ["kennedy", "américas", "americas", "bosa"],
    "Engativá":    ["engativá", "engativa", "boyacá real", "boyaca real", "garcés navas"],
}


def _sin_tildes(texto: str) -> str:
    """Elimina tildes y ñ→n para comparación robusta."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    ).replace('ñ', 'n')


def _barrios_en_bd():
    try:
        conn = conectar()
        cur  = conn.cursor()
        cur.execute("SELECT DISTINCT barrio FROM apartamentos WHERE barrio IS NOT NULL AND barrio != ''")
        barrios = [r[0].lower() for r in cur.fetchall() if r[0]]
        conn.close()
        return sorted(barrios, key=len, reverse=True)
    except Exception:
        return []


def extraer_entidades(texto):
    t = texto.lower()
    entidades = {
        "budget": None, "zona": None, "barrio": None, "radio": 5.0,
        "pets": False, "amenities_req": [],
        "size_deseado": 85, "bedrooms_deseado": 2, "tipo": None,
    }

    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:millones?|mll?\.?)', t)
    if m:
        entidades["budget"] = int(float(m.group(1).replace(",", ".")) * 1_000_000)
    else:
        m = re.search(r'\$?\s*(\d{1,3}(?:[.,]\d{3})+)', t)
        if m:
            entidades["budget"] = int(m.group(1).replace(".", "").replace(",", ""))

    for zona, kws in _ZONA_KEYWORDS.items():
        if any(k in t for k in kws):
            entidades["zona"] = zona
            break

    t_norm = _sin_tildes(t)
    for barrio in _barrios_en_bd():
        if barrio and _sin_tildes(barrio) in t_norm:
            entidades["barrio"] = barrio
            break

    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:km|kilómetros?|kilometros?)', t)
    if m:
        entidades["radio"] = float(m.group(1).replace(",", "."))

    negacion_pets = bool(re.search(
        r'\b(no\s+tengo|no\s+hay|sin|no\s+tiene|tampoco)\b.{0,25}'
        r'\b(gato|gatos|gata|gatas|perro|perros|perra|perras|mascota|mascotas|pet|pets|animal|animales|cachorro|cachorros)\b', t
    ))
    _pets_positivos = [
        "gato", "gata", "gatos", "gatas",
        "perro", "perra", "perros", "perras", "perrita", "perrito",
        "mascota", "mascotas", "pet", "pets",
        "animal", "animales", "cachorro", "cachorros", "canino",
    ]
    if negacion_pets:
        entidades["pets"] = False
    else:
        entidades["pets"] = any(p in t for p in _pets_positivos)

    for amenity, kws in _AMENITY_KEYWORDS.items():
        if any(k in t for k in kws):
            entidades["amenities_req"].append(amenity)

    m = re.search(r'(\d+)\s*(?:habitaciones?|cuartos?|alcobas?|rooms?|dormitorios?)', t)
    if m:
        entidades["bedrooms_deseado"] = int(m.group(1))

    m = re.search(r'(\d+)\s*(?:metros?\s*(?:cuadrados?)?|m2|m²)', t)
    if m:
        entidades["size_deseado"] = int(m.group(1))

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


# ─── Matching ─────────────────────────────────────────────────────────────────

def texto_a_lista(texto):
    if texto is None or texto == "":
        return []
    return [x.strip() for x in texto.split(",")]


def calcular_peso(usuario, apt):
    price = apt["price"]
    distancia = apt["distancia"]
    if pd.isna(price) or pd.isna(distancia):
        return 0
    if float(price) > float(usuario["budget"]):
        return 0
    if float(distancia) > float(usuario["radio"]):
        return 0
    if usuario["pets"] and not apt["pet_friendly"]:
        return 0

    requeridos  = set(texto_a_lista(usuario["amenities_req"]))
    disponibles = set(texto_a_lista(apt["amenities"]))

    if requeridos:
        peso_total = sum(_AMENITY_WEIGHTS.get(a, 0.50) for a in requeridos)
        peso_match = sum(_AMENITY_WEIGHTS.get(a, 0.50) for a in requeridos & disponibles)
        amenity_match = peso_match / peso_total
    else:
        amenity_match = 1.0

    price_score    = 1 - abs(apt["price"] - usuario["budget"]) / usuario["budget"] * 0.5
    location_score = 1 - apt["distancia"] / usuario["radio"]
    amenity_score  = amenity_match
    size_score     = 1 - abs(apt["size"] - usuario["size_deseado"]) / usuario["size_deseado"] * 0.5
    bedroom_score  = 1 - abs(apt["bedrooms"] - usuario["bedrooms_deseado"]) / usuario["bedrooms_deseado"] * 0.5
    pet_score      = 1

    secondary_score = 0.35 * amenity_score + 0.35 * size_score + 0.20 * bedroom_score + 0.10 * pet_score
    peso = 0.40 * price_score + 0.30 * location_score + 0.30 * secondary_score
    return round(max(0, min(1, peso)), 3)


def buscar_compatibles(entidades):
    apartamentos = cargar_tabla("apartamentos")
    usuario = {
        "budget": entidades["budget"], "radio": entidades["radio"],
        "pets": entidades["pets"], "amenities_req": ",".join(entidades["amenities_req"]),
        "size_deseado": entidades["size_deseado"], "bedrooms_deseado": entidades["bedrooms_deseado"],
        "zona": entidades.get("zona"),
    }
    resultados = []
    for _, apt in apartamentos.iterrows():
        peso = calcular_peso(usuario, apt)
        if peso > 0:
            resultados.append({
                "nombre":        apt["nombre"],
                "zona":          apt["zona"],
                "barrio":        apt.get("barrio", "") or "",
                "precio":        apt["price"],
                "distancia":     apt["distancia"],
                "amenities":     apt["amenities"],
                "size":          apt["size"],
                "bedrooms":      apt["bedrooms"],
                "pet_friendly":  apt["pet_friendly"],
                "latitud":       apt.get("latitud"),
                "longitud":      apt.get("longitud"),
                "url":           apt.get("url", ""),
                "descripcion":   apt.get("descripcion", ""),
                "imagen":        apt.get("imagen", ""),
                "compatibilidad": peso,
            })
    resultados.sort(key=lambda x: x["compatibilidad"], reverse=True)

    barrio_pedido = entidades.get("barrio")
    if barrio_pedido:
        en_barrio = [r for r in resultados if barrio_pedido in r["barrio"].lower()]
        if en_barrio:
            return en_barrio, None
        aviso = (
            f"No encontré compatibles en el barrio **{barrio_pedido.title()}**. "
            f"Mostrando alternativas en la zona."
        )
        zona_pedida = entidades.get("zona")
        if zona_pedida:
            en_zona = [r for r in resultados if r["zona"] == zona_pedida]
            return (en_zona if en_zona else resultados), aviso
        return resultados, aviso

    zona_pedida = entidades.get("zona")
    if zona_pedida:
        en_zona = [r for r in resultados if r["zona"] == zona_pedida]
        if en_zona:
            return en_zona, None
        razones = []
        if entidades.get("pets"):
            razones.append("ningún apartamento pet_friendly")
        if entidades.get("amenities_req"):
            razones.append(f"amenities requeridos ({', '.join(entidades['amenities_req'])})")
        razon_str = " y ".join(razones) if razones else "las restricciones aplicadas"
        aviso = (
            f"No encontré apartamentos compatibles en **{zona_pedida}** "
            f"por {razon_str}. Mostrando las mejores alternativas en otras zonas."
        )
        return resultados, aviso

    return resultados, None


def construir_matriz():
    usuarios     = cargar_tabla("usuarios")
    apartamentos = cargar_tabla("apartamentos")
    if usuarios.empty or apartamentos.empty:
        return None, usuarios, apartamentos
    matriz = []
    for _, u in usuarios.iterrows():
        fila = [calcular_peso(u, apt) for _, apt in apartamentos.iterrows()]
        matriz.append(fila)
    W = pd.DataFrame(matriz, index=usuarios["id"], columns=apartamentos["id"])
    return W, usuarios, apartamentos


def ejecutar_matching():
    W, usuarios, apartamentos = construir_matriz()
    if W is None:
        return None, None

    C = W.copy()
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            C.iloc[i, j] = 9999 if C.iloc[i, j] == 0 else 1 - C.iloc[i, j]

    filas, columnas = linear_sum_assignment(C)
    limpiar_asignaciones()

    resultados = []
    for i, j in zip(filas, columnas):
        peso = W.iloc[i, j]
        if peso > 0:
            uid = int(W.index[i])
            aid = int(W.columns[j])
            guardar_asignacion(uid, aid, float(peso))
            resultados.append({
                "usuario":      usuarios.loc[usuarios["id"] == uid, "nombre"].values[0],
                "apartamento":  apartamentos.loc[apartamentos["id"] == aid, "nombre"].values[0],
                "peso": peso,
            })
    return W, pd.DataFrame(resultados)


def ejecutar_matching_maximo():
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
            resultados.append({
                "usuario":     usuarios.loc[usuarios["id"] == uid, "nombre"].values[0],
                "apartamento": apartamentos.loc[apartamentos["id"] == aid, "nombre"].values[0],
                "peso":        peso,
            })

    return W, pd.DataFrame(resultados)


# ─── Visualización ────────────────────────────────────────────────────────────

def crear_mapa_folium(compatibles, top3):
    import folium

    top3_nombres = [a["nombre"] for a in top3]
    con_coords   = [a for a in compatibles if a.get("latitud") and a.get("longitud")]
    if not con_coords:
        return None

    lats   = [a["latitud"]  for a in con_coords]
    lons   = [a["longitud"] for a in con_coords]
    centro = [sum(lats) / len(lats), sum(lons) / len(lons)]

    m = folium.Map(location=centro, zoom_start=13, tiles="CartoDB positron")

    rank_colors = {0: "orange", 1: "lightgray", 2: "beige"}
    rank_labels = {0: "★ #1",   1: "★ #2",      2: "★ #3"}

    for apt in reversed(con_coords):
        es_top = apt["nombre"] in top3_nombres
        rank   = top3_nombres.index(apt["nombre"]) if es_top else -1
        color  = rank_colors.get(rank, "cadetblue")
        pct    = round(apt["compatibilidad"] * 100)
        barrio = apt.get("barrio") or apt["zona"]
        label  = rank_labels.get(rank, "")

        popup_html = f"""
<div style="font-family:'Segoe UI',Arial,sans-serif;min-width:210px;padding:4px 2px;">
  <div style="font-size:13px;font-weight:700;color:#0F172A;margin-bottom:4px;">{label} {apt['nombre']}</div>
  <div style="font-size:15px;font-weight:700;color:#0F766E;margin-bottom:6px;">
    ${apt['precio']:,.0f}<span style="font-size:11px;color:#94A3B8;">/mes</span>
  </div>
  <div style="font-size:12px;color:#475569;line-height:1.7;">
    <b>Barrio:</b> {barrio}<br><b>Zona:</b> {apt['zona']}<br>
    <b>Tamaño:</b> {apt['size']} m² · {apt['bedrooms']} hab<br>
    <b>Dist. TM:</b> {apt['distancia']} km<br>
    <b>Match:</b> <span style="color:{'#059669' if pct>=80 else '#0F766E' if pct>=60 else '#D97706'};font-weight:700;">{pct}%</span>
    {'<br><b>Pet friendly</b>' if apt['pet_friendly'] else ''}
  </div>
  {'<div style="margin-top:8px;"><a href="' + apt["url"] + '" target="_blank" style="color:#0F766E;font-size:12px;font-weight:600;">Ver listing →</a></div>' if apt.get("url") else ''}
</div>"""

        folium.Marker(
            location=[apt["latitud"], apt["longitud"]],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{'★ ' if es_top else ''}{apt['nombre']} — {pct}% match",
            icon=folium.Icon(color=color, icon="home", prefix="fa"),
        ).add_to(m)

    return m


def visualizar_grafo_bipartito(compatibles, top3, entidades):
    """Returns (html_string, height_px) or None."""
    import json

    MAX_SHOW = 15
    mostrar  = compatibles[:MAX_SHOW]
    n        = len(mostrar)
    if n == 0:
        return None

    top3_nombres = [a["nombre"] for a in top3]
    remaining    = len(compatibles) - MAX_SHOW if len(compatibles) > MAX_SHOW else 0

    apt_data = []
    for apt in mostrar:
        rank   = top3_nombres.index(apt["nombre"]) if apt["nombre"] in top3_nombres else -1
        nombre = apt["nombre"]
        if len(nombre) > 22:
            nombre = nombre[:20] + "…"
        apt_data.append({
            "nombre":    nombre,
            "zona":      apt["zona"],
            "barrio":    apt.get("barrio", ""),
            "precio":    apt["precio"],
            "size":      apt["size"],
            "bedrooms":  apt["bedrooms"],
            "distancia": round(float(apt["distancia"]), 1),
            "pet":       bool(apt["pet_friendly"]),
            "amenities": apt["amenities"] or "",
            "compat":    apt["compatibilidad"],
            "isTop":     rank >= 0,
            "rank":      rank,
        })

    user_data = {
        "budget": entidades["budget"],
        "zona":   entidades.get("zona") or "Todas",
        "radio":  entidades.get("radio", 5.0),
        "pets":   bool(entidades.get("pets", False)),
    }

    H  = min(720, max(480, n * 50 + 100))
    CH = H + 24

    RH = (
        '<div id="remaining">+ ' + str(remaining) + ' compatibles adicionales no mostrados</div>'
        if remaining else ""
    )

    APT_JSON  = json.dumps(apt_data,  ensure_ascii=False)
    USER_JSON = json.dumps(user_data, ensure_ascii=False)

    TMPL = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#050A14;font-family:'Segoe UI',system-ui,sans-serif;overflow:hidden;}
#wrap{position:relative;width:100%;height:__H__px;}
svg{display:block;}
#tip{
  position:fixed;display:none;pointer-events:none;
  background:rgba(5,10,20,.96);border:1px solid rgba(94,234,212,.22);
  border-radius:12px;padding:12px 16px;color:#CBD5E1;
  font-size:12px;line-height:1.8;max-width:240px;
  backdrop-filter:blur(16px);z-index:9999;
  box-shadow:0 16px 48px rgba(0,0,0,.65);
}
#tip-nm{font-size:13px;font-weight:700;color:#5EEAD4;margin-bottom:7px;}
#hdr{
  position:absolute;top:12px;left:50%;transform:translateX(-50%);
  text-align:center;pointer-events:none;white-space:nowrap;
}
#hdr-t{color:#CBD5E1;font-size:12.5px;font-weight:600;letter-spacing:.04em;}
#hdr-s{color:#1E3A5F;font-size:9px;letter-spacing:.1em;margin-top:3px;text-transform:uppercase;}
#legend{
  position:absolute;bottom:12px;right:12px;
  background:rgba(5,10,20,.84);border:1px solid rgba(255,255,255,.05);
  border-radius:10px;padding:10px 14px;font-size:10px;color:#475569;
  backdrop-filter:blur(8px);
}
.li{display:flex;align-items:center;gap:8px;margin-bottom:4px;}
.li:last-child{margin-bottom:0;}
.dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
.ln{width:22px;height:2px;border-radius:2px;flex-shrink:0;}
#remaining{position:absolute;bottom:14px;left:12px;color:#1E3A5F;font-size:9px;letter-spacing:.07em;}
</style>
</head>
<body>
<div id="wrap">
  <div id="hdr">
    <div id="hdr-t">G = (U &cup; O, E, w) &nbsp;&mdash;&nbsp; Grafo Bipartito Ponderado</div>
    <div id="hdr-s">hover para detalles &nbsp;&middot;&nbsp; nodos interactivos</div>
  </div>
  <div id="tip"><div id="tip-nm"></div><div id="tip-bd"></div></div>
  <div id="legend">
    <div class="li"><div class="dot" style="background:#14B8A6"></div>Buscador (U)</div>
    <div class="li"><div class="dot" style="background:#D97706"></div>TOP 1</div>
    <div class="li"><div class="dot" style="background:#94A3B8"></div>TOP 2</div>
    <div class="li"><div class="dot" style="background:#92400E"></div>TOP 3</div>
    <div class="li"><div class="dot" style="background:#3B82F6;opacity:.55"></div>Compatible</div>
    <div class="li"><div class="ln" style="background:#0F766E"></div>Arista TOP + partículas</div>
    <div class="li"><div class="ln" style="background:#1E293B"></div>Arista regular</div>
  </div>
  __RH__
  <svg id="g" width="100%" height="__H__" viewBox="0 0 920 __H__" preserveAspectRatio="xMidYMid meet">
    <defs>
      <radialGradient id="ug" cx="35%" cy="35%">
        <stop offset="0%" stop-color="#2DD4BF"/>
        <stop offset="100%" stop-color="#0D9488"/>
      </radialGradient>
      <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
        <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
      <filter id="glow2" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    <g id="eg"></g>
    <g id="ng"></g>
    <g id="lg"></g>
  </svg>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>
(function(){
var apts = __APT_JSON__;
var user = __USER_JSON__;
var H = __H__;
var UX = 125, UY = H / 2;
var AX = 665;
var n  = apts.length;
var sp = H / (n + 1);
var NS   = 'http://www.w3.org/2000/svg';
var XLNS = 'http://www.w3.org/1999/xlink';
var RC = ['#D97706','#94A3B8','#92400E'];
var RS = ['#F59E0B','#CBD5E1','#C2410C'];

function mk(tag, attrs) {
  var e = document.createElementNS(NS, tag);
  if (attrs) Object.keys(attrs).forEach(function(k){ e.setAttribute(k, attrs[k]); });
  return e;
}

var eg  = document.getElementById('eg');
var ng  = document.getElementById('ng');
var lg  = document.getElementById('lg');
var tip = document.getElementById('tip');
var tNm = document.getElementById('tip-nm');
var tBd = document.getElementById('tip-bd');

var aptY = apts.map(function(_, i){ return sp * (i + 1); });

// U / O labels
var uL = mk('text',{x:UX,y:UY-50,'text-anchor':'middle','font-size':11,'font-weight':'700',fill:'#5EEAD4','font-family':'Segoe UI','letter-spacing':'.06em'});
uL.textContent='U'; lg.appendChild(uL);
var oL = mk('text',{x:AX+78,y:Math.min(38,sp*0.5),'text-anchor':'middle','font-size':11,'font-weight':'700',fill:'#334155','font-family':'Segoe UI','letter-spacing':'.06em'});
oL.textContent='O'; lg.appendChild(oL);

// ── Edges ─────────────────────────────────────────────────────────────────
apts.forEach(function(apt, i){
  var ay  = aptY[i];
  var cx1 = UX + 190, cy1 = UY;
  var cx2 = AX - 190, cy2 = ay;
  var d   = 'M'+UX+' '+UY+' C'+cx1+' '+cy1+','+cx2+' '+cy2+','+AX+' '+ay;
  var pid = 'ep'+i;
  var isT = apt.isTop;
  var sw  = isT ? (apt.rank===0?2.6:apt.rank===1?2.1:1.8) : 0.65;
  var opa = isT ? 0.88 : 0.17;
  var pA  = {id:pid,d:d,fill:'none',stroke:isT?'#0F766E':'#1E293B','stroke-width':sw,opacity:0,'stroke-linecap':'round'};
  if(isT) pA.filter='url(#glow2)';
  var path = mk('path', pA);
  eg.appendChild(path);
  var len = path.getTotalLength ? path.getTotalLength() : 720;
  path.setAttribute('stroke-dasharray', len);
  path.setAttribute('stroke-dashoffset', len);
  gsap.to(path,{strokeDashoffset:0,opacity:opa,delay:0.18+i*0.04,duration:isT?0.75:0.33,ease:'power2.out'});

  if(isT){
    var ml  = len * 0.5;
    var mid = path.getPointAtLength ? path.getPointAtLength(ml) : {x:(UX+AX)/2,y:(UY+ay)/2};
    var lg2 = mk('g',{});
    var lbg = mk('rect',{x:mid.x-25,y:mid.y-12,width:50,height:22,rx:5,fill:'#050A14',stroke:'#0F766E','stroke-width':1,opacity:0});
    var ltx = mk('text',{x:mid.x,y:mid.y+5.5,'text-anchor':'middle','font-size':9.5,'font-weight':'700',fill:'#5EEAD4','font-family':'Segoe UI',opacity:0});
    ltx.textContent='w='+apt.compat.toFixed(2);
    lg2.appendChild(lbg); lg2.appendChild(ltx); lg.appendChild(lg2);
    gsap.to([lbg,ltx],{opacity:1,delay:0.88+i*0.05,duration:0.38});

    for(var p=0;p<4;p++){
      var pc = mk('circle',{r:p===0?3:2,fill:'#5EEAD4',opacity:0});
      var am = document.createElementNS(NS,'animateMotion');
      am.setAttribute('dur',(1.8+p*0.55)+'s');
      am.setAttribute('repeatCount','indefinite');
      am.setAttribute('begin',(p*0.45)+'s');
      var mp = document.createElementNS(NS,'mpath');
      mp.setAttributeNS(XLNS,'href','#'+pid);
      mp.setAttribute('href','#'+pid);
      am.appendChild(mp); pc.appendChild(am); eg.appendChild(pc);
      (function(c){ gsap.to(c,{opacity:0.9,delay:1.05+i*0.05,duration:0.3}); })(pc);
    }
  }
});

// ── User node ─────────────────────────────────────────────────────────────
var uG  = mk('g',{cursor:'pointer',opacity:0});
var uRn = mk('circle',{cx:UX,cy:UY,r:42,fill:'rgba(13,148,136,.06)',stroke:'rgba(94,234,212,.1)','stroke-width':1});
var uCi = mk('circle',{cx:UX,cy:UY,r:27,fill:'url(#ug)',stroke:'#5EEAD4','stroke-width':1.5,filter:'url(#glow)'});
var uTU = mk('text',{x:UX,y:UY-4,'text-anchor':'middle','font-size':11.5,'font-weight':'700',fill:'white','font-family':'Segoe UI'});
uTU.textContent='U';
var uTB = mk('text',{x:UX,y:UY+12,'text-anchor':'middle','font-size':8.5,fill:'#5EEAD4','font-family':'Segoe UI'});
uTB.textContent='$'+(user.budget/1e6).toFixed(1)+'M';
[uRn,uCi,uTU,uTB].forEach(function(e){uG.appendChild(e);});
ng.appendChild(uG);
gsap.to(uG,{opacity:1,delay:0.05,duration:0.5,ease:'back.out(1.7)'});
gsap.from(uCi,{attr:{r:0},delay:0.05,duration:0.55,ease:'back.out(2)'});
gsap.to(uRn,{attr:{r:52},opacity:0,duration:2.4,ease:'power1.out',repeat:-1,repeatDelay:0.8});

uG.addEventListener('mouseenter',function(e){
  gsap.to(uCi,{attr:{r:32},duration:0.22,ease:'power2.out'});
  tNm.innerHTML='Buscador (U)';
  tBd.innerHTML='<b>Presupuesto:</b> $'+user.budget.toLocaleString()+'/mes<br><b>Zona:</b> '+user.zona+'<br><b>Radio:</b> '+user.radio+' km<br><b>Mascotas:</b> '+(user.pets?'Sí':'No');
  tip.style.display='block';
});
uG.addEventListener('mousemove',function(e){tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY-8)+'px';});
uG.addEventListener('mouseleave',function(){gsap.to(uCi,{attr:{r:27},duration:0.22});tip.style.display='none';});

// ── Apartment nodes ────────────────────────────────────────────────────────
apts.forEach(function(apt, i){
  var ay  = aptY[i];
  var isT = apt.isTop;
  var rk  = apt.rank;
  var col = rk>=0 ? RC[rk] : '#1E3A5F';
  var stk = rk>=0 ? RS[rk] : '#334155';
  var r   = isT ? 21 : 13;
  var g   = mk('g',{cursor:'pointer',opacity:0});

  if(isT){
    var rng = mk('circle',{cx:AX,cy:ay,r:r+9,fill:col+'1A',stroke:'none'});
    g.appendChild(rng);
  }
  var ci = mk('circle',{cx:AX,cy:ay,r:r,fill:col,stroke:stk,'stroke-width':isT?1.5:1});
  if(isT) ci.setAttribute('filter','url(#glow2)');
  g.appendChild(ci);

  if(isT){
    var rt=mk('text',{x:AX,y:ay+5,'text-anchor':'middle','font-size':10.5,'font-weight':'700',fill:'white','font-family':'Segoe UI'});
    rt.textContent='#'+(rk+1); g.appendChild(rt);
  }

  var xl=AX+r+10;
  var nm=mk('text',{x:xl,y:ay-(isT?4:3),'font-size':isT?10.5:9,'font-weight':isT?'700':'400',fill:isT?'#E2E8F0':'#334155','font-family':'Segoe UI'});
  nm.textContent=apt.nombre; g.appendChild(nm);
  var zn=mk('text',{x:xl,y:ay+(isT?10:9),'font-size':8.5,fill:isT?'#64748B':'#1E3A5F','font-family':'Segoe UI'});
  zn.textContent='$'+(apt.precio/1e6).toFixed(1)+'M · '+apt.bedrooms+'hab · '+Math.round(apt.compat*100)+'%';
  g.appendChild(zn);
  ng.appendChild(g);

  gsap.to(g,{opacity:1,delay:0.12+i*0.05,duration:0.38,ease:'back.out(1.4)'});
  gsap.from(ci,{attr:{r:0},delay:0.12+i*0.05,duration:0.38,ease:'back.out(2)'});

  (function(G,C,R,A){
    G.addEventListener('mouseenter',function(e){
      gsap.to(C,{attr:{r:R+5},duration:0.2,ease:'power2.out'});
      tNm.innerHTML=A.nombre;
      tBd.innerHTML=
        '<b>Precio:</b> $'+A.precio.toLocaleString()+'/mes<br>'+
        '<b>Zona:</b> '+A.zona+(A.barrio?' &middot; '+A.barrio:'')+'<br>'+
        '<b>Tama&ntilde;o:</b> '+A.size+' m&sup2; &middot; '+A.bedrooms+' hab<br>'+
        '<b>Dist. TM:</b> '+A.distancia+' km<br>'+
        '<b>Amenities:</b> '+(A.amenities||'&mdash;')+'<br>'+
        '<b>Compatibilidad:</b> '+Math.round(A.compat*100)+'%'+
        (A.pet?'<br><b>Pet friendly</b>':'');
      tip.style.display='block';
    });
    G.addEventListener('mousemove',function(e){tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY-8)+'px';});
    G.addEventListener('mouseleave',function(){gsap.to(C,{attr:{r:R},duration:0.2});tip.style.display='none';});
  })(g,ci,r,apt);
});
})();
</script>
</body></html>"""

    html = (TMPL
            .replace("__APT_JSON__",  APT_JSON)
            .replace("__USER_JSON__", USER_JSON)
            .replace("__H__",         str(H))
            .replace("__RH__",        RH))

    return html, CH


# ═══════════════════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Aptmatch Bogotá",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

crear_tablas()
cargar_apartamentos_iniciales()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Josefin+Sans:wght@300;400;500;600;700&display=swap');

/* ── BASE ── */
html, body, [class*="css"] { font-family: 'Josefin Sans', sans-serif; color: #0F172A; }
.stApp { background: #F8FAFC !important; }
h1, h2, h3 { font-family: 'Cinzel', serif !important; color: #0F172A !important; }

/* ── SIDEBAR — WHITE ── */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,.04) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: #374151 !important; }
section[data-testid="stSidebar"] label { color: #475569 !important; }
section[data-testid="stSidebar"] svg {
    color: #94A3B8 !important;
    fill: #94A3B8 !important;
    stroke: #94A3B8 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    color: #374151 !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] * { color: #374151 !important; }

/* Sidebar brand */
.sb-brand {
    display: flex; align-items: center; gap: .75rem;
    padding: 1.5rem 1.25rem 1.25rem;
    border-bottom: 1px solid #F1F5F9;
    margin-bottom: .5rem;
}
.sb-icon {
    width: 40px; height: 40px; border-radius: 11px;
    background: linear-gradient(135deg,#0F766E 0%,#0D9488 100%);
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(15,118,110,.35);
}
.sb-icon svg { stroke: white !important; fill: none !important; color: white !important; }
.sb-title {
    font-family: 'Cinzel', serif !important; font-size: 1rem;
    font-weight: 700; color: #0F172A !important; letter-spacing: .03em; line-height: 1.2;
}
.sb-sub {
    font-family: 'Josefin Sans', sans-serif; font-size: .65rem;
    color: #94A3B8 !important; letter-spacing: .07em; margin-top: .1rem;
}
.sb-nav-label {
    font-family: 'Josefin Sans', sans-serif !important; font-size: .62rem !important;
    font-weight: 700 !important; color: #94A3B8 !important;
    text-transform: uppercase !important; letter-spacing: .12em !important;
    padding: .75rem 1.25rem .35rem !important; margin: 0 !important;
}
.sb-footer {
    padding: 1rem 1.25rem; border-top: 1px solid #F1F5F9; margin-top: auto;
    font-family: 'Josefin Sans', sans-serif; font-size: .7rem;
    color: #94A3B8 !important; line-height: 1.6;
}

/* Sidebar radio as nav pills */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    padding: 0 .75rem; display: flex; flex-direction: column; gap: 2px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: .62rem .875rem !important; border-radius: 10px !important;
    transition: background 180ms, color 180ms !important; cursor: pointer !important;
    font-family: 'Josefin Sans', sans-serif !important; font-size: .875rem !important;
    font-weight: 500 !important; color: #475569 !important; margin-bottom: 1px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #F8FAFC !important; color: #0F766E !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(15,118,110,.09) !important;
    color: #0F766E !important; font-weight: 700 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] input:checked + div > div {
    background: #0F766E !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] div[data-baseweb="radio"] > div:first-child {
    border-color: #DDE3EC !important;
}

/* ── HERO ── */
.hero-wrap {
    text-align: center; padding: 5.5rem 2rem 2rem;
    max-width: 700px; margin: 0 auto;
    animation: heroFadeIn 650ms cubic-bezier(.22,1,.36,1) both;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: .5rem;
    background: rgba(15,118,110,.06); color: #0F766E;
    border: 1px solid rgba(15,118,110,.16); border-radius: 100px;
    padding: .32rem 1.15rem; font-family: 'Josefin Sans', sans-serif;
    font-size: .64rem; font-weight: 700; letter-spacing: .11em;
    text-transform: uppercase; margin-bottom: 2.25rem;
}
.hero-eyebrow-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #0F766E; opacity: .45; flex-shrink: 0;
}
.hero-title {
    font-family: 'Cinzel', serif !important;
    font-size: clamp(2.1rem, 4.8vw, 3.5rem) !important; font-weight: 700 !important;
    color: #0F172A !important; line-height: 1.16 !important;
    margin: 0 0 1.4rem !important; letter-spacing: -.025em !important;
}
.hero-accent       { color: #0F766E !important; }
.hero-accent-gold  { color: #D97706 !important; }
.hero-sub {
    font-family: 'Josefin Sans', sans-serif !important; font-size: 1rem !important;
    color: #64748B !important; line-height: 1.75 !important;
    margin: 0 auto 2.75rem !important; max-width: 520px;
}
.hero-hint {
    font-family: 'Josefin Sans', sans-serif !important; font-size: .63rem !important;
    font-weight: 700 !important; color: #CBD5E1 !important;
    text-transform: uppercase !important; letter-spacing: .14em !important;
    margin: 0 0 .8rem !important;
}

/* ── DETAIL BUTTON (below aptcard) ── */
div[data-testid="stChatMessage"] .stButton > button {
    border-radius: 0 0 18px 18px !important;
    border: 1px solid #E8EDF4 !important; border-top: 1px solid #F1F5F9 !important;
    background: #FAFCFF !important; color: #0F766E !important;
    font-family: 'Josefin Sans', sans-serif !important;
    font-size: .72rem !important; font-weight: 700 !important;
    letter-spacing: .05em !important; text-transform: uppercase !important;
    padding: .52rem 1rem !important;
    box-shadow: 0 4px 16px rgba(0,0,0,.05) !important;
    margin-top: -4px !important;
    transition: background 180ms, color 180ms !important;
}
div[data-testid="stChatMessage"] .stButton > button:hover {
    background: rgba(15,118,110,.07) !important; color: #0D6960 !important;
    border-color: rgba(15,118,110,.22) !important;
}

/* ── ANIMATIONS ── */
@keyframes heroFadeIn {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes chatIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
div[data-testid="stChatMessage"] {
    animation: chatIn 380ms cubic-bezier(.22,1,.36,1) both !important;
}

/* ── CHAT INPUT ── */
div[data-testid="stChatInput"] {
    border-top: 1px solid #E2E8F0 !important;
    background: rgba(255,255,255,.97) !important;
    backdrop-filter: blur(12px) !important;
}
div[data-testid="stChatInput"] textarea {
    border-radius: 14px !important; border: 1.5px solid #E2E8F0 !important;
    font-family: 'Josefin Sans', sans-serif !important; font-size: .9rem !important;
    background: #FAFAFA !important; color: #0F172A !important;
    transition: border-color 200ms, box-shadow 200ms !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: #0F766E !important;
    box-shadow: 0 0 0 3px rgba(15,118,110,.1) !important;
    background: white !important; outline: none !important;
}
div[data-testid="stChatInput"] textarea::placeholder { color: #94A3B8 !important; }

/* ── APTCARD — PropTech moderno ── */
.aptcard {
    background: white; border-radius: 18px; overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,.08);
    transition: box-shadow 260ms, transform 260ms;
    font-family: 'Josefin Sans', sans-serif;
    animation: chatIn 420ms cubic-bezier(.22,1,.36,1) both;
}
.aptcard:hover { box-shadow: 0 14px 44px rgba(0,0,0,.13); transform: translateY(-3px); }
.aptcard-photo-wrap {
    position: relative; height: 175px; background: #F1F5F9; overflow: hidden;
}
.aptcard-photo { width: 100%; height: 175px; object-fit: cover; display: block; }
.aptcard-placeholder {
    width: 100%; height: 175px; display: flex;
    align-items: center; justify-content: center;
}
.aptcard-badge-rank {
    position: absolute; top: .75rem; left: .75rem;
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    backdrop-filter: blur(4px);
}
.aptcard-badge-match {
    position: absolute; top: .75rem; right: .75rem;
    width: 52px; height: 52px; border-radius: 50%;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,.18));
}
.aptcard-match-inner {
    position: absolute; inset: 7px; border-radius: 50%;
    background: white; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    font-family: 'Josefin Sans', sans-serif; font-weight: 700; line-height: 1.1;
}
.aptcard-body { padding: .9rem 1rem .9rem; }
.aptcard-cta {
    display: block; margin-top: .8rem; padding: .55rem 1rem;
    background: #0F766E; color: white !important; text-decoration: none !important;
    border-radius: 9px; font-family: 'Josefin Sans', sans-serif;
    font-size: .72rem; font-weight: 700; letter-spacing: .07em;
    text-transform: uppercase; text-align: center; transition: background 200ms;
}
.aptcard-cta:hover { background: #0D6960 !important; color: white !important; }
.cc-name { font-family: 'Cinzel', serif; font-size: .95rem; font-weight: 700; color: #0F172A; line-height: 1.3; margin-bottom: .12rem; }
.cc-zone { font-size: .68rem; color: #0F766E; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; }
.cc-barrio { font-size: .67rem; color: #94A3B8; }
.cc-price { font-family: 'Cinzel', serif; font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: .45rem 0; line-height: 1.15; }
.cc-price-sub { font-family: 'Josefin Sans', sans-serif; font-size: .64rem; font-weight: 400; color: #94A3B8; }
.cc-stats {
    display: flex; flex-wrap: wrap; gap: .35rem .6rem;
    font-size: .71rem; color: #475569;
    padding: .4rem .65rem; background: #F8FAFC;
    border-radius: 8px; margin-bottom: .45rem;
}
.cc-amenities { margin-bottom: .4rem; display: flex; flex-wrap: wrap; gap: .25rem; }
.cc-amenity-tag {
    display: inline-block; background: rgba(15,118,110,.07); color: #0F766E;
    border: 1px solid rgba(15,118,110,.15); border-radius: 20px;
    padding: .1rem .45rem; font-family: 'Josefin Sans', sans-serif;
    font-size: .64rem; font-weight: 600; letter-spacing: .03em;
}

/* ── CHAT PREF PILLS ── */
.chat-pill {
    display: inline-block; background: rgba(15,118,110,.07); color: #0F766E;
    border: 1px solid rgba(15,118,110,.18); border-radius: 20px;
    padding: .18rem .65rem; font-family: 'Josefin Sans', sans-serif;
    font-size: .72rem; font-weight: 600; margin: .1rem .12rem; letter-spacing: .03em;
}

/* ── MAIN CONTENT ── */
section[data-testid="stMain"] > div { padding-top: 0 !important; }

/* ── BUTTONS ── */
.stButton > button[kind="primary"] {
    background: #0F766E !important; border: none !important; color: white !important;
    font-family: 'Josefin Sans', sans-serif !important; font-weight: 700 !important;
    letter-spacing: .06em !important; text-transform: uppercase !important;
    font-size: .78rem !important; border-radius: 10px !important;
    padding: .6rem 1.5rem !important;
    box-shadow: 0 2px 8px rgba(15,118,110,.25) !important;
    transition: all 200ms ease !important; cursor: pointer !important;
}
.stButton > button[kind="primary"]:hover {
    background: #0D6960 !important; transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px rgba(15,118,110,.38) !important;
}
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    border: 1.5px solid #E2E8F0 !important; color: #475569 !important;
    background: white !important; font-family: 'Josefin Sans', sans-serif !important;
    font-weight: 600 !important; font-size: .78rem !important;
    border-radius: 10px !important; padding: .58rem 1.2rem !important;
    transition: all 200ms ease !important; cursor: pointer !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
    border-color: #0F766E !important; color: #0F766E !important;
    background: rgba(15,118,110,.04) !important;
}
button[data-testid="stFormSubmitButton"] > button {
    background: #0F766E !important; border: none !important; color: white !important;
    font-family: 'Josefin Sans', sans-serif !important; font-weight: 700 !important;
    letter-spacing: .08em !important; text-transform: uppercase !important;
    font-size: .78rem !important; border-radius: 10px !important;
    padding: .65rem 2rem !important; width: 100% !important;
    box-shadow: 0 2px 8px rgba(15,118,110,.25) !important;
    transition: all 200ms ease !important; cursor: pointer !important;
}
button[data-testid="stFormSubmitButton"] > button:hover {
    background: #0D6960 !important; transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px rgba(15,118,110,.38) !important;
}
a[data-testid="stLinkButton"] button {
    border: 1.5px solid #0F766E !important; color: #0F766E !important;
    font-family: 'Josefin Sans', sans-serif !important; font-weight: 700 !important;
    border-radius: 10px !important; font-size: .75rem !important;
    letter-spacing: .06em !important; text-transform: uppercase !important;
    transition: all 200ms ease !important;
}
a[data-testid="stLinkButton"] button:hover { background: #0F766E !important; color: white !important; }

/* ── INPUTS ── */
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #FAFAFA !important; border-radius: 10px !important;
    border: 1.5px solid #DDE3EC !important; color: #0F172A !important;
    font-family: 'Josefin Sans', sans-serif !important; font-size: .9rem !important;
    transition: border-color 200ms, box-shadow 200ms !important;
}
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #0F766E !important;
    box-shadow: 0 0 0 3px rgba(15,118,110,.1) !important; background: white !important;
}

/* ── SELECT ── */
div[data-baseweb="select"] > div {
    background: #FAFAFA !important; border-radius: 10px !important;
    border: 1.5px solid #DDE3EC !important; font-family: 'Josefin Sans', sans-serif !important;
}
div[data-baseweb="select"]:focus-within > div {
    border-color: #0F766E !important; box-shadow: 0 0 0 3px rgba(15,118,110,.1) !important;
}
li[role="option"]:hover, li[role="option"][aria-selected="true"] {
    background: rgba(15,118,110,.08) !important; color: #0F766E !important;
}
span[data-baseweb="tag"] {
    background: rgba(15,118,110,.1) !important; color: #0F766E !important; border-radius: 6px !important;
}

/* ── METRICS ── */
div[data-testid="stMetric"] {
    background: white !important; border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important; padding: 1rem 1.25rem !important;
}
div[data-testid="stMetricValue"] {
    color: #0F766E !important; font-family: 'Cinzel', serif !important; font-weight: 700 !important;
}
div[data-testid="stMetricLabel"] {
    color: #64748B !important; font-size: .72rem !important;
    text-transform: uppercase; letter-spacing: .08em;
}

/* ── EXPANDER ── */
div[data-testid="stExpander"] {
    background: white !important; border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important; overflow: hidden !important;
}
div[data-testid="stExpander"] summary {
    font-family: 'Josefin Sans', sans-serif !important; font-weight: 600 !important;
    color: #0F172A !important; padding: .75rem 1rem !important;
}

/* ── TABS ── */
button[data-baseweb="tab"] {
    font-family: 'Josefin Sans', sans-serif !important; font-weight: 600 !important;
    color: #64748B !important; text-transform: uppercase !important; font-size: .75rem !important;
}
button[data-baseweb="tab"][aria-selected="true"] { color: #0F766E !important; }
div[data-baseweb="tab-highlight"] { background: #0F766E !important; }
div[data-baseweb="tab-border"] { background: #E2E8F0 !important; }

/* ── ALERTS ── */
div[data-testid="stAlert"] { border-radius: 12px !important; font-family: 'Josefin Sans', sans-serif !important; }

/* ── DATAFRAME ── */
div[data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important; border: 1px solid #E2E8F0 !important;
}

/* ── CARDS (container border) ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important; border: 1px solid #E2E8F0 !important;
    border-radius: 18px !important; overflow: hidden !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.04) !important;
    animation: chatIn 280ms ease-out both;
}

/* ── TEXT FIX (no !important on styled elements) ── */
div[data-testid="stMain"] div[data-testid="stMarkdownContainer"] p:not([style]) { color: #0F172A !important; }
div[data-testid="stMain"] div[data-testid="stMarkdownContainer"] li:not([style]) { color: #0F172A !important; }
div[data-testid="stMain"] div[data-testid="stMarkdownContainer"] strong:not([style]) { color: #0F172A !important; }
div[data-testid="stMain"] label[data-testid="stWidgetLabel"],
div[data-testid="stMain"] div[data-testid="stWidgetLabel"] p,
div[data-testid="stMain"] div[class*="stRadio"] label,
div[data-testid="stMain"] div[class*="stCheckbox"] label,
div[data-testid="stMain"] div[class*="stMultiSelect"] label,
div[data-testid="stMain"] div[class*="stSelectbox"] label,
div[data-testid="stMain"] div[class*="stTextArea"] label,
div[data-testid="stMain"] div[class*="stTextInput"] label,
div[data-testid="stMain"] div[class*="stNumberInput"] label { color: #374151 !important; }
div[data-testid="stMain"] div[data-testid="stText"] { color: #0F172A !important; }
div[data-testid="stMain"] div[data-testid="stAlert"] p { color: #0F172A !important; }

/* ── MISC ── */
hr { border-color: #E2E8F0 !important; margin: 1.5rem 0 !important; }
a { color: #0F766E !important; }
a:hover { color: #0D6960 !important; }
</style>
""", unsafe_allow_html=True)


# ── Chat helpers ──────────────────────────────────────────────────────────────

@st.dialog("Detalle del apartamento", width="large")
def _detalle_apartamento(apt: dict, fotos: list):
    nombre        = apt.get("nombre", "Apartamento")
    zona          = apt.get("zona", "")
    barrio        = apt.get("barrio", "")
    precio        = apt.get("precio", 0)
    desc          = (apt.get("descripcion") or "").strip()
    amenities_str = apt.get("amenities", "")
    pct           = round(apt.get("compatibilidad", 0) * 100)
    match_clr     = "#059669" if pct >= 80 else "#0F766E" if pct >= 60 else "#D97706"
    loc           = f"{zona}{' · ' + barrio if barrio else ''}"

    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown(
            f'<div style="font-family:\'Cinzel\',serif;font-size:1.3rem;font-weight:700;'
            f'color:#0F172A;line-height:1.2;margin-bottom:.2rem;">{nombre}</div>'
            f'<div style="font-family:\'Josefin Sans\',sans-serif;font-size:.74rem;'
            f'color:#0F766E;font-weight:700;text-transform:uppercase;letter-spacing:.07em;">{loc}</div>',
            unsafe_allow_html=True,
        )
    with hcol2:
        st.markdown(
            f'<div style="text-align:right;">'
            f'<div style="font-family:\'Cinzel\',serif;font-size:1.45rem;font-weight:700;'
            f'color:#0F172A;line-height:1.1;">${precio:,.0f}</div>'
            f'<div style="font-family:\'Josefin Sans\',sans-serif;font-size:.64rem;color:#94A3B8;">'
            f'/mes &nbsp;·&nbsp; <span style="color:{match_clr};font-weight:700;">{pct}% match</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.divider()

    if fotos:
        if len(fotos) == 1:
            st.image(fotos[0], use_container_width=True)
        elif len(fotos) == 2:
            c1, c2 = st.columns(2)
            c1.image(fotos[0], use_container_width=True)
            c2.image(fotos[1], use_container_width=True)
        else:
            mc, sc = st.columns([2, 1])
            with mc:
                st.image(fotos[0], use_container_width=True)
            with sc:
                for f in fotos[1:4]:
                    st.image(f, use_container_width=True)

    st.markdown("<div style='height:.2rem'></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Área", f"{apt.get('size', '—')} m²")
    c2.metric("Habitaciones", apt.get("bedrooms", "—"))
    c3.metric("Dist. TM", f"{apt.get('distancia', '—')} km")
    c4.metric("Mascotas", "Sí" if apt.get("pet_friendly") else "No")

    if amenities_str:
        tags_html = "".join(
            f'<span class="cc-amenity-tag">{a.strip()}</span>'
            for a in amenities_str.split(",") if a.strip()
        )
        st.markdown(
            '<div style="margin:.8rem 0 .3rem;font-family:\'Josefin Sans\',sans-serif;'
            'font-size:.63rem;font-weight:700;color:#94A3B8;text-transform:uppercase;'
            'letter-spacing:.1em;">Amenities</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:.3rem;">{tags_html}</div>',
            unsafe_allow_html=True,
        )

    if desc:
        st.markdown(
            '<div style="margin:.85rem 0 .3rem;font-family:\'Josefin Sans\',sans-serif;'
            'font-size:.63rem;font-weight:700;color:#94A3B8;text-transform:uppercase;'
            'letter-spacing:.1em;">Descripción del inmueble</div>'
            f'<div style="font-family:\'Josefin Sans\',sans-serif;font-size:.84rem;'
            f'color:#475569;line-height:1.75;max-height:220px;overflow-y:auto;'
            f'padding-right:.5rem;">{desc}</div>',
            unsafe_allow_html=True,
        )
    elif not fotos:
        st.info("Sin descripción ni fotos disponibles para este apartamento.")


def _do_search(prompt: str):
    if not prompt.strip():
        return
    st.session_state.setdefault("chat_msgs", [])
    st.session_state["chat_msgs"].append({"role": "user", "content": prompt})

    ent = extraer_entidades(prompt)

    # Heredar parámetros del último mensaje del asistente si no se detectaron en el nuevo
    prev_results = [m for m in st.session_state["chat_msgs"]
                    if m.get("role") == "assistant" and m.get("type") == "results"]
    if prev_results:
        prev = prev_results[-1]["entidades"]
        heredados = []
        if not ent["budget"] and prev.get("budget"):
            ent["budget"]           = prev["budget"]
            ent["_budget_heredado"] = True
            heredados.append(f'presupuesto ${prev["budget"]:,.0f}')
        if not ent["amenities_req"] and prev.get("amenities_req"):
            ent["amenities_req"] = prev["amenities_req"]
            heredados.append("amenities")
        if ent["radio"] == 5.0 and prev.get("radio", 5.0) != 5.0:
            ent["radio"] = prev["radio"]
        if not ent["pets"] and prev.get("pets"):
            ent["pets"] = prev["pets"]
            heredados.append("mascotas")
        if not ent["zona"] and not ent["barrio"] and prev.get("zona"):
            ent["zona"]            = prev["zona"]
            ent["_zona_heredada"]  = True
            heredados.append(f'zona {prev["zona"]}')
        ent["_heredados"] = heredados

    if not ent["budget"]:
        ent["budget"] = 2_000_000
    if not ent["tipo"]:
        ent["tipo"] = "arriendo"

    todos, aviso = buscar_compatibles(ent)
    st.session_state["chat_msgs"].append({
        "role": "assistant", "type": "results",
        "entidades": ent, "todos": todos, "top3": todos[:3], "aviso_zona": aviso,
    })
    st.rerun()


def _render_assistant_msg(msg):
    ent   = msg["entidades"]
    todos = msg["todos"]
    top3  = msg["top3"]
    aviso = msg.get("aviso_zona")

    # Preference pills
    budget_str = f"${ent['budget']:,.0f}" if ent["budget"] else "—"
    pills_data = [("Zona", ent["zona"] or "Todas")]
    if ent.get("barrio"):
        pills_data.insert(0, ("Barrio", ent["barrio"].title()))
    pills_data += [("Presupuesto", budget_str), ("Radio", f"{ent['radio']} km")]
    if ent["pets"]:
        pills_data.append(("Mascotas", "Sí"))
    if ent["amenities_req"]:
        pills_data.append(("Amenities", ", ".join(ent["amenities_req"][:3])))
    if ent["bedrooms_deseado"]:
        pills_data.append(("Habitaciones", str(ent["bedrooms_deseado"])))

    pills_html = "".join(
        f'<span class="chat-pill"><b>{l}:</b> {v}</span>' for l, v in pills_data
    )
    heredados_lista = ent.get("_heredados", [])
    heredado_note = (
        f' <span style="font-size:.7rem;color:#94A3B8;font-style:italic;">'
        f'(recordé del mensaje anterior: {", ".join(heredados_lista)})</span>'
        if heredados_lista else ""
    )
    st.markdown(
        f'<div style="margin-bottom:.8rem;line-height:2.1;font-family:Josefin Sans,sans-serif;'
        f'font-size:.85rem;color:#475569;">Entendí esto: {pills_html}{heredado_note}</div>',
        unsafe_allow_html=True,
    )

    if aviso:
        st.warning(aviso)

    if not todos:
        budget_sug  = f"${int(ent['budget'] * 1.30):,}" if ent.get("budget") else "$2.600.000"
        radio_sug   = round(ent.get("radio", 5) * 1.6, 0)
        st.markdown(f"""
<div style="padding:1.2rem 1.4rem;background:#FFFBEB;border:1px solid #FDE68A;
  border-radius:14px;font-family:'Josefin Sans',sans-serif;">
  <div style="font-size:.85rem;color:#92400E;font-weight:700;margin-bottom:.35rem;">
    Sin resultados con esas restricciones
  </div>
  <div style="font-size:.78rem;color:#78350F;margin-bottom:.8rem;">
    Prueba uno de estos ajustes:
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:.4rem;">
    <span style="padding:.3rem .85rem;background:white;border:1.5px solid #FCD34D;
      border-radius:20px;font-size:.73rem;color:#92400E;font-weight:600;">
      Presupuesto hasta {budget_sug}
    </span>
    <span style="padding:.3rem .85rem;background:white;border:1.5px solid #FCD34D;
      border-radius:20px;font-size:.73rem;color:#92400E;font-weight:600;">
      Radio de {int(radio_sug)} km
    </span>
    <span style="padding:.3rem .85rem;background:white;border:1.5px solid #FCD34D;
      border-radius:20px;font-size:.73rem;color:#92400E;font-weight:600;">
      Buscar en toda Bogotá
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
        return

    n_top = len(top3)
    st.markdown(
        f'<p style="font-family:Josefin Sans,sans-serif;font-size:.9rem;color:#0F172A;margin:0 0 .9rem;">'
        f'Encontré <b>{len(todos)}</b> apartamentos compatibles. '
        f'Aquí están tus <b>top {n_top}</b>:</p>',
        unsafe_allow_html=True,
    )

    rank_colors  = ["#D97706", "#475569", "#B45309"]
    rank_shadows = ["rgba(217,119,6,.28)", "rgba(71,85,105,.22)", "rgba(180,83,9,.22)"]
    rank_names   = ["Mejor opción", "2ª opción", "3ª opción"]

    cols = st.columns(n_top, gap="medium")
    for i, (col, apt) in enumerate(zip(cols, top3)):
        pct       = round(apt["compatibilidad"] * 100)
        clr       = rank_colors[i]
        match_clr = "#059669" if pct >= 80 else "#0F766E" if pct >= 60 else "#D97706"
        fotos     = [u for u in apt.get("imagen", "").split(",") if u.startswith("http")]
        pet_ok    = bool(apt["pet_friendly"])

        amenity_html = "".join(
            f'<span class="cc-amenity-tag">{a.strip()}</span>'
            for a in apt["amenities"].split(",") if a.strip()
        ) if apt["amenities"] else ""

        _house_svg = (
            f'<svg width="38" height="38" viewBox="0 0 24 24" fill="none" '
            f'stroke="{clr}" stroke-width="1.4" opacity=".55">'
            f'<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
            f'<polyline points="9 22 9 12 15 12 15 22"/></svg>'
        )
        foto_url = fotos[0] if fotos else ""
        if foto_url:
            photo_block = (
                f'<img class="aptcard-photo" src="{foto_url}" alt="{apt["nombre"]}" '
                f'onerror="this.style.display=\'none\';'
                f'this.parentNode.style.background=\'linear-gradient(145deg,{clr}18,{clr}38)\';">'
            )
        else:
            photo_block = (
                f'<div class="aptcard-placeholder" '
                f'style="background:linear-gradient(145deg,{clr}18,{clr}38);">{_house_svg}</div>'
            )

        barrio_sep = (
            f'<span style="color:#CBD5E1;margin:0 .25rem;font-size:.6rem;">·</span>'
            f'<span class="cc-barrio">{apt["barrio"]}</span>'
            if apt.get("barrio") else ""
        )
        with col:
            st.markdown(f"""
<div class="aptcard">
  <div class="aptcard-photo-wrap">
    {photo_block}
    <div class="aptcard-badge-rank"
      style="background:{clr};box-shadow:0 3px 12px {rank_shadows[i]};">
      <span style="font-family:'Cinzel',serif;font-size:.82rem;font-weight:700;color:white;line-height:1;">{i+1}</span>
    </div>
    <div class="aptcard-badge-match"
      style="background:conic-gradient({match_clr} {pct}%, rgba(226,232,240,.9) {pct}%);">
      <div class="aptcard-match-inner" style="color:{match_clr};">
        <span style="font-size:.65rem;">{pct}%</span>
        <span style="font-size:.5rem;font-weight:600;opacity:.65;text-transform:uppercase;letter-spacing:.03em;">match</span>
      </div>
    </div>
  </div>
  <div class="aptcard-body">
    <div class="cc-name">{apt['nombre']}</div>
    <div style="display:flex;align-items:center;flex-wrap:wrap;gap:0;margin-bottom:.4rem;">
      <span class="cc-zone">{apt['zona']}</span>{barrio_sep}
    </div>
    <div class="cc-price">${apt['precio']:,.0f}<span class="cc-price-sub"> /mes</span></div>
    <div class="cc-stats">
      <span><b>{apt['size']}</b> m²</span>
      <span><b>{apt['bedrooms']}</b> hab</span>
      <span><b>{apt['distancia']}</b> km TM</span>
      <span style="color:{'#059669' if pet_ok else '#94A3B8'};font-weight:600;">{'Pets OK' if pet_ok else 'Sin pets'}</span>
    </div>
    {f'<div class="cc-amenities">{amenity_html}</div>' if amenity_html else ''}
  </div>
</div>
""", unsafe_allow_html=True)
            if st.button(
                "Ver fotos y descripción",
                key=f"det_{abs(hash(apt['nombre'])) % 99999}_{i}",
                use_container_width=True,
            ):
                _detalle_apartamento(apt, fotos)

    # Map
    try:
        from streamlit_folium import st_folium
        mapa = crear_mapa_folium(todos, top3)
        if mapa:
            top3_sin_coords = [a for a in top3 if not (a.get("latitud") and a.get("longitud"))]
            n_en_mapa = len([a for a in top3 if a.get("latitud") and a.get("longitud")])
            label_mapa = f"Mapa de ubicaciones — {n_en_mapa} de {len(top3)} TOP en el mapa"
            with st.expander(label_mapa, expanded=True):
                if top3_sin_coords:
                    nombres_sin = ", ".join(f"**{a['nombre']}**" for a in top3_sin_coords)
                    st.caption(
                        f"Sin coordenadas GPS (no aparece en el mapa): {nombres_sin}. "
                        "Los datos reales de ese inmueble no incluyen latitud/longitud."
                    )
                st_folium(mapa, width="100%", height=420, returned_objects=[])
    except Exception:
        pass

    # Graph
    with st.expander(f"Grafo bipartito — {len(todos)} nodo(s) compatibles", expanded=False):
        st.markdown(
            '<p style="font-family:Josefin Sans,sans-serif;font-size:.82rem;color:#475569;margin:.2rem 0 .75rem;">'
            'Cada arista (u,&nbsp;o)&nbsp;∈&nbsp;E existe solo si precio, distancia y mascotas son compatibles. '
            'Las aristas teal fluyen con partículas animadas (GSAP). Hover sobre cualquier nodo para ver detalles.</p>',
            unsafe_allow_html=True,
        )
        grafo_result = visualizar_grafo_bipartito(todos, top3, ent)
        if grafo_result:
            grafo_html, grafo_height = grafo_result
            st.components.v1.html(grafo_html, height=grafo_height, scrolling=False)


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sb-brand">
  <div class="sb-icon">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  </div>
  <div>
    <div class="sb-title">Aptmatch</div>
    <div class="sb-sub">Bogotá &nbsp;·&nbsp; Colombia</div>
  </div>
</div>
<p class="sb-nav-label">Navegación</p>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "nav",
    ["Buscar apartamento", "Registrar usuario", "Ejecutar matching", "Universo 3D", "Ver base de datos"],
    label_visibility="collapsed",
    key="main_menu",
)

st.session_state.setdefault("chat_msgs", [])
if menu == "Buscar apartamento" and st.session_state["chat_msgs"]:
    st.sidebar.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)
    if st.sidebar.button("Nueva búsqueda", use_container_width=True, key="clear_chat"):
        st.session_state["chat_msgs"] = []
        st.rerun()

st.sidebar.markdown("""
<div class="sb-footer">
  Universidad del Rosario<br>
  Teoría de Grafos &nbsp;·&nbsp; 4to semestre<br>
  <span style="color:#CBD5E1;font-size:.65rem;">
    Rivera &nbsp;·&nbsp; Sierra &nbsp;·&nbsp; Arroyave &nbsp;·&nbsp; Garzón
  </span>
</div>
""", unsafe_allow_html=True)

amenities_opciones = ["gym", "parqueadero", "ascensor", "piscina", "terraza", "coworking", "zona BBQ", "seguridad"]
zonas = ["Chapinero", "Suba", "Usaquén", "Teusaquillo", "Centro", "Kennedy", "Engativá"]


# ═══════════════════════════════════════════════════════════════════════════════
# BUSCAR APARTAMENTO — CHAT
# ═══════════════════════════════════════════════════════════════════════════════
if menu == "Buscar apartamento":

    if not st.session_state["chat_msgs"]:
        # ── Hero ──────────────────────────────────────────────────────────────
        st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">
    <span class="hero-eyebrow-dot"></span>
    210 apartamentos reales &nbsp;·&nbsp; 7 zonas &nbsp;·&nbsp; Bogotá
    <span class="hero-eyebrow-dot"></span>
  </div>
  <h1 class="hero-title">
    Tu próximo hogar en Bogotá,<br>encontrado con
    <span class="hero-accent">exactitud</span>
    <span class="hero-accent-gold"> matemática</span>
  </h1>
  <p class="hero-sub">
    Describe en lenguaje natural lo que buscas — zona, presupuesto, amenities.
    El algoritmo húngaro calcula el matching óptimo al instante.
  </p>
  <p class="hero-hint">Empieza con un ejemplo</p>
</div>
""", unsafe_allow_html=True)

        ex_col1, ex_col2, ex_col3 = st.columns(3)
        _examples = [
            ("Chapinero, máx $2M, gym y parqueadero, tengo perro",
             "Chapinero · $2M · gym · pet"),
            ("Usaquén o Cedritos, 3 habitaciones, menos de 3.5 millones",
             "Usaquén · 3 hab · $3.5M"),
            ("Suba o Niza, máximo 1.8 millones, con ascensor y seguridad",
             "Suba · $1.8M · ascensor"),
        ]
        for col, (full_query, label) in zip([ex_col1, ex_col2, ex_col3], _examples):
            with col:
                if st.button(f'"{label}"', use_container_width=True, key=f"ex_{label[:8]}"):
                    _do_search(full_query)

    else:
        # ── Chat history ──────────────────────────────────────────────────────
        for msg in st.session_state["chat_msgs"]:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(
                        f'<span style="font-family:Josefin Sans,sans-serif;font-size:.95rem;'
                        f'color:#0F172A;">{msg["content"]}</span>',
                        unsafe_allow_html=True,
                    )
            else:
                with st.chat_message("assistant", avatar="🏠"):
                    _render_assistant_msg(msg)

    # ── Chat input (always visible) ───────────────────────────────────────────
    if prompt := st.chat_input("Describe tu apartamento ideal en Bogotá..."):
        _do_search(prompt)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRAR USUARIO
# ═══════════════════════════════════════════════════════════════════════════════
elif menu == "Registrar usuario":

    st.markdown("""
<div style="padding:1.5rem 0 1rem;">
  <h2 style="font-family:'Cinzel',serif;color:#0F172A;font-size:1.3rem;
      font-weight:700;margin:0 0 .3rem;letter-spacing:.02em;">Registrar Usuario</h2>
  <p style="font-family:'Josefin Sans',sans-serif;color:#64748B;font-size:.87rem;margin:0;">
    Agrega un buscador al sistema para incluirlo en el matching global con el algoritmo húngaro.
  </p>
</div>
""", unsafe_allow_html=True)

    with st.form("form_usuario"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                '<p style="font-family:\'Josefin Sans\',sans-serif;font-size:.7rem;font-weight:700;'
                'color:#94A3B8;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;">'
                'Información básica</p>',
                unsafe_allow_html=True,
            )
            nombre           = st.text_input("Nombre completo")
            budget           = st.number_input("Presupuesto máximo (COP)", min_value=0.0, step=100_000.0, format="%.0f")
            zona             = st.selectbox("Zona preferida", zonas)
            radio            = st.number_input("Radio máximo (km)", min_value=0.0, step=0.5, value=5.0)

        with col2:
            st.markdown(
                '<p style="font-family:\'Josefin Sans\',sans-serif;font-size:.7rem;font-weight:700;'
                'color:#94A3B8;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem;">'
                'Preferencias</p>',
                unsafe_allow_html=True,
            )
            pets             = st.checkbox("Tiene mascota")
            amenities_req    = st.multiselect("Amenities requeridos", amenities_opciones)
            size_deseado     = st.number_input("Tamaño deseado (m²)", min_value=1.0, step=1.0, value=60.0)
            bedrooms_deseado = st.number_input("Habitaciones deseadas", min_value=1, step=1, value=2)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.form_submit_button("Guardar usuario"):
            if not nombre.strip():
                st.error("Por favor ingresa un nombre.")
            elif budget <= 0:
                st.error("El presupuesto debe ser mayor a cero.")
            else:
                insertar_usuario(nombre.strip(), budget, zona, radio, pets, amenities_req,
                                 size_deseado, int(bedrooms_deseado))
                st.success(f"Usuario **{nombre.strip()}** registrado correctamente.")


# ═══════════════════════════════════════════════════════════════════════════════
# EJECUTAR MATCHING
# ═══════════════════════════════════════════════════════════════════════════════
elif menu == "Ejecutar matching":

    st.markdown("""
<div style="padding:1.5rem 0 1rem;">
  <h2 style="font-family:'Cinzel',serif;color:#0F172A;font-size:1.3rem;
      font-weight:700;margin:0 0 .3rem;letter-spacing:.02em;">Matching Óptimo</h2>
  <p style="font-family:'Josefin Sans',sans-serif;color:#64748B;font-size:.87rem;margin:0;">
    Compara dos estrategias sobre los usuarios registrados en la base de datos.
  </p>
</div>
""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
<div style="background:white;border-radius:16px;
    padding:1.25rem 1.5rem;box-shadow:0 4px 20px rgba(0,0,0,.07);border-left:4px solid #0F766E;">
  <div style="font-family:'Cinzel',serif;font-size:.85rem;font-weight:700;color:#0F766E;
      letter-spacing:.04em;text-transform:uppercase;margin-bottom:.5rem;">Peso Máximo</div>
  <div style="font-family:'Josefin Sans',sans-serif;font-size:.82rem;color:#475569;line-height:1.6;">
    Algoritmo Húngaro — <code>linear_sum_assignment</code>.<br>
    Maximiza la <strong style="color:#0F172A;">suma total de compatibilidades</strong>.
    Prioriza calidad sobre cantidad.
  </div>
</div>
""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
<div style="background:white;border-radius:16px;
    padding:1.25rem 1.5rem;box-shadow:0 4px 20px rgba(0,0,0,.07);border-left:4px solid #94A3B8;">
  <div style="font-family:'Cinzel',serif;font-size:.85rem;font-weight:700;color:#475569;
      letter-spacing:.04em;text-transform:uppercase;margin-bottom:.5rem;">Matching Máximo</div>
  <div style="font-family:'Josefin Sans',sans-serif;font-size:.82rem;color:#475569;line-height:1.6;">
    Matriz binaria sobre aristas válidas.<br>
    Maximiza el <strong style="color:#0F172A;">número de asignaciones</strong>
    sin considerar calidad. Prioriza cobertura.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Ejecutar y comparar ambas estrategias", type="primary"):
        W, res_hungaro = ejecutar_matching()

        if W is None:
            st.warning("Debes registrar al menos un usuario para ejecutar el matching.")
        else:
            _, res_maximo = ejecutar_matching_maximo()
            n_usuarios = len(cargar_tabla("usuarios"))

            tab1, tab2 = st.tabs(["Peso Máximo (Húngaro)", "Matching Máximo (Cardinalidad)"])

            with tab1:
                st.markdown(
                    '<p style="font-family:Josefin Sans,sans-serif;font-size:.8rem;color:#64748B;margin:.2rem 0 .75rem;">'
                    'Asignaciones con mayor compatibilidad global. La matriz muestra w(u,o) para cada par.</p>',
                    unsafe_allow_html=True,
                )
                st.dataframe(W, use_container_width=True)
                if res_hungaro is not None and not res_hungaro.empty:
                    st.dataframe(res_hungaro, use_container_width=True, hide_index=True)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Peso total",    round(res_hungaro["peso"].sum(), 3))
                    c2.metric("Peso promedio", round(res_hungaro["peso"].mean(), 3))
                    c3.metric("Cobertura",     f"{round(len(res_hungaro) / n_usuarios * 100, 1)}%")
                else:
                    st.warning("No hubo asignaciones válidas.")

            with tab2:
                st.markdown(
                    '<p style="font-family:Josefin Sans,sans-serif;font-size:.8rem;color:#64748B;margin:.2rem 0 .75rem;">'
                    'Trata todas las aristas válidas como equivalentes. Maximiza número de pares.</p>',
                    unsafe_allow_html=True,
                )
                if res_maximo is not None and not res_maximo.empty:
                    st.dataframe(res_maximo, use_container_width=True, hide_index=True)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Asignaciones",  len(res_maximo))
                    c2.metric("Peso promedio", round(res_maximo["peso"].mean(), 3))
                    c3.metric("Cobertura",     f"{round(len(res_maximo) / n_usuarios * 100, 1)}%")
                else:
                    st.warning("No hubo asignaciones válidas.")

            st.divider()
            st.markdown(
                '<p style="font-family:Cinzel,serif;font-size:.8rem;font-weight:700;'
                'color:#0F766E;text-transform:uppercase;letter-spacing:.12em;margin-bottom:.75rem;">'
                'Tabla Comparativa</p>',
                unsafe_allow_html=True,
            )

            h_asig = len(res_hungaro) if res_hungaro is not None and not res_hungaro.empty else 0
            m_asig = len(res_maximo)  if res_maximo  is not None and not res_maximo.empty  else 0
            h_peso = round(res_hungaro["peso"].sum(), 3) if h_asig else 0
            m_peso = round(res_maximo["peso"].sum(),  3) if m_asig else 0

            comp = pd.DataFrame({
                "Estrategia":    ["Peso Máximo (Húngaro)", "Matching Máximo (Cardinalidad)"],
                "Asignaciones":  [h_asig, m_asig],
                "Peso total":    [h_peso, m_peso],
                "Peso promedio": [round(h_peso/h_asig,3) if h_asig else 0,
                                  round(m_peso/m_asig,3) if m_asig else 0],
                "Cobertura":     [f"{round(h_asig/n_usuarios*100,1)}%",
                                  f"{round(m_asig/n_usuarios*100,1)}%"],
            })
            st.dataframe(comp, use_container_width=True, hide_index=True)

            if h_asig == m_asig:
                msg = (f"Ambas estrategias asignaron el mismo número de usuarios. "
                       f"El Húngaro ofrece mayor calidad total (peso = {h_peso} vs {m_peso}).")
            elif m_asig > h_asig:
                msg = (f"El Matching Máximo asigna {m_asig - h_asig} usuario(s) más que el Húngaro. "
                       "Priorizar calidad dejó a algunos buscadores sin apartamento.")
            else:
                msg = ("El Algoritmo Húngaro asignó más usuarios que el Matching Máximo, "
                       "lo que indica que la calidad no sacrificó cobertura en este dataset.")

            st.info(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# VER BASE DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# UNIVERSO 3D
# ═══════════════════════════════════════════════════════════════════════════════
elif menu == "Universo 3D":
    import json as _json

    _ZONE_COLORS = {
        "Chapinero":   "#5EEAD4",
        "Usaquén":     "#C4B5FD",
        "Suba":        "#93C5FD",
        "Teusaquillo": "#FCD34D",
        "Centro":      "#FCA5A5",
        "Kennedy":     "#86EFAC",
        "Engativá":    "#F9A8D4",
    }

    st.markdown("""
<div style="padding:.75rem 0 .5rem;display:flex;align-items:center;gap:1rem;">
  <h2 style="font-family:'Cinzel',serif;color:#0F172A;font-size:1.2rem;
      font-weight:700;margin:0;letter-spacing:.02em;">Universo del Grafo 3D</h2>
  <span style="font-family:'Josefin Sans',sans-serif;font-size:.7rem;color:#94A3B8;
      background:#F1F5F9;border-radius:20px;padding:.2rem .75rem;letter-spacing:.06em;">
    F = fullscreen &nbsp;·&nbsp; R = reset &nbsp;·&nbsp; E = explosión
  </span>
</div>
""", unsafe_allow_html=True)

    _usuarios     = cargar_tabla("usuarios")
    _apartamentos = cargar_tabla("apartamentos")

    if _usuarios.empty:
        st.warning("No hay usuarios registrados. Ve a **Registrar usuario** primero.")
    else:
        # ── Cargar asignaciones ───────────────────────────────────────────────
        _conn = conectar()
        _asig = pd.read_sql_query(
            "SELECT usuario_id, apartamento_id, peso FROM asignaciones", _conn
        )
        _conn.close()

        _matched_pairs   = set(zip(_asig["usuario_id"].tolist(), _asig["apartamento_id"].tolist()))
        _matched_apt_ids = set(_asig["apartamento_id"].tolist())
        _connected_apt_ids = set()
        _TOP_N = 15

        # ── Calcular compatibilidades por usuario ────────────────────────────
        _user_compat = {}
        for _, _u in _usuarios.iterrows():
            _uid = _u["id"]
            _udict = {
                "budget":           _u["budget"],
                "radio":            _u["radio"],
                "pets":             bool(_u["pets"]),
                "amenities_req":    _u.get("amenities_req") or "",
                "size_deseado":     _u.get("size_deseado", 60),
                "bedrooms_deseado": _u.get("bedrooms_deseado", 2),
            }
            _ws = []
            for _, _apt in _apartamentos.iterrows():
                _w = calcular_peso(_udict, _apt)
                if _w > 0:
                    _ws.append((_apt["id"], _apt, _w))
                    _connected_apt_ids.add(_apt["id"])
            _ws.sort(key=lambda x: x[2], reverse=True)
            _user_compat[_uid] = _ws

        # ── Construir nodos y aristas ────────────────────────────────────────
        _nodes, _links = [], []

        for _, _u in _usuarios.iterrows():
            _uid = _u["id"]
            _nodes.append({
                "id":      f"u_{_uid}",
                "label":   _u["nombre"],
                "type":    "user",
                "color":   "#FCD34D",
                "size":    14,
                "zone":    _u["zona"],
                "matched": False,
                "connected": True,
                "detail": (
                    f"<b>Zona:</b> {_u['zona']}<br>"
                    f"<b>Presupuesto:</b> ${_u['budget']:,.0f}/mes<br>"
                    f"<b>Radio:</b> {_u['radio']} km<br>"
                    f"<b>Mascotas:</b> {'Sí' if _u['pets'] else 'No'}<br>"
                    f"<b>Amenities:</b> {_u.get('amenities_req') or '—'}<br>"
                    f"<b>Habitaciones:</b> {_u.get('bedrooms_deseado', '—')}"
                ),
            })

        for _, _apt in _apartamentos.iterrows():
            _aid         = _apt["id"]
            _zona        = _apt.get("zona", "")
            _color       = _ZONE_COLORS.get(_zona, "#475569")
            _is_matched  = _aid in _matched_apt_ids
            _is_conn     = _aid in _connected_apt_ids
            _size        = 8 if _is_matched else (5 if _is_conn else 2.5)
            _detail      = (
                f"<b>Precio:</b> ${_apt['price']:,.0f}/mes<br>"
                f"<b>Zona:</b> {_zona}<br>"
                f"<b>Barrio:</b> {_apt.get('barrio') or '—'}<br>"
                f"<b>Tamaño:</b> {_apt['size']} m² · {_apt['bedrooms']} hab<br>"
                f"<b>Dist. TM:</b> {_apt['distancia']} km<br>"
                f"<b>Amenities:</b> {_apt.get('amenities') or '—'}"
            ) if _is_conn else ""
            _nodes.append({
                "id":        f"a_{_aid}",
                "label":     _apt["nombre"] if _is_conn else "",
                "type":      "apt",
                "color":     _color,
                "size":      _size,
                "zone":      _zona,
                "matched":   _is_matched,
                "connected": _is_conn,
                "detail":    _detail,
            })

        for _, _u in _usuarios.iterrows():
            _uid = _u["id"]
            for _aid, _apt_row, _w in _user_compat[_uid][:_TOP_N]:
                _is_match = (_uid, _aid) in _matched_pairs
                _links.append({
                    "source":  f"u_{_uid}",
                    "target":  f"a_{_aid}",
                    "weight":  _w,
                    "matched": _is_match,
                    "color":   "#5EEAD4" if _is_match else "#1E3A5F",
                    "width":   3.5 if _is_match else 0.5,
                    "srcZone": _u["zona"],
                })

        # ── Stats ────────────────────────────────────────────────────────────
        _n_users    = len(_usuarios)
        _n_all_apts = len(_apartamentos)
        _n_conn     = len(_connected_apt_ids)
        _n_matched  = sum(1 for _l in _links if _l["matched"])
        _n_links    = len(_links)

        _graph_json = _json.dumps({"nodes": _nodes, "links": _links}, ensure_ascii=False)
        _zone_json  = _json.dumps(_ZONE_COLORS, ensure_ascii=False)

        _legend_items = "".join(
            '<div class="zl" data-zone="' + _z + '" onclick="toggleZone(this,\'' + _z + '\')">'
            '<div class="zd" style="background:' + _c + '"></div><span>' + _z + '</span></div>'
            for _z, _c in _ZONE_COLORS.items()
        )

        # ── HTML Plan C ───────────────────────────────────────────────────────
        _TMPL = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{margin:0;padding:0;width:100%;height:940px;overflow:hidden;background:#05071A;}
#universe{position:relative;width:100%;height:940px;}
#universe::before{
  content:'';position:absolute;inset:0;pointer-events:none;z-index:1;
  background:
    radial-gradient(ellipse 55% 40% at 18% 50%,rgba(45,212,191,.05) 0%,transparent 65%),
    radial-gradient(ellipse 50% 35% at 82% 50%,rgba(167,139,250,.05) 0%,transparent 65%),
    radial-gradient(ellipse 40% 50% at 50% 15%,rgba(245,158,11,.04) 0%,transparent 60%);
}
#g{width:100%;height:940px;position:absolute;inset:0;}
#topbar{
  position:absolute;top:0;left:0;right:0;height:48px;z-index:20;
  background:linear-gradient(to bottom,rgba(0,0,0,.88) 0%,transparent 100%);
  display:flex;align-items:center;justify-content:space-between;padding:0 18px;
}
#tb-title{font-family:'Segoe UI',sans-serif;font-size:11px;font-weight:700;
  color:rgba(255,255,255,.35);letter-spacing:.14em;text-transform:uppercase;}
#tb-stats{display:flex;gap:18px;font-family:'Segoe UI',sans-serif;font-size:10px;
  color:rgba(255,255,255,.22);letter-spacing:.06em;}
.tb-stat b{color:rgba(255,255,255,.65);margin-right:3px;}
#fs-btn{
  position:absolute;top:10px;right:16px;z-index:30;
  background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);
  border-radius:8px;padding:5px 10px;cursor:pointer;
  color:rgba(255,255,255,.45);font-size:10px;font-family:'Segoe UI',sans-serif;
  letter-spacing:.07em;transition:all 180ms;backdrop-filter:blur(8px);
}
#fs-btn:hover{background:rgba(255,255,255,.1);color:rgba(255,255,255,.9);}
#zone-legend{position:absolute;top:56px;left:12px;z-index:20;display:flex;flex-direction:column;gap:3px;}
.zl-hdr{font-family:'Segoe UI',sans-serif;font-size:8.5px;font-weight:700;
  color:rgba(255,255,255,.18);letter-spacing:.14em;text-transform:uppercase;padding:0 10px 5px;}
.zl{display:flex;align-items:center;gap:7px;
  background:rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.05);
  border-radius:8px;padding:5px 10px;cursor:pointer;transition:all 160ms;
  backdrop-filter:blur(8px);font-family:'Segoe UI',sans-serif;
  font-size:10px;color:rgba(255,255,255,.38);letter-spacing:.03em;
}
.zl:hover{background:rgba(255,255,255,.07);color:rgba(255,255,255,.8);}
.zl.active{border-color:rgba(255,255,255,.22);color:rgba(255,255,255,.9);background:rgba(255,255,255,.05);}
.zd{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
#controls{
  position:absolute;top:56px;right:12px;z-index:20;width:196px;
  background:rgba(0,0,0,.72);border:1px solid rgba(255,255,255,.07);
  border-radius:13px;padding:13px 15px;backdrop-filter:blur(14px);
}
.ctrl-hdr{font-family:'Segoe UI',sans-serif;font-size:8.5px;font-weight:700;
  color:rgba(255,255,255,.18);letter-spacing:.14em;text-transform:uppercase;margin-bottom:11px;}
.ctrl-row{margin-bottom:11px;}
.ctrl-lbl{font-family:'Segoe UI',sans-serif;font-size:9.5px;color:rgba(255,255,255,.35);
  margin-bottom:5px;display:flex;justify-content:space-between;}
.ctrl-lbl b{color:rgba(255,255,255,.65);}
input[type=range]{width:100%;height:2.5px;appearance:none;background:rgba(255,255,255,.1);
  border-radius:2px;outline:none;cursor:pointer;}
input[type=range]::-webkit-slider-thumb{appearance:none;width:11px;height:11px;
  background:#5EEAD4;border-radius:50%;cursor:pointer;box-shadow:0 0 5px rgba(94,234,212,.5);}
.ctrl-sep{height:1px;background:rgba(255,255,255,.05);margin:11px -15px;}
.ctrl-tog{display:flex;align-items:center;justify-content:space-between;margin-bottom:9px;}
.ctrl-tog label{font-family:'Segoe UI',sans-serif;font-size:9.5px;color:rgba(255,255,255,.35);cursor:pointer;}
.sw{width:30px;height:15px;background:rgba(255,255,255,.08);border-radius:8px;
  position:relative;cursor:pointer;transition:200ms;flex-shrink:0;}
.sw.on{background:rgba(94,234,212,.4);}
.sw::after{content:'';position:absolute;top:2px;left:2px;width:11px;height:11px;
  border-radius:50%;background:#fff;transition:200ms;}
.sw.on::after{transform:translateX(15px);}
.ctrl-btn{width:100%;padding:6px;background:rgba(94,234,212,.07);
  border:1px solid rgba(94,234,212,.18);border-radius:8px;
  color:rgba(94,234,212,.7);font-size:9.5px;font-family:'Segoe UI',sans-serif;
  letter-spacing:.07em;cursor:pointer;transition:all 160ms;margin-top:5px;}
.ctrl-btn:hover{background:rgba(94,234,212,.14);color:#5EEAD4;}
#focus-lbl{
  position:absolute;top:56px;left:50%;transform:translateX(-50%);z-index:25;display:none;
  background:rgba(245,158,11,.13);border:1px solid rgba(245,158,11,.28);
  border-radius:20px;padding:4px 14px;font-family:'Segoe UI',sans-serif;
  font-size:9.5px;color:#FCD34D;letter-spacing:.06em;cursor:pointer;white-space:nowrap;
}
#focus-lbl:hover{background:rgba(245,158,11,.22);}
#search-wrap{position:absolute;bottom:18px;left:50%;transform:translateX(-50%);z-index:20;}
#search{background:rgba(0,0,0,.65);border:1px solid rgba(255,255,255,.1);border-radius:20px;
  padding:6px 15px;font-family:'Segoe UI',sans-serif;font-size:10.5px;
  color:rgba(255,255,255,.65);outline:none;width:230px;backdrop-filter:blur(8px);transition:all 200ms;}
#search::placeholder{color:rgba(255,255,255,.22);}
#search:focus{border-color:rgba(94,234,212,.38);width:270px;}
#tip{position:fixed;display:none;pointer-events:none;z-index:9999;
  background:rgba(0,0,6,.95);border:1px solid rgba(94,234,212,.2);
  border-radius:12px;padding:11px 14px;color:#CBD5E1;
  font-size:11.5px;line-height:1.8;max-width:235px;
  backdrop-filter:blur(16px);box-shadow:0 16px 48px rgba(0,0,0,.8);}
#tip-nm{font-size:12.5px;font-weight:700;color:#5EEAD4;margin-bottom:6px;}
#hint{position:absolute;bottom:14px;right:14px;z-index:20;
  font-family:'Segoe UI',sans-serif;font-size:8.5px;color:rgba(255,255,255,.12);
  letter-spacing:.05em;line-height:1.8;text-align:right;}
</style>
</head>
<body>
<div id="universe">
  <div id="g"></div>
  <div id="topbar">
    <div id="tb-title">G = (U &cup; O, E, w) &nbsp;&mdash;&nbsp; Universo del Grafo Bipartito</div>
    <div id="tb-stats">
      <div class="tb-stat"><b>__NU__</b>USUARIOS</div>
      <div class="tb-stat"><b>__NA__</b>APTS</div>
      <div class="tb-stat"><b>__NC__</b>CONECTADOS</div>
      <div class="tb-stat"><b>__NM__</b>MATCHED</div>
      <div class="tb-stat"><b>__NL__</b>ARISTAS</div>
    </div>
  </div>
  <button id="fs-btn" onclick="toggleFS()">&#x26F6; FULLSCREEN</button>
  <div id="focus-lbl" onclick="clearFocus()">Modo enfoque activo &mdash; clic para salir</div>
  <div id="zone-legend">
    <div class="zl-hdr">Zonas</div>
    __LEGEND__
    <div class="zl" onclick="toggleZone(this,'__ALL__')" style="margin-top:4px;opacity:.5;">
      <div class="zd" style="background:rgba(255,255,255,.4)"></div><span>Todas</span>
    </div>
  </div>
  <div id="controls">
    <div class="ctrl-hdr">Panel de Control</div>
    <div class="ctrl-row">
      <div class="ctrl-lbl">Rotaci&oacute;n <b id="rv">1.0x</b></div>
      <input type="range" id="rot-sl" min="0" max="30" value="10" oninput="setRot(this.value)">
    </div>
    <div class="ctrl-row">
      <div class="ctrl-lbl">Tama&ntilde;o nodos <b id="sv">1.0x</b></div>
      <input type="range" id="size-sl" min="3" max="25" value="10" oninput="setSz(this.value)">
    </div>
    <div class="ctrl-row">
      <div class="ctrl-lbl">Opacidad aristas <b id="lv">12%</b></div>
      <input type="range" id="link-sl" min="0" max="100" value="12" oninput="setLk(this.value)">
    </div>
    <div class="ctrl-row">
      <div class="ctrl-lbl">Repulsi&oacute;n <b id="cv">-150</b></div>
      <input type="range" id="chrg-sl" min="10" max="300" value="150" oninput="setCh(this.value)">
    </div>
    <div class="ctrl-sep"></div>
    <div class="ctrl-tog">
      <label>Modo enfoque (clic en U)</label>
      <div class="sw on" id="ft" onclick="this.classList.toggle('on');focusMode=this.classList.contains('on');if(!focusMode)clearFocus();"></div>
    </div>
    <div class="ctrl-tog">
      <label>Mostrar sin conexi&oacute;n</label>
      <div class="sw on" id="ut" onclick="this.classList.toggle('on');showUnconn=this.classList.contains('on');refresh();"></div>
    </div>
    <div class="ctrl-tog">
      <label>Part&iacute;culas matching</label>
      <div class="sw on" id="pt" onclick="this.classList.toggle('on');showPart=this.classList.contains('on');Graph.linkDirectionalParticles(function(l){return showPart&&l.matched?6:0;});"></div>
    </div>
    <div class="ctrl-sep"></div>
    <button class="ctrl-btn" onclick="resetView()">Resetear vista</button>
    <button class="ctrl-btn" onclick="explode()" style="margin-top:6px;border-color:rgba(248,113,113,.25);color:rgba(248,113,113,.7);">Explosi&oacute;n</button>
  </div>
  <div id="search-wrap">
    <input type="text" id="search" placeholder="Buscar nodo por nombre..." oninput="searchNode(this.value)">
  </div>
  <div id="tip"><div id="tip-nm"></div><div id="tip-bd"></div></div>
  <div id="hint">
    ARRASTRAR rotar &nbsp;&middot;&nbsp; SCROLL zoom<br>
    CLIC usuario = enfoque &nbsp;&middot;&nbsp; F fullscreen &nbsp;&middot;&nbsp; E explosi&oacute;n
  </div>
</div>
<script src="https://unpkg.com/3d-force-graph@1"></script>
<script>
var data     = __GRAPH_JSON__;
var ZONE_C   = __ZONE_JSON__;
var nodes    = data.nodes;
var links    = data.links;

var focusMode   = true;
var activeZone  = null;
var focusedUser = null;
var showUnconn  = true;
var showPart    = true;
var nodeScale   = 1.0;
var linkOpa     = 0.12;
var chargeStr   = -150;
var rotSpeed    = 0.0015;
var rotAngle    = 0;
var rotTimer    = null;
var Graph;

// Simula opacidad mezclando el color del nodo hacia el fondo (#05071A)
// porque nodeOpacity solo acepta un número global, no accessor por nodo.
var _BG = [5, 7, 26];
function _blend(hex, a) {
  if (a >= 1 || !hex || hex.length < 7) return hex || '#888888';
  var r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16), b = parseInt(hex.slice(5,7),16);
  return '#' + [r,g,b].map(function(v,i){
    return Math.round(v*a + _BG[i]*(1-a)).toString(16).padStart(2,'0');
  }).join('');
}

var tip   = document.getElementById('tip');
var tipNm = document.getElementById('tip-nm');
var tipBd = document.getElementById('tip-bd');

function nodeOpa(n) {
  if (!showUnconn && n.type === 'apt' && !n.connected) return 0;
  if (focusedUser) {
    if (n.id === focusedUser) return 1.0;
    var nb = links.some(function(l){
      return (l.source===focusedUser||l.source.id===focusedUser)&&(l.target===n.id||l.target.id===n.id);
    });
    return nb ? 0.95 : 0.03;
  }
  if (activeZone) {
    if (n.zone === activeZone) return 1.0;
    if (n.type === 'user') return 0.15;
    return 0.02;
  }
  if (n.type === 'user') return 1.0;
  if (n.matched)    return 1.0;
  if (n.connected)  return 0.85;
  return 0.22;
}

function nodeVal(n) { return n.size * nodeScale; }
function nodeColorFn(n) { return _blend(n.color, nodeOpa(n)); }

function refresh() {
  if (!Graph) return;
  Graph.nodeColor(nodeColorFn).nodeVal(nodeVal);
}

document.addEventListener('mousemove',function(e){
  tip.style.left=(e.clientX+14)+'px'; tip.style.top=(e.clientY-8)+'px';
});

function startRot() {
  stopRot();
  if (rotSpeed<=0 || !Graph) return;
  rotTimer = setInterval(function(){
    rotAngle += rotSpeed;
    var p = Graph.cameraPosition();
    var d = Math.hypot(p.x||300, p.z||300);
    Graph.cameraPosition({x:d*Math.sin(rotAngle), z:d*Math.cos(rotAngle)});
  }, 30);
}
function stopRot(){ if(rotTimer) clearInterval(rotTimer); }

window.addEventListener('load', function() {
  if (typeof ForceGraph3D === 'undefined') {
    document.getElementById('g').innerHTML = '<div style="color:#5EEAD4;font-family:sans-serif;padding:60px;text-align:center;font-size:14px">Error: no se pudo cargar la librería 3D.<br>Verifica tu conexión a internet.</div>';
    return;
  }
  var gEl = document.getElementById('g');
  var _w = Math.round(gEl.getBoundingClientRect().width) || gEl.offsetWidth || 900;
  Graph = ForceGraph3D()(gEl)
    .width(_w || 900)
    .height(940)
    .backgroundColor('#05071A')
    .graphData(data)
    .nodeLabel(function(n){ return n.label||''; })
    .nodeColor(nodeColorFn)
    .nodeVal(nodeVal)
    .nodeOpacity(0.9)
    .nodeResolution(14)
    .linkColor(function(l){ return l.color; })
    .linkWidth(function(l){ return l.width; })
    .linkOpacity(Math.min(linkOpa * 5, 0.85))
    .linkCurvature(0.1)
    .linkDirectionalParticles(function(l){ return showPart&&l.matched?6:0; })
    .linkDirectionalParticleSpeed(0.005)
    .linkDirectionalParticleColor(function(){ return '#5EEAD4'; })
    .linkDirectionalParticleWidth(2.2)
    .onNodeHover(function(n){
      document.body.style.cursor = n?'pointer':'default';
      if (n && n.detail) {
        tipNm.innerHTML = n.label||n.id;
        tipBd.innerHTML = n.detail;
        tip.style.display = 'block';
      } else { tip.style.display='none'; }
    })
    .onNodeClick(function(n){
      if (n.type==='user' && focusMode) {
        if (focusedUser===n.id) { clearFocus(); return; }
        focusedUser = n.id;
        document.getElementById('focus-lbl').style.display='block';
        refresh();
        var d=120, m=Math.hypot(n.x||1,n.y||1,n.z||1), r=1+d/m;
        Graph.cameraPosition({x:n.x*r,y:n.y*r,z:n.z*r},n,1000);
      } else {
        var d2=100, m2=Math.hypot(n.x||1,n.y||1,n.z||1), r2=1+d2/m2;
        Graph.cameraPosition({x:n.x*r2,y:n.y*r2,z:n.z*r2},n,1000);
      }
    });
  Graph.d3Force('charge').strength(chargeStr);
  gEl.addEventListener('mousedown', stopRot);
  gEl.addEventListener('mouseup',   startRot);
  startRot();
});

function clearFocus() {
  focusedUser = null;
  document.getElementById('focus-lbl').style.display='none';
  refresh();
}

function toggleZone(el, zone) {
  if (zone==='__ALL__') {
    activeZone=null;
    document.querySelectorAll('.zl').forEach(function(e){e.classList.remove('active');});
  } else {
    activeZone = activeZone===zone ? null : zone;
    document.querySelectorAll('.zl').forEach(function(e){e.classList.remove('active');});
    if (activeZone) el.classList.add('active');
  }
  refresh();
}

function setRot(v) {
  rotSpeed = (v/10)*0.0015;
  document.getElementById('rv').textContent=(v/10).toFixed(1)+'x';
  startRot();
}
function setSz(v) {
  nodeScale=v/10;
  document.getElementById('sv').textContent=(v/10).toFixed(1)+'x';
  refresh();
}
function setLk(v) {
  linkOpa=v/100;
  document.getElementById('lv').textContent=v+'%';
  if (Graph) Graph.linkOpacity(Math.min(linkOpa * 5, 0.85));
}
function setCh(v) {
  chargeStr=-parseInt(v);
  document.getElementById('cv').textContent=chargeStr;
  if (!Graph) return;
  Graph.d3Force('charge').strength(chargeStr);
  Graph.numDimensions(3);
}

function resetView() {
  if (!Graph) return;
  clearFocus();
  activeZone=null;
  document.querySelectorAll('.zl').forEach(function(e){e.classList.remove('active');});
  refresh();
  Graph.cameraPosition({x:0,y:0,z:600},{x:0,y:0,z:0},1200);
}

function explode() {
  if (!Graph) return;
  stopRot();
  Graph.d3Force('charge').strength(-900);
  Graph.numDimensions(3);
  setTimeout(function(){
    Graph.d3Force('charge').strength(chargeStr);
    Graph.numDimensions(3);
    setTimeout(startRot, 2200);
  }, 1600);
}

function searchNode(q) {
  if (!Graph) return;
  if (!q.trim()) { refresh(); return; }
  var ql = q.toLowerCase();
  var found = nodes.filter(function(n){ return n.label&&n.label.toLowerCase().includes(ql); });
  Graph.nodeColor(function(n){
    return found.some(function(f){return f.id===n.id;}) ? n.color : _blend(n.color, 0.04);
  });
  if (found.length===1) {
    var n=found[0], d=120, m=Math.hypot(n.x||1,n.y||1,n.z||1), r=1+d/m;
    Graph.cameraPosition({x:n.x*r,y:n.y*r,z:n.z*r},n,1000);
  }
}

function toggleFS() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(function(){});
  } else { document.exitFullscreen(); }
}
document.addEventListener('fullscreenchange', function(){
  var btn=document.getElementById('fs-btn');
  btn.innerHTML = document.fullscreenElement ? '&#x2715; SALIR' : '&#x26F6; FULLSCREEN';
  if (Graph) setTimeout(function(){ Graph.width(window.innerWidth).height(window.innerHeight); }, 120);
});
document.addEventListener('keydown',function(e){
  if(e.key==='f'||e.key==='F') toggleFS();
  if(e.key==='r'||e.key==='R') resetView();
  if(e.key==='e'||e.key==='E') explode();
  if(e.key==='Escape') clearFocus();
});

// all functions already global (no IIFE wrapper)
</script>
</body></html>"""

        _html = (_TMPL
                 .replace("__GRAPH_JSON__", _graph_json)
                 .replace("__ZONE_JSON__",  _zone_json)
                 .replace("__NU__",  str(_n_users))
                 .replace("__NA__",  str(_n_all_apts))
                 .replace("__NC__",  str(_n_conn))
                 .replace("__NM__",  str(_n_matched))
                 .replace("__NL__",  str(_n_links))
                 .replace("__LEGEND__", _legend_items)
                 .replace("__ALL__", "all"))

        st.components.v1.html(_html, height=960, scrolling=False)

        if not _asig.empty:
            with st.expander("Tabla de asignaciones del matching húngaro", expanded=False):
                _conn2 = conectar()
                _res_display = pd.read_sql_query("""
                    SELECT u.nombre AS Usuario, a.nombre AS Apartamento,
                           a.zona AS Zona, a.price AS Precio, asig.peso AS Compatibilidad
                    FROM asignaciones asig
                    JOIN usuarios u ON u.id = asig.usuario_id
                    JOIN apartamentos a ON a.id = asig.apartamento_id
                    ORDER BY asig.peso DESC
                """, _conn2)
                _conn2.close()
                st.dataframe(_res_display, use_container_width=True, hide_index=True)


elif menu == "Ver base de datos":

    st.markdown("""
<div style="padding:1.5rem 0 1rem;">
  <h2 style="font-family:'Cinzel',serif;color:#0F172A;font-size:1.3rem;
      font-weight:700;margin:0 0 .3rem;letter-spacing:.02em;">Base de Datos</h2>
  <p style="font-family:'Josefin Sans',sans-serif;color:#64748B;font-size:.87rem;margin:0;">
    Contenido actual de las tres tablas SQLite del sistema.
  </p>
</div>
""", unsafe_allow_html=True)

    df_users = cargar_tabla("usuarios")
    df_apts  = cargar_tabla("apartamentos")
    df_asig  = cargar_asignaciones_detalladas()

    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem;">
  <div style="background:white;border:1px solid #E2E8F0;border-radius:16px;
      padding:1.25rem 1.5rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.05);">
    <div style="font-family:'Cinzel',serif;font-size:2rem;font-weight:700;color:#0F766E;line-height:1;">{len(df_users)}</div>
    <div style="font-family:'Josefin Sans',sans-serif;font-size:.7rem;text-transform:uppercase;
        letter-spacing:.1em;color:#94A3B8;margin-top:.35rem;font-weight:700;">Usuarios</div>
  </div>
  <div style="background:white;border:1px solid #E2E8F0;border-radius:16px;
      padding:1.25rem 1.5rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.05);">
    <div style="font-family:'Cinzel',serif;font-size:2rem;font-weight:700;color:#0F766E;line-height:1;">{len(df_apts)}</div>
    <div style="font-family:'Josefin Sans',sans-serif;font-size:.7rem;text-transform:uppercase;
        letter-spacing:.1em;color:#94A3B8;margin-top:.35rem;font-weight:700;">Apartamentos</div>
  </div>
  <div style="background:white;border:1px solid #E2E8F0;border-radius:16px;
      padding:1.25rem 1.5rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.05);">
    <div style="font-family:'Cinzel',serif;font-size:2rem;font-weight:700;color:#0F766E;line-height:1;">{len(df_asig)}</div>
    <div style="font-family:'Josefin Sans',sans-serif;font-size:.7rem;text-transform:uppercase;
        letter-spacing:.1em;color:#94A3B8;margin-top:.35rem;font-weight:700;">Asignaciones</div>
  </div>
</div>
""", unsafe_allow_html=True)

    def _section_label(texto, count):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:.75rem;margin:1.25rem 0 .5rem;">'
            f'<p style="font-family:Josefin Sans,sans-serif;font-size:.72rem;font-weight:700;'
            f'color:#0F766E;text-transform:uppercase;letter-spacing:.12em;margin:0;">{texto}</p>'
            f'<span style="background:rgba(15,118,110,.1);color:#0F766E;border-radius:20px;'
            f'padding:.1rem .55rem;font-family:Josefin Sans,sans-serif;font-size:.68rem;font-weight:700;">'
            f'{count}</span></div>',
            unsafe_allow_html=True,
        )

    _section_label("Usuarios registrados", len(df_users))
    st.dataframe(df_users, use_container_width=True, hide_index=True)

    _section_label("Apartamentos en inventario", len(df_apts))
    st.dataframe(df_apts, use_container_width=True, hide_index=True)

    _section_label("Asignaciones guardadas", len(df_asig))
    if df_asig.empty:
        st.markdown(
            '<p style="font-family:Josefin Sans,sans-serif;font-size:.82rem;color:#94A3B8;'
            'text-align:center;padding:1rem;margin:0;">'
            'No hay asignaciones. Ejecuta el matching para generarlas.</p>',
            unsafe_allow_html=True,
        )
    else:
        st.dataframe(df_asig, use_container_width=True, hide_index=True)
