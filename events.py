"""Dynamic events (Member 4)."""

import random

from navigation import astar


class DynamicEvents:
    """Blocks one cell on the agent's planned path every N steps,
    but only if the agent can still finish the room afterwards."""

    def __init__(self, seed, every_n_steps, check_route=True):
        self.rng = random.Random(seed)
        self.every_n_steps = every_n_steps
        self.check_route = check_route
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
            and cell != world.start
            and cell != world.key
            and cell != world.door
            and cell != agent.position
        ]
        self.rng.shuffle(candidates)

        for cell in candidates:
            world.block(cell)
            if not self.check_route or self._route_remains(world, agent):
                return cell
            world.unblock(cell)

        return None

    def _route_remains(self, world, agent):
        """True if the agent can still reach the key (if it has not got it yet)
        and then the door."""
        if agent.has_key:
            legs = [(agent.position, world.door)]
        else:
            legs = [(agent.position, world.key), (world.key, world.door)]

        for begin, end in legs:
            path, _ = astar(world, begin, end)
            if path is None:
                return False
        return True
# Difficulty levels: how many steps pass between two events (0 = no events).
# The experiment runner loops over these names.
DIFFICULTY_LEVELS = {
    "none": 0,
    "easy": 30,
    "medium": 20,
    "hard": 10,
}


def events_for_level(level, seed):
    """Create the DynamicEvents object for a named difficulty level."""
    if level not in DIFFICULTY_LEVELS:
        raise ValueError(f"unknown difficulty level: {level}")
    return DynamicEvents(seed, DIFFICULTY_LEVELS[level])
