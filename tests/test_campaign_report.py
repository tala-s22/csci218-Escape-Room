"""Coverage for report generation, reproducibility, and output formatting."""

import csv
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")

import pytest

from agent import AdaptiveAgent
from baseline import StaticAgent
from campaign import LEVELS, run_campaign
from campaign_report import (
    CHART_FILENAME, CSV_FIELDS, create_chart, run_campaign_benchmark,
    run_campaign_report, save_results, summarise_rows,
)


def small_campaign_benchmark():
    return run_campaign_benchmark(seeds=range(3))


def test_campaign_benchmark_returns_both_agents_for_every_seed():
    rows = small_campaign_benchmark()
    assert len(rows) == 2 * 3
    assert Counter(row["agent"] for row in rows) == {"Adaptive": 3, "Baseline": 3}
    assert {row["campaign_seed"] for row in rows} == {0, 1, 2}


def test_campaign_rows_have_exact_csv_fields():
    assert all(list(row) == CSV_FIELDS for row in small_campaign_benchmark())


def test_each_row_matches_the_actual_campaign_outcome():
    for row in small_campaign_benchmark():
        agent = AdaptiveAgent if row["agent"] == "Adaptive" else StaticAgent
        original = run_campaign(agent, row["campaign_seed"])
        for key in CSV_FIELDS[2:]:
            assert row[key] == original[key]


def test_campaign_reproducibility():
    assert small_campaign_benchmark() == small_campaign_benchmark()


def test_adaptive_campaigns_complete_all_five_levels():
    rows = small_campaign_benchmark()
    assert all(r["completed"] and r["levels_cleared"] == len(LEVELS)
               for r in rows if r["agent"] == "Adaptive")


def test_completed_implies_all_levels_cleared():
    for row in small_campaign_benchmark():
        assert row["completed"] == (row["levels_cleared"] == len(LEVELS))
        assert row["total_levels"] == len(LEVELS)
        assert 0 <= row["levels_cleared"] <= len(LEVELS)
        assert row["steps"] >= 0
        assert row["nodes_expanded"] >= 0
        assert row["replans"] >= 0
        assert row["pin_guesses"] >= 0


def test_save_results_creates_csv_with_expected_headers(tmp_path):
    output = tmp_path / "export" / "campaign_results.csv"
    rows = small_campaign_benchmark()
    assert save_results(rows, str(output)) == str(output)
    with open(output, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == CSV_FIELDS
        saved_rows = list(reader)
    assert len(saved_rows) == len(rows)
    assert saved_rows[0]["agent"] == rows[0]["agent"]
    assert saved_rows[0]["campaign_seed"] == str(rows[0]["campaign_seed"])


def test_summary_counts_all_campaigns():
    rows = small_campaign_benchmark()
    summaries = summarise_rows(rows)
    assert set(summaries) == {"Adaptive", "Baseline"}
    for name, summary in summaries.items():
        assert summary["campaigns"] == 3
        assert sum(summary["stopped_after"].values()) == 3
    assert summaries["Adaptive"]["mean_levels_cleared"] == 5.0


def test_chart_creates_png(tmp_path):
    filename = create_chart(small_campaign_benchmark(), str(tmp_path))
    assert filename == str(tmp_path / CHART_FILENAME)
    assert os.path.getsize(filename) > 1000
    with open(filename, "rb") as f:
        assert f.read(8) == b"\x89PNG\r\n\x1a\n"


def test_empty_chart_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="empty"):
        create_chart([], str(tmp_path))


def test_report_creates_both_artifacts(tmp_path):
    csv_path = tmp_path / "campaign_results.csv"
    chart_dir = tmp_path / "charts"
    rows = run_campaign_report(seeds=range(2), csv_path=str(csv_path),
                               chart_dir=str(chart_dir))
    assert len(rows) == 4
    assert csv_path.is_file()
    assert (chart_dir / CHART_FILENAME).is_file()


def test_report_rejects_zero_seeds(tmp_path):
    with pytest.raises(ValueError, match="seed"):
        run_campaign_report(seeds=[], csv_path=str(tmp_path / "out.csv"),
                            chart_dir=str(tmp_path / "charts"))


def test_chart_data_distribution_matches_100_seed_campaign_report():
    # Regression check for the results reported in CSCI218_REPORT.docx.
    rows = run_campaign_benchmark(seeds=range(100))
    summary = summarise_rows(rows)
    assert summary["Adaptive"]["stopped_after"] == {5: 100}
    assert summary["Baseline"]["stopped_after"] == {1: 17, 2: 52, 3: 29, 4: 2}
    assert summary["Adaptive"]["completed"] == 100
    assert summary["Baseline"]["completed"] == 0
    assert summary["Baseline"]["mean_levels_cleared"] == pytest.approx(2.16)


def test_generator_seeds_are_reused_for_both_agents():
    rows = run_campaign_benchmark(seeds=(i for i in range(2)))
    assert [r["campaign_seed"] for r in rows] == [0, 1, 0, 1]
