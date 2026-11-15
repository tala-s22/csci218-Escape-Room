import csv
import os
from statistics import mean, stdev

import matplotlib.pyplot as plt

from environment import World
from events import DIFFICULTY_LEVELS, events_for_level

CSV_FIELDS = ["agent", "difficulty", "event_interval", "seed",
              "success", "steps", "nodes_expanded", "replans"]

# (column, y-axis label, file name)
CHARTS = [
    ("success", "Success Rate (%)", "success_rate.png"),
    ("steps", "Mean Steps", "mean_steps.png"),
    ("nodes_expanded", "Mean Nodes Expanded", "mean_nodes_expanded.png"),
]


def run_trial(agent_class, seed, difficulty, max_ticks=500):
    """Run one agent in one room and return its statistics."""
    world = World.from_seed(seed)
    agent = agent_class(world)
    events = events_for_level(difficulty, seed)

    for _ in range(max_ticks):
        if agent.done():
            break
        events.apply(world, agent)
        agent.step()

    return {
        "success": agent.state == "ESCAPED",
        "steps": agent.steps,
        "nodes_expanded": agent.nodes_expanded,
        "replans": agent.replans,
    }


def run_benchmark(adaptive_class, baseline_class, seeds):
    """Both agents, every difficulty level, the same rooms (seeds)."""
    agents = {"Adaptive": adaptive_class, "Baseline": baseline_class}
    rows = []

    for difficulty, interval in DIFFICULTY_LEVELS.items():
        for name, agent_class in agents.items():
            for seed in seeds:
                row = run_trial(agent_class, seed, difficulty)
                row.update(agent=name, difficulty=difficulty,
                           event_interval=interval, seed=seed)
                rows.append(row)

    return rows


def save_results(rows, filename="results.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print("Results saved:", filename)


def create_charts(rows, output_dir="charts", show=True):
    """One line chart per metric: x = difficulty, one line per agent."""
    os.makedirs(output_dir, exist_ok=True)
    levels = list(DIFFICULTY_LEVELS)
    agents = list(dict.fromkeys(row["agent"] for row in rows))

    for column, label, filename in CHARTS:
        plt.figure(figsize=(9, 5))

        for agent in agents:
            means, spreads = [], []
            for level in levels:
                values = [float(r[column]) for r in rows
                          if r["agent"] == agent and r["difficulty"] == level]
                means.append(mean(values) if values else 0)
                spreads.append(stdev(values) if len(values) > 1 else 0)

            if column == "success":
                plt.plot(levels, [m * 100 for m in means], marker="o", label=agent)
            else:
                plt.errorbar(levels, means, yerr=spreads, marker="o",
                             capsize=4, label=agent)

        plt.title(f"{label} by Difficulty")
        plt.xlabel("Difficulty")
        plt.ylabel(label)
        plt.legend()
        plt.tight_layout()

        path = os.path.join(output_dir, filename)
        plt.savefig(path, dpi=150)
        print("Chart saved:", path)

    if show:
        plt.show()
    plt.close("all")


def run_full_experiment(adaptive_class, baseline_class, seeds=range(100), show=True):
    """Run everything: results.csv plus the three charts."""
    rows = run_benchmark(adaptive_class, baseline_class, list(seeds))
    save_results(rows)
    create_charts(rows, show=show)
    return rows


if __name__ == "__main__":
    from agent import AdaptiveAgent
    from baseline import StaticAgent

    run_full_experiment(AdaptiveAgent, StaticAgent)
