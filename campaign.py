from collections import Counter
from statistics import mean, pstdev

from agent import AdaptiveAgent
from baseline import StaticAgent
from events import DIFFICULTY_LEVELS
from experiments import run_trial
from pin_level import PinAdaptiveAgent, PinStaticAgent, play_pin_level

# Level 1 = "none", Level 2 = "easy", Level 3 = "medium", Level 4 = "hard", Level 5 = the PIN level
PIN_LEVEL = "pin"
LEVELS = [
    {"number": number, "difficulty": name}
    for number, name in enumerate(DIFFICULTY_LEVELS, start=1)
] + [{"number": len(DIFFICULTY_LEVELS) + 1, "difficulty": PIN_LEVEL}]

# The levels with random blocking events (everything except the PIN level)
EVENT_LEVELS = [level for level in LEVELS if level["difficulty"] != PIN_LEVEL]

# The PIN level needs its own agents; this says which one belongs to which campaign agent.
PIN_AGENTS = {AdaptiveAgent: PinAdaptiveAgent, StaticAgent: PinStaticAgent}


def level_seed(campaign_seed, level_number):
    """Every level gets its own room, always the same for the same campaign seed."""
    return campaign_seed * 100 + level_number


def run_campaign(agent_class, campaign_seed):
    """Play the levels in order. The campaign ends at the first level the agent fails."""
    results = []

    for level in LEVELS:
        seed = level_seed(campaign_seed, level["number"])
        if level["difficulty"] == PIN_LEVEL:
            if agent_class not in PIN_AGENTS:
                raise ValueError(f"no PIN-level agent for {agent_class.__name__}")
            result = play_pin_level(PIN_AGENTS[agent_class], seed)
        else:
            result = run_trial(agent_class, seed, level["difficulty"])
        result["level"] = level["number"]
        result["difficulty"] = level["difficulty"]
        results.append(result)

        if not result["success"]:
            break

    cleared = sum(1 for result in results if result["success"])
    return {
        "levels_cleared": cleared,
        "total_levels": len(LEVELS),
        "completed": cleared == len(LEVELS),
        "steps": sum(result["steps"] for result in results),
        "replans": sum(result["replans"] for result in results),
        "nodes_expanded": sum(result["nodes_expanded"] for result in results),
        "pin_guesses": sum(result.get("guesses", 0) for result in results),
        "levels": results,
    }


def run_many_campaigns(agent_class, campaign_seeds):
    return [run_campaign(agent_class, seed) for seed in campaign_seeds]


def summarise(campaigns):
    """How far did the agent get, on average?"""
    cleared = [campaign["levels_cleared"] for campaign in campaigns]
    return {
        "campaigns": len(campaigns),
        "mean_levels_cleared": mean(cleared),
        "sd_levels_cleared": pstdev(cleared),
        "completed": sum(1 for campaign in campaigns if campaign["completed"]),
        "stopped_after": dict(sorted(Counter(cleared).items())),
    }


def print_campaign(name, campaign):
    print(f"{name}: cleared {campaign['levels_cleared']} of {campaign['total_levels']} levels")
    for result in campaign["levels"]:
        outcome = "ESCAPED" if result["success"] else "FAILED"
        if result["difficulty"] == PIN_LEVEL:
            detail = f"{result['steps']} steps, {result['guesses']} PIN guesses"
        else:
            detail = f"{result['steps']} steps, {result['replans']} replans"
        print(f"  Level {result['level']} ({result['difficulty']}): {outcome}, {detail}")


if __name__ == "__main__":
    agents = {"Adaptive": AdaptiveAgent, "Baseline": StaticAgent}

    print("One campaign (campaign seed 0):")
    for name, agent_class in agents.items():
        print_campaign(name, run_campaign(agent_class, 0))

    print("\n100 campaigns:")
    for name, agent_class in agents.items():
        summary = summarise(run_many_campaigns(agent_class, range(100)))
        print(f"{name}: mean levels cleared {summary['mean_levels_cleared']:.2f} "
              f"(SD {summary['sd_levels_cleared']:.2f}), "
              f"finished all levels {summary['completed']}/{summary['campaigns']}, "
              f"campaigns that ended after N levels cleared: {summary['stopped_after']}")
