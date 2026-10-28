"""Compara políticas aleatorias, Q-learning y red neuronal."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from neural_q_learning import NeuralQAgent
from parking_env import ParkingEnv
from q_learning import QLearningAgent, train as train_tabular


def run_episode(env: ParkingEnv, action_fn) -> tuple[float, bool, int]:
    observation, _ = env.reset()
    total = 0.0
    for step in range(env.max_steps):
        action = action_fn(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        total += reward
        if terminated or truncated:
            return total, bool(info["success"]), step + 1
    return total, False, env.max_steps


def evaluate(episodes: int = 30, output: str = "metrics.png") -> None:
    env = ParkingEnv()
    tabular_agent, _ = train_tabular(episodes=300)
    neural_agent = NeuralQAgent(env.observation_space.shape[0], env.action_space.n)

    policies = {
        "aleatoria": lambda obs: env.action_space.sample(),
        "q_learning": lambda obs: tabular_agent.choose_action(tabular_agent.discretize(obs), greedy=True),
        "red_neuronal": lambda obs: neural_agent.choose_action(obs, greedy=True),
    }
    results: dict[str, list[float]] = {name: [] for name in policies}
    successes: dict[str, int] = {name: 0 for name in policies}
    for name, policy in policies.items():
        for _ in range(episodes):
            reward, success, _ = run_episode(env, policy)
            results[name].append(reward)
            successes[name] += int(success)

    output_path = Path(output)
    plt.figure(figsize=(8, 4))
    plt.boxplot(results.values(), tick_labels=list(results.keys()))
    plt.ylabel("Recompensa por episodio")
    plt.title("Comparación de políticas")
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Métricas guardadas en {output_path}")
    for name in policies:
        print(f"{name}: recompensa media={np.mean(results[name]):.2f}, éxito={successes[name] / episodes:.1%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=30)
    parser.add_argument("--output", default="metrics.png")
    args = parser.parse_args()
    evaluate(args.episodes, args.output)
