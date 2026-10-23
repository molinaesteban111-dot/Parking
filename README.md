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
