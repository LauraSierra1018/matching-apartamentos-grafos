import sqlite3
import pandas as pd
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


def registrar_usuario(nombre, budget, zona, radio, pets, amenities_req, size_deseado, bedrooms_deseado):
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


def registrar_apartamento(nombre, price, zona, distancia, pet_friendly, amenities, size, bedrooms):
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


def cargar_datos():
    conn = conectar()

    usuarios = pd.read_sql_query("SELECT * FROM usuarios", conn)
    apartamentos = pd.read_sql_query("SELECT * FROM apartamentos", conn)

    conn.close()

    return usuarios, apartamentos


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
    pet_score = 1 if usuario["pets"] == apt["pet_friendly"] or usuario["pets"] == 0 else 0

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


def construir_matriz(usuarios, apartamentos):
    matriz = []

    for _, usuario in usuarios.iterrows():
        fila = []

        for _, apt in apartamentos.iterrows():
            peso = calcular_peso(usuario, apt)
            fila.append(peso)

        matriz.append(fila)

    W = pd.DataFrame(
        matriz,
        index=usuarios["id"],
        columns=apartamentos["id"]
    )

    return W


def ejecutar_matching():
    usuarios, apartamentos = cargar_datos()

    W = construir_matriz(usuarios, apartamentos)

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
    peso_total = 0

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

            peso_total += peso

    conn.commit()
    conn.close()

    return W, pd.DataFrame(resultados), peso_total


# -----------------------------
# Ejemplo de uso
# -----------------------------

crear_tablas()

registrar_usuario(
    "Jhon",
    2000000,
    "Chapinero",
    3,
    True,
    ["gym", "parqueadero"],
    50,
    2
)

registrar_usuario(
    "Maria",
    1800000,
    "Suba",
    4,
    False,
    ["ascensor"],
    45,
    1
)

registrar_apartamento(
    "Apt1",
    1800000,
    "Chapinero",
    1.2,
    True,
    ["gym", "parqueadero", "ascensor"],
    52,
    2
)

registrar_apartamento(
    "Apt2",
    1700000,
    "Suba",
    2.0,
    False,
    ["ascensor"],
    42,
    1
)

W, resultado, peso_total = ejecutar_matching()

print("Matriz de pesos generada desde la base de datos:")
print(W)

print("\nAsignaciones óptimas:")
print(resultado)

print("\nPeso total:", round(peso_total, 3))