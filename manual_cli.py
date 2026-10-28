"""Control manual del vehículo desde la terminal."""

from __future__ import annotations

from parking_env import ParkingEnv


ACTIONS = {
    "w": (0, "avanzar"),
    "s": (1, "retroceder"),
    "a": (2, "girar izquierda"),
    "d": (3, "girar derecha"),
    "b": (4, "frenar"),
}


def show_state(observation, info, step: int) -> None:
    x, y, heading, velocity, error_x, error_y = observation
    print(
        f"Paso {step} | posición=({x:.2f}, {y:.2f}) | "
        f"orientación={heading:.2f} rad | velocidad={velocity:.2f} | "
        f"distancia={info['distance']:.2f}"
    )


def main() -> None:
    env = ParkingEnv()
    observation, info = env.reset()
    step = 0

    print("=== Autonomous Parking: control manual ===")
    print("w: avanzar | s: retroceder | a: izquierda | d: derecha | b: frenar")
    print("r: reiniciar | q: salir")
    show_state(observation, info, step)

    while True:
        try:
            command = input("\nComando: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        if command == "q":
            print("Saliendo...")
            break
        if command == "r":
            observation, info = env.reset()
            step = 0
            print("Episodio reiniciado.")
            show_state(observation, info, step)
            continue
        if command not in ACTIONS:
            print("Comando inválido. Usa w, s, a, d, b, r o q.")
            continue

        action, description = ACTIONS[command]
        observation, reward, terminated, truncated, info = env.step(action)
        step += 1
        print(f"Acción: {description} | recompensa={reward:.2f}")
        show_state(observation, info, step)

        if terminated or truncated:
            if info["success"]:
                print("¡Estacionamiento exitoso!")
            elif info["collision"]:
                print("Colisión detectada.")
            else:
                print("Se alcanzó el máximo de pasos.")
            print("Usa r para reiniciar o q para salir.")

    env.close()


if __name__ == "__main__":
    main()
