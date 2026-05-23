# Documentación Técnica Completa — Matching de Apartamentos con Teoría de Grafos

**Proyecto:** Sistema de asignación óptima de apartamentos mediante grafos bipartitos ponderados  
**Asignatura:** Teoría de Grafos · 4to semestre · Universidad del Rosario  
**Autores:** Jhon Rivera · Laura Sierra · Alejandro Arroyave · Juan José Garzón  
**Tecnologías:** Python · Streamlit · SQLite · scipy · folium · GSAP · Three.js  
**Última actualización:** Sesión 7 (2026-05-17)

---

## Índice

1. [Descripción general del sistema](#1-descripción-general-del-sistema)
2. [Arquitectura y estructura de archivos](#2-arquitectura-y-estructura-de-archivos)
3. [Modelo matemático](#3-modelo-matemático)
4. [Base de datos — Esquema SQLite](#4-base-de-datos--esquema-sqlite)
5. [Módulo NLP — Extracción de entidades](#5-módulo-nlp--extracción-de-entidades)
6. [Algoritmo de matching](#6-algoritmo-de-matching)
7. [Datos reales — Pipeline de carga](#7-datos-reales--pipeline-de-carga)
8. [Features implementadas](#8-features-implementadas)
9. [Visualizaciones](#9-visualizaciones)
10. [Interfaz de usuario — Diseño y CSS](#10-interfaz-de-usuario--diseño-y-css)
11. [Usuarios de prueba y resultados del matching](#11-usuarios-de-prueba-y-resultados-del-matching)
12. [Bugs corregidos por sesión](#12-bugs-corregidos-por-sesión)
13. [Dependencias e instrucciones de ejecución](#13-dependencias-e-instrucciones-de-ejecución)

---

## 1. Descripción general del sistema

El sistema resuelve el problema de asignación óptima entre buscadores de vivienda y apartamentos disponibles en Bogotá. En lugar de usar filtros lineales tradicionales, modela el problema como un **grafo bipartito ponderado** y aplica el **Algoritmo Húngaro** para encontrar la asignación globalmente óptima.

### Flujo principal del sistema

```
Entrada de usuario en lenguaje natural
           ↓
   Extracción NLP (regex en español)
   → presupuesto, zona, barrio, mascotas,
     amenities, habitaciones, tamaño, radio
           ↓
  Construcción del grafo bipartito G=(U∪O, E, w)
  + cálculo de peso w(u,o) para cada par válido
           ↓
  Algoritmo Húngaro (scipy.optimize.linear_sum_assignment)
           ↓
  TOP 3 resultados + Mapa interactivo + Grafo bipartito
```

### Dos versiones del sistema

| | `app_local.py` | `app.py` |
|---|---|---|
| Base de datos | SQLite local | Supabase (PostgreSQL cloud) |
| Requiere secrets | No | Sí (SUPABASE_URL + SUPABASE_KEY) |
| NLP completo | Sí (sesión 5+) | Versión básica |
| Mapa interactivo | Sí | No |
| Barrios | Sí | No |
| UI rediseñada | Sí (Clean · High Contrast) | Básica |
| **Versión recomendada** | **Principal** | Solo cloud/demo |

---

## 2. Arquitectura y estructura de archivos

```
matching-apartamentos-grafos/
├── app_local.py             # Aplicación principal (2388 líneas)
│   ├── Módulo NLP           # extraer_entidades(), _barrios_en_bd(), _sin_tildes()
│   ├── Módulo Matching      # calcular_peso(), buscar_compatibles(), construir_matriz()
│   │                        # ejecutar_matching(), ejecutar_matching_maximo()
│   ├── Módulo Visualización # crear_mapa_folium(), visualizar_grafo_bipartito()
│   └── Módulo UI (Streamlit)# 5 secciones: chat, registro, matching, 3D, BD
├── app.py                   # Versión cloud (Supabase)
├── database.py              # Capa de datos SQLite (182 líneas)
│   ├── crear_tablas()
│   ├── insertar_usuario(), insertar_apartamento()
│   ├── cargar_usuarios(), cargar_apartamentos()
│   ├── guardar_asignacion(), limpiar_asignaciones()
│   └── cargar_asignaciones_detalladas()
├── cargar_datos_reales.py   # Script de carga (277 líneas)
│   ├── Descarga 2 datasets de GitHub (procesado + raw)
│   ├── Filtra arriendo, rango de precio, zonas
│   ├── Muestreo diversificado (diversidad de pet_friendly)
│   └── Carga 210 apartamentos en SQLite
├── database.db              # SQLite generado automáticamente
├── docs/
│   ├── proyecto_teoria_grafos.md    # Documentación académica
│   └── documentacion_tecnica_completa.md  # Este archivo
├── design-system/
│   └── matching-apartamentos/MASTER.md    # Design tokens
└── .venv/                   # Entorno virtual Python
```

### Dependencias entre módulos

```
app_local.py
  └── importa: database.py
               re, unicodedata (stdlib)
               pandas, streamlit
               scipy.optimize.linear_sum_assignment
               folium, streamlit_folium
               json (stdlib)
               st.components.v1.html (Streamlit built-in)

database.py
  └── importa: sqlite3, pandas

cargar_datos_reales.py
  └── importa: database.py
               ast, json, math, os, random, urllib.request (stdlib)
```

---

## 3. Modelo matemático

### Grafo bipartito ponderado

```
G = (U ∪ O, E, w)
```

- **U** = conjunto de buscadores (usuarios registrados en BD)
- **O** = conjunto de apartamentos disponibles
- **E** ⊆ U × O = aristas de compatibilidad (solo existen si se cumplen restricciones duras)
- **w : E → [0, 1]** = función de peso/compatibilidad

### Restricciones duras (hard constraints)

Una arista `(u, o) ∈ E` existe **únicamente** si se cumplen **todas** las siguientes condiciones:

```python
def calcular_peso(usuario, apt):
    # Restricción 1: Precio dentro del presupuesto
    if float(apt["price"]) > float(usuario["budget"]):
        return 0
    # Restricción 2: Distancia dentro del radio
    if float(apt["distancia"]) > float(usuario["radio"]):
        return 0
    # Restricción 3: Compatibilidad con mascotas
    if usuario["pets"] and not apt["pet_friendly"]:
        return 0
    # Si pasa las 3 → la arista existe, se calcula w(u,o)
```

> **Nota importante:** La condición `amenity_match ≥ 0.50` fue degradada de restricción dura a restricción blanda en sesión 4. Con el dataset de 210 apartamentos y un solo amenity requerido, el hard cut eliminaba todos los apartamentos de ciertas zonas. Los amenities ahora solo influyen en el score.

### Función de peso w(u, o)

```
w(u, o) = 0.40 · price_score + 0.30 · location_score + 0.30 · secondary_score
```

**Desglose de cada componente:**

```python
# price_score: qué tan cercano está el precio al presupuesto
price_score = 1 - abs(apt["price"] - usuario["budget"]) / usuario["budget"] * 0.5

# location_score: qué tan cerca está dentro del radio
location_score = 1 - apt["distancia"] / usuario["radio"]

# secondary_score: amenities + tamaño + habitaciones + mascotas
amenity_score  = peso_match / peso_total  # ponderado por importancia del amenity
size_score     = 1 - abs(apt["size"] - usuario["size_deseado"]) / usuario["size_deseado"] * 0.5
bedroom_score  = 1 - abs(apt["bedrooms"] - usuario["bedrooms_deseado"]) / usuario["bedrooms_deseado"] * 0.5
pet_score      = 1

secondary_score = 0.35*amenity_score + 0.35*size_score + 0.20*bedroom_score + 0.10*pet_score
```

**Pesos individuales de amenities:**

| Amenity | Peso | Justificación |
|---|---|---|
| parqueadero | 0.80 | Alta demanda en Bogotá, escasez urbana |
| ascensor | 0.70 | Accesibilidad y comodidad |
| seguridad | 0.70 | Vigilancia 24h, portería |
| gym | 0.50 | Valor agregado moderado |
| piscina | 0.50 | Valor agregado moderado |
| coworking | 0.50 | Relevante trabajo remoto |
| terraza | 0.40 | Preferencia estética |
| zona BBQ | 0.40 | Preferencia social |

**Cálculo ponderado de amenities:**

```python
requeridos  = set(texto_a_lista(usuario["amenities_req"]))  # ej: {"gym", "parqueadero"}
disponibles = set(texto_a_lista(apt["amenities"]))

if requeridos:
    peso_total = sum(_AMENITY_WEIGHTS.get(a, 0.50) for a in requeridos)
    peso_match = sum(_AMENITY_WEIGHTS.get(a, 0.50) for a in requeridos & disponibles)
    amenity_match = peso_match / peso_total
else:
    amenity_match = 1.0  # sin requisitos → score perfecto
```

### Problema de optimización

Se formula como un Programa Lineal Entero (ILP):

```
max  Σᵢⱼ w(uᵢ, oⱼ) · xᵢⱼ

s.t. Σⱼ xᵢⱼ ≤ 1    ∀i ∈ U    (cada buscador a máximo un apartamento)
     Σᵢ xᵢⱼ ≤ 1    ∀j ∈ O    (cada apartamento a máximo un buscador)
     xᵢⱼ ∈ {0, 1}
```

---

## 4. Base de datos — Esquema SQLite

### Implementación en `database.py`

```python
def crear_tablas():
    # Tabla usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        budget REAL,
        zona TEXT,
        radio REAL,
        pets INTEGER,           -- 0 o 1
        amenities_req TEXT,     -- CSV: "gym,parqueadero"
        size_deseado REAL,
        bedrooms_deseado INTEGER
    )""")

    # Tabla apartamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apartamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,            -- código del listing (ej: "MC-12345")
        price REAL,             -- precio mensual en COP
        zona TEXT,              -- localidad (Chapinero, Suba, ...)
        barrio TEXT,            -- barrio real (ej: "S.C. Chico Norte")
        distancia REAL,         -- km a estación TransMilenio más cercana
        pet_friendly INTEGER,   -- 0 o 1
        amenities TEXT,         -- CSV: "gym,ascensor,parqueadero"
        size REAL,              -- área en m²
        bedrooms INTEGER,       -- número de habitaciones
        latitud REAL,           -- coordenada GPS (WGS84)
        longitud REAL,          -- coordenada GPS (WGS84)
        url TEXT,               -- link al listing en MetroCuadrado
        descripcion TEXT,       -- descripción del inmueble (max 400 chars)
        imagen TEXT             -- URLs de fotos separadas por coma (hasta 6)
    )""")

    # Tabla asignaciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asignaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,       -- FK → usuarios.id
        apartamento_id INTEGER,   -- FK → apartamentos.id
        peso REAL                 -- w(u,o) ∈ [0,1]
    )""")
```

### Convenciones de datos

- `amenities` y `amenities_req`: strings CSV, ej: `"gym,ascensor,parqueadero"`. La función `texto_a_lista()` los convierte a lista: `[x.strip() for x in texto.split(",")]`.
- `imagen`: URLs separadas por coma, hasta 6 fotos por apartamento (CDN MetroCuadrado).
- `distancia`: distancia en **km** a la estación de TransMilenio más cercana (proxy de centralidad/accesibilidad urbana).
- `pet_friendly`: inferido de la descripción del listing porque el campo `permite_mascotas` del scraper original es 0 para todos los registros (bug del scraper).

### Funciones CRUD implementadas

| Función | Descripción |
|---|---|
| `crear_tablas()` | CREATE TABLE IF NOT EXISTS para las 3 tablas |
| `insertar_usuario(nombre, budget, zona, radio, pets, amenities_req, size_deseado, bedrooms_deseado)` | INSERT en tabla usuarios |
| `insertar_apartamento(nombre, price, zona, distancia, pet_friendly, amenities, size, bedrooms, url, descripcion, imagen, barrio, latitud, longitud)` | INSERT en tabla apartamentos |
| `cargar_usuarios()` | SELECT * FROM usuarios → DataFrame |
| `cargar_apartamentos()` | SELECT * FROM apartamentos → DataFrame |
| `guardar_asignacion(usuario_id, apartamento_id, peso)` | INSERT en asignaciones |
| `limpiar_asignaciones()` | DELETE FROM asignaciones (antes de nuevo matching) |
| `cargar_asignaciones_detalladas()` | JOIN de las 3 tablas → DataFrame con nombre usuario, nombre apt, peso |

---

## 5. Módulo NLP — Extracción de entidades

### Función principal: `extraer_entidades(texto)`

Parsea texto libre en español sin modelos de ML. Usa exclusivamente expresiones regulares (módulo `re`) y comparación de subcadenas.

**Entidades extraídas:**

| Entidad | Ejemplos detectados | Implementación |
|---|---|---|
| `budget` | "2 millones", "1.800.000", "$2,000,000" | `re.search(r'(\d+(?:[.,]\d+)?)\s*(?:millones?\|mll?\.?)', t)` |
| `zona` | "Chapinero", "Usaquén", "Kennedy" | Lookup en `_ZONA_KEYWORDS` dict |
| `barrio` | "Chico Reservado", "Niza", "Rafael Núñez" | `_barrios_en_bd()` + `_sin_tildes()` |
| `radio` | "5 km", "3 kilómetros" | regex km |
| `pets` | "perrita", "gato", "mascota", "canino" | Lista `_pets_positivos` + regex negación |
| `amenities` | "gym", "parqueadero", "ascensor" | Lookup en `_AMENITY_KEYWORDS` dict |
| `bedrooms` | "2 habitaciones", "3 cuartos", "1 alcoba" | regex habitaciones |
| `size` | "60 metros", "80 m2", "80 m²" | regex metros/m2 |
| `tipo` | "arriendo", "alquiler", "compra", "venta" | keywords + inferencia por presupuesto |

**Defaults automáticos cuando no se detecta:**
- `budget` → `$2,000,000` + aviso `st.info()` al usuario
- `tipo` → `"arriendo"` (todos los datos son arriendo)
- `radio` → `5.0` km
- `bedrooms_deseado` → `2`
- `size_deseado` → `85` m²

### Diccionarios de keywords

```python
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

_ZONA_KEYWORDS = {
    "Chapinero":   ["chapinero", "chico reservado", "chico norte", "chico",
                    "rosales", "cabrera", "antiguo country"],
    "Suba":        ["suba", "niza", "alhambra", "prado veraniego", "rincón"],
    "Usaquén":     ["usaquén", "usaquen", "santa bárbara", "santa barbara",
                    "cedritos", "country club", "unicentro"],
    "Teusaquillo": ["teusaquillo", "palermo", "la soledad", "armenia"],
    "Centro":      ["centro", "candelaria", "santa fe", "mártires", "martires", "la concordia"],
    "Kennedy":     ["kennedy", "américas", "americas", "bosa"],
    "Engativá":    ["engativá", "engativa", "boyacá real", "boyaca real", "garcés navas"],
}
```

### Detección robusta de barrios con tildes/ñ

**Problema:** el barrio en la BD puede llamarse `"Rafael Nunez"` (sin ñ) pero el usuario escribe `"Rafael Núñez"`. La comparación directa falla porque `ñ ≠ n`.

**Solución:** función `_sin_tildes()` que normaliza vía `unicodedata.NFD`:

```python
import unicodedata

def _sin_tildes(texto: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'   # elimina diacríticos
    ).replace('ñ', 'n')
```

**Detección dinámica de barrios:**

```python
def _barrios_en_bd():
    """Consulta la BD en cada búsqueda para detectar barrios disponibles."""
    conn = conectar()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT barrio FROM apartamentos WHERE barrio IS NOT NULL AND barrio != ''")
    barrios = [r[0].lower() for r in cur.fetchall() if r[0]]
    conn.close()
    return sorted(barrios, key=len, reverse=True)  # más largos primero → evita falsos positivos
```

En `extraer_entidades()`, tras detectar zona, se hace un segundo pass:

```python
t_norm = _sin_tildes(t)
for barrio in _barrios_en_bd():
    if barrio and _sin_tildes(barrio) in t_norm:
        entidades["barrio"] = barrio
        break
```

### Detección de mascotas con negación

```python
# Primero verificar negación
negacion_pets = bool(re.search(
    r'\b(no\s+tengo|no\s+hay|sin|no\s+tiene|tampoco)\b.{0,25}'
    r'\b(gato|gatos|gata|gatas|perro|perros|perra|perras|'
    r'mascota|mascotas|pet|pets|animal|animales|cachorro|cachorros)\b', t
))

# Lista completa de términos positivos (incluye diminutivos)
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
```

### Herencia de parámetros entre mensajes del chat

En la interfaz conversacional, si el nuevo mensaje no menciona ciertos parámetros, se heredan del mensaje anterior:

```python
prev_results = [m for m in st.session_state["chat_msgs"]
                if m.get("role") == "assistant" and m.get("type") == "results"]
if prev_results:
    prev = prev_results[-1]["entidades"]
    heredados = []
    if not ent["budget"] and prev.get("budget"):
        ent["budget"] = prev["budget"]
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
        ent["zona"] = prev["zona"]
        heredados.append(f'zona {prev["zona"]}')
    ent["_heredados"] = heredados
```

Los parámetros heredados se muestran al usuario con nota: `"(recordé del mensaje anterior: presupuesto $4,000,000)"`.

### Jerarquía de filtros geográficos en `buscar_compatibles()`

```
barrio (más específico)
  → si hay resultados: retorna resultados del barrio
  → si no: aviso + fallback a zona

zona (localidad)
  → si hay resultados: retorna resultados de la zona
  → si no: aviso con razón + fallback a todas las zonas

sin filtro geográfico
  → retorna todos los compatibles ordenados por compatibilidad
```

---

## 6. Algoritmo de matching

### Estrategia 1: Peso máximo (Algoritmo Húngaro)

El algoritmo Húngaro resuelve el problema de asignación óptima en tiempo O(n³). `scipy.optimize.linear_sum_assignment` implementa la versión eficiente de Kuhn-Munkres.

**El algoritmo minimiza**, por lo que se convierte la matriz de maximización:
- Si `w(u,o) = 0` → costo = `9999` (arista inválida, nunca asignar)
- Si `w(u,o) > 0` → costo = `1 - w(u,o)` (invertir para minimizar)

```python
def ejecutar_matching():
    W, usuarios, apartamentos = construir_matriz()
    # W[i,j] = w(usuario_i, apartamento_j) ∈ [0, 1]

    C = W.copy()
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            C.iloc[i, j] = 9999 if C.iloc[i, j] == 0 else 1 - C.iloc[i, j]

    filas, columnas = linear_sum_assignment(C)  # ← ALGORITMO HÚNGARO
    limpiar_asignaciones()  # borra asignaciones previas

    for i, j in zip(filas, columnas):
        peso = W.iloc[i, j]
        if peso > 0:
            guardar_asignacion(uid, aid, float(peso))
    # retorna W (matriz completa) + DataFrame con asignaciones
```

### Estrategia 2: Matching máximo (Cardinalidad)

Misma infraestructura pero con matriz binaria: `0` si compatible (arista válida), `9999` si no. Maximiza el **número** de asignaciones sin considerar calidad.

```python
def ejecutar_matching_maximo():
    W, usuarios, apartamentos = construir_matriz()

    C = W.copy()
    for i in range(C.shape[0]):
        for j in range(C.shape[1]):
            C.iloc[i, j] = 9999 if C.iloc[i, j] == 0 else 0  # binario

    filas, columnas = linear_sum_assignment(C)
    # NO guarda en BD → solo para comparación visual
```

### Construcción de la matriz de pesos

```python
def construir_matriz():
    usuarios     = cargar_tabla("usuarios")
    apartamentos = cargar_tabla("apartamentos")

    matriz = []
    for _, u in usuarios.iterrows():
        fila = [calcular_peso(u, apt) for _, apt in apartamentos.iterrows()]
        matriz.append(fila)

    W = pd.DataFrame(matriz,
                     index=usuarios["id"],      # filas = IDs de usuarios
                     columns=apartamentos["id"]) # columnas = IDs de apartamentos
    return W, usuarios, apartamentos
```

La matriz W tiene dimensiones `|U| × |O|` (usuarios × apartamentos). Con 10 usuarios y 210 apartamentos: matriz 10×210.

### Resultados con los 10 usuarios de prueba

| Estrategia | Asignados | Peso promedio | Cobertura |
|---|---|---|---|
| Húngaro (peso máximo) | 10/10 | **0.897** | 100% |
| Cardinalidad máxima | 10/10 | 0.695 | 100% |
| **Diferencia** | igual | **+0.202 (+29%)** | igual |

El Húngaro produce matches de significativamente mayor calidad sin sacrificar cobertura.

---

## 7. Datos reales — Pipeline de carga

### Fuente de datos

**Dataset:** [github.com/builker-col/bogota-apartments](https://github.com/builker-col/bogota-apartments)  
**Versión:** v2.0.0-august-2024  
**Scraping:** MetroCuadrado + Habi

Se descargan dos archivos JSON:

| Archivo | Registros | Uso |
|---|---|---|
| `processed_v2.0.0_august_2_2024.json` | 43,013 | Todos los campos tipados (precio, área, barrio, coords, amenities) |
| `raw_v2.0.0_august_2_2024.json` | 44,436 | Campo `imagenes` con URLs del CDN |

### Pipeline de procesamiento

```python
def main():
    # 1. Descargar datasets
    data = json.load(urllib.request.urlopen(DATASET_URL))        # procesado
    raw_data = json.load(urllib.request.urlopen(RAW_URL))        # raw (fotos)
    indice_imgs = construir_indice_imagenes(raw_data)             # {codigo: "url1,url2,..."}
    del raw_data  # liberar memoria

    # 2. Filtrar registros válidos
    for apt in data:
        # Solo arriendo
        if apt.get("tipo_operacion") != "ARRIENDO": continue
        # Precio en rango $600k - $4M
        precio = extraer_numero(apt.get("precio_arriendo"))
        if not (600_000 <= precio <= 4_000_000): continue
        # Solo zonas soportadas (7 localidades)
        zona = LOCALIDAD_ZONA.get(apt.get("localidad"))
        if not zona: continue
        # Área y habitaciones válidos
        if not area or not habitaciones: continue

    # 3. Muestreo diversificado por zona
    for zona, lista in por_zona.items():
        lista.sort(key=lambda x: x["price"])
        pet      = [a for a in lista if a["pet_friendly"]]
        no_pet   = [a for a in lista if not a["pet_friendly"]]
        n_pet    = min(len(pet), max(3, 30 // 4))   # máx 25% → ≥7 pet/zona
        n_no_pet = 30 - n_pet
        muestra  = _sample_evenly(pet, n_pet) + _sample_evenly(no_pet, n_no_pet)
        muestra  = muestra[:30]

    # 4. Cargar en SQLite (borra BD anterior)
    recrear_db()
    insertar_apartamentos_reales(seleccionados)
```

### Detección de pet_friendly desde descripción

El campo `permite_mascotas` del scraper es 0 para **todos** los registros (bug documentado). Se infiere desde el texto de la descripción:

```python
_PET_KEYWORDS = [
    "mascota", "mascotas", "pet friendly", "petfriendly",
    "admite perro", "acepta perro", "admite mascota", "acepta mascota",
    "perros permitidos", "gatos permitidos"
]

def _es_pet_friendly(apt):
    val = extraer_numero(apt.get("permite_mascotas")) or 0
    if val == 1: return True  # por si acaso
    desc = str(apt.get("descripcion") or "").lower()
    return any(k in desc for k in _PET_KEYWORDS)
```

### Extracción de amenities desde campos booleanos del dataset

```python
def construir_amenities(apt):
    lista = []
    if extraer_numero(apt.get("gimnasio")):      lista.append("gym")
    if extraer_numero(apt.get("ascensor")):      lista.append("ascensor")
    if extraer_numero(apt.get("piscina")):       lista.append("piscina")
    if extraer_numero(apt.get("terraza")):       lista.append("terraza")
    if extraer_numero(apt.get("vigilancia")):    lista.append("seguridad")
    parq = extraer_numero(apt.get("parqueaderos")) or 0
    if parq > 0:                                 lista.append("parqueadero")
    if extraer_numero(apt.get("salon_comunal")): lista.append("coworking")
    return lista
```

### Resultado del pipeline

| Zona | Apts cargados | Pet-friendly | Barrios únicos aprox. |
|---|---|---|---|
| Chapinero | 30 | ≥7 | ~20 |
| Usaquén | 30 | ≥7 | ~20 |
| Suba | 30 | ≥7 | ~20 |
| Engativá | 30 | ≥7 | ~15 |
| Kennedy | 30 | ≥7 | ~15 |
| Teusaquillo | 30 | ≥7 | ~12 |
| Centro | 30 | ≥7 | ~18 |
| **Total** | **210** | **≥49** | **~140** |

- Rango de precios: $600,000 – $4,000,000 COP/mes
- Todos los apartamentos tienen coordenadas GPS reales (WGS84)
- URLs a listings originales en MetroCuadrado
- Hasta 6 fotos por apartamento (CDN de MetroCuadrado)

---

## 8. Features implementadas

### Feature 1 — NLP Input

El usuario describe en texto libre lo que busca. No requiere formularios ni campos estructurados.

**Ejemplo:**
> "Busco apartamento en chico reservado, máximo 3 millones, con gym y parqueadero. Tengo una perrita."

### Feature 2 — Entity Extraction

`extraer_entidades()` extrae automáticamente todos los parámetros relevantes. Ver sección 5 para detalle completo.

### Feature 3 — Amenities ponderados

Cada amenity tiene un peso individual en el cálculo de compatibilidad (no todos valen igual). Parqueadero y ascensor/seguridad tienen mayor peso que terraza o BBQ. Ver tabla en sección 3.

### Feature 4 — Manejo de ambigüedad

Si el NLP no detecta presupuesto o tipo, se aplican **defaults automáticos** en lugar de bloquear con un formulario intermedio:
- `budget` no detectado → default `$2,000,000` + aviso `st.info()` explicativo
- `tipo` no detectado → default `"arriendo"` (todos los datos son arriendo)
- Los resultados se muestran **inmediatamente** con un solo clic

### Feature 5 — TOP 3 resultados

Los 3 apartamentos con mayor peso de compatibilidad. Cada tarjeta muestra:

```html
<div class="aptcard">
  <!-- Foto principal con onerror fallback al placeholder SVG -->
  <!-- Badge de ranking (dorado/#1, plata/#2, bronce/#3) -->
  <!-- Badge de match circular: conic-gradient verde≥80%, teal≥60%, ámbar<60% -->
  <!-- Nombre en Cinzel + zona (pill teal) + barrio real (pill gris) -->
  <!-- Precio prominente en Cinzel -->
  <!-- Stats row: tamaño m², habitaciones, distancia TM km, pet badge -->
  <!-- Pills de amenities disponibles -->
  <!-- Botón "Ver fotos y descripción" → st.dialog() con galería completa -->
</div>
```

El badge de match usa `conic-gradient` CSS:
```html
style="background: conic-gradient(#059669 85%, rgba(226,232,240,.9) 85%);"
```

### Feature 6 — Visualización del grafo bipartito 2D (SVG + GSAP)

`visualizar_grafo_bipartito()` retorna `(html_string, height_px)` renderizado con `st.components.v1.html()`.

**Técnica de inyección de datos Python → JS:**
```python
# Template con tokens, NO f-string (evita escapar {} del JS)
TMPL = """...(html con __APT_JSON__ y __USER_JSON__)..."""
html = (TMPL
        .replace("__APT_JSON__",  json.dumps(apt_data))
        .replace("__USER_JSON__", json.dumps(user_data))
        .replace("__H__",         str(H)))
```

**Animaciones GSAP:**
- Nodos entran con `gsap.from(circle, {attr:{r:0}, ease:'back.out(2)'})` escalonado
- Aristas se dibujan con `stroke-dasharray` + `stroke-dashoffset` animado
- Pulso radial infinito en nodo U: `gsap.to(uRing, {attr:{r:52}, opacity:0, repeat:-1})`
- Etiquetas `w=0.85` aparecen después de las aristas
- 4 partículas por arista TOP via `<animateMotion>` + `<mpath href="#pid">`
- Hover: tooltip flotante, GSAP escala el nodo

**Layout:**
- Nodo U (buscador) a la izquierda en `x=125`
- Nodos O (apartamentos) a la derecha en `x=665`, distribuidos verticalmente
- Aristas como curvas Bézier cúbicas
- MAX_SHOW = 15 apartamentos
- Altura dinámica: `min(720, max(480, n*50+100))`

### Feature 7 — Datos reales + fotos + coordenadas

210 apartamentos reales de Bogotá con:
- Fotos reales del CDN de MetroCuadrado (hasta 6 por apartamento)
- Barrio real de cada inmueble (140 barrios únicos)
- Coordenadas GPS para todos → habilita el mapa interactivo
- Link directo al listing original

### Feature 8 — Comparación de estrategias de matching

Sección "Ejecutar matching" con dos tabs:
- **Tab 1 — Peso máximo (Húngaro):** usa `linear_sum_assignment` con costo `1 - w`. Maximiza compatibilidad total.
- **Tab 2 — Matching máximo (Cardinalidad):** usa matriz binaria. Maximiza número de asignaciones.
- **Tabla comparativa:** asignaciones, peso total, peso promedio, cobertura lado a lado.
- **Insight dinámico:** mensaje adaptado según cuál estrategia asignó más usuarios.

### Feature 9 — Mapa interactivo de ubicaciones

```python
def crear_mapa_folium(compatibles, top3):
    m = folium.Map(location=centro, zoom_start=13, tiles="CartoDB positron")

    rank_colors = {0: "orange", 1: "lightgray", 2: "beige"}
    rank_labels = {0: "★ #1",   1: "★ #2",      2: "★ #3"}

    for apt in reversed(con_coords):
        folium.Marker(
            location=[apt["latitud"], apt["longitud"]],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{'★ ' if es_top else ''}{apt['nombre']} — {pct}% match",
            icon=folium.Icon(color=color, icon="home", prefix="fa"),
        ).add_to(m)
    return m
```

El popup HTML incluye: nombre, precio, barrio, zona, tamaño, habitaciones, distancia TM, % match, link al listing.

El mapa se renderiza con `st_folium(mapa, width="100%", height=420, returned_objects=[])` dentro de un expander `expanded=True`.

### Feature 10 — Universo 3D del grafo

```python
# Tecnología: 3d-force-graph (Three.js) desde CDN unpkg.com
# Sin dependencias Python adicionales — renderizado en HTML/JS via st.components.v1.html()
```

**Estructura del grafo 3D:**

```python
_nodes = [
    {"id": "u_1", "label": "Felipe Herrera", "type": "user",
     "color": "#FCD34D", "size": 14, "zone": "Chapinero"},
    {"id": "a_45", "label": "MC-12345", "type": "apt",
     "color": "#5EEAD4",  # color por zona
     "size": 8,           # 8=matched, 5=compatible, 2.5=sin conexión
     "matched": True, "connected": True},
    ...
]

_links = [
    {"source": "u_1", "target": "a_45",
     "weight": 0.923, "matched": True,
     "color": "#5EEAD4",  # teal para matched, navy oscuro para compatible
     "width": 3.5},       # 3.5 para matched, 0.5 para compatible
]
```

**Colores por zona:**

| Zona | Color |
|---|---|
| Chapinero | `#5EEAD4` |
| Usaquén | `#C4B5FD` |
| Suba | `#93C5FD` |
| Teusaquillo | `#FCD34D` |
| Centro | `#FCA5A5` |
| Kennedy | `#86EFAC` |
| Engativá | `#F9A8D4` |

**Inicialización del grafo (dentro de `window.addEventListener('load', ...)`):**

```javascript
window.addEventListener('load', function() {
    var gEl = document.getElementById('g');
    var _w = Math.round(gEl.getBoundingClientRect().width) || 900;
    Graph = ForceGraph3D()(gEl)
        .width(_w || 900).height(940)
        .backgroundColor('#05071A')
        .graphData(data)
        .nodeColor(nodeColorFn).nodeVal(nodeVal)
        .nodeOpacity(0.9).nodeResolution(14)
        .linkColor(l => l.color).linkWidth(l => l.width)
        .linkOpacity(0.6)
        .linkDirectionalParticles(l => showPart && l.matched ? 6 : 0)
        .linkDirectionalParticleSpeed(0.005)
        .linkDirectionalParticleColor(() => '#5EEAD4')
        .onNodeClick(n => { /* modo enfoque o zoom */ })
        .onNodeHover(n => { /* tooltip */ });
    Graph.d3Force('charge').strength(-150);
    startRot();  // rotación automática suave
});
```

**Funcionalidades interactivas:**
- Hover → tooltip con detalle del nodo
- Clic en usuario → modo enfoque (solo sus conexiones)
- Drag → rotación 3D libre
- Scroll → zoom
- 4 sliders: rotación, tamaño nodos, opacidad aristas, repulsión
- 3 toggles: modo enfoque, mostrar desconectados, partículas
- Botones: resetear vista, explosión (repulsión -900 temporal)
- Teclas: F (fullscreen), R (reset), E (explosión), Escape (salir enfoque)
- Leyenda izquierda clicable para filtrar por zona
- Buscador de nodos por nombre

---

## 9. Visualizaciones

### Grafo bipartito 2D — Resumen técnico

| Aspecto | Detalle |
|---|---|
| Tecnología | SVG inline + GSAP 3.12.5 (CDN) |
| Fondo | `#050A14` (navy oscuro) |
| Nodo U | Esfera teal `radialGradient`, pulso infinito, tooltip |
| Nodo TOP 1 | Dorado `#D97706`, tamaño 21, label `#1` |
| Nodo TOP 2 | Gris `#94A3B8`, tamaño 21, label `#2` |
| Nodo TOP 3 | Bronce `#92400E`, tamaño 21, label `#3` |
| Nodo compatible | Azul oscuro `#1E3A5F`, tamaño 13 |
| Aristas TOP | Teal `#0F766E`, animada con `stroke-dashoffset`, 4 partículas |
| Aristas regulares | Gris `#1E293B`, opacidad 17% |
| Labels de peso | `w=0.87` sobre rectángulo fondo oscuro |
| Hover | GSAP escala nodo + tooltip flotante CSS |
| Renderizado | `st.components.v1.html(html, height=CH)` |

### Mapa interactivo — Resumen técnico

| Aspecto | Detalle |
|---|---|
| Tecnología | `folium` + `streamlit-folium` |
| Tiles | CartoDB Positron (claro, neutro, sin API key) |
| Marcador TOP 1 | Naranja `orange`, ícono FA `home` |
| Marcador TOP 2 | Gris claro `lightgray` |
| Marcador TOP 3 | Beige `beige` |
| Marcador compatible | Azul claro `cadetblue` |
| Popup | HTML con nombre, precio, barrio, zona, stats, % match, link |
| Centro | Centroide calculado dinámicamente de todos los resultados |
| Renderizado | `st_folium(mapa, width="100%", height=420, returned_objects=[])` |

### Universo 3D — Resumen técnico

| Aspecto | Detalle |
|---|---|
| Tecnología | `3d-force-graph@1` (Three.js) desde CDN `unpkg.com` |
| Fondo | `#05071A` navy oscuro |
| Dimensiones | 940px altura fija (CSS + JS) |
| Física | d3-force 3D, repulsión configurable |
| Aristas matched | Teal `#5EEAD4`, ancho 3.5, 6 partículas animadas |
| Aristas compatibles | Navy `#1E3A5F`, ancho 0.5, sin partículas |
| Datos | Todos los 210 apts + usuarios, top-15 aristas por usuario |
| Renderizado | `st.components.v1.html(_html, height=960)` |

---

## 10. Interfaz de usuario — Diseño y CSS

### Design tokens

| Token | Valor | Uso |
|---|---|---|
| Fondo app | `#F8FAFC` | `stApp background` |
| Sidebar | `#FFFFFF` + borde `#E2E8F0` | Fondo blanco limpio |
| Color primario (teal) | `#0F766E` | Botones, links, badges |
| Texto principal | `#0F172A` | Máximo contraste |
| Texto secundario | `#475569` / `#64748B` | Subtítulos, labels |
| Rank #1 | `#D97706` | Dorado |
| Rank #2 | `#475569` | Slate |
| Rank #3 | `#B45309` | Bronce |
| Fuente títulos | Cinzel (serif elegante, Google Fonts) | `h1`, `h2`, precios, métricas |
| Fuente cuerpo | Josefin Sans (Google Fonts) | Todo el resto |
| Cards border-radius | `18px` | Cards de apartamentos |
| Animación cards | `fadeSlideUp 280ms ease-out` | Entrada de tarjetas |

### Carga de fuentes (solución al bug de CSS visible)

**Problema:** usar `<link href="...">` antes de `<style>` hacía que el CSS apareciera como texto en la UI de Streamlit.

**Solución:** cargar fuentes con `@import url(...)` dentro del bloque `<style>`:

```css
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Josefin+Sans:wght@300;400;500;600;700&display=swap');
/* resto del CSS... */
</style>
```

### Navegación lateral como nav pills

```css
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: rgba(15,118,110,.09) !important;
    color: #0F766E !important;
    font-weight: 700 !important;
}
```

### Fixes de CSS conocidos para Streamlit

| Problema | Causa | Fix aplicado |
|---|---|---|
| CSS visible como texto | `<link>` antes de `<style>` | Usar `@import url(...)` dentro del `<style>` |
| Texto blanco sobre cards blancas | dark-theme de Streamlit aplica `color:white` | Override con `color: #0F172A !important` en `stMarkdownContainer p` |
| Color azul en selectbox/radio | Color por defecto de BaseUI | Override en `li[role="option"]` y `span[data-baseweb="tag"]` |
| Texto sidebar invisible tras fondo oscuro | `color` no heredado | `section[data-testid="stSidebar"] * { color:#E2E8F0 !important }` |

### Menú de la app

| Opción | Descripción técnica |
|---|---|
| Buscar apartamento | Chat conversacional: `st.chat_input` + historial en `session_state["chat_msgs"]` |
| Registrar usuario | `st.form` 2 columnas, validación inline, `insertar_usuario()` |
| Ejecutar matching | `ejecutar_matching()` + `ejecutar_matching_maximo()`, 2 tabs + tabla comparativa |
| Universo 3D | `st.components.v1.html()` con 3d-force-graph, 940px |
| Ver base de datos | Stats bar + 3 DataFrames de las tablas SQLite |

---

## 11. Usuarios de prueba y resultados del matching

Estos 10 usuarios fueron insertados directamente en `database.db` para tener un dataset de prueba representativo:

| # | Nombre | Presupuesto | Zona | Pets | Amenities requeridos |
|---|---|---|---|---|---|
| 1 | Felipe Herrera | $3,800,000 | Chapinero | No | gym · piscina · parqueadero · terraza |
| 2 | Valentina Rueda | $2,500,000 | Chapinero | No | gym · parqueadero |
| 3 | Santiago Torres | $3,500,000 | Usaquén | No | gym · piscina · terraza |
| 4 | Laura Méndez | $2,800,000 | Usaquén | Sí | gym · ascensor · coworking |
| 5 | Sebastián Gómez | $2,000,000 | Suba | No | parqueadero · seguridad |
| 6 | María Fernanda López | $1,800,000 | Suba | Sí | ascensor · seguridad |
| 7 | Daniela Castro | $2,200,000 | Teusaquillo | No | coworking · ascensor · terraza |
| 8 | Andrés Morales | $1,500,000 | Kennedy | No | seguridad |
| 9 | Camilo Jiménez | $1,650,000 | Engativá | Sí | parqueadero · seguridad |
| 10 | Natalia Vargas | $1,300,000 | Centro | No | ascensor · seguridad |

**Resultados del matching húngaro:**
- 10/10 usuarios asignados
- Peso promedio: **0.897**
- Cobertura: **100%**

**Comparación con matching de cardinalidad máxima:**
- 10/10 usuarios asignados (misma cobertura)
- Peso promedio: **0.695**
- **Diferencia: +0.202 promedio a favor del húngaro (+29% de calidad)**

---

## 12. Bugs corregidos por sesión

### Sesión 7 (2026-05-17)

**Bug: NLP — barrios con ñ no detectados (ej. "Rafael Núñez")**
- Síntoma: `"¿hay apartamentos en Rafael Núñez?"` → `barrio=None`
- Causa: BD almacena `"Rafael Nunez"` (sin tilde), usuario escribe `"Rafael Núñez"`. `"rafael nunez" in "rafael nuñez"` → `False`
- Fix: función `_sin_tildes()` con `unicodedata.NFD` para normalizar ambos lados antes de comparar

**Bug: Universo 3D — nodos no visibles**
- Síntoma: fondo oscuro visible pero nodos y aristas no aparecen
- Causa probable: `ForceGraph3D()` inicializa antes de que el DOM esté listo, lee dimensiones 0
- Fix aplicado: mover toda la inicialización a `window.addEventListener('load', ...)`
- Estado: parcialmente corregido, pendiente verificación completa

### Sesión 6 (2026-05-15/16)

**Bug: Chat — parámetros olvidados entre mensajes**
- Síntoma: usuario dice "$4 millones" en mensaje 1, luego "¿hay algo en Rafael Núñez?" → sistema usa default $2M → sin resultados
- Fix: `_do_search()` hereda parámetros del último mensaje del asistente

**Bug: Mapa — TOP 3 con apartamento sin coordenadas no avisaba**
- Fix: label del expander dice `"Mapa de ubicaciones — N de M TOP en el mapa"` + `st.caption()` explicativo

**Mejora: `set_page_config` agregado**
- `st.set_page_config(page_title="Aptmatch Bogotá", page_icon="🏠", layout="wide")` como primera llamada Streamlit

### Sesión 5 (2026-05-15)

**Bug: NLP — "perrita" no detectada como mascota**
- Causa: `"perro" in "perrita"` → `False` (son substrings distintos)
- Fix: lista `_pets_positivos` con todas las formas (incluye diminutivos)

**Bug: NLP — barrios no reconocidos**
- Fix 1: `_ZONA_KEYWORDS` ampliado con barrios representativos
- Fix 2: `_barrios_en_bd()` para detección dinámica desde la BD

**Bug: UX — segundo botón "Confirmar y buscar" bloqueaba resultados**
- Fix: eliminar formulario de clarificación intermedio → defaults automáticos + resultados inmediatos

### Sesión 4 (2026-05-13)

**Bug: NLP — negación de mascotas no detectada**
- Síntoma: `"No tengo mascotas"` → `pets=True`
- Fix: regex de negación evaluada antes del check positivo

**Bug: Zona ignorada en el matching**
- Síntoma: búsqueda en "Usaquén" mostraba apartamentos de "Engativá"
- Fix: post-filtro por zona + fallback a todas las zonas + `st.warning()` explicativo

**Bug: NaN en precio/distancia pasaban el filtro**
- Fix: `if pd.isna(price) or pd.isna(distancia): return 0`

**Bug: Amenity hard cut dejaba sin resultados**
- Fix: eliminado `if amenity_match < 0.50: return 0`. Amenities pasaron a ser restricción blanda.

---

## 13. Dependencias e instrucciones de ejecución

### Instalación

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar (PowerShell)
.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install streamlit pandas scipy matplotlib folium streamlit-folium
```

### Dependencias por función

| Paquete | Versión mínima | Uso |
|---|---|---|
| `streamlit` | ≥1.30 | Framework de UI, chat, componentes |
| `pandas` | ≥1.5 | DataFrames para la BD, matrices de pesos |
| `scipy` | ≥1.10 | `linear_sum_assignment` (Algoritmo Húngaro) |
| `folium` | ≥0.14 | Mapa interactivo |
| `streamlit-folium` | ≥0.15 | `st_folium()` para renderizar folium en Streamlit |
| `3d-force-graph` | @1 (CDN) | Universo 3D — Three.js, cargado desde `unpkg.com` |
| `GSAP` | 3.12.5 (CDN) | Animaciones del grafo 2D — `cdnjs.cloudflare.com` |
| `sqlite3` | stdlib | Base de datos local |
| `re`, `unicodedata` | stdlib | NLP, normalización de texto |

### Ejecución

```powershell
# 1. Activar entorno virtual
.venv\Scripts\Activate.ps1

# 2. (Primera vez o al cambiar datos) Cargar 210 apartamentos reales
python cargar_datos_reales.py

# 3. Lanzar la aplicación
.venv\Scripts\streamlit run app_local.py
# → Disponible en http://localhost:8501
```

### Notas de despliegue

- `cargar_datos_reales.py` **borra y recrea** `database.db` cada vez que se ejecuta para evitar conflictos de esquema entre versiones.
- Los usuarios registrados se pierden al volver a correr `cargar_datos_reales.py`. Los 10 usuarios de prueba deben re-insertarse manualmente.
- El Universo 3D requiere conexión a internet para cargar la librería `3d-force-graph` desde `unpkg.com` y GSAP desde `cdnjs.cloudflare.com`.
- El mapa folium usa tiles CartoDB Positron (OpenStreetMap) — también requiere internet.
- La app funciona completamente offline si solo se usa la búsqueda NLP, el matching y la visualización 2D del grafo (las librerías JS del grafo 2D se cargan desde CDN, pero el grafo 2D renderiza con SVG inline y solo requiere GSAP que también viene de CDN).

---

*Documento generado automáticamente desde el código fuente. Versión del proyecto: Sesión 7 (2026-05-17).*
