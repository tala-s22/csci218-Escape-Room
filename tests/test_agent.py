"""Tests for the adaptive agent (Member 3)."""

import unittest
from agent import AdaptiveAgent
from environment import World


class TestAdaptiveAgent(unittest.TestCase):

    def test_start(self):
        world = World(5, set(), (0, 0), (0, 2), (0, 4))
        agent = AdaptiveAgent(world)

        self.assertEqual(agent.position, (0, 0))
        self.assertEqual(agent.state, "FIND_KEY")
        self.assertFalse(agent.has_key)

    def test_pick_up_key(self):
        world = World(5, set(), (0, 0), (0, 2), (0, 4))
        agent = AdaptiveAgent(world)

        agent.step()
        agent.step()

        self.assertTrue(agent.has_key)
        self.assertEqual(agent.state, "GO_TO_DOOR")

    def test_escape(self):
        world = World(5, set(), (0, 0), (0, 2), (0, 4))
        agent = AdaptiveAgent(world)

        for i in range(20):
            if agent.done():
                break
            agent.step()

        self.assertEqual(agent.state, "ESCAPED")
        self.assertTrue(agent.done())

    def test_replanning(self):
        world = World(5, set(), (0, 0), (0, 4), (4, 4))
        agent = AdaptiveAgent(world)

        agent.step()
        world.block((0, 2))
        agent.step()

        self.assertEqual(agent.replans, 1)
        self.assertNotEqual(agent.position, (0, 2))

    def test_no_path(self):
        walls = {(0, 1), (1, 0)}
        world = World(3, walls, (0, 0), (2, 2), (2, 1))
        agent = AdaptiveAgent(world)

        agent.step()

        self.assertEqual(agent.state, "FAILED")
        self.assertTrue(agent.done())


if __name__ == "__main__":
    unittest.main()
