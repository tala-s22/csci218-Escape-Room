from events import DynamicEvents


class FakeWorld:
    def __init__(self):
        self.blocked = set()
        self.key = (0, 9)
        self.door = (9, 9)

    def is_free(self, cell):
        return cell not in self.blocked

    def block(self, cell):
        self.blocked.add(cell)

    def unblock(self, cell):
        self.blocked.discard(cell)


class FakeAgent:
    def __init__(self, route):
        self.position = route[0]
        self.path = list(route[1:])


ROUTE = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]


def run_events(seed, every_n_steps, ticks=9):
    world = FakeWorld()
    agent = FakeAgent(ROUTE)
    events = DynamicEvents(seed, every_n_steps)
    history = []
    for _ in range(ticks):
        events.apply(world, agent)
        history.append(set(world.blocked))
    return history


def test_no_events_when_zero():
    history = run_events(seed=1, every_n_steps=0)
    assert all(len(blocked) == 0 for blocked in history)


def test_event_fires_every_n_steps():
    history = run_events(seed=1, every_n_steps=3)
    sizes = [len(blocked) for blocked in history]
    assert sizes == [0, 0, 1, 1, 1, 2, 2, 2, 3]


def test_same_seed_same_events():
    assert run_events(5, 3) == run_events(5, 3)


def test_never_blocks_key_door_or_agent():
    world = FakeWorld()
    agent = FakeAgent([(0, 0), (0, 1), (0, 9), (9, 9)])
    events = DynamicEvents(seed=2, every_n_steps=1)
    for _ in range(20):
        events.apply(world, agent)
    assert world.key not in world.blocked
    assert world.door not in world.blocked
    assert agent.position not in world.blocked


def test_no_crash_when_nothing_to_block():
    world = FakeWorld()
    agent = FakeAgent([(0, 0)])
    events = DynamicEvents(seed=1, every_n_steps=1)
    assert events.apply(world, agent) is None
    assert world.blocked == set()


if __name__ == "__main__":
    test_no_events_when_zero()
    test_event_fires_every_n_steps()
    test_same_seed_same_events()
    test_never_blocks_key_door_or_agent()
    test_no_crash_when_nothing_to_block()
    print("All events tests passed")
