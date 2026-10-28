"""Agente Q-learning con una red neuronal pequeña implementada con NumPy."""

from __future__ import annotations

import numpy as np

from parking_env import ParkingEnv


class NeuralQAgent:
    """Aproxima Q(s, a) con una red de una capa oculta."""

    def __init__(self, observation_size: int, action_count: int, hidden_size: int = 32) -> None:
        self.action_count = action_count
        self.learning_rate = 0.001
        self.discount_factor = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        self.weights_1 = np.random.default_rng(42).normal(0, 0.1, (observation_size, hidden_size))
        self.bias_1 = np.zeros(hidden_size)
        self.weights_2 = np.random.default_rng(43).normal(0, 0.1, (hidden_size, action_count))
        self.bias_2 = np.zeros(action_count)

    def _forward(self, observation: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Normalización aproximada de los rangos definidos por ParkingEnv.
        normalized = np.asarray(observation, dtype=np.float64) / np.array(
            [10.0, 10.0, np.pi, 1.0, 10.0, 10.0]
        )
        hidden_linear = normalized @ self.weights_1 + self.bias_1
        hidden = np.tanh(hidden_linear)
        q_values = hidden @ self.weights_2 + self.bias_2
        return normalized, hidden, q_values

    def predict(self, observation: np.ndarray) -> np.ndarray:
        return self._forward(observation)[2]

    def choose_action(self, observation: np.ndarray, greedy: bool = False) -> int:
        if not greedy and np.random.random() < self.epsilon:
            return int(np.random.randint(self.action_count))
        return int(np.argmax(self.predict(observation)))

    def update(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool,
    ) -> None:
        normalized, hidden, q_values = self._forward(observation)
        next_q_values = self.predict(next_observation)
        target = reward if done else reward + self.discount_factor * float(np.max(next_q_values))
        error = float(q_values[action] - target)

        output_gradient = np.zeros(self.action_count)
        output_gradient[action] = error
        hidden_gradient = (1.0 - hidden**2) * (self.weights_2 @ output_gradient)

        self.weights_2 -= self.learning_rate * np.outer(hidden, output_gradient)
        self.bias_2 -= self.learning_rate * output_gradient
        self.weights_1 -= self.learning_rate * np.outer(normalized, hidden_gradient)
        self.bias_1 -= self.learning_rate * hidden_gradient

    def finish_episode(self) -> None:
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


def train(episodes: int = 500) -> list[float]:
    env = ParkingEnv()
    agent = NeuralQAgent(env.observation_space.shape[0], env.action_space.n)
    rewards: list[float] = []

    for _ in range(episodes):
        observation, _ = env.reset()
        total_reward = 0.0
        terminated = truncated = False
        while not (terminated or truncated):
            action = agent.choose_action(observation)
            next_observation, reward, terminated, truncated, _ = env.step(action)
            agent.update(observation, action, reward, next_observation, terminated or truncated)
            observation = next_observation
            total_reward += reward
        agent.finish_episode()
        rewards.append(total_reward)

    env.close()
    return rewards


if __name__ == "__main__":
    history = train()
    print(f"Episodios: {len(history)}")
    print(f"Recompensa promedio final: {np.mean(history[-50:]):.2f}")
