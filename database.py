import sqlite3
import pandas as pd

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
        barrio TEXT,
        distancia REAL,
        pet_friendly INTEGER,
        amenities TEXT,
        size REAL,
        bedrooms INTEGER,
        latitud REAL,
        longitud REAL,
        url TEXT,
        descripcion TEXT,
        imagen TEXT
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


def limpiar_datos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM asignaciones")
    cursor.execute("DELETE FROM usuarios")
    cursor.execute("DELETE FROM apartamentos")

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


def insertar_apartamento(nombre, price, zona, distancia, pet_friendly, amenities, size, bedrooms,
                         url="", descripcion="", imagen="", barrio="", latitud=None, longitud=None):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO apartamentos
    (nombre, price, zona, barrio, distancia, pet_friendly, amenities, size, bedrooms,
     latitud, longitud, url, descripcion, imagen)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nombre,
        price,
        zona,
        barrio,
        distancia,
        int(pet_friendly),
        ",".join(amenities),
        size,
        bedrooms,
        latitud,
        longitud,
        url,
        descripcion,
        imagen,
    ))

    conn.commit()
    conn.close()


def cargar_usuarios():
    conn = conectar()
    usuarios = pd.read_sql_query("SELECT * FROM usuarios", conn)
    conn.close()
    return usuarios


def cargar_apartamentos():
    conn = conectar()
    apartamentos = pd.read_sql_query("SELECT * FROM apartamentos", conn)
    conn.close()
    return apartamentos


def guardar_asignacion(usuario_id, apartamento_id, peso):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO asignaciones (usuario_id, apartamento_id, peso)
    VALUES (?, ?, ?)
    """, (usuario_id, apartamento_id, peso))

    conn.commit()
    conn.close()


def limpiar_asignaciones():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM asignaciones")

    conn.commit()
    conn.close()


def cargar_asignaciones_detalladas():
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
