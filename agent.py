
"""Adaptive agent: Finite State Machine with replanning (Member 3)."""

from navigation import astar


class AdaptiveAgent:
    def __init__(self, world):
        self.world = world
        self.position = world.start
        self.has_key = False

        self.state = "FIND_KEY"
        self.path = []

        self.steps = 0
        self.replans = 0
        self.nodes_expanded = 0

    def plan_path(self):
        """Use A* to find a path to the current goal."""
        if self.has_key:
            goal = self.world.door
        else:
            goal = self.world.key

        path, stats = astar(self.world, self.position, goal)
        self.nodes_expanded += stats["nodes_expanded"]

        if path is None:
            self.state = "FAILED"
            self.path = []
            return False

        self.path = path
        return True

    def step(self):
        """Move one cell per tick and replan if the path is blocked."""
        if self.done():
            return

        # Handle starting directly on the key.
        if self.position == self.world.key and not self.has_key:
            self.has_key = True
            self.state = "GO_TO_DOOR"
            self.path = []

        if self.has_key and self.position == self.world.door:
            self.state = "ESCAPED"
            return

        # Create a path if we don't already have one.
        if not self.path:
            if not self.plan_path():
                return

        # Check whether any remaining path cell is blocked.
        if any(
            not self.world.is_free(cell)
            for cell in self.path[1:]
        ):
            self.state = "REPLAN"
            self.replans += 1

            if not self.plan_path():
                return

            self.state = (
                "GO_TO_DOOR" if self.has_key else "FIND_KEY"
            )

        # Move exactly one cell.
        if len(self.path) > 1:
            self.position = self.path[1]
            self.path.pop(0)
            self.steps += 1

        # Pick up the key.
        if self.position == self.world.key and not self.has_key:
            self.has_key = True
            self.state = "GO_TO_DOOR"
            self.path = []

        # Escape after reaching the door with the key.
        if self.position == self.world.door and self.has_key:
            self.state = "ESCAPED"

    def done(self):
        """Return True when the agent escapes or fails."""
        return self.state in ("ESCAPED", "FAILED")
