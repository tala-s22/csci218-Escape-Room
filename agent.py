"""Adaptive agent: Finite State Machine with replanning (Member 3)."""


class AdaptiveAgent:
    def __init__(self, world):
        raise NotImplementedError("G1/G2")

    def step(self):
        raise NotImplementedError("G2/G3: one move per tick, replan if blocked")

    def done(self):
        raise NotImplementedError("G2: True when ESCAPED or FAILED")
