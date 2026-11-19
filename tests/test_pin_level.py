from statistics import mean

from navigation import astar
from pin_extension import PIN_DIGITS
from pin_level import (PinAdaptiveAgent, PinStaticAgent, PinWorld, new_pin_game,
                       play_pin_level)

SEEDS = range(50)


def test_key_is_hidden_until_revealed():
    world = PinWorld.from_seed(0)
    assert world.key is None
    assert world.hidden_key is not None
    world.reveal_key()
    assert world.key == world.hidden_key


def test_pin_cell_is_a_different_cell_from_start_key_and_door():
    for seed in SEEDS:
        world = PinWorld.from_seed(seed)
        cells = {world.start, world.hidden_key, world.door, world.pin_cell}
        assert len(cells) == 4
        assert world.is_free(world.pin_cell)


def test_everything_is_reachable_from_the_start():
    for seed in SEEDS:
        world = PinWorld.from_seed(seed)
        for goal in [world.pin_cell, world.hidden_key, world.door]:
            path, _ = astar(world, world.start, goal)
            assert path is not None


def test_same_seed_gives_the_same_world():
    first = PinWorld.from_seed(7)
    second = PinWorld.from_seed(7)
    assert (first.walls, first.start, first.hidden_key, first.door, first.pin_cell,
            first.lock.secret) == (second.walls, second.start, second.hidden_key,
                                   second.door, second.pin_cell, second.lock.secret)


def test_secret_is_a_pin_with_the_right_number_of_digits():
    secrets = set()
    for seed in SEEDS:
        secret = PinWorld.from_seed(seed).lock.secret
        assert len(secret) == PIN_DIGITS and secret.isdigit()
        secrets.add(secret)
    assert len(secrets) > 10        # not the same PIN every time


def test_copy_keeps_the_pin_world():
    world = PinWorld.from_seed(3)
    copy = world.copy()
    assert isinstance(copy, PinWorld)
    assert copy.pin_cell == world.pin_cell and copy.lock.secret == world.lock.secret
    assert copy.key is None


def test_adaptive_agent_clears_the_pin_level():
    for seed in SEEDS:
        result = play_pin_level(PinAdaptiveAgent, seed)
        assert result["success"] is True


def test_adaptive_agent_cracks_the_pin_with_few_guesses():
    guesses = [play_pin_level(PinAdaptiveAgent, seed)["guesses"] for seed in SEEDS]
    assert mean(guesses) < 15
    assert max(guesses) < 50


def test_adaptive_agent_goes_through_the_states_in_order():
    for seed in range(10):
        states = []

        def record(world, agent):
            if not states or states[-1] != agent.state:
                states.append(agent.state)

        play_pin_level(PinAdaptiveAgent, seed, on_tick=record)
        assert states == ["GO_TO_PIN", "CRACK_PIN", "FIND_KEY", "GO_TO_DOOR", "ESCAPED"]


def test_key_appears_exactly_when_the_lock_opens():
    for agent_class in [PinAdaptiveAgent, PinStaticAgent]:
        seen = []

        def record(world, agent):
            seen.append((world.key is not None) == world.lock.unlocked)

        play_pin_level(agent_class, 4, on_tick=record)
        assert all(seen)


def test_adaptive_ticks_are_steps_plus_guesses():
    for seed in range(10):
        result = play_pin_level(PinAdaptiveAgent, seed)
        assert result["ticks"] == result["steps"] + result["guesses"]


def test_baseline_clears_the_pin_level_only_if_the_key_is_on_its_route():
    for seed in SEEDS:
        world = PinWorld.from_seed(seed)
        route_from_pin, _ = astar(world, world.pin_cell, world.door)
        key_on_route = world.hidden_key in route_from_pin[1:]
        result = play_pin_level(PinStaticAgent, seed)
        assert result["success"] == key_on_route
        assert result["replans"] == 0


def test_baseline_is_lucky_only_rarely():
    wins = sum(play_pin_level(PinStaticAgent, seed)["success"] for seed in range(200))
    assert 0 < wins < 40            


def test_baseline_guesses_in_order_so_guesses_equal_the_secret_plus_one():
    for seed in range(10):
        world = PinWorld.from_seed(seed)
        result = play_pin_level(PinStaticAgent, seed)
        assert result["guesses"] == int(world.lock.secret) + 1


def test_baseline_opens_the_lock_but_fails_at_the_door_without_the_key():
    for seed in SEEDS:
        world, agent = new_pin_game(PinStaticAgent, seed)
        route_from_pin, _ = astar(world, world.pin_cell, world.door)
        if world.hidden_key in route_from_pin[1:]:
            continue                
        while not agent.done():
            agent.step()
        assert world.lock.unlocked
        assert agent.has_key is False
        assert agent.state == "FAILED"
        assert agent.position == world.door
        return
    assert False, "no unlucky room found"


def test_baseline_picks_up_the_key_when_it_lies_on_its_route():
    for seed in range(200):
        world, agent = new_pin_game(PinStaticAgent, seed)
        route_from_pin, _ = astar(world, world.pin_cell, world.door)
        if world.hidden_key not in route_from_pin[1:]:
            continue
        while not agent.done():
            agent.step()
        assert agent.has_key is True
        assert agent.state == "ESCAPED"
        return
    assert False, "no lucky room found in 200 seeds"


def test_no_cells_are_blocked_in_this_level():
    for agent_class in [PinAdaptiveAgent, PinStaticAgent]:
        world, agent = new_pin_game(agent_class, 5)
        while not agent.done():
            agent.step()
        assert world.blocked == set()


def test_adaptive_agent_still_replans_when_its_path_is_blocked():
    for seed in range(50):
        world, agent = new_pin_game(PinAdaptiveAgent, seed)
        agent.step()                        # makes the first plan and moves one cell
        for cell in agent.path[2:-1]:       # a cell ahead on the way to P, not P itself
            world.block(cell)
            path, _ = astar(world, agent.position, world.pin_cell)
            if path is not None:
                break
            world.unblock(cell)
        else:
            continue                        # no cell could be blocked safely in this room
        while not agent.done():
            agent.step()
        assert agent.replans >= 1
        assert agent.state == "ESCAPED"
        return
    assert False, "no room found where a cell could be blocked"


def test_same_seed_gives_the_same_result():
    for agent_class in [PinAdaptiveAgent, PinStaticAgent]:
        assert play_pin_level(agent_class, 11) == play_pin_level(agent_class, 11)


if __name__ == "__main__":
    test_key_is_hidden_until_revealed()
    test_pin_cell_is_a_different_cell_from_start_key_and_door()
    test_everything_is_reachable_from_the_start()
    test_same_seed_gives_the_same_world()
    test_secret_is_a_pin_with_the_right_number_of_digits()
    test_copy_keeps_the_pin_world()
    test_adaptive_agent_clears_the_pin_level()
    test_adaptive_agent_cracks_the_pin_with_few_guesses()
    test_adaptive_agent_goes_through_the_states_in_order()
    test_key_appears_exactly_when_the_lock_opens()
    test_adaptive_ticks_are_steps_plus_guesses()
    test_baseline_clears_the_pin_level_only_if_the_key_is_on_its_route()
    test_baseline_is_lucky_only_rarely()
    test_baseline_guesses_in_order_so_guesses_equal_the_secret_plus_one()
    test_baseline_opens_the_lock_but_fails_at_the_door_without_the_key()
    test_baseline_picks_up_the_key_when_it_lies_on_its_route()
    test_no_cells_are_blocked_in_this_level()
    test_adaptive_agent_still_replans_when_its_path_is_blocked()
    test_same_seed_gives_the_same_result()
    print("All PIN level tests passed")
