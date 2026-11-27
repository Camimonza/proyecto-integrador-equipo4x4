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

## **Laboratorio 11**

**¿Qué les resultó más fácil en Dash que en Streamlit?**
El control del diseño. Con `display: flex` y `flex: 1` pudimos decidir cómo se reparten el ancho las tarjetas y las gráficas, algo que en Streamlit con `st.columns()` es más limitado. También nos gustó poder definir los estilos una sola vez en diccionarios y reutilizarlos en varios componentes.

**¿Qué les resultó más difícil o más lento?**
Armar el árbol de componentes: hay que cuidar corchetes y paréntesis, y un error de sintaxis puede apuntar a una línea muy lejana al problema. También fue más lento por los detalles de configuración, como ejecutar con `python dash/app.py` desde la raíz del repositorio y lidiar con un proceso viejo que dejó ocupado el puerto 8050 y mostraba una versión anterior del tablero.

**¿Hay algo de su wireframe original que en Streamlit no pudieron construir y en Dash sí?**
Sí, la distribución exacta de los bloques: una gráfica ancha arriba y dos gráficas lado a lado con tarjetas del mismo estilo. En Dash lo logramos con filas flex y proporciones propias, con más libertad sobre espacios y apariencia que en Streamlit.

**Con lo visto hasta hoy, ¿con cuál se inclinan? ¿Por qué?**
Por ahora nos inclinamos por Dash, por el control que da sobre el diseño y porque la estructura en componentes es clara. Streamlit sigue siendo más rápido y sencillo para prototipar, y todavía no hemos visto los callbacks de Dash, así que la decisión final la tomaremos en la sesión 5.

## **Laboratorio 12**

### Observaciones de A.3: romper las reglas del callback

**1. Cambiar `Input("color", ...)` por `Input("colores", ...)`**
La aplicación sí arrancó, pero al abrir la página apareció un error: *A nonexistent object was used in an `Input` of a Dash callback*. El mensaje dice que el id "colores" no existe en el layout. Dash no detecta el error al iniciar el servidor, sino cuando la página se carga en el navegador.

**2. Agregar `Output("salida2", "children")` sin crear el componente ni cambiar el return**
Apareció un error por usar un objeto inexistente en un `Output`, al cargar la página y antes de que el callback se ejecutara. Si el componente existiera pero el return siguiera devolviendo un solo valor, el error sería otro (*Expected 2 outputs, got 1*) y aparecería al ejecutarse el callback.

**3. Cambiar `value` por `options` en el Input**
No hubo error. La función recibió la lista completa de opciones y el texto mostró `Elegiste: ['Rojo', 'Azul', 'Verde']` en lugar del color elegido. Dash escucha la propiedad que se le indique, y el nombre de la propiedad define qué valor llega a la función.

### Bitácora de comparación (cierre): Streamlit vs Dash

**¿En cuál de las dos escribieron menos código para el mismo resultado?**
En Streamlit. El script se lee de arriba hacia abajo: se lee el valor del filtro, se filtra el DataFrame y se dibuja, todo en el mismo lugar. En Dash tuvimos que declarar ids en cada componente, escribir un callback con 4 Input y 8 Output, y mantener el mismo orden entre argumentos y valores de retorno. El resultado visible es el mismo, pero Dash pide más estructura.

**¿En cuál entendieron mejor *por qué* pasaban las cosas?**
En Dash. En Streamlit el script se reejecuta completo cada vez, y eso pasa sin que uno lo vea, así que los comportamientos parecen automáticos. En Dash la conexión es explícita: cada Input y cada Output nombra el componente y la propiedad, y con `minimo.py` pudimos ver que Dash ejecuta la función solo cuando cambia lo que escucha. Cuando algo falla, el mensaje nos dice qué id o qué orden está mal.

**¿Qué les dio más problemas en Streamlit? ¿Y en Dash?**
En Streamlit: el diseño es más limitado, porque `st.columns()` da poco control sobre proporciones y espacios, y hay que usar caché (`@st.cache_data`) para no releer los datos en cada reejecución. En Dash: la sintaxis del árbol (corchetes y paréntesis), el orden de los Input y los Output, que si se desordena no marca error y solo muestra datos equivocados, y un proceso viejo que quedó ocupando el puerto 8050 y mostraba una versión anterior del tablero.

**Pensando en cómo va a crecer su plataforma, ¿con cuál se quedan y por qué?**
Nos quedamos con Dash. Cuando la plataforma crezca, el trabajo será agregar filtros, vistas y gráficas. En Dash cada pieza tiene un id, el árbol de componentes se divide en funciones reutilizables como `tarjeta()`, y cada callback declara exactamente qué lee y qué actualiza, así que es más fácil saber qué se afecta al cambiar algo y trabajar en equipo sin pisarse. También da control total sobre el diseño y permite refrescar solo las partes que cambian. El costo es escribir más código al inicio, pero para una plataforma que va a seguir creciendo lo vemos como una buena inversión.