import sqlite3
import pandas as pd
import streamlit as st
from scipy.optimize import linear_sum_assignment

DB_NAME = "database.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        budget REAL,
        zona TEXT,
        radio REAL,
        pets INTEGER,
        amenities_req TEXT,
        size_deseado REAL,
        bedrooms_deseado INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apartamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        price REAL,
        zona TEXT,
        distancia REAL,
        pet_friendly INTEGER,
        amenities TEXT,
        size REAL,
        bedrooms INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asignaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        apartamento_id INTEGER,
        peso REAL
    )
    """)

    conn.commit()
    conn.close()


def insertar_usuario(nombre, budget, zona, radio, pets, amenities_req, size_deseado, bedrooms_deseado):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO usuarios
    (nombre, budget, zona, radio, pets, amenities_req, size_deseado, bedrooms_deseado)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nombre,
        budget,
        zona,
        radio,
        int(pets),
        ",".join(amenities_req),
        size_deseado,
        bedrooms_deseado
    ))

    conn.commit()
    conn.close()


def insertar_apartamento(nombre, price, zona, distancia, pet_friendly, amenities, size, bedrooms):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO apartamentos
    (nombre, price, zona, distancia, pet_friendly, amenities, size, bedrooms)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nombre,
        price,
        zona,
        distancia,
        int(pet_friendly),
        ",".join(amenities),
        size,
        bedrooms
    ))

    conn.commit()
    conn.close()


def cargar_tabla(nombre_tabla):
    conn = conectar()
    df = pd.read_sql_query(f"SELECT * FROM {nombre_tabla}", conn)
    conn.close()
    return df


def texto_a_lista(texto):
    if texto is None or texto == "":
        return []
    return [x.strip() for x in texto.split(",")]


def calcular_peso(usuario, apt):
    if apt["price"] > usuario["budget"]:
        return 0

    if apt["distancia"] > usuario["radio"]:
        return 0

    if usuario["pets"] == 1 and apt["pet_friendly"] == 0:
        return 0

    requeridos = set(texto_a_lista(usuario["amenities_req"]))
    disponibles = set(texto_a_lista(apt["amenities"]))

    if len(requeridos) > 0:
        amenity_match = len(requeridos & disponibles) / len(requeridos)
    else:
        amenity_match = 1

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
        return None

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

    return W


def ejecutar_matching():
    W = construir_matriz()

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

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM asignaciones")

    resultados = []

    for i, j in zip(filas, columnas):
        peso = W.iloc[i, j]

        if peso > 0:
            usuario_id = int(W.index[i])
            apartamento_id = int(W.columns[j])

            cursor.execute("""
            INSERT INTO asignaciones (usuario_id, apartamento_id, peso)
            VALUES (?, ?, ?)
            """, (usuario_id, apartamento_id, float(peso)))

            resultados.append({
                "usuario_id": usuario_id,
                "apartamento_id": apartamento_id,
                "peso": peso
            })

    conn.commit()
    conn.close()

    return W, pd.DataFrame(resultados)


def asignaciones_detalladas():
    conn = conectar()

    query = """
    SELECT 
        u.nombre AS usuario,
        a.nombre AS apartamento,
        asig.peso
    FROM asignaciones asig
    JOIN usuarios u ON asig.usuario_id = u.id
    JOIN apartamentos a ON asig.apartamento_id = a.id
    """

    df = pd.read_sql_query(query, conn)

    conn.close()
    return df


crear_tablas()

st.title("Sistema de Matching de Apartamentos")
st.write("Registro dinámico de usuarios, apartamentos y asignación óptima usando algoritmo húngaro.")

menu = st.sidebar.selectbox(
    "Menú",
    [
        "Registrar usuario",
        "Registrar apartamento",
        "Ver base de datos",
        "Ejecutar matching"
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

if menu == "Registrar usuario":
    st.header("Registrar usuario")

    with st.form("form_usuario"):
        nombre = st.text_input("Nombre")
        budget = st.number_input("Presupuesto máximo", min_value=0, step=100000)
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
            st.success("Usuario guardado correctamente.")

elif menu == "Registrar apartamento":
    st.header("Registrar apartamento")

    with st.form("form_apartamento"):
        nombre = st.text_input("Nombre o código del apartamento")
        price = st.number_input("Precio", min_value=0, step=100000)
        zona = st.selectbox("Zona", zonas)
        distancia = st.number_input("Distancia al usuario/zona en km", min_value=0.0, step=0.5)
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
            st.success("Apartamento guardado correctamente.")

elif menu == "Ver base de datos":
    st.header("Base de datos actual")

    st.subheader("Usuarios")
    st.dataframe(cargar_tabla("usuarios"))

    st.subheader("Apartamentos")
    st.dataframe(cargar_tabla("apartamentos"))

    st.subheader("Asignaciones")
    st.dataframe(asignaciones_detalladas())

elif menu == "Ejecutar matching":
    st.header("Matching óptimo")

    if st.button("Ejecutar algoritmo húngaro"):
        W, resultado = ejecutar_matching()

        if W is None:
            st.warning("Debes registrar al menos un usuario y un apartamento.")
        else:
            st.subheader("Matriz de pesos generada automáticamente")
            st.dataframe(W)

            st.subheader("Asignaciones óptimas")
            detalladas = asignaciones_detalladas()
            st.dataframe(detalladas)

            if not detalladas.empty:
                peso_total = detalladas["peso"].sum()
                peso_promedio = detalladas["peso"].mean()
                cobertura = len(detalladas) / len(cargar_tabla("usuarios")) * 100

                st.metric("Peso total", round(peso_total, 3))
                st.metric("Peso promedio", round(peso_promedio, 3))
                st.metric("Cobertura de usuarios", f"{round(cobertura, 2)}%")
            else:
                st.warning("No hubo asignaciones válidas.") 