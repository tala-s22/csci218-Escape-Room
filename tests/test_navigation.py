import random
from navigation import astar, bfs, manhattan
from environment import World


class GridWorld:

    def __init__(self, rows):
        self.rows = rows
        self.blocked = set()

    def is_free(self, cell):
        r = cell[0]
        c = cell[1]
        if r < 0 or r >= len(self.rows) or c < 0 or c >= len(self.rows[0]):
            return False
        if self.rows[r][c] == '#':
            return False
        return cell not in self.blocked

    def neighbors(self, cell):
        r = cell[0]
        c = cell[1]
        result = []
        for nxt in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if self.is_free(nxt):
                result.append(nxt)
        return result


def check_path(world, path, start, goal, cost):
    assert path[0] == start
    assert path[len(path) - 1] == goal
    assert len(path) - 1 == cost
    for i in range(len(path) - 1):
        assert manhattan(path[i], path[i + 1]) == 1
        assert world.is_free(path[i + 1])


def test_start_equals_goal():
    world = GridWorld(['...', '...', '...'])
    path, stats = astar(world, (1, 1), (1, 1))
    assert path == [(1, 1)]
    assert stats == {'nodes_expanded': 0, 'path_cost': 0}


def test_no_route():
    world = GridWorld(['..#..',
                       '..#..',
                       '..#..'])
    path, stats = astar(world, (0, 0), (0, 4))
    assert path == None
    assert stats['path_cost'] == None
    assert stats['nodes_expanded'] == 6


def test_goal_surrounded_by_walls():
    world = GridWorld(['.....',
                       '..#..',
                       '.#.#.',
                       '..#..'])
    path, stats = astar(world, (0, 0), (2, 2))
    assert path == None


def test_goal_blocked_during_run():
    world = GridWorld(['.....'])
    world.blocked.add((0, 2))
    path, stats = astar(world, (0, 0), (0, 4))
    assert path == None


test_start_equals_goal()
test_no_route()
test_goal_surrounded_by_walls()
test_goal_blocked_during_run()
print('Edge case tests passed')
