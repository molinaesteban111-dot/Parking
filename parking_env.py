"""Ambiente mínimo de estacionamiento autónomo para Gymnasium."""

from __future__ import annotations

import math
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class ParkingEnv(gym.Env[np.ndarray, int]):
    """Ambiente 2D donde un vehículo debe llegar a un cupo de estacionamiento.

    Acciones:
        0: avanzar
        1: retroceder
        2: girar a la izquierda
        3: girar a la derecha
        4: frenar
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        max_steps: int = 200,
        noise_std: float = 0.0,
        randomize_target: bool = False,
        obstacles: list[tuple[float, float, float]] | None = None,
    ) -> None:
        super().__init__()
        self.max_steps = max_steps
        self.noise_std = noise_std
        self.randomize_target = randomize_target
        self.obstacles = obstacles or [(1.0, 1.0, 0.35), (1.0, -1.0, 0.35)]

        # [x, y, orientación, velocidad, error_x, error_y]
        self.observation_space = spaces.Box(
            low=np.array([-10.0, -10.0, -math.pi, -1.0, -10.0, -10.0], dtype=np.float32),
            high=np.array([10.0, 10.0, math.pi, 1.0, 10.0, 10.0], dtype=np.float32),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(5)

        self.target = np.array([2.0, 0.0], dtype=np.float32)
        self.position = np.zeros(2, dtype=np.float32)
        self.heading = 0.0
        self.velocity = 0.0
        self.steps = 0

    def _get_obs(self) -> np.ndarray:
        error = self.target - self.position
        observation = np.array(
            [
                self.position[0],
                self.position[1],
                self.heading,
                self.velocity,
                error[0],
                error[1],
            ],
            dtype=np.float32,
        )
        if self.noise_std > 0:
            observation += self.np_random.normal(0, self.noise_std, size=observation.shape)
        return np.clip(observation, self.observation_space.low, self.observation_space.high)

    def _distance_to_target(self) -> float:
        return float(np.linalg.norm(self.target - self.position))

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)
        self.position = np.array([0.0, 0.0], dtype=np.float32)
        if self.randomize_target:
            self.target = self.np_random.uniform([-2.0, -2.0], [3.0, 2.0]).astype(np.float32)
        self.heading = 0.0
        self.velocity = 0.0
        self.steps = 0
        return self._get_obs(), {"distance": self._distance_to_target()}

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        previous_distance = self._distance_to_target()
        action = int(action)

        if action == 0:  # avanzar
            self.velocity = min(self.velocity + 0.1, 1.0)
        elif action == 1:  # retroceder
            self.velocity = max(self.velocity - 0.1, -1.0)
        elif action == 2:  # izquierda
            self.heading += 0.2
        elif action == 3:  # derecha
            self.heading -= 0.2
        elif action == 4:  # frenar
            self.velocity *= 0.5
        else:
            raise ValueError(f"Acción inválida: {action}")

        self.heading = (self.heading + math.pi) % (2 * math.pi) - math.pi
        self.position += self.velocity * np.array(
            [math.cos(self.heading), math.sin(self.heading)], dtype=np.float32
        )
        self.steps += 1

        distance = self._distance_to_target()
        reached_target = distance < 0.25 and abs(self.velocity) < 0.2
        collision = bool(np.any(np.abs(self.position) > 10.0))
        collision = collision or any(
            np.linalg.norm(self.position - np.array(obstacle[:2])) < obstacle[2]
            for obstacle in self.obstacles
        )
        terminated = reached_target or collision
        truncated = self.steps >= self.max_steps and not terminated

        # Recompensa por acercarse; castigo fuerte por colisión y bono por éxito.
        reward = previous_distance - distance - 0.01
        if collision:
            reward -= 10.0
        if reached_target:
            reward += 10.0

        info = {
            "distance": distance,
            "success": reached_target,
            "collision": collision,
        }
        return self._get_obs(), float(reward), terminated, truncated, info


if __name__ == "__main__":
    env = ParkingEnv()
    observation, info = env.reset(seed=42)
    print("Observación inicial:", observation)
    print("Distancia inicial:", info["distance"])
    env.close()
