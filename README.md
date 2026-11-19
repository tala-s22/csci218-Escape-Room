# CSCI218: AI Escape Room

A computer agent has to find a key, unlock a door and escape from a 15×15 grid room. While it moves, the room changes: certain cells in its path gets blocked. The agent plans its route with A* search and uses a Finite State Machine to decide what to do (find the key, go to the door or replan). We compare it with a baseline agent that plans once and never changes its plan, over many randomly generated rooms and four difficulty levels. A campaign plays the levels one after another (Levels 1 to 4 are the difficulty levels, Level 5 is a PIN lock) and stops at the first level the agent fails.

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

4. **Campaign demo, adaptive agent.** One window plays Level 1, 2, 3, 4 and 5 in order, with a level banner, a scoreboard and a "LEVEL CLEARED" message after each level. You can choose the level to start at.
5. **Campaign demo, baseline agent.** The same, with the baseline agent. It usually fails Level 2 or 3, so start at level 5 to watch it on the PIN level.

The experiments are repeatable: the same seeds always give the same results. The campaign demo uses more frequent events than the experiments (every 10, 7 and 5 steps instead of 30, 20 and 10) so that the replanning is easy to see; the experiments and `results.csv` are not affected.

Other commands:

```
python campaign.py                       # campaign results for both agents (100 campaigns)
python campaign_report.py                # writes campaign_results.csv and charts/campaign_levels_cleared.png
python pin_level.py                      # Level 5 results for both agents (100 rooms)
python campaign_demo.py baseline --seed 0 --start-level 5     # the demo with command-line options
```

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

## Levels and the campaign

| Level | Name   | What happens                                                              |
|-------|--------|---------------------------------------------------------------------------|
| 1     | none   | no events                                                                 |
| 2     | easy   | a blocked cell every 30 steps                                             |
| 3     | medium | a blocked cell every 20 steps                                             |
| 4     | hard   | a blocked cell every 10 steps                                             |
| 5     | pin    | the key is hidden; crack the PIN lock on cell P first, then the key appears |

Every level of a campaign is a different room: the room seed is `campaign seed * 100 + level number`.

**Level 5, the PIN level.** The lock on cell P has a secret 3-digit PIN and only says how many digits are in the right place. The adaptive agent walks to P, uses that feedback to cross out impossible codes (about 9 guesses on average), then fetches the key and goes to the door. The baseline plans start, P, door once and guesses 000, 001, 002, ... (about 500 guesses on average); it never goes to fetch the key, so it escapes only if the key happens to lie on its route. There are no random blocking events in this level.

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
| `pin_level.py`   | Level 5: the PIN world, the two PIN agents and `play_pin_level`    |
| `campaign.py`    | Campaign: the five levels in order, stops at the first failure     |
| `campaign_report.py` | Campaign results: `campaign_results.csv` and a chart           |
| `campaign_demo.py` | Animated campaign demo                                           |
| `main.py`        | Menu that launches the demos or the experiments                    |
| `tests/`         | One test file per part                                             | 

## Conventions

- A cell is a `(row, col)` pair. `(0, 0)` is the top-left corner.
- `AdaptiveAgent.path` starts with the agent's current cell, so `path[1]` is the next cell to move to. `StaticAgent.path` holds only the cells still left to walk. `DynamicEvents` works with both, because it never blocks the agent's own cell.
