from environment import World
from baseline import StaticAgent
from events import DIFFICULTY_LEVELS, events_for_level
from navigation import astar


class FakeAgent:
    def __init__(self, route, has_key=False):
        self.position = route[0]
        self.path = list(route[1:])
        self.has_key = has_key


def test_levels_get_harder():
    assert DIFFICULTY_LEVELS["none"] == 0
    gaps = [DIFFICULTY_LEVELS[name] for name in ("easy", "medium", "hard")]
    assert gaps == sorted(gaps, reverse=True)      # a shorter gap means harder
    assert all(gap > 0 for gap in gaps)


def count_events(level, ticks=60):
    world = World.from_seed(1)
    path, _ = astar(world, world.start, world.door)
    agent = FakeAgent(path, has_key=True)
    events = events_for_level(level, seed=1)
    fired = 0
    for _ in range(ticks):
        if events.apply(world, agent) is not None:
            fired += 1
    return fired


def test_harder_levels_fire_more_events():
    assert count_events("none") == 0
    assert count_events("hard") > count_events("easy") > 0


def test_unknown_level_raises():
    try:
        events_for_level("impossible", seed=1)
    except ValueError:
        return
    raise AssertionError("expected ValueError for an unknown level")


def baseline_success_rate(level, rooms=100):
    escaped = 0
    for seed in range(rooms):
        world = World.from_seed(seed)
        agent = StaticAgent(world)
        events = events_for_level(level, seed)
        for _ in range(500):
            if agent.done():
                break
            events.apply(world, agent)
            agent.step()
        if agent.state == "ESCAPED":
            escaped += 1
    return escaped


def test_harder_levels_hurt_the_baseline_more():
    rates = [baseline_success_rate(name) for name in ("none", "easy", "medium", "hard")]
    assert rates[0] == 100                        # nothing changes, always escapes
    assert rates == sorted(rates, reverse=True)   # success never rises as it gets harder
    assert rates[-1] < rates[0]


if __name__ == "__main__":
    test_levels_get_harder()
    test_harder_levels_fire_more_events()
    test_unknown_level_raises()
    test_harder_levels_hurt_the_baseline_more()
    print("All difficulty tests passed")
