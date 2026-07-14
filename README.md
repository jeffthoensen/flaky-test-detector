# flaky-test-detector

Runs a pytest suite N times and reports which tests are flaky, which are stable, and which are just consistently broken (not the same thing as flaky).

A test that fails every single time isn't flaky, it's wrong. A test that fails sometimes is the one that erodes trust in a suite, because you can't tell if a red run means a real bug or just bad luck. This tool runs your suite repeatedly and tells you which is which.

## Usage

```
pip install -r requirements.txt
playwright install chromium

python flaky_detector.py --runs 20 path/to/tests/
```

Anything after the flags gets passed straight through to `pytest`, so you can target a file, a directory, or use normal pytest filters.

## Try it against the included demo

The `demo/` folder has two Playwright tests against a page that reveals an element after a random 0-100ms delay:

- `test_reveal_waits_properly` waits for the element itself. Stable, every time.
- `test_reveal_with_a_race_condition` waits a fixed 50ms instead. Sometimes that's enough, sometimes it isn't. That's an intentional race condition, not a bug.

```
python flaky_detector.py --runs 15 demo/
```

Output:

```
FLAKY (1):
  demo/test_flaky_demo.py::test_reveal_with_a_race_condition[chromium]: passed 10/15 (5 failures)

STABLE (1): passed all 15 runs
```

## How it classifies

- **Stable** — passed every run.
- **Flaky** — passed some runs and failed others.
- **Consistently failing** — failed every run. This isn't flakiness, it's a real broken test or a real bug, and it's called out separately so it doesn't get lost in the flaky list.

## Tests

```
pytest tests/
```

Unit tests for the aggregation and classification logic, no subprocess calls involved.

---

Built by [Jeff Thoensen](https://jeffthoensen.com), a Context-Driven QA Engineer focused on automation, API testing, and exploratory testing.
