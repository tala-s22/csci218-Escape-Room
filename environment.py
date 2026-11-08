"""Grid world and layout generator (Member 1)."""


class World:
    @staticmethod
    def from_seed(seed, size=15, wall_density=0.2):
        raise NotImplementedError("W2: layout generator with solvability check")

    def is_free(self, cell):
        raise NotImplementedError("W1: inside grid, not a wall, not blocked")

    def neighbors(self, cell):
        raise NotImplementedError("W1: free cells up, down, left, right")

    def block(self, cell):
        raise NotImplementedError("W1: used by dynamic events")

    def unblock(self, cell):
        raise NotImplementedError("W1")

    def copy(self):
        raise NotImplementedError("W1: identical layout for the baseline run")
