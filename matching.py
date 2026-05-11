import pandas as pd
from scipy.optimize import linear_sum_assignment

from database import (
    cargar_usuarios,
    cargar_apartamentos,
    guardar_asignacion,
    limpiar_asignaciones
)


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

    if usuario["pets"] == 1:
        pet_score = 1 if apt["pet_friendly"] == 1 else 0
    else:
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
    usuarios = cargar_usuarios()
    apartamentos = cargar_apartamentos()

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
    W = construir_matriz()

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
    peso_total = 0

    for i, j in zip(filas, columnas):
        peso = W.iloc[i, j]

        if peso > 0:
            usuario_id = int(W.index[i])
            apartamento_id = int(W.columns[j])

            guardar_asignacion(usuario_id, apartamento_id, float(peso))

            resultados.append({
                "usuario_id": usuario_id,
                "apartamento_id": apartamento_id,
                "peso": peso
            })

            peso_total += peso

    resultado = pd.DataFrame(resultados)

    return W, resultado, peso_total