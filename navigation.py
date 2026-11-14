"""A* search (Member 2)."""

import heapq
from collections import deque
from itertools import count

STEP_COST = 1  
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def rebuild_path(came_from, cell):
    path = [cell]
    while cell in came_from:
        cell = came_from[cell]
        path.append(cell)
    path.reverse()
    return path


def astar(world, start, goal):
    open_list = [start]   
    g = {start: 0}        
    came_from = {}        
    closed = set()        
    nodes_expanded = 0

    while len(open_list) > 0:
        best = open_list[0]
        for cell in open_list:
            if g[cell] + manhattan(cell, goal) < g[best] + manhattan(best, goal):
                best = cell
        open_list.remove(best)
        if best == goal:
            return rebuild_path(came_from, best), {'nodes_expanded': nodes_expanded, 'path_cost': g[best]}

        closed.add(best)
        nodes_expanded = nodes_expanded + 1
        for nxt in world.neighbors(best):
            if nxt not in closed and (nxt not in g or g[best] + 1 < g[nxt]):
                g[nxt] = g[best] + 1
                came_from[nxt] = best
                if nxt not in open_list:
                    open_list.append(nxt)

    return None, {'nodes_expanded': nodes_expanded, 'path_cost': None}

def bfs(world, start, goal):
    queue = [start]      
    came_from = {}        
    seen = set()          
    seen.add(start)
    nodes_expanded = 0

    while len(queue) > 0:
        cell = queue.pop(0)   
        if cell == goal:
            path = rebuild_path(came_from, cell)
            return path, {'nodes_expanded': nodes_expanded, 'path_cost': len(path) - 1}

        nodes_expanded = nodes_expanded + 1
        for nxt in world.neighbors(cell):
            if nxt not in seen:
                seen.add(nxt)
                came_from[nxt] = cell
                queue.append(nxt)

    return None, {'nodes_expanded': nodes_expanded, 'path_cost': None}
