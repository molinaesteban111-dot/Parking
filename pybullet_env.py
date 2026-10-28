"""Ambiente Gymnasium de estacionamiento con física PyBullet."""

from __future__ import annotations

import math
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

try:
    import pybullet as bullet
except ImportError as exc:  # pragma: no cover - depende de la instalación local
    raise ImportError(
        "PyBullet no está instalado. Ejecuta `pip install pybullet` "
        "o instala un compilador C++ para Python 3.14."
    ) from exc


class PyBulletParkingEnv(gym.Env[np.ndarray, np.ndarray]):
    """Vehículo 3D simplificado con control de aceleración y dirección."""

    def __init__(self, max_steps: int = 300, render: bool = False) -> None:
        super().__init__()
        self.max_steps = max_steps
        self.client = bullet.connect(bullet.GUI if render else bullet.DIRECT)
        bullet.setGravity(0, 0, -9.81, physicsClientId=self.client)
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0], dtype=np.float32),
            high=np.array([1.0, 1.0], dtype=np.float32),
            dtype=np.float32,
        )
        self.observation_space = spaces.Box(
            low=np.array([-10, -10, -math.pi, -2, -2, -math.pi], dtype=np.float32),
            high=np.array([10, 10, math.pi, 2, 2, math.pi], dtype=np.float32),
            dtype=np.float32,
        )
        self.vehicle = -1
        self.target = np.array([2.0, 0.0], dtype=np.float32)
        self.steps = 0
        self._build_world()

    def _build_world(self) -> None:
        bullet.resetSimulation(physicsClientId=self.client)
        bullet.setGravity(0, 0, -9.81, physicsClientId=self.client)
        plane_shape = bullet.createCollisionShape(bullet.GEOM_BOX, halfExtents=[5, 3, .05], physicsClientId=self.client)
        bullet.createMultiBody(0, plane_shape, physicsClientId=self.client)
        wall_shape = bullet.createCollisionShape(bullet.GEOM_BOX, halfExtents=[.4, .6, .4], physicsClientId=self.client)
        for x, y in ((1, 1.6), (1, -1.6)):
            bullet.createMultiBody(1, wall_shape, basePosition=[x, y, .4], physicsClientId=self.client)
        car_shape = bullet.createCollisionShape(bullet.GEOM_BOX, halfExtents=[.55, .9, .25], physicsClientId=self.client)
        self.vehicle = bullet.createMultiBody(1, car_shape, basePosition=[-3, 0, .35], physicsClientId=self.client)

    def _get_obs(self) -> np.ndarray:
        position, orientation = bullet.getBasePositionAndOrientation(self.vehicle, physicsClientId=self.client)
        velocity, _ = bullet.getBaseVelocity(self.vehicle, physicsClientId=self.client)
        heading = bullet.getEulerFromQuaternion(orientation)[2]
        error = self.target - np.array(position[:2])
        return np.array([position[0], position[1], heading, velocity[0], error[0], error[1]], dtype=np.float32)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        self._build_world()
        self.steps = 0
        return self._get_obs(), {"distance": float(np.linalg.norm(self.target - self._get_obs()[:2]))}

    def step(self, action: np.ndarray):
        action = np.clip(np.asarray(action, dtype=np.float32), -1, 1)
        previous = self._get_obs()
        force = [float(action[0] * 18 * math.cos(previous[2])), float(action[0] * 18 * math.sin(previous[2])), 0]
        bullet.applyExternalForce(self.vehicle, -1, force, [0, 0, 0], bullet.WORLD_FRAME, physicsClientId=self.client)
        bullet.applyExternalTorque(self.vehicle, -1, [0, 0, float(action[1] * 4)], bullet.WORLD_FRAME, physicsClientId=self.client)
        bullet.stepSimulation(physicsClientId=self.client)
        self.steps += 1
        observation = self._get_obs()
        distance = float(np.linalg.norm(observation[4:6]))
        contacts = bullet.getContactPoints(self.vehicle, physicsClientId=self.client)
        success = distance < .3 and abs(observation[3]) < .2
        collision = bool(contacts)
        terminated = success or collision
        truncated = self.steps >= self.max_steps and not terminated
        reward = float(np.linalg.norm(previous[4:6]) - distance - .01)
        if collision: reward -= 10
        if success: reward += 10
        return observation, reward, terminated, truncated, {"distance": distance, "success": success, "collision": collision}

    def close(self) -> None:
        if bullet.isConnected(self.client):
            bullet.disconnect(self.client)
