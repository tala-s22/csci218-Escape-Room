import random
from navigation import astar, bfs
from environment import World


class GridWorld:

    def __init__(self, rows):
        self.rows = rows
        self.blocked = set()

    def neighbors(self, cell):
        r = cell[0]
        c = cell[1]
        result = []
        for nxt in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if 0 <= nxt[0] < len(self.rows) and 0 <= nxt[1] < len(self.rows[0]):
                if self.rows[nxt[0]][nxt[1]] == '.' and nxt not in self.blocked:
                    result.append(nxt)
        return result


def test_start_equals_goal():
    world = GridWorld(['...'])
    path, stats = astar(world, (0, 1), (0, 1))
    assert path == [(0, 1)]
    assert stats['path_cost'] == 0


def test_no_route():
    world = GridWorld(['..#..'])
    path, stats = astar(world, (0, 0), (0, 4))
    assert path == None
    assert stats['path_cost'] == None


def test_straight_corridor():
    world = GridWorld(['.....'])
    path, stats = astar(world, (0, 0), (0, 4))
    assert path == [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
    assert stats['path_cost'] == 4
    assert stats['nodes_expanded'] == 4


def test_reroutes_when_blocked():
    world = GridWorld(['.....',
                       '.###.',
                       '.....'])
    path, stats = astar(world, (0, 0), (0, 4))
    assert stats['path_cost'] == 4
    world.blocked.add((0, 2))
    path, stats = astar(world, (0, 0), (0, 4))
    assert stats['path_cost'] == 8
    assert (0, 2) not in path


test_start_equals_goal()
test_no_route()
test_straight_corridor()
test_reroutes_when_blocked()
print('Small grid tests passed')



def test_100_random_worlds():
    random.seed(218)
    astar_total = 0
    bfs_total = 0
    for i in range(100):
        rows = []
        for r in range(12):
            line = ''
            for c in range(12):
                if random.random() < 0.3:
                    line = line + '#'
                else:
                    line = line + '.'
            rows.append(line)
        world = GridWorld(rows)
        start = (random.randint(0, 11), random.randint(0, 11))
        goal = (random.randint(0, 11), random.randint(0, 11))
        a_path, a_stats = astar(world, start, goal)
        b_path, b_stats = bfs(world, start, goal)
        assert a_stats['path_cost'] == b_stats['path_cost']
        astar_total = astar_total + a_stats['nodes_expanded']
        bfs_total = bfs_total + b_stats['nodes_expanded']
    assert astar_total <= bfs_total
    print('A* explored', astar_total, 'cells, BFS explored', bfs_total)


def test_real_world():
    for seed in range(100):
        world = World.from_seed(seed)
        a_path, a_stats = astar(world, world.start, world.key)
        b_path, b_stats = bfs(world, world.start, world.key)
        assert a_path != None
        assert a_stats['path_cost'] == b_stats['path_cost']


test_100_random_worlds()
test_real_world()
print('A* vs BFS tests passed')
