from agent import AdaptiveAgent
from baseline import StaticAgent
from campaign import (EVENT_LEVELS, LEVELS, PIN_LEVEL, level_seed, print_campaign,
                      run_campaign, run_many_campaigns, summarise)
from events import DIFFICULTY_LEVELS
from experiments import run_trial


def test_levels_follow_the_difficulty_levels_then_the_pin_level():
    assert [level["number"] for level in LEVELS] == [1, 2, 3, 4, 5]
    assert [level["difficulty"] for level in LEVELS] == list(DIFFICULTY_LEVELS) + [PIN_LEVEL]
    assert LEVELS[0]["difficulty"] == "none"
    assert LEVELS[-1]["difficulty"] == PIN_LEVEL
    assert EVENT_LEVELS == LEVELS[:4]


def test_each_level_gets_its_own_room_seed():
    seeds = [level_seed(5, level["number"]) for level in LEVELS]
    assert len(set(seeds)) == len(LEVELS)
    assert level_seed(5, 2) == level_seed(5, 2)


def test_adaptive_agent_clears_every_level():
    for seed in range(20):
        campaign = run_campaign(AdaptiveAgent, seed)
        assert campaign["completed"]
        assert campaign["levels_cleared"] == len(LEVELS)
        assert len(campaign["levels"]) == len(LEVELS)


def test_the_four_event_levels_give_the_same_results_as_before():
    for agent_class in [AdaptiveAgent, StaticAgent]:
        for seed in range(10):
            campaign = run_campaign(agent_class, seed)
            for result in campaign["levels"][:4]:
                expected = run_trial(agent_class, level_seed(seed, result["level"]),
                                     result["difficulty"])
                assert {key: result[key] for key in expected} == expected


def test_level_five_is_the_pin_level():
    for seed in range(10):
        level = run_campaign(AdaptiveAgent, seed)["levels"][4]
        assert level["level"] == 5 and level["difficulty"] == PIN_LEVEL
        assert level["guesses"] > 0
    campaign = run_campaign(AdaptiveAgent, 0)
    assert campaign["pin_guesses"] == campaign["levels"][4]["guesses"]


def test_baseline_that_clears_the_four_event_levels_still_has_to_play_the_pin_level():
    for seed in range(300):
        campaign = run_campaign(StaticAgent, seed)
        if campaign["levels_cleared"] >= 4:
            assert len(campaign["levels"]) == 5
            assert campaign["levels"][4]["guesses"] > 0
            return
    assert False, "no baseline campaign cleared four levels in 300 seeds"


def test_print_campaign_shows_the_pin_guesses(capsys=None):
    import contextlib
    import io
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        print_campaign("Adaptive", run_campaign(AdaptiveAgent, 0))
    text = buffer.getvalue()
    assert "Level 5 (pin)" in text and "PIN guesses" in text


def test_baseline_always_clears_level_one():
    for seed in range(30):
        assert run_campaign(StaticAgent, seed)["levels_cleared"] >= 1


def test_campaign_stops_at_the_first_failed_level():
    for seed in range(30):
        campaign = run_campaign(StaticAgent, seed)
        if not campaign["completed"]:
            assert len(campaign["levels"]) == campaign["levels_cleared"] + 1
            assert campaign["levels"][-1]["success"] is False
            assert all(level["success"] for level in campaign["levels"][:-1])


def test_same_campaign_seed_gives_the_same_result():
    assert run_campaign(StaticAgent, 7) == run_campaign(StaticAgent, 7)


def test_totals_add_up_the_levels():
    campaign = run_campaign(AdaptiveAgent, 3)
    assert campaign["steps"] == sum(level["steps"] for level in campaign["levels"])
    assert campaign["replans"] == sum(level["replans"] for level in campaign["levels"])


def test_summarise_counts_how_far_agents_got():
    campaigns = [
        {"levels_cleared": 5, "completed": True},
        {"levels_cleared": 2, "completed": False},
        {"levels_cleared": 2, "completed": False},
    ]
    summary = summarise(campaigns)
    assert summary["campaigns"] == 3
    assert summary["completed"] == 1
    assert summary["stopped_after"] == {2: 2, 5: 1}
    assert abs(summary["mean_levels_cleared"] - 9 / 3) < 1e-9


def test_adaptive_gets_further_than_baseline_on_average():
    adaptive = summarise(run_many_campaigns(AdaptiveAgent, range(40)))
    baseline = summarise(run_many_campaigns(StaticAgent, range(40)))
    assert adaptive["mean_levels_cleared"] > baseline["mean_levels_cleared"]


if __name__ == "__main__":
    test_levels_follow_the_difficulty_levels_then_the_pin_level()
    test_each_level_gets_its_own_room_seed()
    test_adaptive_agent_clears_every_level()
    test_the_four_event_levels_give_the_same_results_as_before()
    test_level_five_is_the_pin_level()
    test_baseline_that_clears_the_four_event_levels_still_has_to_play_the_pin_level()
    test_print_campaign_shows_the_pin_guesses()
    test_baseline_always_clears_level_one()
    test_campaign_stops_at_the_first_failed_level()
    test_same_campaign_seed_gives_the_same_result()
    test_totals_add_up_the_levels()
    test_summarise_counts_how_far_agents_got()
    test_adaptive_gets_further_than_baseline_on_average()
    print("All campaign tests passed")
