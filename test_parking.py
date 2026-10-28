import unittest

import numpy as np

from parking_env import ParkingEnv
from q_learning import QLearningAgent


class ParkingTests(unittest.TestCase):
    def test_reset_and_step_follow_gymnasium_api(self):
        env = ParkingEnv()
        observation, info = env.reset(seed=7)
        self.assertTrue(env.observation_space.contains(observation))
        self.assertIn("distance", info)
        next_observation, reward, terminated, truncated, info = env.step(0)
        self.assertTrue(env.observation_space.contains(next_observation))
        self.assertIsInstance(reward, float)
        self.assertIsInstance(terminated, bool)
        self.assertIsInstance(truncated, bool)
        self.assertIn("collision", info)

    def test_seed_is_reproducible(self):
        first = ParkingEnv(randomize_target=True, noise_std=0).reset(seed=11)[0]
        second = ParkingEnv(randomize_target=True, noise_std=0).reset(seed=11)[0]
        np.testing.assert_array_equal(first, second)

    def test_q_agent_state_shape(self):
        env = ParkingEnv()
        agent = QLearningAgent(env.action_space.n)
        state = agent.discretize(env.reset()[0])
        self.assertEqual(len(state), 4)
        self.assertEqual(agent.q_table.shape[-1], env.action_space.n)


if __name__ == "__main__":
    unittest.main()
