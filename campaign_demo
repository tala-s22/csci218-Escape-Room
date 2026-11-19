"""Animated campaign demo: play Level 1, 2, 3, ... 5 in one window.

    python campaign_demo.py                  adaptive agent, random campaign
    python campaign_demo.py baseline         baseline agent
    python campaign_demo.py baseline --seed 0
    python campaign_demo.py baseline --start-level 5    watch only the PIN level
    python campaign_demo.py --official       use the same event intervals as the experiments
"""

import argparse
import random

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle

from agent import AdaptiveAgent
from baseline import StaticAgent
from campaign import LEVELS, PIN_AGENTS, PIN_LEVEL, level_seed
from environment import World
from events import DIFFICULTY_LEVELS, DynamicEvents
from pin_extension import PIN_DIGITS
from pin_level import MAX_PIN_TICKS, play_pin_level

HOLD_FRAMES = 3         # how many frames the "LEVEL CLEARED / FAILED" message stays on screen
SHOW_FIRST_GUESSES = 15 # while cracking the PIN, every guess is a frame up to this many guesses ...
GUESS_SKIP = 50         # ... after that only every 50th guess (brute force needs hundreds)

# Steps between two events in the demo. The experiments use DIFFICULTY_LEVELS (30, 20, 10),
# but the rooms are small, so there events hardly ever show up. The demo uses shorter
# intervals so that the replanning can actually be seen. Level 1 stays event-free.
DEMO_INTERVALS = {"none": 0, "easy": 10, "medium": 7, "hard": 5}

AGENT_NAMES = {AdaptiveAgent: "Adaptive agent", StaticAgent: "Baseline agent"}


def record_level(agent_class, seed, interval, max_ticks=500):
    """Play one event room and return (world, frames). Each frame is a snapshot of
    everything that changes from tick to tick. Same loop as experiments.run_trial."""
    world = World.from_seed(seed)
    agent = agent_class(world)
    events = DynamicEvents(seed, interval)

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


def thin_guess_frames(frames):
    """Keep every frame except most of the PIN guesses after the first few: a brute-force
    agent makes hundreds of guesses and the animation would take minutes."""
    return [
        frame for frame in frames
        if frame["state"] != "CRACK_PIN"
        or frame["guesses"] <= SHOW_FIRST_GUESSES
        or frame["guesses"] % GUESS_SKIP == 0
    ]


def record_pin_level(agent_class, seed):
    """Play Level 5 (the PIN level) and return (world, frames)."""
    frames = []
    worlds = []

    def snapshot(world, agent):
        if not worlds:
            worlds.append(world)
        frames.append({
            "blocked": set(world.blocked),
            "path": list(agent.path),
            "position": agent.position,
            "has_key": agent.has_key,
            "state": agent.state,
            "steps": agent.steps,
            "replans": agent.replans,
            "key_visible": world.key is not None,     # the key only appears when the lock opens
            "guesses": agent.guesses,
            "last_guess": agent.last_guess,
            "last_feedback": agent.last_feedback,
        })

    play_pin_level(PIN_AGENTS[agent_class], seed, MAX_PIN_TICKS, on_tick=snapshot)
    return worlds[0], thin_guess_frames(frames)


def record_campaign(agent_class, campaign_seed, intervals=DIFFICULTY_LEVELS, max_ticks=500,
                    start_level=1):
    """Play the levels in order and keep every frame. Stops at the first failed level.
    With the default intervals this is exactly campaign.run_campaign.
    start_level=5 plays only the PIN level (the earlier levels are skipped)."""
    records = []

    for level in LEVELS:
        if level["number"] < start_level:
            continue

        seed = level_seed(campaign_seed, level["number"])
        if level["difficulty"] == PIN_LEVEL:
            interval = 0
            world, frames = record_pin_level(agent_class, seed)
        else:
            interval = intervals[level["difficulty"]]
            world, frames = record_level(agent_class, seed, interval, max_ticks)

        success = frames[-1]["state"] == "ESCAPED"
        records.append({
            "level": level["number"],
            "start_level": start_level,
            "difficulty": level["difficulty"],
            "interval": interval,
            "seed": seed,
            "world": world,
            "frames": frames,
            "success": success,
        })
        if not success:
            break

    return records


def build_timeline(records):
    """One list of everything to draw: every frame of every level, plus a few
    'hold' frames after each level that carry the outcome message."""
    timeline = []

    for record in records:
        for frame in record["frames"]:
            timeline.append({"record": record, "frame": frame, "message": ""})

        if not record["success"]:
            message = f"LEVEL {record['level']} FAILED - campaign over"
        elif record["level"] == len(LEVELS):
            message = "ALL LEVELS CLEARED"
        else:
            message = f"LEVEL {record['level']} CLEARED"

        for _ in range(HOLD_FRAMES):
            timeline.append({"record": record, "frame": record["frames"][-1],
                             "message": message})

    return timeline


def scoreboard_text(record, finished):
    """One line: the status of every level, e.g. 'L1: cleared   L2: playing   L3: -   ...'."""
    parts = []
    start_level = record.get("start_level", 1)

    for level in LEVELS:
        number = level["number"]
        if number < start_level:
            status = "skipped"
        elif number < record["level"]:
            status = "cleared"
        elif number == record["level"]:
            if not finished:
                status = "playing"
            else:
                status = "cleared" if record["success"] else "FAILED"
        else:
            status = "-"
        parts.append(f"L{number}: {status}")

    return "   ".join(parts)


def make_figure():
    """The figure for the animation. constrained layout re-fits the title and the
    labels on every redraw, so the title and the scoreboard are never cut off."""
    return plt.subplots(figsize=(8, 9), layout="constrained")


def draw_frame(ax, entry, agent_name, campaign_seed):
    """Draw one timeline entry on the given axes."""
    record, frame, message = entry["record"], entry["frame"], entry["message"]
    world = record["world"]
    size = world.size
    is_pin_level = record["difficulty"] == PIN_LEVEL

    ax.clear()
    ax.set_xlim(0, size)
    ax.set_ylim(size, 0)                # row 0 at the top
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

    # start, key, door letters (in the PIN level the key is hidden until the lock opens)
    letters = [(world.start, "S", "blue"), (world.door, "D", "green")]
    if frame.get("key_visible", True):
        letters.append((getattr(world, "hidden_key", world.key), "K", "orange"))
    if is_pin_level:
        unlocked = frame["key_visible"]
        row, col = world.pin_cell
        ax.add_patch(Rectangle((col, row), 1, 1, facecolor="green" if unlocked else "purple",
                               alpha=0.3))
        letters.append((world.pin_cell, "P", "green" if unlocked else "purple"))
    for (row, col), letter, color in letters:
        ax.text(col + 0.5, row + 0.5, letter, ha="center", va="center",
                fontsize=14, fontweight="bold", color=color)

    # the agent
    row, col = frame["position"]
    ax.add_patch(Circle((col + 0.5, row + 0.5), 0.3, color="blue"))

    # the level banner (title) and the scoreboard (below the grid)
    interval = record["interval"]
    if is_pin_level:
        events = "PIN lock, no events"
        detail = f"PIN guesses: {frame['guesses']}"
        if frame["last_guess"] is not None:
            detail += f" | last: {frame['last_guess']} ({frame['last_feedback']} of {PIN_DIGITS} right)"
    else:
        events = f"event every {interval} steps" if interval > 0 else "no events"
        detail = f"Replans: {frame['replans']}"
    ax.set_title(
        f"LEVEL {record['level']} of {len(LEVELS)} ({record['difficulty']}, {events}) | "
        f"{agent_name} | campaign seed {campaign_seed}\n"
        f"State: {frame['state']} | Steps: {frame['steps']} | {detail} | "
        f"Key: {'Yes' if frame['has_key'] else 'No'}",
        fontsize=10,
    )
    legend = "black = wall   red = blocked during run   light blue = planned path"
    if is_pin_level:
        legend += "\nP = PIN lock (the key appears when it opens)"
    label = scoreboard_text(record, finished=bool(message)) + "\n" + legend
    if not is_pin_level and interval != DIFFICULTY_LEVELS[record["difficulty"]]:
        label += "\nDemo: events are more frequent than in the experiments"
    ax.set_xlabel(label)

    # the outcome message in the middle of the room
    if message:
        color = "green" if record["success"] else "red"
        ax.text(size / 2, size / 2, message, ha="center", va="center",
                fontsize=20, fontweight="bold", color=color,
                bbox=dict(facecolor="white", edgecolor=color, alpha=0.9, pad=10))


def animate_campaign(agent_class=AdaptiveAgent, campaign_seed=None, official=False,
                     start_level=1, interval=400, show=True):
    """Show an agent playing the whole campaign, one tick per frame.
    official=True uses the experiment intervals; the default uses the denser demo ones."""
    if campaign_seed is None:
        campaign_seed = random.randint(0, 1_000_000)

    intervals = DIFFICULTY_LEVELS if official else DEMO_INTERVALS
    records = record_campaign(agent_class, campaign_seed, intervals, start_level=start_level)
    timeline = build_timeline(records)
    fig, ax = make_figure()
    agent_name = AGENT_NAMES.get(agent_class, agent_class.__name__)

    def draw(index):
        draw_frame(ax, timeline[index], agent_name, campaign_seed)

    animation = FuncAnimation(fig, draw, frames=len(timeline),
                              interval=interval, repeat=False)
    if show:
        plt.show()
    return animation        # keep a reference so the animation is not garbage collected


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Animated escape-room campaign.")
    parser.add_argument("agent", nargs="?", choices=["adaptive", "baseline"],
                        default="adaptive", help="which agent plays (default: adaptive)")
    parser.add_argument("--seed", type=int, default=None,
                        help="campaign seed (default: random)")
    parser.add_argument("--start-level", type=int, default=1, choices=range(1, len(LEVELS) + 1),
                        metavar="N", help=f"first level to play, 1 to {len(LEVELS)} (default: 1)")
    parser.add_argument("--official", action="store_true",
                        help="use the event intervals of the experiments, not the denser demo ones")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    agent_class = AdaptiveAgent if args.agent == "adaptive" else StaticAgent
    animate_campaign(agent_class, campaign_seed=args.seed, official=args.official,
                     start_level=args.start_level)
