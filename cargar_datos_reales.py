"""
Descarga el dataset real de apartamentos en arriendo de Bogotá
(fuente: github.com/builker-col/bogota-apartments) y carga ~70
apartamentos representativos en la base de datos local SQLite.

Uso:
    python cargar_datos_reales.py
"""

import ast
import json
import math
import os
import random
import urllib.request
import sys

# ── Importar funciones de la base de datos ────────────────────────────────────
from database import crear_tablas, conectar

DB_PATH = "database.db"

BASE_URL    = "https://github.com/builker-col/bogota-apartments/releases/download/v2.0.0-august.2-2024/"
DATASET_URL = BASE_URL + "processed_v2.0.0_august_2_2024.json"
RAW_URL     = BASE_URL + "raw_v2.0.0_august_2_2024.json"

# Mapeo localidad → zona del sistema
LOCALIDAD_ZONA = {
    "CHAPINERO":      "Chapinero",
    "USAQUEN":        "Usaquén",
    "SUBA":           "Suba",
    "ENGATIVA":       "Engativá",
    "KENNEDY":        "Kennedy",
    "TEUSAQUILLO":    "Teusaquillo",
    "SANTA FE":       "Centro",
    "LOS MARTIRES":   "Centro",
    "ANTONIO NARINO": "Centro",
}

APTS_POR_ZONA = 30   # ~210 apartamentos en total
PRECIO_MIN    = 600_000
PRECIO_MAX    = 4_000_000


def extraer_numero(v):
    """Desempaqueta valores numéricos MongoDB ({$numberDouble, $numberInt, etc.})."""
    if isinstance(v, dict):
        for key in ("$numberDouble", "$numberInt", "$numberLong", "$numberDecimal"):
            if key in v:
                try:
                    return float(v[key])
                except (ValueError, TypeError):
                    return None
        return None
    return v


def es_nan(v):
    v = extraer_numero(v)
    if v is None:
        return True
    try:
        return math.isnan(float(v))
    except (TypeError, ValueError):
        return True


_PET_KEYWORDS = ["mascota", "mascotas", "pet friendly", "petfriendly",
                  "admite perro", "acepta perro", "admite mascota", "acepta mascota",
                  "perros permitidos", "gatos permitidos"]

def _es_pet_friendly(apt):
    # Primero el campo del scraper (casi siempre 0, pero por si acaso)
    val = extraer_numero(apt.get("permite_mascotas")) or 0
    if val == 1:
        return True
    # Fallback: buscar en la descripción
    desc = str(apt.get("descripcion") or "").lower()
    return any(k in desc for k in _PET_KEYWORDS)


def construir_amenities(apt):
    lista = []
    if extraer_numero(apt.get("gimnasio")):     lista.append("gym")
    if extraer_numero(apt.get("ascensor")):     lista.append("ascensor")
    if extraer_numero(apt.get("piscina")):      lista.append("piscina")
    if extraer_numero(apt.get("terraza")):      lista.append("terraza")
    if extraer_numero(apt.get("vigilancia")):   lista.append("seguridad")
    parq = extraer_numero(apt.get("parqueaderos")) or 0
    if parq > 0:                                lista.append("parqueadero")
    if extraer_numero(apt.get("salon_comunal")): lista.append("coworking")
    return lista


def recrear_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    crear_tablas()


def insertar_apartamentos_reales(lista):
    conn = conectar()
    cursor = conn.cursor()
    for apt in lista:
        cursor.execute("""
            INSERT INTO apartamentos
            (nombre, price, zona, barrio, distancia, pet_friendly, amenities, size, bedrooms,
             latitud, longitud, url, descripcion, imagen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            apt["nombre"],
            apt["price"],
            apt["zona"],
            apt.get("barrio", ""),
            apt["distancia"],
            apt["pet_friendly"],
            ",".join(apt["amenities"]),
            apt["size"],
            apt["bedrooms"],
            apt.get("latitud"),
            apt.get("longitud"),
            apt.get("url", ""),
            apt.get("descripcion", ""),
            apt.get("imagen", ""),
        ))
    conn.commit()
    conn.close()


def construir_indice_imagenes(raw_data):
    """Devuelve {codigo: 'url1,url2,...'} con hasta 6 fotos por apartamento."""
    indice = {}
    for d in raw_data:
        codigo = d.get("codigo", "")
        if not codigo:
            continue
        imgs_str = d.get("imagenes", "[]")
        try:
            imgs = ast.literal_eval(str(imgs_str))
            urls = [u for u in imgs if str(u).startswith("http")][:6]
            if urls:
                indice[codigo] = ",".join(urls)
        except Exception:
            pass
    return indice


def main():
    print("Descargando dataset procesado...")
    try:
        with urllib.request.urlopen(DATASET_URL, timeout=60) as resp:
            data = json.load(resp)
    except Exception as e:
        print(f"Error al descargar dataset procesado: {e}")
        sys.exit(1)
    print(f"  {len(data):,} registros totales")

    print("Descargando dataset raw (imagenes)...")
    try:
        with urllib.request.urlopen(RAW_URL, timeout=60) as resp:
            raw_data = json.load(resp)
        indice_imgs = construir_indice_imagenes(raw_data)
        print(f"  {len(indice_imgs):,} registros con imagen")
        del raw_data
    except Exception as e:
        print(f"  No se pudo descargar raw ({e}), continuando sin imagenes")
        indice_imgs = {}

    # ── Filtrar arriendo en las zonas soportadas ──────────────────────────────
    por_zona: dict[str, list] = {z: [] for z in LOCALIDAD_ZONA.values()}

    for apt in data:
        if apt.get("tipo_operacion") != "ARRIENDO":
            continue

        precio = extraer_numero(apt.get("precio_arriendo"))
        if precio is None or es_nan(precio) or precio <= 0:
            continue
        precio = int(precio)
        if not (PRECIO_MIN <= precio <= PRECIO_MAX):
            continue

        localidad = apt.get("localidad", "")
        zona = LOCALIDAD_ZONA.get(localidad)
        if not zona:
            continue

        area = extraer_numero(apt.get("area"))
        habitaciones = extraer_numero(apt.get("habitaciones"))
        if es_nan(area) or es_nan(habitaciones) or not area or not habitaciones:
            continue

        distancia_tm = extraer_numero(apt.get("distancia_estacion_tm_m"))
        distancia_km = (
            round(float(distancia_tm) / 1000, 2)
            if distancia_tm and not es_nan(distancia_tm)
            else 2.0
        )

        amenities = construir_amenities(apt)

        barrio_raw = str(apt.get("barrio") or "").strip().title()

        lat = extraer_numero(apt.get("latitud"))
        lon = extraer_numero(apt.get("longitud"))
        lat = float(lat) if lat and not es_nan(lat) else None
        lon = float(lon) if lon and not es_nan(lon) else None

        codigo = apt.get("codigo", "")
        por_zona[zona].append({
            "nombre":       codigo if codigo else f"Apt-{apt.get('_id', {}).get('$oid', 'X')[-6:]}",
            "price":        precio,
            "zona":         zona,
            "barrio":       barrio_raw,
            "distancia":    min(distancia_km, 9.9),
            "pet_friendly": int(_es_pet_friendly(apt)),
            "amenities":    amenities,
            "size":         int(area),
            "bedrooms":     int(habitaciones),
            "latitud":      lat,
            "longitud":     lon,
            "_codigo":      codigo,
            "_descripcion": str(apt.get("descripcion") or ""),
        })

    # ── Seleccionar N por zona con diversidad de precio y pet_friendly ──────────
    seleccionados = []
    random.seed(42)

    def _sample_evenly(group, k):
        """Toma k elementos distribuidos uniformemente por precio."""
        if len(group) <= k:
            return list(group)
        paso = max(1, len(group) // k)
        return group[::paso][:k]

    for zona, lista in por_zona.items():
        if not lista:
            print(f"  WARN  Sin datos para zona: {zona}")
            continue

        lista.sort(key=lambda x: x["price"])

        # Garantizar representación pet_friendly: hasta 25% de la cuota
        pet      = [a for a in lista if a["pet_friendly"]]
        no_pet   = [a for a in lista if not a["pet_friendly"]]
        n_pet    = min(len(pet), max(3, APTS_POR_ZONA // 4))
        n_no_pet = APTS_POR_ZONA - n_pet

        muestra = _sample_evenly(pet, n_pet) + _sample_evenly(no_pet, n_no_pet)
        muestra.sort(key=lambda x: x["price"])
        muestra = muestra[:APTS_POR_ZONA]

        for a in muestra:
            codigo = a.get("_codigo", "")
            a["url"]         = f"https://www.metrocuadrado.com/inmueble/detalle/{codigo}/" if codigo else ""
            a["descripcion"] = a.get("_descripcion", "")[:400]
            a["imagen"]      = indice_imgs.get(codigo, "")

        seleccionados.extend(muestra)
        n_pf = sum(1 for a in muestra if a["pet_friendly"])
        print(f"  OK {zona}: {len(muestra)} apts (pet_friendly: {n_pf}) — de {len(lista):,} disponibles")

    # ── Cargar en SQLite ──────────────────────────────────────────────────────
    print(f"\nCargando {len(seleccionados)} apartamentos reales en la base de datos...")
    recrear_db()
    insertar_apartamentos_reales(seleccionados)

    print(f"\nOK Listo. {len(seleccionados)} apartamentos reales cargados.")
    print("   Rango de precios:", f"${min(a['price'] for a in seleccionados):,}", "–",
          f"${max(a['price'] for a in seleccionados):,}")
    print("   Ejecuta la app con: .venv/Scripts/streamlit run app_local.py")


if __name__ == "__main__":
    main()
