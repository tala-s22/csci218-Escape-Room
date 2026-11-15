from agent import AdaptiveAgent
from baseline import StaticAgent
from events import DIFFICULTY_LEVELS


def ask_difficulty(default="medium"):
    names = list(DIFFICULTY_LEVELS)
    answer = input(f"Difficulty {names} [{default}]: ").strip().lower()
    return answer if answer in DIFFICULTY_LEVELS else default


def main():
    print("\n=== ESCAPE ROOM ===")
    print("1. Animated demo - Adaptive agent")
    print("2. Animated demo - Baseline agent")
    print("3. Run experiments (saves results.csv and charts/)")

    choice = input("Choose 1, 2 or 3: ").strip()

    if choice in ("1", "2"):
        from visualise import animate_demo
        agent_class = AdaptiveAgent if choice == "1" else StaticAgent
        animate_demo(agent_class, difficulty=ask_difficulty())

    elif choice == "3":
        from experiments import run_full_experiment
        run_full_experiment(AdaptiveAgent, StaticAgent, seeds=range(100))

    else:
        print("Invalid choice. Please choose 1, 2 or 3.")


if __name__ == "__main__":
    main()
