"""Lanza una demostración visual del ambiente físico PyBullet."""

import time

import numpy as np

from pybullet_env import PyBulletParkingEnv


def main() -> None:
    env = PyBulletParkingEnv(render=True)
    observation, _ = env.reset()
    print("PyBullet abierto. El vehículo avanzará para demostrar la física.")
    print("Cierra la ventana o presiona Ctrl+C para terminar.")
    try:
        for step in range(600):
            # Demostración sencilla: aceleración y pequeñas correcciones de dirección.
            steering = 0.25 if step < 100 else (-0.15 if step < 220 else 0.0)
            observation, _, terminated, truncated, info = env.step(np.array([0.35, steering], dtype=np.float32))
            if step % 60 == 0:
                print(f"Paso {step} | distancia={info['distance']:.2f}")
            if terminated or truncated:
                print("Episodio terminado:", info)
                break
            time.sleep(1 / 60)
    except KeyboardInterrupt:
        print("Demostración detenida.")
    finally:
        env.close()


if __name__ == "__main__":
    main()
