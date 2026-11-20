import csv
import os
import tempfile

import matplotlib
matplotlib.use("Agg")

from agent import AdaptiveAgent
from baseline import StaticAgent
from campaign import LEVELS
import campaign_report

AGENTS = {"Adaptive": AdaptiveAgent, "Baseline": StaticAgent}


def test_one_row_per_agent_and_campaign_seed():
    rows = campaign_report.campaign_rows(AGENTS, range(5))
    assert len(rows) == 2 * 5
    assert {row["agent"] for row in rows} == {"Adaptive", "Baseline"}
    assert set(rows[0]) == set(campaign_report.CSV_FIELDS)


def test_adaptive_rows_all_completed_every_level():
    rows = campaign_report.campaign_rows(AGENTS, range(10))
    adaptive = [row for row in rows if row["agent"] == "Adaptive"]
    assert all(row["completed"] for row in adaptive)
    assert all(row["levels_cleared"] == len(LEVELS) for row in adaptive)


def test_csv_is_written_and_readable():
    rows = campaign_report.campaign_rows(AGENTS, range(3))
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "campaign_results.csv")
        campaign_report.save_campaign_csv(rows, path)
        with open(path) as file:
            saved = list(csv.DictReader(file))
    assert len(saved) == len(rows)
    assert list(saved[0]) == campaign_report.CSV_FIELDS


def test_chart_is_created():
    rows = campaign_report.campaign_rows(AGENTS, range(5))
    with tempfile.TemporaryDirectory() as folder:
        campaign_report.create_campaign_chart(rows, folder, show=False)
        assert os.path.exists(os.path.join(folder, "campaign_levels_cleared.png"))


if __name__ == "__main__":
    test_one_row_per_agent_and_campaign_seed()
    test_adaptive_rows_all_completed_every_level()
    test_csv_is_written_and_readable()
    test_chart_is_created()
    print("All campaign report tests passed")