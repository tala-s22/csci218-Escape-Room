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
