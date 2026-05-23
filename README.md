# AptMatch Bogotá — Matching de Apartamentos con Teoría de Grafos

Sistema de asignación óptima de apartamentos modelado como un **grafo bipartito ponderado** con algoritmo húngaro. Proyecto académico de Teoría de Grafos, Universidad del Rosario.

**Autores:** Jhon Rivera · Laura Sierra · Alejandro Arroyave · Juan José Garzón

---

## Cómo correr el proyecto

```powershell
# 1. Activar el entorno virtual
.venv\Scripts\Activate.ps1

# 2. Primera vez: cargar los 210 apartamentos reales
python cargar_datos_reales.py

# 3. Lanzar la app (SQLite local, sin dependencias cloud)
.venv\Scripts\streamlit run app_local.py
```

La app queda disponible en **http://localhost:8501**

> `app.py` es la versión cloud (Supabase). Requiere secrets de Supabase y está desactualizada respecto a `app_local.py`.

---

## Estructura de archivos

```
matching-apartamentos-grafos/
├── app_local.py             # App principal — Streamlit + SQLite
├── app.py                   # App cloud — Streamlit + Supabase (desactualizada)
├── database.py              # Capa de datos SQLite
├── cargar_datos_reales.py   # Carga 210 apts reales desde GitHub (Metrocuadrado/Habi)
├── database.db              # BD SQLite (generada por cargar_datos_reales.py)
├── docs/
│   └── proyecto_teoria_grafos.md   # Documentación académica
├── design-system/
│   └── matching-apartamentos/
│       └── MASTER.md        # Design system (Cinzel · Josefin Sans · Teal · Navy)
└── pruebas/
    ├── main.py
    ├── p1.py
    └── test_matching.py
```

---

## Modelo matemático

El problema se modela como un grafo bipartito ponderado:

```
G = (U ∪ O, E, w)
```

- **U** — buscadores (usuarios)
- **O** — apartamentos
- **E** — aristas de compatibilidad (solo existen si se cumplen las restricciones duras)
- **w : E → [0,1]** — función de compatibilidad

**Objetivo:** encontrar el matching M ⊆ E que maximice Σ w(u,o), con cada nodo en máximo una arista.

### Restricciones duras (hard constraints)

Una arista (u, o) existe únicamente si se cumplen **todas**:

1. `apt.price ≤ usuario.budget`
2. `apt.distancia ≤ usuario.radio`
3. Si `usuario.pets = True` → `apt.pet_friendly = True`

### Función de peso

```
w(u, o) = 0.40 · price_score + 0.30 · location_score + 0.30 · secondary_score

price_score    = 1 - |apt.price - budget| / budget × 0.5
location_score = 1 - apt.distancia / radio
secondary_score = 0.35·amenity_score + 0.35·size_score + 0.20·bedroom_score + 0.10·pet_score
```

Los amenities son **restricción blanda** (influyen en el score, no eliminan la arista). Pesos individuales:

| Amenity      | Peso |
|--------------|------|
| parqueadero  | 0.80 |
| ascensor     | 0.70 |
| seguridad    | 0.70 |
| gym          | 0.50 |
| piscina      | 0.50 |
| coworking    | 0.50 |
| terraza      | 0.40 |
| zona BBQ     | 0.40 |

### Algoritmo húngaro

Se usa `scipy.optimize.linear_sum_assignment`. Como minimiza, se convierte:
- `w > 0` → costo = `1 - w`
- `w = 0` → costo = `9999` (arista inválida)

---

## Features implementadas

| # | Feature | Descripción |
|---|---------|-------------|
| 1 | **NLP Input** | El usuario describe en texto libre lo que busca |
| 2 | **Entity Extraction** | Extrae budget, zona, barrio, radio, mascotas, amenities, habitaciones, tamaño |
| 3 | **Amenities ponderados** | Cada amenity tiene peso individual en el score |
| 4 | **Manejo de ambigüedad** | Defaults automáticos si no se detecta budget o tipo |
| 5 | **TOP 3 resultados** | Tarjetas con fotos, badge de match circular, galería, link Metrocuadrado |
| 6 | **Grafo bipartito 2D** | SVG + animaciones GSAP (nodos, aristas, partículas, hover tooltip) |
| 7 | **Datos reales + fotos** | 210 apts de Bogotá con fotos CDN, barrio real y coordenadas GPS |
| 8 | **Comparación de estrategias** | Húngaro vs Cardinalidad máxima con tabla comparativa |
| 9 | **Mapa interactivo** | Folium + CartoDB Positron, marcadores diferenciados por rank |
| 10 | **Universo 3D** | Grafo 3D interactivo con Three.js / 3d-force-graph, filtros por zona, modo enfoque |

### Menú de la app

| Opción | Descripción |
|--------|-------------|
| Buscar apartamento | Chat NLP → TOP 3 + mapa + grafo 2D |
| Registrar usuario | Formulario para agregar usuario a la BD |
| Ejecutar matching | Húngaro vs Cardinalidad + tabla comparativa |
| Universo 3D | Grafo 3D interactivo de todo el dataset |
| Ver base de datos | Stats + tablas de las 3 entidades |

---

## Datos reales

**Fuente:** [github.com/builker-col/bogota-apartments](https://github.com/builker-col/bogota-apartments) — scraping de Metrocuadrado y Habi (v2.0.0-august-2024)

- **210 apartamentos**, 30 por zona, solo arriendo ($600K–$4M COP/mes)
- **7 zonas:** Chapinero · Usaquén · Suba · Engativá · Kennedy · Teusaquillo · Centro
- **140 barrios únicos** con coordenadas GPS reales (WGS84)
- **≥7 pet_friendly** garantizados por zona (49 total) — inferidos de la descripción del listing
- Hasta **6 fotos por apartamento** desde el CDN de Metrocuadrado

---

## Base de datos

Tres tablas SQLite:

```sql
usuarios     (id, nombre, budget, zona, radio, pets, amenities_req, size_deseado, bedrooms_deseado)
apartamentos (id, nombre, price, zona, barrio, distancia, pet_friendly, amenities, size, bedrooms,
              latitud, longitud, url, descripcion, imagen)
asignaciones (id, usuario_id, apartamento_id, peso)
```

- `amenities` y `amenities_req`: strings CSV (`"gym,ascensor,parqueadero"`)
- `imagen`: URLs de fotos separadas por coma (hasta 6)
- `distancia`: km a la estación de TransMilenio más cercana (proxy de centralidad urbana)

---

## Dependencias

```
streamlit
pandas
scipy
matplotlib
folium
streamlit-folium
```

```bash
pip install streamlit pandas scipy matplotlib folium streamlit-folium
```
