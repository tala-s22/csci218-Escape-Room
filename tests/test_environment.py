from environment import World


def test_from_seed_is_reproducible():
    world1 = World.from_seed(42)
    world2 = World.from_seed(42)
    assert world1.start == world2.start
    assert world1.key == world2.key
    assert world1.door == world2.door


def test_from_seed_is_solvable():
    for seed in range(10):
        world = World.from_seed(seed)
        assert world._is_solvable(), f"World with seed {seed} is not solvable!"


def test_block_and_unblock():
    world = World.from_seed(42)
    free_cell = None
    for r in range(world.size):
        for c in range(world.size):
            cell = (r, c)
            if world.is_free(cell) and cell != world.start and cell != world.key and cell != world.door:
                free_cell = cell
                break
        if free_cell:
            break
    
    
    world.block(free_cell)
    assert not world.is_free(free_cell)
    
    
    world.unblock(free_cell)
    assert world.is_free(free_cell)


def test_copy():
    world1 = World.from_seed(42)
    world2 = world1.copy()
    
    assert world1.start == world2.start
    assert world1.walls == world2.walls
    
    
    world2.block((2, 2))
    assert (2, 2) not in world1.blocked


if __name__ == "__main__":
    test_from_seed_is_reproducible()
    test_from_seed_is_solvable()
    test_block_and_unblock()
    test_copy()
    print("All environment tests passed")
