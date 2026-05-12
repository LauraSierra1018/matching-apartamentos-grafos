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


def calcular_peso(usuario, apt):
    if apt["price"] > usuario["budget"]:
        return 0

    if apt["distancia"] > usuario["radio"]:
        return 0

    if usuario["pets"] and not apt["pet_friendly"]:
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

cargar_apartamentos_iniciales()
st.title("Sistema de Matching de Apartamentos")
st.write("Base de datos remota en Supabase + algoritmo húngaro.")

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
    st.dataframe(cargar_tabla("asignaciones"))


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
            st.dataframe(resultado)

            if not resultado.empty:
                peso_total = resultado["peso"].sum()
                peso_promedio = resultado["peso"].mean()
                usuarios = cargar_tabla("usuarios")
                cobertura = len(resultado) / len(usuarios) * 100

                st.metric("Peso total", round(peso_total, 3))
                st.metric("Peso promedio", round(peso_promedio, 3))
                st.metric("Cobertura de usuarios", f"{round(cobertura, 2)}%")
            else:
                st.warning("No hubo asignaciones válidas.")