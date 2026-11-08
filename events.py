"""Dynamic events (Member 4)."""


class DynamicEvents:
    def __init__(self, seed, every_n_steps):
        raise NotImplementedError("E1: 0 means no events")

    def apply(self, world, agent):
        raise NotImplementedError("E1/E2: may block a cell on the agent's path")
