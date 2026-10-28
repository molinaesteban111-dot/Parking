# Autonomous Parking

Proyecto educativo para diseñar y evaluar un agente que estacione un vehículo de forma autónoma dentro de un cupo delimitado.

## Objetivo

El agente debe ubicar el vehículo dentro del espacio asignado, alineado y detenido, sin tocar otros vehículos ni los límites del parqueadero.

## Entorno del problema

El mundo se modela como un parqueadero plano compuesto por:

- Cupos de estacionamiento.
- Pasillo de maniobra.
- Bordillos y obstáculos estáticos.
- Vehículos estacionados.
- Un vehículo controlado por el agente.

La física y las colisiones hacen parte del entorno de simulación. Los vehículos y el cupo objetivo permanecen en el mismo estado durante cada episodio, salvo las acciones ejecutadas por el agente.

## Estado, observación y acciones

### Estado del mundo

- Posición del vehículo.
- Orientación.
- Velocidad.
- Dirección de las ruedas.
- Cupo objetivo.
- Tiempo transcurrido.
- Contactos o colisiones.

### Observación

El agente debe recibir, como mínimo:

- Distancia relativa al cupo objetivo.
- Orientación relativa al cupo.
- Velocidad y dirección de giro.
- Información de sensores alrededor del vehículo.

### Acción

Las acciones pueden expresarse mediante:

- Aceleración o frenado.
- Ángulo de dirección.

La acción debe respetar los límites de velocidad, aceleración y dirección definidos por la configuración del entorno.

## Parámetros iniciales

| Parámetro | Unidad | Qué controla |
| --- | --- | --- |
| Ancho y largo del cupo | m | Margen disponible para estacionar |
| Distancia entre ejes | m | Radio de giro del vehículo |
| Velocidad máxima | m/s | Límite para maniobrar |
| Tolerancia angular | grados | Alineación exigida |

Estos valores son propuestas iniciales y deben calibrarse mediante experimentos.

## Recompensa y éxito

La recompensa debe considerar:

- Reducción del error de posición y orientación.
- Costo por tiempo transcurrido.
- Penalización por colisiones.
- Bono único al completar el estacionamiento.

Un episodio es exitoso cuando el vehículo permanece dentro del cupo, alineado y casi inmóvil durante un intervalo definido.

## Evaluación

Se recomienda medir:

- Porcentaje de estacionamientos válidos.
- Error final de posición y orientación.
- Tiempo hasta completar el episodio.
- Número de colisiones.
- Robustez ante cupos más estrechos y sensores con ruido.

## Flujo de trabajo

1. Definir el mapa y los rangos de los parámetros.
2. Implementar el entorno compatible con Gymnasium.
3. Probar las transiciones de observación, acción y recompensa.
4. Ejecutar episodios de prueba.
5. Comparar resultados y ajustar las condiciones.

## Ambiente implementado

El archivo `parking_env.py` contiene el primer ambiente funcional compatible con Gymnasium.

### Estado

La observación contiene seis valores:

1. Posición `x` del vehículo.
2. Posición `y` del vehículo.
3. Orientación.
4. Velocidad.
5. Error de posición en `x` respecto al objetivo.
6. Error de posición en `y` respecto al objetivo.

### Acciones

El espacio de acciones es discreto:

| Acción | Comportamiento |
| --- | --- |
| `0` | Avanzar |
| `1` | Retroceder |
| `2` | Girar a la izquierda |
| `3` | Girar a la derecha |
| `4` | Frenar |

### Recompensa y terminación

El agente recibe una recompensa proporcional a la reducción de la distancia al cupo y un costo pequeño por cada paso. Las colisiones reciben una penalización fuerte y estacionarse correctamente entrega un bono.

El episodio termina cuando el vehículo llega al cupo o colisiona. También se trunca al alcanzar el número máximo de pasos.

### Validación

El ambiente fue validado con `gymnasium.utils.env_checker.check_env`.

## Entorno Python

El proyecto usa el entorno virtual ubicado en `../.venv`. Para activarlo:

```bash
source ../.venv/bin/activate
```

Gymnasium está instalado y se puede comprobar con:

```bash
python -c "import gymnasium; print(gymnasium.__version__)"
```

## Próximos pasos

- Crear la clase del entorno de Gymnasium.
- Definir los espacios de observación y acción.
- Implementar colisiones y condiciones de terminación.
- Diseñar un agente base para comparar políticas.
- Ejecutar cinco transiciones iniciales y registrar sus métricas.

## Agente Q-learning

El archivo `q_learning.py` contiene el primer agente de aprendizaje por refuerzo.

Como el ambiente usa observaciones continuas y Q-learning tabular necesita estados discretos, el agente convierte la posición, orientación y velocidad en intervalos. La tabla Q aprende el valor de cada combinación de estado y acción.

El agente utiliza exploración epsilon-greedy: al comienzo explora muchas acciones y reduce gradualmente `epsilon` para aprovechar lo aprendido. El entrenamiento básico se ejecuta con:

```bash
python q_learning.py
```

Esto genera `q_table.npy` con los valores aprendidos. Los parámetros principales son la tasa de aprendizaje, el factor de descuento, el epsilon mínimo y la cantidad de episodios.
