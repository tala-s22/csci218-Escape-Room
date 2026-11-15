import csv
import os
import tempfile

import matplotlib
matplotlib.use("Agg")      

from baseline import StaticAgent
from environment import World
from experiments import (CSV_FIELDS, CHARTS, run_trial, run_benchmark,
                         save_results, create_charts)
from events import DIFFICULTY_LEVELS
from visualise import record_episode

# These tests use StaticAgent for both agents so they do not depend on agent.py.


def small_benchmark(seeds=range(3)):
    return run_benchmark(StaticAgent, StaticAgent, list(seeds))


# ---------- run_trial ----------

def test_run_trial_has_expected_keys():
    result = run_trial(StaticAgent, seed=1, difficulty="none")
    assert set(result) == {"success", "steps", "nodes_expanded", "replans"}


def test_run_trial_without_events_escapes():
    for seed in range(10):
        result = run_trial(StaticAgent, seed, "none")
        assert result["success"] is True
        assert result["steps"] > 0
        assert result["replans"] == 0


def test_run_trial_is_reproducible():
    assert run_trial(StaticAgent, 7, "hard") == run_trial(StaticAgent, 7, "hard")


def test_run_trial_unknown_difficulty_raises():
    try:
        run_trial(StaticAgent, 1, "impossible")
    except ValueError:
        return
    raise AssertionError("expected ValueError for an unknown difficulty")


# ---------- run_benchmark ----------

def test_benchmark_row_count():
    rows = small_benchmark(range(3))
    assert len(rows) == len(DIFFICULTY_LEVELS) * 2 * 3      # levels x agents x seeds


def test_benchmark_rows_have_every_csv_field():
    for row in small_benchmark(range(2)):
        assert set(row) == set(CSV_FIELDS)


def test_benchmark_uses_both_agent_names_and_all_levels():
    rows = small_benchmark(range(2))
    assert {row["agent"] for row in rows} == {"Adaptive", "Baseline"}
    assert {row["difficulty"] for row in rows} == set(DIFFICULTY_LEVELS)


# ---------- save_results / create_charts ----------

def test_save_results_writes_a_readable_csv():
    rows = small_benchmark(range(2))
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "results.csv")
        save_results(rows, path)
        with open(path, newline="") as file:
            reader = csv.DictReader(file)
            saved = list(reader)
            assert reader.fieldnames == CSV_FIELDS
    assert len(saved) == len(rows)


def test_create_charts_saves_all_three_images():
    rows = small_benchmark(range(3))
    with tempfile.TemporaryDirectory() as folder:
        create_charts(rows, output_dir=folder, show=False)
        for _, _, filename in CHARTS:
            path = os.path.join(folder, filename)
            assert os.path.exists(path) and os.path.getsize(path) > 0


# ---------- visualise.record_episode ----------

def test_record_episode_without_events():
    world, frames = record_episode(StaticAgent, seed=2, difficulty="none", max_ticks=500)
    assert frames[0]["position"] == world.start
    assert frames[-1]["state"] == "ESCAPED"
    assert frames[-1]["position"] == world.door
    assert len(frames) == frames[-1]["steps"] + 1            # one frame per move


def test_record_episode_stops_at_max_ticks():
    _, frames = record_episode(StaticAgent, seed=2, difficulty="none", max_ticks=3)
    assert len(frames) <= 4                                  # start frame + 3 ticks


def test_record_episode_blocked_cells_only_grow_or_stay():
    _, frames = record_episode(StaticAgent, seed=4, difficulty="hard", max_ticks=200)
    for before, after in zip(frames, frames[1:]):
        assert before["blocked"] <= after["blocked"]


if __name__ == "__main__":
    test_run_trial_has_expected_keys()
    test_run_trial_without_events_escapes()
    test_run_trial_is_reproducible()
    test_run_trial_unknown_difficulty_raises()
    test_benchmark_row_count()
    test_benchmark_rows_have_every_csv_field()
    test_benchmark_uses_both_agent_names_and_all_levels()
    test_save_results_writes_a_readable_csv()
    test_create_charts_saves_all_three_images()
    test_record_episode_without_events()
    test_record_episode_stops_at_max_ticks()
    test_record_episode_blocked_cells_only_grow_or_stay()
    print("All experiments tests passed")
