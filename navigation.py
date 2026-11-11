"""A* search (Member 2)."""

import heapq
from collections import deque
from itertools import count

STEP_COST = 1  # fixed scope: 4-direction movement, every move costs 1

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(world, start, goal):
    """Return (path, stats). path is None if there is no route.
    stats = {'nodes_expanded': int, 'path_cost': int}"""
    raise NotImplementedError("A1/A2: A* with counters")
