from environment import World
from events import DynamicEvents
from navigation import astar


class FakeWorld:
    def __init__(self):
        self.blocked = set()
        self.start = (0, 0)
        self.key = (0, 9)
        self.door = (9, 9)

    def is_free(self, cell):
        return cell not in self.blocked

    def block(self, cell):
        self.blocked.add(cell)

    def unblock(self, cell):
        self.blocked.discard(cell)


class FakeAgent:
    def __init__(self, route, has_key=False):
        self.position = route[0]
        self.path = list(route[1:])
        self.has_key = has_key


ROUTE = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]


def run_events(seed, every_n_steps, ticks=9):
    world = FakeWorld()
    agent = FakeAgent(ROUTE)
    events = DynamicEvents(seed, every_n_steps, check_route=False)
    history = []
    for _ in range(ticks):
        events.apply(world, agent)
        history.append(set(world.blocked))
    return history


# ---------- tests of the event timing and cell choice (fake world) ----------

def test_no_events_when_zero():
    history = run_events(seed=1, every_n_steps=0)
    assert all(len(blocked) == 0 for blocked in history)


def test_event_fires_every_n_steps():
    history = run_events(seed=1, every_n_steps=3)
    sizes = [len(blocked) for blocked in history]
    assert sizes == [0, 0, 1, 1, 1, 2, 2, 2, 3]


def test_same_seed_same_events():
    assert run_events(5, 3) == run_events(5, 3)


def test_never_blocks_start_key_door_or_agent():
    world = FakeWorld()
    agent = FakeAgent([(0, 0), (0, 1), (0, 9), (9, 9)])
    events = DynamicEvents(seed=2, every_n_steps=1, check_route=False)
    for _ in range(20):
        events.apply(world, agent)
    assert world.start not in world.blocked
    assert world.key not in world.blocked
    assert world.door not in world.blocked
    assert agent.position not in world.blocked


def test_no_crash_when_nothing_to_block():
    world = FakeWorld()
    agent = FakeAgent([(0, 0)])
    events = DynamicEvents(seed=1, every_n_steps=1, check_route=False)
    assert events.apply(world, agent) is None
    assert world.blocked == set()


# ---------- tests of the "a route always remains" check (real World and astar) ----------

def one_lane_world():
    walls = {(row, col) for row in range(1, 5) for col in range(5)}
    return World(5, walls, (0, 0), (0, 2), (0, 4))


def two_lane_world():
    walls = {(row, col) for row in range(2, 5) for col in range(5)}
    return World(5, walls, (0, 0), (0, 2), (0, 4))


CORRIDOR = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]


def test_skips_event_when_it_would_seal_the_room():
    world = one_lane_world()
    agent = FakeAgent(CORRIDOR)
    events = DynamicEvents(seed=1, every_n_steps=1)
    for _ in range(10):
        assert events.apply(world, agent) is None
    assert world.blocked == set()


def test_blocks_when_another_route_exists():
    world = two_lane_world()
    agent = FakeAgent(CORRIDOR)
    events = DynamicEvents(seed=1, every_n_steps=1)
    for _ in range(5):
        events.apply(world, agent)
    assert world.blocked == {(0, 1), (0, 3)}
    assert astar(world, world.start, world.key)[0] is not None
    assert astar(world, world.key, world.door)[0] is not None


def test_route_always_remains_on_random_worlds():
    for seed in range(50):
        world = World.from_seed(seed)
        path, _ = astar(world, world.start, world.key)
        agent = FakeAgent(path)
        events = DynamicEvents(seed, every_n_steps=1)
        for _ in range(30):
            events.apply(world, agent)
            assert astar(world, agent.position, world.key)[0] is not None
            assert astar(world, world.key, world.door)[0] is not None


def test_after_key_only_the_door_route_matters():
    world = two_lane_world()
    agent = FakeAgent([(0, 2), (0, 3), (0, 4)], has_key=True)
    events = DynamicEvents(seed=1, every_n_steps=1)
    events.apply(world, agent)
    assert astar(world, agent.position, world.door)[0] is not None


if __name__ == "__main__":
    test_no_events_when_zero()
    test_event_fires_every_n_steps()
    test_same_seed_same_events()
    test_never_blocks_start_key_door_or_agent()
    test_no_crash_when_nothing_to_block()
    test_skips_event_when_it_would_seal_the_room()
    test_blocks_when_another_route_exists()
    test_route_always_remains_on_random_worlds()
    test_after_key_only_the_door_route_matters()
    print("All events tests passed")
