# CSCI218: AI Escape Room

A computer agent has to find a key, unlock a door and escape from a 15×15 grid room. While it moves, the room changes: certain cells in its path gets blocked. The agent plans its route with A* search and uses a Finite State Machine to decide what to do (find the key, go to the door or replan). We compare it with a baseline agent that plans once and never changes its plan, over many randomly generated rooms and four difficulty levels.

## Requirements

- Python 3.9 or newer
- The packages in `requirements.txt` (matplotlib and pytest)

## Install

```
git clone https://github.com/tala-s22/csci218-Escape-Room.git
cd csci218-Escape-Room
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

You can also download the repository as a ZIP from GitHub, unzip it, and continue from the `python -m venv` line.

## Run

```
python main.py
```

A menu appears:

1. **Animated demo, adaptive agent.** A window opens and plays one run. The agent, the start (S), the key (K), the door (D), the blocked cells and the planned path are drawn in different colours, and the title shows the state, steps and replans. You are asked to choose a difficulty level (none, easy, medium or hard; the default is medium). Close the window to finish.
2. **Animated demo, baseline agent.** The same, with the baseline agent.
3. **Run the experiments.** Plays 800 runs (both agents, 4 difficulty levels, 100 random rooms each), which takes a few seconds. It writes `results.csv` (one row per run) and three charts into `charts/`: success rate, mean steps and mean nodes expanded.

The experiments are repeatable: the same seeds always give the same results.

## Run the tests

```
python -m pytest -q
```

All tests should pass. You can also run one test file on its own, for example `python -m tests.test_events`.

## Difficulty levels

A blocked cell appears on the agent's path every N steps, but only if the agent can still finish the room.

| Level | Steps between events |
|-------|----------------------|
| none  | no events            |
| easy  | 30                   |
| medium| 20                   |
| hard  | 10                   |

## Project structure

| File             | What it does                                                       |
|------------------|--------------------------------------------------------------------|
| `environment.py` | Grid world and random room generator                               |
| `navigation.py`  | A* search (and a BFS used to check it)                             |
| `agent.py`       | Adaptive agent: Finite State Machine with replanning               |
| `events.py`      | Dynamic events and the difficulty levels                           |
| `baseline.py`    | Baseline agent that never replans                                  |
| `experiments.py` | Experiment runner that generates `results.csv` and charts          |
| `visualise.py`   | Animated demo                                                      |
| `pin_extension.py` | PIN lock, feedback and the two PIN crackers                      |
| `pin_level.py`   | Level 5: the PIN world, the two PIN agents and the level runner    |
| `main.py`        | Menu that launches the demo or the experiments                     |
| `tests/`         | One test file per part                                             |

## Conventions

- A cell is a `(row, col)` pair. `(0, 0)` is the top-left corner.
- `AdaptiveAgent.path` starts with the agent's current cell, so `path[1]` is the next cell to move to. `StaticAgent.path` holds only the cells still left to walk. `DynamicEvents` works with both, because it never blocks the agent's own cell.
