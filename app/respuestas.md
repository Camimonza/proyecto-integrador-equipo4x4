# **RESPUESTAS**

## **Laboratorio 9**
**Contador**
Después de presionar el botón el contador va a subir hasta 5 si se presiona 5 veces el boton. 

1. ¿Por qué el contador nunca pasa de 1, por más veces que presionen el botón?

Porque se vuelve a correr el porgrama desdde cero y pasa por la variable contador = 0 que reinicia la sumatoria a 0


2. Si quisieran que el valor se conservara entre una interacción y la siguiente, ¿dónde tendría que
guardarse, si no puede ser en una variable normal del script?

podría modificarse el if ppor un for o un while que mantenga en un ciclo la sumatoria hasta que se cumpla una condición para salir. 

## **Laboratorio 10**
| Interacción | Sin caché (s) | Con caché (s) |
|---|---:|---:|
| 1  | 5.91 | 0.82 |
| 2  | 2.50 | 1.08 |
| 3  | 3.22 | 0.89 |
| 4  | 2.71 | 0.88 |
| 5  | 3.11 | 0.89 |
| **Promedio (cambios 2 a 5)** | **2.89** | **0.94** |

Al agregar `@st.cache_data`, el tiempo promedio de respuesta al cambiar filtros bajó de 2.89 s a 0.94 s, lo que representa una reducción del 67.6% (aproximadamente 3 veces más rápido). Esto ocurre porque Streamlit evita volver a leer el archivo CSV y ejecutar la espera simulada en cada interacción, reutilizando los datos ya cargados en memoria.