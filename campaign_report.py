"""Campaign results: a CSV file and a chart of how far each agent got."""

import csv
import os
from collections import Counter

import matplotlib.pyplot as plt

from agent import AdaptiveAgent
from baseline import StaticAgent
from campaign import LEVELS, run_many_campaigns, summarise

CSV_FIELDS = ["agent", "campaign_seed", "levels_cleared", "completed",
              "steps", "replans", "pin_guesses", "nodes_expanded"]


def campaign_rows(agents, campaign_seeds):
    """One row per campaign: which agent, which seed, and how far it got."""
    campaign_seeds = list(campaign_seeds)
    rows = []
    for name, agent_class in agents.items():
        campaigns = run_many_campaigns(agent_class, campaign_seeds)
        for seed, campaign in zip(campaign_seeds, campaigns):
            rows.append({
                "agent": name,
                "campaign_seed": seed,
                "levels_cleared": campaign["levels_cleared"],
                "completed": campaign["completed"],
                "steps": campaign["steps"],
                "replans": campaign["replans"],
                "pin_guesses": campaign["pin_guesses"],
                "nodes_expanded": campaign["nodes_expanded"],
            })
    return rows


def save_campaign_csv(rows, filename="campaign_results.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print("Campaign results saved:", filename)


def create_campaign_chart(rows, output_dir="charts", show=True):
    """Bars: out of 100 campaigns, how many ended after 0, 1, 2, ... levels cleared?"""
    os.makedirs(output_dir, exist_ok=True)
    agents = list(dict.fromkeys(row["agent"] for row in rows))
    outcomes = list(range(len(LEVELS) + 1))          # 0, 1, ..., all levels
    width = 0.8 / len(agents)

    plt.figure(figsize=(9, 5))
    for index, agent in enumerate(agents):
        cleared = [row["levels_cleared"] for row in rows if row["agent"] == agent]
        counts = Counter(cleared)
        percentages = [100 * counts[number] / len(cleared) for number in outcomes]
        positions = [number - 0.4 + width * (index + 0.5) for number in outcomes]
        plt.bar(positions, percentages, width=width, label=agent)

    labels = [str(number) for number in outcomes]
    labels[-1] = f"{outcomes[-1]} (all)"
    plt.xticks(outcomes, labels)
    plt.title("How far each agent got in the campaign")
    plt.xlabel("Levels cleared")
    plt.ylabel("Campaigns (%)")
    plt.legend()
    plt.tight_layout()

    path = os.path.join(output_dir, "campaign_levels_cleared.png")
    plt.savefig(path, dpi=150)
    print("Chart saved:", path)

    if show:
        plt.show()
    plt.close("all")


def run_campaign_report(campaign_seeds=range(100), csv_filename="campaign_results.csv",
                        chart_dir="charts", show=True):
    """Run the campaigns for both agents, save the CSV and the chart, print a summary."""
    agents = {"Adaptive": AdaptiveAgent, "Baseline": StaticAgent}
    rows = campaign_rows(agents, campaign_seeds)

    for name in agents:
        summary = summarise([row for row in rows if row["agent"] == name])
        print(f"{name}: mean levels cleared {summary['mean_levels_cleared']:.2f} "
              f"(SD {summary['sd_levels_cleared']:.2f}), "
              f"finished all levels {summary['completed']}/{summary['campaigns']}")

    save_campaign_csv(rows, csv_filename)
    create_campaign_chart(rows, chart_dir, show=show)
    return rows


if __name__ == "__main__":
    run_campaign_report()