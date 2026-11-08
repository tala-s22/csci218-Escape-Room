"""Non-adaptive baseline agent (Member 4)."""


class StaticAgent:
    def __init__(self, world):
        raise NotImplementedError("B1: plan once with astar")

    def step(self):
        raise NotImplementedError("B1: follow the plan, FAILED if blocked")

    def done(self):
        raise NotImplementedError("B1")
