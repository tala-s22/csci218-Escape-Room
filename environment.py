"""Grid world and layout generator (Member 1)."""
 
import random
from collections import deque
 
 
class World:
    def __init__(self, size, walls, start, key, door):
        self.size = size
        self.walls = walls      # cells that are always walls
        self.blocked = set()    # cells blocked during the run
        self.start = start
        self.key = key
        self.door = door
 
    @staticmethod
    def from_seed(seed, size=15, wall_density=0.2):
        rng = random.Random(seed)   
 
        while True:  # keep trying until the room is solvable
            walls = set()
            for row in range(1, size - 1):
                for col in range(1, size - 1):
                    if rng.random() < wall_density:
                        walls.add((row, col))
 
            free_cells = []
            for row in range(size):
                for col in range(size):
                    if (row, col) not in walls:
                        free_cells.append((row, col))
 

            start, key, door = rng.sample(free_cells, 3)
 
            world = World(size, walls, start, key, door)
            if world._is_solvable():
                return world
 
    def is_free(self, cell):
        row, col = cell
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False   
        if cell in self.walls or cell in self.blocked:
            return False
        return True
 
    def neighbors(self, cell):
        row, col = cell
        up = (row - 1, col)
        down = (row + 1, col)
        left = (row, col - 1)
        right = (row, col + 1)
 
        result = []
        for next_cell in [up, down, left, right]:
            if self.is_free(next_cell):
                result.append(next_cell)
        return result
 
    def block(self, cell):
        if cell != self.start and cell != self.key and cell != self.door:
            self.blocked.add(cell)
 
    def unblock(self, cell):
        if cell in self.blocked:
            self.blocked.remove(cell)
 
    def copy(self):
        new_world = World(self.size, set(self.walls), self.start, self.key, self.door)
        new_world.blocked = set(self.blocked)
        return new_world
 
    def _is_solvable(self):
        can_get_key = self._can_reach(self.start, self.key)
        can_get_door = self._can_reach(self.key, self.door)
        return can_get_key and can_get_door
 
    def _can_reach(self, start, goal):
        to_visit = deque([start])
        visited = {start}
 
        while len(to_visit) > 0:
            current_cell = to_visit.popleft()
            
            if current_cell == goal:
                return True
                
            for next_cell in self.neighbors(current_cell):
                if next_cell not in visited:
                    visited.add(next_cell)
                    to_visit.append(next_cell)
 
        return False
 
    def render(self):
        # A = start, K = key, D = door, # = wall, X = blocked, . = empty
        for row in range(self.size):
            line = ""
            for col in range(self.size):
                cell = (row, col)
                if cell == self.start:
                    line += "A "
                elif cell == self.key:
                    line += "K "
                elif cell == self.door:
                    line += "D "
                elif cell in self.walls:
                    line += "# "
                elif cell in self.blocked:
                    line += "X "
                else:
                    line += ". "
            print(line)
        print("")
 
 
if __name__ == "__main__":
    world = World.from_seed(42)
    world.render()
    print("Solvable?", world._is_solvable())
