import sqlite3
import pandas as pd
from scipy.optimize import linear_sum_assignment

DB_NAME = "database.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS asignaciones")
    cursor.execute("DROP TABLE IF EXISTS usuarios")
    cursor.execute("DROP TABLE IF EXISTS apartamentos")

    cursor.execute("""
    CREATE TABLE usuarios (
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
    CREATE TABLE apartamentos (
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
    CREATE TABLE asignaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        apartamento_id INTEGER,
        peso REAL
    )
    """)

    conn.commit()
    conn.close()


def insertar_datos_prueba():
    conn = conectar()
    cursor = conn.cursor()

    usuarios = [
        ("Jhon", 2000000, "Chapinero", 3, 1, "gym,parqueadero", 50, 2),
        ("Maria", 1800000, "Suba", 4, 0, "ascensor", 45, 1),
        ("Laura", 2500000, "Chapinero", 5, 1, "gym,ascensor", 60, 2),
    ]

    apartamentos = [
        ("Apt1", 1800000, "Chapinero", 1.2, 1, "gym,parqueadero,ascensor", 52, 2),
        ("Apt2", 1700000, "Suba", 2.0, 0, "ascensor", 42, 1),
        ("Apt3", 2400000, "Chapinero", 2.5, 1, "gym,ascensor", 58, 2),
    ]

    cursor.executemany("""
    INSERT INTO usuarios
    (nombre, budget, zona, radio, pets, amenities_req, size_deseado, bedrooms_deseado)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, usuarios)

    cursor.executemany("""
    INSERT INTO apartamentos
    (nombre, price, zona, distancia, pet_friendly, amenities, size, bedrooms)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, apartamentos)

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

    return pd.DataFrame(
        matriz,
        index=usuarios["id"],
        columns=apartamentos["id"]
    )


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


def mostrar_asignaciones_detalladas():
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

    resultado = pd.read_sql_query(query, conn)

    conn.close()

    return resultado


# -----------------------------
# PRUEBA COMPLETA
# -----------------------------

crear_tablas()
insertar_datos_prueba()

usuarios, apartamentos = cargar_datos()

print("\nUsuarios guardados:")
print(usuarios)

print("\nApartamentos guardados:")
print(apartamentos)

W, resultado, peso_total = ejecutar_matching()

print("\nMatriz de pesos generada automáticamente:")
print(W)

print("\nAsignaciones guardadas:")
print(resultado)

print("\nAsignaciones detalladas:")
print(mostrar_asignaciones_detalladas())

print("\nPeso total:", round(peso_total, 3))

if len(resultado) > 0:
    print("Peso promedio:", round(peso_total / len(resultado), 3))
else:
    print("No hubo asignaciones válidas.")

print("\n✅ Prueba terminada correctamente.")