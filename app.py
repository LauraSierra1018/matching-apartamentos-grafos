import pandas as pd
import streamlit as st
from scipy.optimize import linear_sum_assignment
from supabase import create_client


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