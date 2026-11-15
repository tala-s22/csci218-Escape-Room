import random

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle

from agent import AdaptiveAgent
from environment import World
from events import events_for_level


def record_episode(agent_class, seed, difficulty, max_ticks):
    """Play one episode and return (world, frames). Each frame is a snapshot
    of everything that changes from tick to tick."""
    world = World.from_seed(seed)
    agent = agent_class(world)
    events = events_for_level(difficulty, seed)

    def snapshot():
        return {
            "blocked": set(world.blocked),
            "path": list(agent.path),
            "position": agent.position,
            "has_key": agent.has_key,
            "state": agent.state,
            "steps": agent.steps,
            "replans": agent.replans,
        }

    frames = [snapshot()]
    for _ in range(max_ticks):
        if agent.done():
            break
        events.apply(world, agent)
        agent.step()
        frames.append(snapshot())

    return world, frames


def animate_demo(agent_class=AdaptiveAgent, seed=None, difficulty="medium",
                 max_ticks=500, interval=400):
    """Show an agent solving a random room, one tick per frame."""
    if seed is None:
        seed = random.randint(0, 1_000_000)

    world, frames = record_episode(agent_class, seed, difficulty, max_ticks)
    size = world.size
    fig, ax = plt.subplots(figsize=(8, 8))

    def draw(index):
        frame = frames[index]
        ax.clear()
        ax.set_xlim(0, size)
        ax.set_ylim(size, 0)            # row 0 at the top
        ax.set_aspect("equal")
        ax.set_xticks(range(size + 1))
        ax.set_yticks(range(size + 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(True, color="lightgray")

        # cells: walls, blocked cells, planned path (drawn in that order)
        for cells, color, alpha in [(world.walls, "black", 1.0),
                                    (frame["blocked"], "red", 1.0),
                                    (frame["path"], "lightblue", 0.7)]:
            for row, col in cells:
                ax.add_patch(Rectangle((col, row), 1, 1, facecolor=color, alpha=alpha))

        # start, key, door letters
        for (row, col), letter, color in [(world.start, "S", "blue"),
                                          (world.key, "K", "orange"),
                                          (world.door, "D", "green")]:
            ax.text(col + 0.5, row + 0.5, letter, ha="center", va="center",
                    fontsize=14, fontweight="bold", color=color)

        # the agent
        row, col = frame["position"]
        ax.add_patch(Circle((col + 0.5, row + 0.5), 0.3, color="blue"))

        ax.set_title(
            f"{agent_class.__name__} | seed {seed} | difficulty: {difficulty}\n"
            f"State: {frame['state']} | Steps: {frame['steps']} | "
            f"Replans: {frame['replans']} | Key: {'Yes' if frame['has_key'] else 'No'}"
        )
        ax.set_xlabel("black = wall   red = blocked during run   light blue = planned path")

    animation = FuncAnimation(fig, draw, frames=len(frames),
                              interval=interval, repeat=False)
    plt.tight_layout()
    plt.show()
    return animation        # keep a reference so the animation is not garbage collected


if __name__ == "__main__":
    animate_demo()
