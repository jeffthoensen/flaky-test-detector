import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaky_detector import aggregate, classify  # noqa: E402


def test_aggregate_combines_results_across_runs():
    runs = [
        {"test_a": "passed", "test_b": "failed"},
        {"test_a": "passed", "test_b": "passed"},
    ]

    result = aggregate(runs)

    assert result["test_a"] == ["passed", "passed"]
    assert result["test_b"] == ["failed", "passed"]


def test_classify_stable_pass():
    outcomes = {"test_a": ["passed", "passed", "passed"]}

    stable_pass, stable_fail, flaky = classify(outcomes)

    assert stable_pass == [("test_a", 3, 0)]
    assert stable_fail == []
    assert flaky == []


def test_classify_stable_fail():
    outcomes = {"test_a": ["failed", "failed"]}

    stable_pass, stable_fail, flaky = classify(outcomes)

    assert stable_fail == [("test_a", 0, 2)]
    assert stable_pass == []
    assert flaky == []


def test_classify_flaky():
    outcomes = {"test_a": ["passed", "failed", "passed"]}

    stable_pass, stable_fail, flaky = classify(outcomes)

    assert flaky == [("test_a", 2, 1)]
    assert stable_pass == []
    assert stable_fail == []


def test_classify_handles_multiple_tests_at_once():
    outcomes = {
        "test_stable": ["passed", "passed"],
        "test_broken": ["failed", "failed"],
        "test_flaky": ["passed", "failed"],
    }

    stable_pass, stable_fail, flaky = classify(outcomes)

    assert [nodeid for nodeid, _, _ in stable_pass] == ["test_stable"]
    assert [nodeid for nodeid, _, _ in stable_fail] == ["test_broken"]
    assert [nodeid for nodeid, _, _ in flaky] == ["test_flaky"]
