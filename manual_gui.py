"""Interfaz gráfica 2D para controlar manualmente el ambiente."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from parking_env import ParkingEnv


class ParkingGUI:
    def __init__(self) -> None:
        self.env = ParkingEnv()
        self.observation, self.info = self.env.reset()
        self.step_count = 0

        self.figure, self.axis = plt.subplots(figsize=(10, 6))
        self.figure.canvas.manager.set_window_title("Autonomous Parking - Control manual")
        self.figure.canvas.mpl_connect("key_press_event", self.on_key)
        self.draw()

    def draw(self) -> None:
        self.axis.clear()
        self.axis.set_title("Autonomous Parking | w/s: mover | a/d: girar | b: frenar | r: reiniciar | q: salir")
        self.axis.set_xlim(-3, 4)
        self.axis.set_ylim(-3, 3)
        self.axis.set_aspect("equal")
        self.axis.set_xlabel("x")
        self.axis.set_ylabel("y")
        self.axis.grid(alpha=0.25)

        target_x, target_y = self.env.target
        self.axis.add_patch(Rectangle((target_x - 0.5, target_y - 1), 1, 2, color="limegreen", alpha=0.55))
        self.axis.text(target_x, target_y, "CUPO", ha="center", va="center", weight="bold")

        for obstacle_x, obstacle_y, radius in self.env.obstacles:
            self.axis.add_patch(Circle((obstacle_x, obstacle_y), radius, color="crimson", alpha=0.75))

        x, y, heading, velocity, _, _ = self.observation
        car = Rectangle((x - 0.3, y - 0.5), 0.6, 1.0, color="darkorange", alpha=0.9)
        car.set_rotation(math.degrees(heading), rotation_point="center")
        self.axis.add_patch(car)
        self.axis.arrow(x, y, 0.7 * math.cos(heading), 0.7 * math.sin(heading), color="black", width=0.025)
        self.axis.text(
            -2.9,
            2.65,
            f"Paso: {self.step_count} | Distancia: {self.info['distance']:.2f} | Velocidad: {velocity:.2f}",
        )
        self.figure.canvas.draw_idle()

    def on_key(self, event) -> None:
        actions = {"w": 0, "s": 1, "a": 2, "d": 3, "b": 4}
        if event.key == "q":
            plt.close(self.figure)
            return
        if event.key == "r":
            self.observation, self.info = self.env.reset()
            self.step_count = 0
            self.draw()
            return
        if event.key not in actions:
            return

        self.observation, _, terminated, truncated, self.info = self.env.step(actions[event.key])
        self.step_count += 1
        self.draw()
        if terminated or truncated:
            self.axis.set_title("¡Estacionamiento exitoso! Presiona r para reiniciar o q para salir.") if self.info["success"] else self.axis.set_title("Episodio terminado: colisión o límite. Presiona r para reiniciar.")
            self.figure.canvas.draw_idle()

    def show(self) -> None:
        print("Ventana gráfica iniciada. Haz clic en ella para activar el teclado.")
        plt.show()
        self.env.close()


if __name__ == "__main__":
    ParkingGUI().show()
