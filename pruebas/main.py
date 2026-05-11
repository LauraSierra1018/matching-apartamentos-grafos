from database import (
    crear_tablas,
    limpiar_datos,
    insertar_usuario,
    insertar_apartamento,
    cargar_usuarios,
    cargar_apartamentos,
    cargar_asignaciones_detalladas
)

from matching import ejecutar_matching


crear_tablas()
limpiar_datos()

# -----------------------------
# Insertar usuarios
# -----------------------------

insertar_usuario(
    "Jhon",
    2000000,
    "Chapinero",
    3,
    True,
    ["gym", "parqueadero"],
    50,
    2
)

insertar_usuario(
    "Maria",
    1800000,
    "Suba",
    4,
    False,
    ["ascensor"],
    45,
    1
)

insertar_usuario(
    "Laura",
    2500000,
    "Chapinero",
    5,
    True,
    ["gym", "ascensor"],
    60,
    2
)

# -----------------------------
# Insertar apartamentos
# -----------------------------

insertar_apartamento(
    "Apt1",
    1800000,
    "Chapinero",
    1.2,
    True,
    ["gym", "parqueadero", "ascensor"],
    52,
    2
)

insertar_apartamento(
    "Apt2",
    1700000,
    "Suba",
    2.0,
    False,
    ["ascensor"],
    42,
    1
)

insertar_apartamento(
    "Apt3",
    2400000,
    "Chapinero",
    2.5,
    True,
    ["gym", "ascensor"],
    58,
    2
)

# -----------------------------
# Mostrar datos guardados
# -----------------------------

print("\nUsuarios guardados:")
print(cargar_usuarios())

print("\nApartamentos guardados:")
print(cargar_apartamentos())

# -----------------------------
# Ejecutar matching
# -----------------------------

W, resultado, peso_total = ejecutar_matching()

print("\nMatriz de pesos:")
print(W)

print("\nAsignaciones por ID:")
print(resultado)

print("\nAsignaciones detalladas:")
print(cargar_asignaciones_detalladas())

print("\nPeso total:", round(peso_total, 3))

if len(resultado) > 0:
    print("Peso promedio:", round(peso_total / len(resultado), 3))
else:
    print("No hubo asignaciones válidas.")