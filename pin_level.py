"""Level 5: the PIN level."""

import random
from statistics import mean

from agent import AdaptiveAgent
from environment import World
from navigation import astar
from pin_extension import PIN_DIGITS, BruteForceCracker, PinCracker, PinLock

MAX_PIN_TICKS = 5000    # brute force can need up to 1000 guesses, so more than the 500 of the other levels


class PinWorld(World):
    """A normal room plus a PIN lock on cell P. world.key is None (hidden) until the lock opens."""

    def __init__(self, size, walls, start, key, door, pin_cell, secret):
        super().__init__(size, walls, start, None, door)   # None = the agent cannot see the key yet
        self.hidden_key = key
        self.pin_cell = pin_cell
        self.lock = PinLock(secret)

    @staticmethod
    def from_seed(seed, size=15, wall_density=0.2):
        room = World.from_seed(seed, size, wall_density)   # a solvable room: start, key and door are connected
        rng = random.Random(f"pin-world-{seed}")           # a separate random stream for P and the secret

        # Every cell the agent can walk to from the start. The key and the door are in this
        # group, so a P chosen from it keeps the whole level solvable.
        reachable = {room.start}
        to_visit = [room.start]
        while to_visit:
            cell = to_visit.pop()
            for neighbour in room.neighbors(cell):
                if neighbour not in reachable:
                    reachable.add(neighbour)
                    to_visit.append(neighbour)

        candidates = sorted(reachable - {room.start, room.key, room.door})
        pin_cell = rng.choice(candidates)
        secret = str(rng.randrange(10 ** PIN_DIGITS)).zfill(PIN_DIGITS)
        return PinWorld(room.size, room.walls, room.start, room.key, room.door, pin_cell, secret)

    def reveal_key(self):
        """Called when the lock opens: the key appears."""
        self.key = self.hidden_key

    def copy(self):
        new_world = PinWorld(self.size, set(self.walls), self.start, self.hidden_key,
                             self.door, self.pin_cell, self.lock.secret)
        new_world.blocked = set(self.blocked)
        new_world.key = self.key
        return new_world


class PinAdaptiveAgent(AdaptiveAgent):
    """The normal adaptive agent (A*, replans when its path is blocked) with two extra states:
    GO_TO_PIN and CRACK_PIN. The walking and replanning code is inherited from AdaptiveAgent."""

    def __init__(self, world, cracker=None):
        super().__init__(world)
        self.state = "GO_TO_PIN"
        self.cracker = cracker if cracker is not None else PinCracker()
        self.pin_cracked = False
        self.last_guess = None
        self.last_feedback = None

    @property
    def guesses(self):
        return self.cracker.guesses

    def plan_path(self):
        """A* to the current goal: P first, then the key, then the door."""
        if not self.pin_cracked:
            goal = self.world.pin_cell
        elif not self.has_key:
            goal = self.world.key
        else:
            goal = self.world.door

        path, stats = astar(self.world, self.position, goal)
        self.nodes_expanded += stats["nodes_expanded"]

        if path is None:
            self.state = "FAILED"
            self.path = []
            return False

        self.path = path
        return True

    def step(self):
        """One tick: either one move or one PIN guess."""
        if self.done():
            return

        if self.state == "REPLAN":      # REPLAN lasts one tick, then back to what we were doing
            self.state = self._walking_state()

        if self.state == "CRACK_PIN":
            self._guess_once()
            return

        super().step()                  # walk one cell (replans if the path is blocked)

        if not self.pin_cracked and not self.done() and self.position == self.world.pin_cell:
            self.state = "CRACK_PIN"
            self.path = []

    def _walking_state(self):
        if not self.pin_cracked:
            return "GO_TO_PIN"
        if not self.has_key:
            return "FIND_KEY"
        return "GO_TO_DOOR"

    def _guess_once(self):
        guess = self.cracker.next_guess()
        feedback = self.world.lock.try_code(guess)
        self.cracker.learn(feedback)
        self.last_guess = guess
        self.last_feedback = feedback

        if self.world.lock.unlocked:
            self.world.reveal_key()     # the key appears, the agent can now plan to it
            self.pin_cracked = True
            self.state = "FIND_KEY"
            self.path = []


class PinStaticAgent:
    """Baseline: plans start -> P -> door once and follows it. It guesses the PIN in order
    (000, 001, ...) and ignores the lock's feedback. It never learns where the key appears
    and never goes to fetch it. It picks the key up only if the key (visible once the lock
    is open) happens to be on a cell of its fixed route. Reaching the door without the key
    is a failure."""

    def __init__(self, world, cracker=None):
        self.world = world
        self.position = world.start
        self.has_key = False            # only becomes True if the key lies on its route
        self.steps = 0
        self.replans = 0                # always 0, this agent never replans
        self.state = "GO_TO_PIN"
        self.path = []
        self.cracker = cracker if cracker is not None else BruteForceCracker()
        self.pin_cracked = False
        self.last_guess = None
        self.last_feedback = None

        to_pin, pin_stats = astar(world, world.start, world.pin_cell)
        to_door, door_stats = astar(world, world.pin_cell, world.door)
        self.nodes_expanded = pin_stats["nodes_expanded"] + door_stats["nodes_expanded"]

        if to_pin is None or to_door is None:
            self.state = "FAILED"
            return

        full_plan = to_pin + to_door[1:]    # to_door[1:] drops P, already the last cell of to_pin
        self.path = full_plan[1:]           # drop the start cell, we are standing on it

    @property
    def guesses(self):
        return self.cracker.guesses

    def step(self):
        """One tick: one PIN guess, or one move along the plan, or fail."""
        if self.done():
            return

        if self.state == "CRACK_PIN":
            self._guess_once()
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

        if not self.pin_cracked:
            if self.position == self.world.pin_cell:
                self.state = "CRACK_PIN"
            return

        # The lock is open, so the key is visible: lucky if we walk over it.
        if self.position == self.world.key:
            self.has_key = True
        if self.position == self.world.door:
            self.state = "ESCAPED" if self.has_key else "FAILED"    # no key = locked door

    def done(self):
        return self.state in ("ESCAPED", "FAILED")

    def _guess_once(self):
        guess = self.cracker.next_guess()
        feedback = self.world.lock.try_code(guess)
        self.cracker.learn(feedback)
        self.last_guess = guess
        self.last_feedback = feedback

        if self.world.lock.unlocked:
            self.world.reveal_key()     # the key appears, but this agent does not look for it
            self.pin_cracked = True
            self.state = "GO_TO_DOOR"


def new_pin_game(agent_class, seed):
    """A fresh PIN room and an agent standing in it."""
    world = PinWorld.from_seed(seed)
    return world, agent_class(world)


def play_pin_level(agent_class, seed, max_ticks=MAX_PIN_TICKS, on_tick=None):
    """Play Level 5 once. Returns the statistics, like experiments.run_trial.
    on_tick(world, agent), if given, is called before the first tick and after every tick
    (the demo uses it to record frames)."""
    world, agent = new_pin_game(agent_class, seed)
    ticks = 0

    if on_tick is not None:
        on_tick(world, agent)

    while ticks < max_ticks and not agent.done():
        agent.step()
        ticks += 1
        if on_tick is not None:
            on_tick(world, agent)

    return {
        "success": agent.state == "ESCAPED",
        "steps": agent.steps,
        "nodes_expanded": agent.nodes_expanded,
        "replans": agent.replans,
        "guesses": agent.guesses,
        "ticks": ticks,
    }


if __name__ == "__main__":
    for name, agent_class in {"Adaptive": PinAdaptiveAgent, "Baseline": PinStaticAgent}.items():
        results = [play_pin_level(agent_class, seed) for seed in range(100)]
        escaped = sum(1 for result in results if result["success"])
        print(f"{name}: escaped {escaped}/100, "
              f"mean steps {mean(r['steps'] for r in results):.1f}, "
              f"mean PIN guesses {mean(r['guesses'] for r in results):.1f}, "
              f"max PIN guesses {max(r['guesses'] for r in results)}")
