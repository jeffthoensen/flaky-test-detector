import argparse
import json
import subprocess
import sys
import tempfile
from collections import defaultdict


def run_once(pytest_args):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        report_path = tmp.name

    cmd = ["pytest", "--json-report", f"--json-report-file={report_path}", *pytest_args]
    subprocess.run(cmd, capture_output=True, text=True)

    with open(report_path) as f:
        report = json.load(f)

    return {test["nodeid"]: test["outcome"] for test in report.get("tests", [])}


def aggregate(all_runs):
    outcomes = defaultdict(list)
    for run in all_runs:
        for nodeid, outcome in run.items():
            outcomes[nodeid].append(outcome)
    return dict(outcomes)


def classify(outcomes):
    stable_pass = []
    stable_fail = []
    flaky = []
    for nodeid, results in outcomes.items():
        passed = results.count("passed")
        failed = len(results) - passed
        if failed == 0:
            stable_pass.append((nodeid, passed, failed))
        elif passed == 0:
            stable_fail.append((nodeid, passed, failed))
        else:
            flaky.append((nodeid, passed, failed))
    return stable_pass, stable_fail, flaky


def main():
    parser = argparse.ArgumentParser(
        description="Run a pytest suite N times and report which tests are flaky, "
        "stable, or consistently broken."
    )
    parser.add_argument(
        "--runs", type=int, default=10, help="Number of times to run the suite (default: 10)"
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Args passed through to pytest, e.g. a test path",
    )
    args = parser.parse_args()

    print(f"Running suite {args.runs} times...\n")
    all_runs = []
    for i in range(args.runs):
        print(f"  run {i + 1}/{args.runs}", end="\r")
        all_runs.append(run_once(args.pytest_args))
    print()

    outcomes = aggregate(all_runs)
    stable_pass, stable_fail, flaky = classify(outcomes)

    if flaky:
        print(f"\nFLAKY ({len(flaky)}):")
        for nodeid, passed, failed in sorted(flaky, key=lambda x: x[2], reverse=True):
            total = passed + failed
            print(f"  {nodeid}: passed {passed}/{total} ({failed} failures)")

    if stable_fail:
        print(f"\nCONSISTENTLY FAILING ({len(stable_fail)}):")
        for nodeid, _, _ in stable_fail:
            print(f"  {nodeid}")

    print(f"\nSTABLE ({len(stable_pass)}): passed all {args.runs} runs")

    if flaky or stable_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
