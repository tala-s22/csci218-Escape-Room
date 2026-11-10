"""Dynamic events (Member 4)."""

import random


class DynamicEvents:
    """Blocks one cell on the agent's planned path every N steps."""

    def __init__(self, seed, every_n_steps):
        self.rng = random.Random(seed)
        self.every_n_steps = every_n_steps
        self.tick = 0

    def apply(self, world, agent):
        """Called once per tick. Returns the blocked cell, or None."""
        self.tick += 1

        if self.every_n_steps <= 0:
            return None
        if self.tick % self.every_n_steps != 0:
            return None

        candidates = [
            cell for cell in agent.path
            if world.is_free(cell)
            and cell != world.key
            and cell != world.door
            and cell != agent.position
        ]
        if not candidates:
            return None

        cell = self.rng.choice(candidates)
        world.block(cell)
        return cell
