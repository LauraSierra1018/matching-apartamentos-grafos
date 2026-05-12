# Apartment Matching System using Graph Theory

Sistema de asignación óptima de apartamentos basado en teoría de grafos, matching bipartito ponderado y algoritmo húngaro.

---

## Descripción del Proyecto

Este proyecto modela el problema de recomendación y asignación de apartamentos como un grafo bipartito ponderado:

\[
G = (U \cup O, E, w)
\]

donde:

- \(U\): conjunto de usuarios
- \(O\): conjunto de apartamentos
- \(E\): aristas de compatibilidad
- \(w\): función de peso o compatibilidad

El objetivo es encontrar un matching óptimo que maximice la compatibilidad total entre usuarios y apartamentos.

---

## Características

- Registro dinámico de usuarios
- Base de datos remota con Supabase
- Apartamentos precargados automáticamente
- Construcción automática del grafo bipartito
- Cálculo automático de pesos de compatibilidad
- Algoritmo Húngaro (Hungarian Algorithm)
- Matching máximo ponderado
- Interfaz gráfica con Streamlit
- Persistencia de datos en la nube

---

## Tecnologías Utilizadas

- Python
- Streamlit
- Supabase (PostgreSQL)
- Pandas
- SciPy
- Teoría de Grafos

---

## Modelo Matemático

La compatibilidad entre un usuario \(u_i\) y un apartamento \(o_j\) se calcula mediante:

\[
w(u_i,o_j)=0.40ps+0.30ls+0.30ss
\]

donde:

- \(ps\): Price Score
- \(ls\): Location Score
- \(ss\): Secondary Score

El sistema resuelve:

\[
\max \sum w_{ij}x_{ij}
\]

sujeto a restricciones de matching uno-a-uno.

---

## Restricciones

Una arista entre un usuario y un apartamento existe únicamente si:

1. El apartamento está dentro del presupuesto.
2. La distancia está dentro del radio permitido.
3. Cumple restricciones de mascotas.
4. Cumple al menos el 50% de amenities requeridos.

---

## Algoritmo Utilizado

Se utiliza el algoritmo húngaro para resolver el problema de matching máximo ponderado.

### Flujo del sistema

```text
Usuarios + Apartamentos
        ↓
Construcción del grafo
        ↓
Cálculo de pesos
        ↓
Matriz de compatibilidad
        ↓
Algoritmo Húngaro
        ↓
Asignaciones óptimas
