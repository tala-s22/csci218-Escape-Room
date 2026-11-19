"""Repeatable five-level campaign benchmark and its CSV/chart outputs.

Run with ``python campaign_report.py`` from the repository root. Each campaign
plays the five levels consecutively and ends immediately upon the first failure.
This file delegates campaign logic to campaign.py; it does not change the agents.
"""

import csv
import os
from collections import Counter

from agent import AdaptiveAgent
from baseline import StaticAgent
from campaign import LEVELS, run_campaign, summarise

CSV_FIELDS = [
    "agent", "campaign_seed", "levels_cleared", "total_levels",
    "completed", "steps", "nodes_expanded", "replans", "pin_guesses",
]
CHART_FILENAME = "campaign_levels_cleared.png"


def run_campaign_benchmark(adaptive_class=AdaptiveAgent,
                           baseline_class=StaticAgent, seeds=range(100)):
    """One CSV-ready row per agent per seed, on the same seeded campaigns.

    The order matches experiments.py: all Adaptive runs, then all Baseline runs.
    Every new level receives its own deterministic room via campaign.level_seed.
    """
    agents = {"Adaptive": adaptive_class, "Baseline": baseline_class}
    seeds = list(seeds)  # also handle generators: both agents must see the same seeds
    rows = []
    for agent_name, agent_class in agents.items():
        for campaign_seed in seeds:
            outcome = run_campaign(agent_class, campaign_seed)
            row = {"agent": agent_name, "campaign_seed": campaign_seed}
            for field in CSV_FIELDS[2:]:
                row[field] = outcome[field]
            rows.append(row)
    return rows


def save_results(rows, filename="campaign_results.csv"):
    """Write the complete trial-level results, including CSV header."""
    directory = os.path.dirname(os.path.abspath(filename))
    os.makedirs(directory, exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return filename


def summarise_rows(rows):
    """Give each agent's number of completions and mean levels cleared."""
    summaries = {}
    for agent_name in dict.fromkeys(row["agent"] for row in rows):
        agent_rows = [row for row in rows if row["agent"] == agent_name]
        outcomes = [{"levels_cleared": row["levels_cleared"],
                     "completed": row["completed"]} for row in agent_rows]
        summaries[agent_name] = summarise(outcomes)
    return summaries


def create_chart(rows, output_dir="charts", show=False):
    """Plot % of campaigns ending with 0, 1, ..., 5 completed levels."""
    if not rows:
        raise ValueError("Cannot make a campaign chart from empty results")

    # Import locally so callers can use CSV generation without matplotlib.
    import matplotlib.pyplot as plt

    os.makedirs(output_dir, exist_ok=True)
    levels = list(range(len(LEVELS) + 1))
    agent_names = list(dict.fromkeys(row["agent"] for row in rows))
    xs = list(range(len(levels)))
    width = 0.75 / len(agent_names)

    fig, ax = plt.subplots(figsize=(9, 5))
    for agent_index, name in enumerate(agent_names):
        group = [row for row in rows if row["agent"] == name]
        counts = Counter(int(row["levels_cleared"]) for row in group)
        fractions = [counts[level] * 100 / len(group) for level in levels]
        shift = (agent_index - (len(agent_names) - 1) / 2) * width
        ax.bar([x + shift for x in xs], fractions, width=width,
               label=name)

    ax.set_title("How far each agent got in the campaign")
    ax.set_xlabel("Levels cleared")
    ax.set_ylabel("Campaigns (%)")
    ax.set_xticks(xs)
    ax.set_xticklabels([str(level) if level < len(LEVELS) else f"{len(LEVELS)} (all)"
                        for level in levels])
    ax.set_ylim(0, 105)
    ax.legend()
    fig.tight_layout()
    path = os.path.join(output_dir, CHART_FILENAME)
    fig.savefig(path, dpi=150)
    if show:
        plt.show()
    plt.close(fig)
    return path


def run_campaign_report(seeds=range(100), csv_path="campaign_results.csv",
                        chart_dir="charts", show=False):
    """Run the complete reproducible campaign report and save both outputs."""
    rows = run_campaign_benchmark(seeds=seeds)
    if not rows:
        raise ValueError("At least one campaign seed is required")
    csv_file = save_results(rows, csv_path)
    chart_file = create_chart(rows, output_dir=chart_dir, show=show)
    print("Results saved:", csv_file)
    print("Chart saved:", chart_file)
    for name, stats in summarise_rows(rows).items():
        print(f"{name}: mean levels cleared {stats['mean_levels_cleared']:.2f} "
              f"(SD {stats['sd_levels_cleared']:.2f}), "
              f"completed {stats['completed']}/{stats['campaigns']}, "
              f"levels-cleared distribution {stats['stopped_after']}")
    return rows


if __name__ == "__main__":
    run_campaign_report()
