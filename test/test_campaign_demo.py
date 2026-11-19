import matplotlib

matplotlib.use("Agg")       # no window needed when testing

import gc
import warnings

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from agent import AdaptiveAgent
from baseline import StaticAgent
from campaign import LEVELS, PIN_LEVEL, run_campaign
from campaign_demo import (DEMO_INTERVALS, GUESS_SKIP, HOLD_FRAMES, SHOW_FIRST_GUESSES, animate_campaign, build_timeline,
                           draw_frame, make_figure, parse_args, record_campaign,
                           scoreboard_text)
from events import DIFFICULTY_LEVELS

AGENTS = [AdaptiveAgent, StaticAgent]


def test_recorded_campaign_matches_run_campaign():
    for agent_class in AGENTS:
        for seed in range(5):
            records = record_campaign(agent_class, seed)
            campaign = run_campaign(agent_class, seed)
            assert len(records) == len(campaign["levels"])
            for record, result in zip(records, campaign["levels"]):
                last = record["frames"][-1]
                assert record["success"] == result["success"]
                assert last["steps"] == result["steps"]
                assert last["replans"] == result["replans"]
                assert record["level"] == result["level"]
                if record["difficulty"] == PIN_LEVEL:
                    assert last["guesses"] == result["guesses"]


def test_recording_stops_at_the_first_failed_level():
    for seed in range(30):
        records = record_campaign(StaticAgent, seed)
        assert all(record["success"] for record in records[:-1])
        if len(records) < len(LEVELS):
            assert records[-1]["success"] is False


def test_adaptive_record_has_every_level():
    records = record_campaign(AdaptiveAgent, 0)
    assert [record["level"] for record in records] == [1, 2, 3, 4, 5]
    assert all(record["success"] for record in records)


def test_timeline_length_and_final_message():
    records = record_campaign(AdaptiveAgent, 0)
    timeline = build_timeline(records)
    frames = sum(len(record["frames"]) for record in records)
    assert len(timeline) == frames + HOLD_FRAMES * len(records)
    assert timeline[-1]["message"] == "ALL LEVELS CLEARED"
    assert timeline[0]["message"] == ""


def test_timeline_ends_with_failure_message_for_a_failed_campaign():
    for seed in range(30):
        records = record_campaign(StaticAgent, seed)
        if not records[-1]["success"]:
            timeline = build_timeline(records)
            assert "FAILED" in timeline[-1]["message"]
            return
    assert False, "no baseline campaign failed in 30 seeds"


def test_scoreboard_text():
    record = {"level": 2, "success": True}
    assert scoreboard_text(record, finished=False) == "L1: cleared   L2: playing   L3: -   L4: -   L5: -"
    assert scoreboard_text(record, finished=True) == "L1: cleared   L2: cleared   L3: -   L4: -   L5: -"
    failed = {"level": 2, "success": False}
    assert scoreboard_text(failed, finished=True) == "L1: cleared   L2: FAILED   L3: -   L4: -   L5: -"


def test_every_frame_can_be_drawn():
    fig, ax = make_figure()
    for agent_class in AGENTS:
        timelines = [build_timeline(record_campaign(agent_class, 1)),
                     build_timeline(record_campaign(agent_class, 1, start_level=5))]
        for timeline in timelines:
            for entry in timeline:
                draw_frame(ax, entry, agent_class.__name__, 1)
    plt.close(fig)


def test_animate_campaign_builds_without_showing():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")     # matplotlib warns that we never played the animation
        animation = animate_campaign(AdaptiveAgent, campaign_seed=0, show=False)
        assert isinstance(animation, FuncAnimation)
        del animation
        plt.close("all")
        gc.collect()                        # delete the animation now, while the warning is muted


def test_demo_intervals_cover_the_same_levels_and_are_denser():
    assert list(DEMO_INTERVALS) == list(DIFFICULTY_LEVELS)
    assert DEMO_INTERVALS["none"] == 0
    for name in ["easy", "medium", "hard"]:
        assert 0 < DEMO_INTERVALS[name] < DIFFICULTY_LEVELS[name]
    assert DEMO_INTERVALS["easy"] > DEMO_INTERVALS["medium"] > DEMO_INTERVALS["hard"]


def test_demo_adaptive_agent_still_clears_every_level():
    for seed in range(20):
        records = record_campaign(AdaptiveAgent, seed, DEMO_INTERVALS)
        assert len(records) == len(LEVELS)
        assert all(record["success"] for record in records)


def test_demo_level_one_has_no_blocked_cells_and_hard_level_has_more_than_official():
    demo_blocks = official_blocks = 0
    for seed in range(20):
        demo = record_campaign(AdaptiveAgent, seed, DEMO_INTERVALS)
        official = record_campaign(AdaptiveAgent, seed, DIFFICULTY_LEVELS)
        assert demo[0]["frames"][-1]["blocked"] == set()
        demo_blocks += len(demo[3]["frames"][-1]["blocked"])
        official_blocks += len(official[3]["frames"][-1]["blocked"])
    assert demo_blocks > official_blocks


def test_title_and_scoreboard_fit_inside_the_figure():
    fig, ax = make_figure()
    for agent_class in AGENTS:
        timeline = (build_timeline(record_campaign(agent_class, 0, DEMO_INTERVALS))
                    + build_timeline(record_campaign(agent_class, 0, start_level=5)))
        for entry in timeline[::7] + [timeline[-1]]:
            draw_frame(ax, entry, "Adaptive agent", 0)
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            for text in [ax.title, ax.xaxis.label]:
                box = text.get_window_extent(renderer)
                assert box.x0 >= 0 and box.y0 >= 0
                assert box.x1 <= fig.bbox.x1 and box.y1 <= fig.bbox.y1
    plt.close(fig)


def test_scoreboard_marks_skipped_levels():
    record = {"level": 5, "success": True, "start_level": 5}
    assert scoreboard_text(record, finished=False) == (
        "L1: skipped   L2: skipped   L3: skipped   L4: skipped   L5: playing")


def test_pin_level_hides_the_key_until_the_lock_opens():
    for agent_class in AGENTS:
        for seed in range(5):
            record = record_campaign(agent_class, seed, start_level=5)[0]
            visible = [frame["key_visible"] for frame in record["frames"]]
            assert visible[0] is False
            assert visible == sorted(visible)           # False ... False True ... True
            first = visible.index(True)
            assert record["frames"][first - 1]["state"] == "CRACK_PIN"
            assert record["frames"][first]["state"] != "CRACK_PIN"


def test_adaptive_pin_level_shows_every_guess():
    for seed in range(5):
        record = record_campaign(AdaptiveAgent, seed, start_level=5)[0]
        guesses = record["frames"][-1]["guesses"]
        cracking = [frame for frame in record["frames"] if frame["state"] == "CRACK_PIN"]
        assert len(cracking) == guesses         # nothing was skipped


def test_baseline_pin_level_skips_most_guesses_but_still_ends_correctly():
    for seed in range(5):
        record = record_campaign(StaticAgent, seed, start_level=5)[0]
        world = record["world"]
        last = record["frames"][-1]
        assert last["guesses"] == int(world.lock.secret) + 1
        assert len(record["frames"]) < last["steps"] + SHOW_FIRST_GUESSES + last["guesses"] // GUESS_SKIP + 10


def test_start_level_plays_only_the_later_levels():
    records = record_campaign(AdaptiveAgent, 0, start_level=5)
    assert [record["level"] for record in records] == [5]
    assert build_timeline(records)[-1]["message"] == "ALL LEVELS CLEARED"


def test_parse_args():
    assert parse_args([]).agent == "adaptive"
    args = parse_args(["baseline", "--seed", "3", "--official"])
    assert (args.agent, args.seed, args.official) == ("baseline", 3, True)
    assert parse_args([]).start_level == 1
    assert parse_args(["--start-level", "5"]).start_level == 5


if __name__ == "__main__":
    test_recorded_campaign_matches_run_campaign()
    test_recording_stops_at_the_first_failed_level()
    test_adaptive_record_has_every_level()
    test_timeline_length_and_final_message()
    test_timeline_ends_with_failure_message_for_a_failed_campaign()
    test_scoreboard_text()
    test_every_frame_can_be_drawn()
    test_animate_campaign_builds_without_showing()
    test_demo_intervals_cover_the_same_levels_and_are_denser()
    test_demo_adaptive_agent_still_clears_every_level()
    test_demo_level_one_has_no_blocked_cells_and_hard_level_has_more_than_official()
    test_title_and_scoreboard_fit_inside_the_figure()
    test_scoreboard_marks_skipped_levels()
    test_pin_level_hides_the_key_until_the_lock_opens()
    test_adaptive_pin_level_shows_every_guess()
    test_baseline_pin_level_skips_most_guesses_but_still_ends_correctly()
    test_start_level_plays_only_the_later_levels()
    test_parse_args()
    print("All campaign demo tests passed")
