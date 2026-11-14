"""Non-adaptive baseline agent (Member 4)."""

from navigation import astar


class StaticAgent:
    """Plans the whole route once (start -> key -> door) and then follows it
    blindly. It never replans: if the next cell is blocked, it gives up."""

    def __init__(self, world):
        self.world = world
        self.position = world.start
        self.has_key = False
        self.steps = 0
        self.replans = 0          # always 0, this agent never replans
        self.state = "FIND_KEY"
        self.path = []            # cells still to walk (not including the current cell)

        to_key, key_stats = astar(world, world.start, world.key)
        to_door, door_stats = astar(world, world.key, world.door)
        self.nodes_expanded = key_stats["nodes_expanded"] + door_stats["nodes_expanded"]

        if to_key is None or to_door is None:
            self.state = "FAILED"
            return

        full_plan = to_key + to_door[1:]   # to_door[1:] drops the key cell, already in to_key
        self.path = full_plan[1:]          # drop the start cell, we are standing on it
        self._update_state()

    def step(self):
        """Move one cell along the plan, or fail if the way is blocked."""
        if self.done():
            return

        if not self.path:
            self.state = "FAILED"
            return

        next_cell = self.path[0]
        if not self.world.is_free(next_cell):
            self.state = "FAILED"
            return

        self.path.pop(0)
        self.position = next_cell
        self.steps += 1
        self._update_state()

    def done(self):
        return self.state in ("ESCAPED", "FAILED")

    def _update_state(self):
        if self.position == self.world.key:
            self.has_key = True
        if self.has_key:
            self.state = "GO_TO_DOOR"
        if self.has_key and self.position == self.world.door:
            self.state = "ESCAPED"
