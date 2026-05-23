# Matching de Apartamentos — Documentación del Proyecto

Proyecto académico de **Teoría de Grafos** (4to semestre, Universidad del Rosario).
Sistema de asignación óptima de apartamentos modelado como un grafo bipartito ponderado
con algoritmo húngaro.

**Autores:** Jhon Rivera, Laura Sierra, Alejandro Arroyave, Juan José Garzón

---

## Cómo correr el proyecto

```powershell
# 1. Activar el entorno virtual (PowerShell)
.venv\Scripts\Activate.ps1

# 2. (Primera vez o al cambiar datos) Cargar apartamentos reales
python cargar_datos_reales.py

# 3. Lanzar la app local (SQLite, sin Supabase)
.venv\Scripts\streamlit run app_local.py

# 4. Lanzar la app cloud (requiere secrets de Supabase)
.venv\Scripts\streamlit run app.py
```

App disponible en: http://localhost:8501

---

## Estructura de archivos

```
matching-apartamentos-grafos/
├── app.py                   # App Streamlit con Supabase (cloud) — UI básica
├── app_local.py             # App Streamlit con SQLite (local) — versión principal
├── database.py              # Capa de datos SQLite
├── cargar_datos_reales.py   # Script para cargar datos reales desde GitHub
├── database.db              # Base de datos SQLite (generada automáticamente)
├── docs/
│   └── proyecto_teoria_grafos.md   # Documentación académica del proyecto
├── design-system/
│   └── matching-apartamentos/
│       └── MASTER.md        # Design system (Cinzel/Josefin Sans · Teal · Navy)
├── pruebas/
│   ├── main.py              # Prueba modular (database.py + matching.py)
│   ├── p1.py                # Prototipo standalone con SQLite
│   └── test_matching.py     # Test completo con datos de prueba
└── .venv/                   # Entorno virtual Python
```

---

## Modelo matemático

El sistema modela el problema como un **grafo bipartito ponderado**:

```
G = (U ∪ O, E, w)
```

- **U** = conjunto de buscadores (usuarios)
- **O** = conjunto de apartamentos
- **E** = aristas de compatibilidad (solo existen si se cumplen restricciones duras)
- **w: E → [0,1]** = función de peso/compatibilidad

**Objetivo:** encontrar el matching M ⊆ E que maximice Σ w(u,o) para (u,o) ∈ M,
sujeto a que cada nodo participe en máximo una arista.

---

## Restricciones duras (hard constraints)

Una arista (u, o) ∈ E existe únicamente si se cumplen **todas**:

1. `apt.price ≤ usuario.budget`
2. `apt.distancia ≤ usuario.radio`
3. Si `usuario.pets = True` → `apt.pet_friendly = True`

Si alguna falla, `w(u,o) = 0` y la arista no existe en el grafo.

> **Nota (sesión 4):** `amenity_match ≥ 0.50` fue degradada de restricción dura a restricción
> blanda. Con datasets pequeños (210 apts) y un solo amenity requerido, el hard cut eliminaba
> todos los apartamentos de la zona si ninguno tenía exactamente ese amenity. Ahora los amenities
> solo influyen en el score (`secondary_score`), garantizando que siempre haya resultados.

---

## Función de peso

```
w(u, o) = 0.40 · price_score + 0.30 · location_score + 0.30 · secondary_score
```

Donde:
```
price_score    = 1 - |apt.price - budget| / budget × 0.5
location_score = 1 - apt.distancia / radio
secondary_score = 0.35·amenity_score + 0.35·size_score + 0.20·bedroom_score + 0.10·pet_score
```

### Pesos individuales de amenities (PRD §4)

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

El `amenity_score` es ponderado:
```python
peso_total = sum(AMENITY_WEIGHTS[a] for a in requeridos)
peso_match = sum(AMENITY_WEIGHTS[a] for a in requeridos & disponibles)
amenity_match = peso_match / peso_total
```

---

## Algoritmo húngaro

Se usa `scipy.optimize.linear_sum_assignment` (implementación del algoritmo húngaro).

Como el algoritmo minimiza, se convierte la matriz de maximización:
- Si `w(u,o) = 0` → costo = `9999` (arista inválida, no asignar)
- Si `w(u,o) > 0` → costo = `1 - w(u,o)`

```python
filas, columnas = linear_sum_assignment(C)
```

---

## Base de datos

Tres tablas SQLite:

```sql
usuarios     (id, nombre, budget, zona, radio, pets, amenities_req, size_deseado, bedrooms_deseado)
apartamentos (id, nombre, price, zona, barrio, distancia, pet_friendly, amenities, size, bedrooms,
              latitud, longitud, url, descripcion, imagen)
asignaciones (id, usuario_id, apartamento_id, peso)
```

- `amenities` y `amenities_req` se almacenan como strings CSV (ej: `"gym,ascensor,parqueadero"`)
- `imagen` almacena URLs de fotos separadas por coma (hasta 6 fotos por apartamento)
- `url` es el link al listing original en MetroCuadrado
- `distancia` = distancia en km a la estación de TransMilenio más cercana (proxy de centralidad)
- `barrio` = nombre del barrio/sector (ej: `"S.C. Chico Norte"`, `"URB. Niza"`)
- `latitud` / `longitud` = coordenadas GPS reales del inmueble (WGS84)

---

## Datos reales (`cargar_datos_reales.py`)

**Fuente:** [github.com/builker-col/bogota-apartments](https://github.com/builker-col/bogota-apartments)
- Scraping de **Metrocuadrado** y **Habi**
- Versión usada: v2.0.0-august-2024

**Dataset procesado:** 43,013 registros (campos tipados, localidades, coordenadas, barrios)
**Dataset raw:** 44,436 registros (incluye campo `imagenes` con URLs de fotos CDN)

El script combina ambos datasets:
1. Usa el procesado para todos los campos del apartamento (precio, área, barrio, coords, amenities)
2. Usa el raw para extraer hasta 6 URLs de fotos por apartamento
3. Filtra solo `tipo_operacion = 'ARRIENDO'`
4. Rango de precios: $600,000 – $4,000,000 COP/mes
5. Selecciona **30 apartamentos por zona** (210 total) con muestreo diversificado
6. 7 zonas: Chapinero, Usaquén, Suba, Engativá, Kennedy, Teusaquillo, Centro

**Estrategia de muestreo (sesión 4):** garantiza diversidad de pet_friendly por zona.
- Hasta 25% de la cuota (≥3) se reserva para apartamentos `pet_friendly=True`
- El resto se distribuye uniformemente por precio
- Resultado: 7 pet_friendly garantizados por zona (49 en total)

**Nota importante:** El campo `permite_mascotas` en el dataset es 0 para todos los registros
(bug del scraper). Se detecta `pet_friendly` desde la descripción del listing usando keywords:
`"mascota", "mascotas", "pet friendly", "admite perro", "acepta mascota"`, etc.

**Campos geográficos disponibles en el dataset fuente:**
- `barrio` — nombre del barrio/UPZ
- `latitud`, `longitud` — coordenadas GPS del inmueble
- `estacion_tm_cercana` — nombre de la estación TM más cercana
- `distancia_estacion_tm_m` — distancia en metros (dividida entre 1000 → km en la BD)

---

## Features implementadas

### Feature 9 — Mapa interactivo de ubicaciones *(sesión 5)*

Mapa `folium` que aparece automáticamente debajo de las tarjetas TOP 3 cuando hay resultados.
- Tecnología: `folium` + `streamlit-folium` (OpenStreetMap/CartoDB, sin API key)
- Marcadores diferenciados: dorado `★ #1`, gris `★ #2`, beige `★ #3`, azul para compatibles
- Popup al hacer clic en cada marcador: nombre, barrio, precio, tamaño, habitaciones, match%, link
- Centrado automático en el centroide de los resultados mostrados

```python
mapa = crear_mapa_folium(todos, top3)  # devuelve folium.Map
st_folium(mapa, width="100%", height=440)
```

### Feature 8 — Comparación de estrategias de matching *(sesión 2)*

Sección "Ejecutar matching" con dos tabs y tabla comparativa:
- **Tab 1 — Peso máximo (Húngaro):** usa `linear_sum_assignment` con costo `1 - w`. Maximiza compatibilidad total.
- **Tab 2 — Matching máximo (Cardinalidad):** usa matriz binaria (0 si compatible, 9999 si no). Maximiza número de asignaciones sin considerar calidad.
- **Tabla comparativa:** muestra asignaciones, peso total, peso promedio y cobertura lado a lado.
- **Insight dinámico:** mensaje adaptado según cuál estrategia asignó más usuarios.

Función nueva: `ejecutar_matching_maximo()` en ambas versiones (`app.py` y `app_local.py`).

---

### Feature 1 — NLP Input
El usuario describe en texto libre lo que busca. El sistema parsea la descripción
con regex en español (sin ML).

Ejemplo de query:
> "Busco apartamento en chico reservado, máximo 3 millones, con gym y parqueadero. Tengo una perrita."

### Feature 2 — Entity Extraction *(actualizada sesión 5)*
Extracción automática de entidades con `extraer_entidades()`:

| Campo | Detecta |
|-------|---------|
| budget | "2 millones", "1.800.000", "$2,000,000" |
| zona | Chapinero, Suba, Usaquén, Teusaquillo, Centro, Kennedy, Engativá + barrios por zona |
| barrio | Cualquier barrio registrado en la BD — 140 barrios detectables dinámicamente |
| radio | "5 km", "3 kilómetros" |
| pets | "gato/a", "perro/a", "perrita/o", "mascota", "cachorro", "canino", "pet", "animal" |
| amenities | gym, parqueadero, ascensor, piscina, terraza, coworking, seguridad, BBQ |
| bedrooms | "2 habitaciones", "3 cuartos", "1 alcoba" |
| size | "60 metros", "80 m2" |
| tipo | "arriendo"/"alquiler" → arriendo; "compra"/"venta" → compra |

**Jerarquía de filtros de ubicación:** barrio > zona > sin filtro  
**Defaults automáticos si no se detectan:** `radio=5km`, `bedrooms=2`, `size=85m²`, `budget=2M`, `tipo=arriendo`

**Detección de barrios:** dinámica, no hardcodeada. `_barrios_en_bd()` consulta la BD
y verifica coincidencia de subcadena en el texto (los más largos primero para evitar falsos positivos).

**Keywords de zona incluyen barrios conocidos:**
```python
"Chapinero": ["chapinero", "chico reservado", "chico norte", "rosales", "cabrera", ...]
"Usaquén":   ["usaquén", "santa bárbara", "cedritos", "country club", ...]
"Suba":      ["suba", "niza", "alhambra", "prado veraniego", ...]
# etc.
```

Inferencia de tipo por presupuesto si no se especifica:
- ≤ 5M → arriendo
- ≥ 100M → compra

### Feature 3 — Amenities ponderados
Cada amenity tiene un peso individual en el cálculo de compatibilidad (no todos valen igual).
Ver tabla de pesos en la sección de función de peso.

### Feature 4 — Manejo de ambigüedad *(actualizada sesión 5)*
Si el NLP no detecta presupuesto o tipo, se aplican **defaults automáticos** en lugar de
bloquear con un formulario intermedio:
- `budget` no detectado → default `$2,000,000` + aviso `st.info()` explicando el default
- `tipo` no detectado → default `"arriendo"` (todos los datos son arriendo)
- Los resultados se muestran **inmediatamente** con un solo clic, sin segundo botón de confirmación

> **Sesión anterior (sesión 4):** se pedía budget interactivamente con `st.number_input` + botón
> "Confirmar y buscar". Esto causaba que muchos usuarios no vieran resultados porque no
> notaban el segundo botón. Eliminado en sesión 5.

### Feature 5 — TOP 3 resultados *(actualizada sesión 5)*
Los 3 apartamentos con mayor peso de compatibilidad. Cada tarjeta muestra:
- Rank badge (1/2/3) con borde lateral de color (dorado/plata/bronce)
- Nombre en Cinzel + zona (pill teal) + **barrio real** (pill gris con 📍)
- Precio prominente en Cinzel + fila de stats: tamaño, habitaciones, distancia TM, pet badge
- Amenities disponibles como pills
- Badge de match circular con `conic-gradient` (verde ≥80%, teal ≥60%, ámbar <60%)
- Foto principal + galería expandible
- Descripción del listing expandible
- Link "Ver en Metrocuadrado"

### Feature 6 — Visualización del grafo bipartito *(actualizada sesión 5)*
Expander bajo el mapa. Dibuja con matplotlib con **fondo oscuro** (`#0F172A`):
- Nodo teal **U** (el buscador) con su presupuesto
- Nodos **O** (apartamentos): dorado/gris/marrón para TOP 3, azul oscuro para compatibles
- Aristas teal para TOP 3 con etiqueta `w=0.85` sobre fondo oscuro
- Aristas gris oscuro para compatibles no seleccionados
- Título `G = (U ∪ O, E, w) — Grafo Bipartito Ponderado`
- Leyenda con fondo oscuro integrado

### Feature 7 — Datos reales + fotos + coordenadas *(actualizada sesión 5)*
- 210 apartamentos reales de Bogotá (Metrocuadrado/Habi), 30 por zona
- Fotos reales del CDN de MetroCuadrado (hasta 6 por apartamento)
- **Barrio real** de cada inmueble (140 barrios únicos)
- **Coordenadas GPS** para todos los apartamentos → habilita el mapa interactivo

---

## Menú de la app

| Opción | Descripción |
|--------|-------------|
| Buscar apartamento | NLP → TOP 3 + mapa interactivo + grafo bipartito |
| Registrar usuario | Formulario 2 columnas para agregar usuario a la BD |
| Registrar apartamento | Formulario 2 columnas para agregar apartamento a la BD |
| Ver base de datos | Stats bar de conteos + tablas de las 3 entidades |
| Ejecutar matching | Húngaro vs Matching máximo + tabla comparativa + insight |

---

## Dependencias

```
streamlit
pandas
scipy
matplotlib
folium
streamlit-folium
supabase          # solo para app.py (cloud)
```

Instalación:
```bash
pip install streamlit pandas scipy matplotlib folium streamlit-folium
```

---

## UI / Design System *(rediseño completo sesión 5)*

| Token | Valor |
|-------|-------|
| Estilo | Clean · High Contrast · PropTech |
| Fondo app | `#F1F5F9` (slate claro) |
| Sidebar | `#0B1120 → #0F172A` (gradiente navy) |
| Cards | `white` + `border-radius:18px` + `box-shadow` real |
| Texto principal | `#0F172A` (negro, máximo contraste) |
| Texto secundario | `#475569` / `#64748B` |
| Color primario | `#0F766E` (teal sólido) |
| Rank #1 | `#D97706` (dorado) |
| Rank #2 | `#475569` (slate) |
| Rank #3 | `#B45309` (bronce) |
| Fuente títulos | Cinzel (serif elegante, Google Fonts) |
| Fuente cuerpo | Josefin Sans (Google Fonts) |
| Fonts cargadas | `@import url(...)` dentro de `<style>` — NO usar `<link>` antes de `<style>` |
| Animación | `fadeSlideUp 280ms ease-out` en tarjetas |
| Mapa tiles | CartoDB Positron (claro, neutro) |

**Componentes clave en `app_local.py`:**
- Header: stats en vivo (# apts / zonas / usuarios), badge `SQLite · Local`
- Sidebar: gradiente navy, brand area + chip teal del algoritmo + footer académico
- Cards TOP 3: borde lateral de color según ranking, precio en Cinzel `1.25rem`, stats en fila con bg `#F8FAFC`
- Badge de match: `conic-gradient` circular (verde ≥80%, teal ≥60%, ámbar <60%)
- Barrio: pill `#F1F5F9` con 📍 debajo del nombre del apartamento
- Mapa: `folium` con tiles CartoDB Positron, marcadores FA icons
- Formularios: layout 2 columnas (info básica | preferencias), validación inline
- DB view: stats bar 3 contadores Cinzel + labels con badges de conteo
- Grafo: fondo `#0F172A`, aristas teal para TOP 3

### Bugs de CSS Streamlit — soluciones conocidas

| Bug | Causa | Fix |
|-----|-------|-----|
| CSS visible como texto en la UI | `<link href="...">` antes de `<style>` | Usar `@import url(...)` dentro del `<style>` |
| Texto blanco sobre cards blancas | Streamlit dark-theme aplica `color:white` a `<p>` | CSS override en `stMarkdownContainer p/strong/em` con `!important` |
| Azul de Streamlit en selectbox/radio/tags | Color por defecto de BaseUI | Override en `li[role="option"]`, `span[data-baseweb="tag"]`, etc. |
| Texto sidebar invisible tras fondo oscuro | `color` no heredado por todos los elementos | `section[data-testid="stSidebar"] * { color:#E2E8F0 !important }` |

---

## Dos versiones del sistema

| | `app.py` | `app_local.py` |
|---|---|---|
| Base de datos | Supabase (PostgreSQL cloud) | SQLite local |
| Requiere secrets | Sí (SUPABASE_URL + SUPABASE_KEY) | No |
| Uso | Producción / demo cloud | Desarrollo / demo local |
| Datos | Cargados desde Supabase | Cargados con `cargar_datos_reales.py` |
| NLP (mascotas) | Bug: no detecta "perrita", negación falla | Corregido sesión 5 |
| NLP (barrios) | No tiene | Corregido sesión 5 |
| Filtro por barrio | No tiene | Sesión 5 |
| Mapa interactivo | No tiene | Sesión 5 |
| Barrio en tarjetas | No tiene | Sesión 5 |
| Clarificación budget | Interactiva (formulario) | Default automático (sesión 5) |
| UI rediseñada | No (UI básica) | Sí — Clean · High Contrast (sesión 5) |
| Feature 8 (comparación) | Sí | Sí |

---

## Notas técnicas

- **`distancia` en el dataset real** = distancia en metros a la estación de TransMilenio
  más cercana, dividida entre 1000 para convertir a km. Es un proxy de centralidad/accesibilidad
  urbana en Bogotá, no distancia geográfica a la zona preferida del usuario.

- **`zona` y `barrio` como filtros de presentación:** ninguno afecta el score `w(u,o)`.
  Son filtros de post-procesamiento en `buscar_compatibles()`. La jerarquía es:
  barrio (más específico) → zona (localidad) → sin filtro geográfico.

- **Detección dinámica de barrios:** `_barrios_en_bd()` consulta la BD en cada búsqueda.
  Matching por subcadena (más largo primero). No requiere mantenimiento al agregar datos.

- **`pet_friendly` en datos reales** se infiere de la descripción del listing porque
  el campo `permite_mascotas` del scraper es 0 para todos los registros.

- **El algoritmo húngaro** en "Ejecutar matching" opera sobre usuarios registrados en la BD
  vs todos los apartamentos. La búsqueda NLP (TOP 3) es independiente y no guarda el usuario.

- **`cargar_datos_reales.py`** borra y recrea `database.db` cada vez que se corre
  para evitar conflictos de esquema entre versiones.

- **Mapa folium:** solo renderiza apartamentos con `latitud IS NOT NULL`. Con datos reales,
  todos los 210 tienen coordenadas. Con datos de fallback (35 sintéticos), no aparece el mapa.

---

## Bugs corregidos (sesión 5 — 2026-05-15)

### Bug 1 — NLP: "perrita" y diminutivos no detectados como mascota
**Síntoma:** "Tengo una perrita" → `pets=False`. La regex `"perro" in texto` es `False`
para "perrita" porque son substrings distintos (`perr-o` ≠ `perr-ita`). Como resultado,
el filtro `pet_friendly` no se activaba y el usuario recibía apartamentos que no aceptan mascotas.

**Fix en `extraer_entidades()`:**
```python
_pets_positivos = [
    "gato", "gata", "gatos", "gatas",
    "perro", "perra", "perros", "perras", "perrita", "perrito",
    "mascota", "mascotas", "pet", "pets",
    "animal", "animales", "cachorro", "cachorros", "canino",
]
entidades["pets"] = any(p in t for p in _pets_positivos)
```

### Bug 2 — NLP: barrios y sectores de Bogotá no reconocidos
**Síntoma:** "Busco en chico reservado" → `zona=None`, `barrio=None`. El NLP solo reconocía
los nombres oficiales de localidades. Barrios como Chico, Rosales, Niza, Cedritos quedaban
sin mapear, produciendo búsquedas sin filtro geográfico.

**Fix 1 — `_ZONA_KEYWORDS` ampliado** con barrios representativos por localidad:
```python
"Chapinero": ["chapinero", "chico reservado", "chico norte", "rosales", "cabrera", ...],
"Usaquén":   ["usaquén", "santa bárbara", "cedritos", "country club", ...],
```

**Fix 2 — `_barrios_en_bd()`** detecta barrios dinámicamente desde la BD.
En `extraer_entidades()`, tras detectar zona, se hace un segundo pass buscando el barrio exacto.

### Bug 3 — UX: segundo botón "Confirmar y buscar" bloqueaba resultados
**Síntoma:** Sin presupuesto en el texto, aparecía un formulario con un segundo botón.
Si el usuario no lo clickeaba (lo cual era frecuente por no ser visible), `mostrar_resultados`
nunca se ponía en `True` y la sección de resultados nunca se renderizaba.

**Fix:** Eliminar el formulario de clarificación intermedio. Si `budget=None` → default `$2,000,000`
con `st.info()` explicativo. Si `tipo=None` → default `"arriendo"`. Los resultados
aparecen inmediatamente con un solo clic en "Analizar y buscar".

---

## Bugs corregidos (sesión 4 — 2026-05-13)

### Bug 1 — NLP: negación de mascotas no detectada
**Síntoma:** "No tengo mascotas" → `pets=True`. La regex solo buscaba la palabra "mascota"
sin considerar el contexto negativo.

**Fix:** Regex de negación antes del check positivo:
```python
negacion_pets = bool(re.search(
    r'\b(no\s+tengo|no\s+hay|sin|no\s+tiene|tampoco)\b.{0,25}'
    r'\b(gato|gatos|perro|perros|mascota|mascotas|pet|pets|animal|animales)\b', t
))
```

### Bug 2 — Zona ignorada en el matching
**Síntoma:** Búsqueda en "Usaquén" mostraba apartamentos de "Engativá". La zona se
extraía del NLP pero nunca se usaba en `buscar_compatibles()`.

**Fix:** Post-filtro por zona + fallback a todas las zonas + `st.warning()` explicativo.

### Bug 3 — NaN en precio/distancia pasaban el filtro
**Fix:**
```python
if pd.isna(price) or pd.isna(distancia):
    return 0
```

### Bug 4 — Amenity hard cut dejaba sin resultados
**Fix:** Eliminado `if amenity_match < 0.50: return 0`. Los amenities son restricción blanda.

### Mejora — Dataset ampliado de 70 a 210 apartamentos
- `APTS_POR_ZONA`: 10 → 30 · `PRECIO_MAX`: $3.5M → $4M
- Muestreo diversificado: garantiza ≥7 pet_friendly por zona (49 en total)

---

## Sesión 6 — 2026-05-15 / 2026-05-16

### Rediseño completo de UI: interfaz conversacional tipo chat

El menú de búsqueda fue reemplazado por una **interfaz de chat conversacional** usando los componentes nativos de Streamlit (`st.chat_message`, `st.chat_input`).

**Hero section** (cuando no hay mensajes):
- Título grande en Cinzel: *"Encuentra el apartamento perfecto en Bogotá"*
- Sin notación matemática en el header
- 3 chips de ejemplo clicables que lanzan búsquedas predefinidas
- `st.chat_input` fijo en el fondo

**Chat conversacional:**
- Cada búsqueda añade un par (mensaje usuario + respuesta asistente) al historial en `session_state["chat_msgs"]`
- La respuesta muestra: pills de preferencias detectadas → tarjetas TOP 3 en columnas → mapa folium (expandido por defecto) → grafo bipartito
- El historial acumula múltiples rondas (conversación completa)
- Botón "Nueva búsqueda" en el sidebar limpia el historial

**Sidebar rediseñado (blanco limpio):**
- Fondo `#FFFFFF` + borde `1px solid #E2E8F0` (reemplaza el gradiente navy oscuro)
- Radio buttons estilizados como nav pills (teal en ítem activo vía CSS `:has(input:checked)`)
- Sin chip técnico de "Algoritmo Húngaro · scipy.optimize"
- Quitado **"Registrar apartamento"** del menú (datos vienen del dataset real)

**Menú actual:**
1. Buscar apartamento *(chat)*
2. Registrar usuario
3. Ejecutar matching
4. Universo 3D *(nuevo)*
5. Ver base de datos

### Feature 10 — Universo 3D del grafo *(sesión 6)*

Nueva sección "Universo 3D" que renderiza el grafo bipartito completo en tres dimensiones dentro de Streamlit vía `st.components.v1.html()`.

**Tecnología:** librería `3d-force-graph` (Three.js) cargada desde CDN `unpkg.com`. Sin dependencias Python adicionales.

**Visual:**
- Fondo espacio oscuro `#050A14`
- Nodos usuario: esferas teal `#0D9488` (tamaño 9)
- Nodos apartamento asignado por húngaro: dorado `#D97706` (tamaño 7)
- Nodos apartamento compatible: azul `#3B82F6` (tamaño 3.5)
- Aristas matching: teal `#5EEAD4`, ancho 4, **5 partículas animadas** fluyendo
- Aristas compatibles: gris `#1E3A5F`, ancho 0.7, opacidad 22%

**Interacciones:**
- Hover → panel flotante con detalle del nodo (precio, zona, barrio, amenities, compatibilidad)
- Clic → zoom animado hacia el nodo (1200ms)
- Drag → rotación 3D libre
- Scroll → zoom
- Rotación automática suave al cargar (se detiene al primer mousedown)

**Datos mostrados:**
- Todos los usuarios registrados en BD
- Top 6 apartamentos compatibles por usuario (para densidad visual manejable)
- Aristas del último matching húngaro ejecutado (desde tabla `asignaciones`)
- Tabla de asignaciones debajo del grafo

```python
# Lógica: calcular_peso() para cada par usuario-apartamento, tomar top-6, destacar matched
_conn.execute("SELECT usuario_id, apartamento_id, peso FROM asignaciones")
```

### Usuarios de prueba creados *(sesión 6)*

10 usuarios insertados en `database.db` cubriendo todos los perfiles relevantes del proyecto:

| Nombre | Presupuesto | Zona | Pets | Amenities |
|--------|-------------|------|------|-----------|
| Felipe Herrera | $3.800.000 | Chapinero | No | gym · piscina · parqueadero · terraza |
| Valentina Rueda | $2.500.000 | Chapinero | No | gym · parqueadero |
| Santiago Torres | $3.500.000 | Usaquén | No | gym · piscina · terraza |
| Laura Méndez | $2.800.000 | Usaquén | Sí | gym · ascensor · coworking |
| Sebastián Gómez | $2.000.000 | Suba | No | parqueadero · seguridad |
| María Fernanda López | $1.800.000 | Suba | Sí | ascensor · seguridad |
| Daniela Castro | $2.200.000 | Teusaquillo | No | coworking · ascensor · terraza |
| Andrés Morales | $1.500.000 | Kennedy | No | seguridad |
| Camilo Jiménez | $1.650.000 | Engativá | Sí | parqueadero · seguridad |
| Natalia Vargas | $1.300.000 | Centro | No | ascensor · seguridad |

**Resultado del matching con estos 10 usuarios:**
- Húngaro: 10/10 asignados, peso promedio **0.897**
- Cardinalidad máxima: 10/10 asignados, peso promedio **0.695**
- Diferencia de calidad: +0.202 promedio a favor del húngaro (29% mejor)

---

## Bugs corregidos (sesión 6 — 2026-05-15/16)

### Bug 1 — NLP: barrios con ñ no detectados (ej. Rafael Núñez)

**Síntoma:** "¿hay apartamentos en Rafael Núñez?" → `barrio=None`. El barrio en la BD se llama `"Rafael Nunez"` (sin ñ, sin acento), pero el usuario escribe `"rafael nuñez"`. El check `"rafael nunez" in "rafael nuñez"` devuelve `False` porque `ñ ≠ n`.

**Fix:** función `_sin_tildes()` que normaliza vía `unicodedata.NFD` + strip de categoría `Mn` antes de comparar:

```python
import unicodedata

def _sin_tildes(texto: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    ).replace('ñ', 'n')

# En extraer_entidades():
t_norm = _sin_tildes(t)
for barrio in _barrios_en_bd():
    if _sin_tildes(barrio) in t_norm:
        entidades["barrio"] = barrio
        break
```

### Bug 2 — Chat: parámetros olvidados entre mensajes

**Síntoma:** En la búsqueda anterior el usuario mencionó "$4 millones". Al preguntar "¿hay algo en Rafael Núñez?" el sistema usaba el default $2M → el único apartamento ($3M) no pasaba el filtro de precio → "sin resultados".

**Fix:** `_do_search()` hereda parámetros del último mensaje del asistente si el nuevo no los menciona:
- Presupuesto, amenities, radio, mascotas, zona (en este orden de prioridad)
- Los campos heredados se muestran con nota `"(recordé del mensaje anterior: ...)"` en la respuesta

```python
prev_results = [m for m in st.session_state["chat_msgs"]
                if m.get("role") == "assistant" and m.get("type") == "results"]
if prev_results:
    prev = prev_results[-1]["entidades"]
    if not ent["budget"]:
        ent["budget"] = prev.get("budget", 2_000_000)
    # idem para amenities, radio, pets, zona
```

### Bug 3 — Mapa: TOP 3 con apartamento sin coordenadas no avisaba

**Síntoma:** 3 tarjetas mostradas, solo 2 marcadores en el mapa — sin explicación.

**Fix:**
1. El expander del mapa ahora dice `"Mapa de ubicaciones — N de M TOP en el mapa"`
2. Si algún TOP 3 no tiene coordenadas, aparece `st.caption()` con su nombre y la razón
3. El mapa abre `expanded=True` por defecto para que sea visible sin clic extra

### Mejora — set_page_config agregado

`st.set_page_config(page_title="Aptmatch Bogotá", page_icon="🏠", layout="wide")` añadido como primera llamada Streamlit antes de cualquier otro comando.

---

## Sesión 7 — 2026-05-17

### Feature 6 rediseñada — Grafo bipartito 2D: SVG + GSAP (reemplaza matplotlib)

`visualizar_grafo_bipartito()` fue completamente reescrita. Ya **no usa matplotlib**. Retorna `(html_string, height_px)` renderizado con `st.components.v1.html()`.

**Técnica de inyección de datos Python → JS sin conflictos de f-string:**
Usar template string con tokens `__PLACEHOLDER__` + `.replace()` en vez de f-string con `{{}}`. Esto evita escapar todos los `{` y `}` del JS.

```python
TMPL = """...(html con JS)..."""
html = TMPL.replace("__APT_JSON__", apt_json).replace("__H__", str(H))
return html, CH
```

**Animaciones GSAP** (CDN `cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`):
- Nodos entran con `gsap.from(circle, {attr:{r:0}, ease:'back.out(2)'})` escalonado
- Aristas se dibujan con `stroke-dasharray` + `stroke-dashoffset` animado
- Pulso radial infinito en nodo U: `gsap.to(uRing, {attr:{r:52}, opacity:0, repeat:-1})`
- Etiquetas `w=0.87` aparecen después de las aristas con `gsap.to([lbg,ltx], {opacity:1})`
- 4 partículas por arista TOP via `<animateMotion>` + `<mpath href="#pid">`
- Hover: tooltip flotante, GSAP escala el círculo del nodo

**Límites:** MAX_SHOW=15 apartamentos. Height = `min(720, max(480, n*50+100)) + 24`.

### Feature 10 rediseñada — Universo 3D Plan C

**Qué se implementó** (reemplaza la versión básica de sesión 6):

| Feature | Descripción |
|---|---|
| Todos los 210 apts | Nodos dim para sin conexión, brillantes para conectados/matched |
| Colores por zona | 7 colores pastel brillantes (ver tabla abajo) |
| Top-15 aristas/usuario | Antes top-6 |
| Panel de control | 4 sliders + 3 toggles |
| Modo enfoque | Clic en usuario → solo sus conexiones, zoom automático |
| Filtro zona | Leyenda izquierda clicable |
| Búsqueda | Input de texto abajo al centro |
| Fullscreen | Botón + tecla F (`requestFullscreen()`) |
| Explosión | Tecla E / botón → repulsión -900 temporal |
| Reset | Tecla R / botón |

**Colores de zona (sesión 7):**
| Zona | Color |
|---|---|
| Chapinero | `#5EEAD4` |
| Usaquén | `#C4B5FD` |
| Suba | `#93C5FD` |
| Teusaquillo | `#FCD34D` |
| Centro | `#FCA5A5` |
| Kennedy | `#86EFAC` |
| Engativá | `#F9A8D4` |

**CRÍTICO — Variables globales:** El JS NO usa IIFE. Los `onclick` inline de HTML no pueden acceder a variables en scope de IIFE. Todo debe ser global.

**Altura fija:** `940px` en CSS (`html,body`, `#universe`, `#g`) + `.width(gEl.offsetWidth || 900).height(940)` explícito al inicializar `ForceGraph3D`.

---

## Bug activo — Universo 3D: nodos no visibles (2026-05-17)

**Síntoma:** El componente renderiza (fondo oscuro + overlays visibles) pero los nodos y aristas 3D no aparecen.

**Intentos realizados y descartados:**
1. `height:100%` → CSS no hereda alto en iframes Streamlit (queda 0px)
2. `height:100vh` → igual resultado
3. `window.innerWidth/innerHeight` al init → puede ser 0 antes de que el iframe tenga dimensiones
4. Variables en IIFE → controles sin efecto (no accesibles desde `onclick` inline)
5. Fondo `#000000` puro → nodos oscuros invisibles por falta de contraste

**Estado actual tras los fixes:**
- Altura fija `940px` en CSS y `.height(940)` en JS
- Fondo `#05071A` (navy oscuro)
- Opacidad mínima 0.22 (antes 0.08), tamaño mínimo 2.5 (antes 1.2)
- Variables globales (sin IIFE)

**Hipótesis pendiente:** `ForceGraph3D()` puede estar inicializando antes de que el DOM esté completamente listo, leyendo dimensiones 0 del canvas. Fix sugerido para próxima sesión:
```javascript
window.addEventListener('load', function() {
  // mover TODA la inicialización aquí
});
```
También probar: abrir DevTools → Console → buscar errores WebGL o Three.js, verificar que el `<canvas>` tiene dimensiones > 0.
