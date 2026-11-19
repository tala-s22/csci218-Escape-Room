from agent import AdaptiveAgent
from baseline import StaticAgent
from events import DIFFICULTY_LEVELS


def ask_difficulty(default="medium"):
    names = list(DIFFICULTY_LEVELS)
    answer = input(f"Difficulty {names} [{default}]: ").strip().lower()
    return answer if answer in DIFFICULTY_LEVELS else default


def ask_start_level(default=1):
    from campaign import LEVELS
    numbers = [str(level["number"]) for level in LEVELS]
    answer = input(f"Start at level {numbers[0]}-{numbers[-1]} [{default}]: ").strip()
    return int(answer) if answer in numbers else default


def main():
    print("\n=== ESCAPE ROOM ===")
    print("1. Animated demo - Adaptive agent")
    print("2. Animated demo - Baseline agent")
    print("3. Run experiments (saves results.csv and charts/)")
    print("4. Campaign demo - Adaptive agent (Levels 1 to 5)")
    print("5. Campaign demo - Baseline agent (Levels 1 to 5)")

    choice = input("Choose 1, 2, 3, 4 or 5: ").strip()

    if choice in ("1", "2"):
        from visualise import animate_demo
        agent_class = AdaptiveAgent if choice == "1" else StaticAgent
        animate_demo(agent_class, difficulty=ask_difficulty())

    elif choice == "3":
        from experiments import run_full_experiment
        run_full_experiment(AdaptiveAgent, StaticAgent, seeds=range(100))

    elif choice in ("4", "5"):
        from campaign_demo import animate_campaign
        agent_class = AdaptiveAgent if choice == "4" else StaticAgent
        animate_campaign(agent_class, start_level=ask_start_level())

    else:
        print("Invalid choice. Please choose 1, 2, 3, 4 or 5.")


if __name__ == "__main__":
    main()
