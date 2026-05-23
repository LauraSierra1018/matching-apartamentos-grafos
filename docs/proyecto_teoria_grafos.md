# Optimización de la Asignación de Vivienda mediante Teoría de Grafos

**Autores:** Jhon Rivera, Laura Sierra, Alejandro Arroyave, Juan José Garzón  
**Asignatura:** Teoría de Grafos  
**Institución:** Facultad de Ciencias e Ingeniería, Universidad del Rosario

---

## I. Introducción

El mercado de vivienda se interpreta como un sistema de asignación entre oferentes (apartamentos) y demandantes (buscadores). A diferencia de los filtros tradicionales, este proyecto utiliza **grafos bipartitos** y problemas de **emparejamiento (matching)** para garantizar una asignación globalmente eficiente.

El problema se modela como un grafo bipartito ponderado $G = (U \cup O, E, w)$ donde:

- **U**: Conjunto de buscadores
- **O**: Conjunto de apartamentos
- **E**: Aristas de compatibilidad
- **w**: Función que cuantifica el nivel de adecuación

La solución se obtiene mediante el **Algoritmo Húngaro**, que resuelve el problema en tiempo polinómico.

---

## II. Descripción del Problema

El objetivo es determinar una asignación uno-a-uno que maximice la compatibilidad global del sistema.

### A. Naturaleza Combinatoria

Existe competencia estructural por recursos limitados. El modelamiento se apoya en:

- **Teorema de Hall**: Caracteriza la existencia de un matching completo.
- **Teorema de Kőnig**: Relaciona el matching máximo y la cobertura mínima en grafos bipartitos.

### B. Dificultad del Problema

Las decisiones locales no garantizan la optimalidad global; elegir la mejor opción individual puede impedir configuraciones de mayor beneficio agregado.

---

## III. Objetivos

**Objetivo General:** Diseñar un sistema basado en teoría de grafos que optimice la asignación entre buscadores y apartamentos, maximizando la compatibilidad global.

**Objetivos Específicos:**

1. Modelar el problema como un grafo bipartito ponderado.
2. Definir una función de compatibilidad basada en criterios obligatorios y opcionales.
3. Implementar y comparar estrategias como matching máximo y matching de peso máximo.

---

## IV. Marco Teórico

| Concepto | Descripción |
|---|---|
| **Teorema de Hall** | Garantiza que no haya cuellos de botella en la asignación |
| **Matching de Peso Máximo** | Maximiza la suma de los pesos de las aristas, optimizando la calidad global |
| **Algoritmo Húngaro** | Garantiza soluciones óptimas eficientes computacionalmente |

---

## V. Modelamiento del Problema

### A. Criterios de Existencia de Arista

Una arista $(u_i, o_j)$ existe únicamente si se cumplen **todas** las siguientes condiciones:

1. **Precio**: $o_j.price \le u_i.budget$
2. **Ubicación**: $d(u_i, o_j) \le u_i.radius$
3. **Mascotas**: Compatibilidad con la política del apartamento
4. **Amenities**: Coincidencia mínima del 50%

### B. Función de Peso

$$w(u_i, o_j) = 0.40 \cdot ps + 0.30 \cdot ls + 0.30 \cdot ss$$

Donde:

- **ps (Price Score)**: Qué tan cercano está el precio al presupuesto del buscador
- **ls (Location Score)**: Qué tan cerca está el apartamento dentro del radio deseado
- **ss (Secondary Score)**: Incluye amenities, tamaño y número de habitaciones

### C. Problema de Optimización

Se formula como un programa lineal entero:

$$\max \sum_{i,j} w_{ij} x_{ij}$$

Sujeto a:

$$\sum_j x_{ij} \le 1 \quad \forall i \in U \qquad \text{(cada buscador a máximo un apartamento)}$$

$$\sum_i x_{ij} \le 1 \quad \forall j \in O \qquad \text{(cada apartamento a máximo un buscador)}$$

$$x_{ij} \in \{0, 1\}$$

---

## VI. Solución Propuesta

El sistema sigue un pipeline de tres etapas:

```
Texto libre del usuario
        ↓
   Extracción NLP
   (regex en español)
        ↓
Construcción del grafo bipartito
   + cálculo de pesos w(u,o)
        ↓
   Algoritmo Húngaro
   (scipy.optimize.linear_sum_assignment)
        ↓
  Asignaciones óptimas
```

### Ventajas del enfoque

- Garantiza una solución **globalmente óptima** (no solo localmente buena)
- Respeta restricciones uno-a-uno
- Incorpora criterios **duros** (viabilidad: precio, distancia, mascotas) y **suaves** (preferencias: amenities, tamaño, habitaciones)

---

## Referencias

1. C. Berge, *Theory of Graphs*, 1957.
2. P. Hall, "On Representatives of Subsets", 1935.
3. H. W. Kuhn, "The Hungarian Method for the Assignment Problem", 1955.
4. A. Schrijver, *Theory of Linear and Integer Programming*, 1998.
