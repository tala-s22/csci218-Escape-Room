from environment import World
from baseline import StaticAgent
from events import DynamicEvents
from navigation import astar


def two_lane_world():
    walls = {(row, col) for row in range(2, 5) for col in range(5)}
    return World(5, walls, (0, 0), (0, 2), (0, 4))


def run_to_end(agent, world, events=None, max_steps=500):
    for _ in range(max_steps):
        if agent.done():
            break
        if events is not None:
            events.apply(world, agent)
        agent.step()
    return agent


def test_escapes_when_nothing_changes():
    world = World.from_seed(1)
    agent = StaticAgent(world)
    run_to_end(agent, world)
    assert agent.state == "ESCAPED"
    assert agent.has_key
    assert agent.position == world.door
    assert agent.replans == 0


def test_steps_match_the_planned_cost():
    world = World.from_seed(2)
    to_key, _ = astar(world, world.start, world.key)
    to_door, _ = astar(world, world.key, world.door)
    expected = (len(to_key) - 1) + (len(to_door) - 1)
    agent = StaticAgent(world)
    run_to_end(agent, world)
    assert agent.steps == expected


def test_path_is_the_cells_still_to_walk():
    world = World.from_seed(3)
    agent = StaticAgent(world)
    assert agent.path[0] != agent.position
    assert agent.path[-1] == world.door


def test_does_not_walk_through_the_door_without_the_key():
    world = World.from_seed(4)
    agent = StaticAgent(world)
    while not agent.done():
        agent.step()
        if agent.position == world.door and not agent.has_key:
            assert agent.state == "FIND_KEY"


def test_fails_when_next_cell_is_blocked_even_if_a_detour_exists():
    world = two_lane_world()
    agent = StaticAgent(world)
    world.block(agent.path[0])
    agent.step()
    assert agent.state == "FAILED"
    assert agent.steps == 0
    assert agent.position == world.start
    assert astar(world, world.start, world.key)[0] is not None


def test_fails_part_way_through():
    world = two_lane_world()
    agent = StaticAgent(world)
    agent.step()
    agent.step()                      # now standing on the key
    assert agent.has_key
    world.block(agent.path[0])        # block the next cell on the way to the door
    agent.step()
    assert agent.state == "FAILED"
    assert agent.steps == 2


def test_fails_at_start_when_there_is_no_route():
    world = World.from_seed(5)
    for cell in list(world.neighbors(world.key)):
        world.block(cell)
    agent = StaticAgent(world)
    assert agent.state == "FAILED"
    assert agent.done()


def test_always_finishes_with_events():
    for seed in range(30):
        world = World.from_seed(seed)
        agent = StaticAgent(world)
        events = DynamicEvents(seed, every_n_steps=5)
        run_to_end(agent, world, events, max_steps=200)
        assert agent.done()
        assert agent.state in ("ESCAPED", "FAILED")


if __name__ == "__main__":
    test_escapes_when_nothing_changes()
    test_steps_match_the_planned_cost()
    test_path_is_the_cells_still_to_walk()
    test_does_not_walk_through_the_door_without_the_key()
    test_fails_when_next_cell_is_blocked_even_if_a_detour_exists()
    test_fails_part_way_through()
    test_fails_at_start_when_there_is_no_route()
    test_always_finishes_with_events()
    print("All baseline tests passed")
