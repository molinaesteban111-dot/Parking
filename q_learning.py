"""Agente Q-learning tabular para el ambiente de estacionamiento."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from parking_env import ParkingEnv


class QLearningAgent:
    """Agente tabular con discretización de posición, orientación y velocidad."""

    def __init__(
        self,
        action_count: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        bins: tuple[int, int, int, int] = (10, 10, 12, 5),
    ) -> None:
        self.action_count = action_count
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.bins = bins
        self.q_table = np.zeros((*bins, action_count), dtype=np.float32)

    def discretize(self, observation: np.ndarray) -> tuple[int, int, int, int]:
        """Convierte la observación continua en un estado de la tabla Q."""
        x, y, heading, velocity, _, _ = observation
        values = (x, y, heading, velocity)
        limits = ((-10.0, 10.0), (-10.0, 10.0), (-np.pi, np.pi), (-1.0, 1.0))
        indexes = []
        for value, (low, high), bin_count in zip(values, limits, self.bins):
            scaled = (float(value) - low) / (high - low)
            indexes.append(int(np.clip(scaled * bin_count, 0, bin_count - 1)))
        return tuple(indexes)  # type: ignore[return-value]

    def choose_action(self, state: tuple[int, int, int, int], greedy: bool = False) -> int:
        if not greedy and np.random.random() < self.epsilon:
            return int(np.random.randint(self.action_count))
        return int(np.argmax(self.q_table[state]))

    def update(
        self,
        state: tuple[int, int, int, int],
        action: int,
        reward: float,
        next_state: tuple[int, int, int, int],
        done: bool,
    ) -> None:
        best_next = 0.0 if done else float(np.max(self.q_table[next_state]))
        target = reward + self.discount_factor * best_next
        current = self.q_table[state + (action,)]
        self.q_table[state + (action,)] = current + self.learning_rate * (target - current)

    def finish_episode(self) -> None:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path: str | Path) -> None:
        np.save(path, self.q_table)


def train(episodes: int = 500, seed: int = 42) -> tuple[QLearningAgent, list[float]]:
    """Entrena el agente y devuelve el historial de recompensas."""
    env = ParkingEnv()
    agent = QLearningAgent(env.action_space.n)
    rewards: list[float] = []

    for episode in range(episodes):
        observation, _ = env.reset(seed=seed + episode)
        state = agent.discretize(observation)
        total_reward = 0.0
        terminated = truncated = False

        while not (terminated or truncated):
            action = agent.choose_action(state)
            next_observation, reward, terminated, truncated, _ = env.step(action)
            next_state = agent.discretize(next_observation)
            agent.update(state, action, reward, next_state, terminated or truncated)
            state = next_state
            total_reward += reward

        agent.finish_episode()
        rewards.append(total_reward)

    env.close()
    return agent, rewards


if __name__ == "__main__":
    trained_agent, history = train()
    trained_agent.save("q_table.npy")
    print(f"Episodios: {len(history)}")
    print(f"Recompensa promedio final: {np.mean(history[-50:]):.2f}")
    print(f"Epsilon final: {trained_agent.epsilon:.3f}")
