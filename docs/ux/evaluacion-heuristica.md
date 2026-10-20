# Evaluación heurística
## **Cinepolis**

# Tareas:
1. Quiero comprar un boleto para dos personas en sala normal. 

| descripción | tiempo | dudo | qué dudó? |
|---|---|---|---|
| Entré a la página de Cinépolis y busqué la película que quería ver. | 15s | Sí | No sabía inicialmente dónde buscar la película. |
| Seleccioné la película y revisé los horarios disponibles. | 17s | No | 
| Seleccioné el cine donde quería ver la película. | 20s | Sí |No estaba seguro de haber seleccionado el cine correcto.
| Seleccioné dos asientos en la sala. | 10s | No |
| Revisé el resumen de la compra y el precio de los boletos. | 20s | Sí | Busqué confirmar que fueran dos boletos para sala normal.
| Llegué a la pantalla de pago y me detuve antes de confirmar la compra. | 10s | No |

# Hallazgos

## H1. Dificultad para identificar la sala tradicional

* **Dónde:** Pantalla de selección del tipo de sala.
* **Principio:** Reconocimiento antes que recuerdo.
* **Qué pasa:** Se muestran diferentes tipos de sala y el usuario debe revisar las opciones para identificar cuál corresponde a una sala tradicional.
* **Consecuencia:** Aumenta el tiempo de selección y existe el riesgo de elegir una sala diferente a la deseada.

## H2. Falta de claridad en la disponibilidad de asientos

* **Dónde:** Pantalla del mapa de asientos.
* **Principio:** Visibilidad del estado del sistema.
* **Qué pasa:** El usuario debe consultar las indicaciones del mapa para distinguir los asientos disponibles, ocupados y seleccionados.
* **Consecuencia:** Puede confundirse al elegir los asientos e invertir tiempo adicional en identificar los lugares disponibles.

## H3. Dificultad para seleccionar dos asientos juntos

* **Dónde:** Pantalla de selección de asientos.
* **Principio:** Prevención de errores.
* **Qué pasa:** El usuario debe identificar manualmente dos asientos contiguos y comprobar que ambos estén disponibles antes de continuar.
* **Consecuencia:** Puede seleccionar asientos separados y tener que repetir el proceso de selección.

## H4. Precio total de compra poco claro

* **Dónde:** Pantalla de resumen de compra antes del pago.
* **Principio:** Visibilidad del estado del sistema.
* **Qué pasa:** El usuario debe revisar el precio de los boletos y los posibles cargos adicionales para conocer el importe total.
* **Consecuencia:** Puede tardar más en calcular el costo final o continuar sin tener claro cuánto pagará.

## H5. Dificultad para modificar la función seleccionada

* **Dónde:** Pantalla posterior a la selección de la función.
* **Principio:** Control y libertad del usuario.
* **Qué pasa:** Para cambiar el cine o el horario seleccionado, el usuario debe regresar a pantallas anteriores del proceso de compra.
* **Consecuencia:** Pierde tiempo y puede necesitar repetir algunas selecciones.

## H6. Opciones adicionales durante el proceso de compra

* **Dónde:** Pantallas intermedias entre la selección de asientos y el pago.
* **Principio:** Diseño estético y minimalista.
* **Qué pasa:** Se presentan opciones adicionales relacionadas con la compra que el usuario debe revisar antes de continuar.
* **Consecuencia:** Aumenta el número de decisiones y el tiempo necesario para completar la compra.

## H7. Mensajes de error poco claros

* **Dónde:** Pantalla de selección de asientos o durante la confirmación de la compra.
* **Principio:** Ayuda a los usuarios a reconocer, diagnosticar y recuperarse de los errores.
* **Qué pasa:** Cuando una selección no puede completarse, el usuario necesita identificar qué acción debe realizar para resolver el problema y continuar.
* **Consecuencia:** Puede repetir acciones o perder tiempo intentando corregir el error.

## H8. Falta de claridad sobre el paso actual de la compra

* **Dónde:** Flujo de compra desde la selección de la función hasta el pago.
* **Principio:** Visibilidad del estado del sistema.
* **Qué pasa:** El usuario debe interpretar la información de cada pantalla para identificar en qué etapa se encuentra y cuál es el siguiente paso.
* **Consecuencia:** Puede dudar sobre cómo continuar y tardar más en completar la compra.

# Priorizar por severidad

## Asignación de severidad

| Hallazgo | Severidad | Justificación |
|---|---|---|
| H1. Identificar la sala tradicional | 2 · Menor | Puede generar dudas al elegir el tipo de sala, pero permite continuar con la compra. |
| H2. Disponibilidad de asientos | 3 · Mayor | La confusión puede retrasar la selección de lugares. |
| H3. Seleccionar dos asientos juntos | 3 · Mayor | Puede provocar una selección incorrecta y obligar al usuario a repetir pasos. |
| H4. Claridad del precio total | 3 · Mayor | La falta de claridad sobre el costo final puede dificultar la decisión de pagar. |
| H5. Modificar la función seleccionada | 2 · Menor | Regresar a pantallas anteriores puede aumentar el tiempo de compra. |
| H6. Opciones adicionales durante la compra | 2 · Menor | Las opciones adicionales pueden distraer al usuario y alargar el proceso. |
| H7. Mensajes de error poco claros | 3 · Mayor | El usuario puede tener dificultades para resolver un error y continuar. |
| H8. Identificar el paso actual | 2 · Menor | Puede generar dudas sobre qué acción realizar a continuación. |

## Cruce de severidad con frecuencia

| Severidad | Ocurre pocas veces | Ocurre en casi cada uso |
|---|---|---|
| Alta (3-4) | H7. Mensajes de error poco claros | H2. Disponibilidad de asientos; H3. Seleccionar dos asientos juntos; H4. Claridad del precio total |
| Baja (1-2) | H1. Identificar la sala tradicional; H5. Modificar la función; H8. Identificar el paso actual | H6. Opciones adicionales durante la compra |

## Orden final de prioridad

| Prioridad | Hallazgo | Severidad | Frecuencia |
|---:|---|---|---|
| 1 | H2. Disponibilidad de asientos | 3 · Mayor | Casi cada uso |
| 2 | H3. Seleccionar dos asientos juntos | 3 · Mayor | Casi cada uso |
| 3 | H4. Claridad del precio total | 3 · Mayor | Casi cada uso |
| 4 | H7. Mensajes de error poco claros | 3 · Mayor | Pocas veces |
| 5 | H6. Opciones adicionales durante la compra | 2 · Menor | Casi cada uso |
| 6 | H8. Identificar el paso actual | 2 · Menor | Pocas veces |
| 7 | H5. Modificar la función seleccionada | 2 · Menor | Pocas veces |
| 8 | H1. Identificar la sala tradicional | 2 · Menor | Pocas veces |

## Proponer mejoras

### Mejora para H2. Disponibilidad de asientos

- **Problema:** El usuario puede confundirse al distinguir los asientos disponibles, ocupados y seleccionados.
- **Propuesta:** Diferenciar los estados de los asientos mediante colores contrastantes, símbolos y una leyenda visible junto al mapa.
- **Principio que resuelve:** Visibilidad del estado del sistema.
- **Resultado esperado:** El usuario identifica rápidamente los asientos disponibles y reduce el tiempo de selección.

### Mejora para H3. Seleccionar dos asientos juntos

- **Problema:** El usuario debe comprobar manualmente que los dos asientos seleccionados estén juntos y disponibles.
- **Propuesta:** Resaltar visualmente los asientos contiguos seleccionados y mostrar una confirmación antes de continuar con la compra.
- **Principio que resuelve:** Prevención de errores.
- **Resultado esperado:** Se reducen las selecciones incorrectas y la necesidad de repetir pasos.

### Mejora para H4. Claridad del precio total

- **Problema:** El usuario debe revisar los precios de los boletos y los cargos adicionales para calcular el costo final.
- **Propuesta:** Mostrar un resumen visible con la cantidad de boletos, el precio individual, los cargos adicionales y el total antes de pasar al pago.
- **Principio que resuelve:** Visibilidad del estado del sistema.
- **Resultado esperado:** El usuario conoce el importe total antes de pagar y puede tomar una decisión informada.

## ¿Qué aprendimos?

Sergio: Aprendimos a identificar problemas de usabilidad en una plataforma mediante una evaluación heurística. Comprendimos cómo clasificar los hallazgos según su severidad y frecuencia para establecer prioridades.

Juan Pablo: Aprendí que una evaluación sirve más cuando se revisa una tarea completa como comprar dos boletos porque los problemas aparecen al pasar de una pantalla a otra casi siempre. Igual que tenemos que describir lo observamos y no dar opiniones y que priorizar ayuda a decidir qué es lo más importante por arreglar primero como el mapa de asientos de Cinépolis por ejemplo.