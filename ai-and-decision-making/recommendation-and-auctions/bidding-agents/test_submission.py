import ast
import contextlib
import importlib.util
import io
import math
from pathlib import Path
import random
import statistics
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "id_000000000_000000000.py"
sys.path.insert(0, str(ROOT))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def static_checks():
    source = TARGET.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= {"collections", "random"}, imports


def edge_and_timing_checks(student):
    expected_id = TARGET.stem
    durations_ms = []

    for cls in (student.BiddingAgent1, student.BiddingAgent2):
        assert cls().get_id() == expected_id

    zero = student.BiddingAgent1()
    zero.start_simulation(4, 3, [0.7, 0.4, 0.2], 0.0, float("inf"), 10)
    assert zero.get_bid(float("inf")) == 0.0
    zero.notify_round_results([])

    budget_zero = student.BiddingAgent2()
    budget_zero.start_simulation(4, 3, [0.7, 0.4, 0.2], 50.0, 0.0, 10)
    assert budget_zero.get_bid(0.0) == 0.0
    budget_zero.notify_round_results([])

    for cls, budgeted in ((student.BiddingAgent1, False),
                          (student.BiddingAgent2, True)):
        agent = cls()
        total_budget = 10000.0 if budgeted else float("inf")
        agent.start_simulation(5, 4, [0.72, 0.43, 0.26, 0.15],
                               87.0, total_budget, 3000)
        remaining = total_budget
        for round_no in range(250):
            start = time.perf_counter()
            bid = agent.get_bid(remaining)
            durations_ms.append((time.perf_counter() - start) * 1000.0)
            assert isinstance(bid, (int, float)) and math.isfinite(bid)
            assert 0.0 <= bid <= 87.0 + 1e-9
            if budgeted:
                assert bid <= remaining + 1e-9

            opponents = [
                ("opponent_a", 0, 62.0 + (round_no % 7)),
                ("opponent_b", 1, 43.0 + (round_no % 5)),
                (expected_id if round_no % 2 else "opponent_c", 2,
                 25.0 + (round_no % 3)),
                ("opponent_d", 3, 8.0 + (round_no % 2)),
            ]
            start = time.perf_counter()
            agent.notify_round_results(opponents)
            durations_ms.append((time.perf_counter() - start) * 1000.0)
            if budgeted:
                remaining = max(0.0, remaining - 1.0)

    return max(durations_ms), statistics.mean(durations_ms)


def enforced_integration_checks(student):
    server = load_module("server_under_test", ROOT / "server.py")
    dummy1 = load_module("dummy1_under_test", ROOT / "id_dummy_1.py")
    dummy2 = load_module("dummy2_under_test", ROOT / "id_dummy_2.py")
    dummy3 = load_module("dummy3_under_test", ROOT / "id_dummy_3.py")

    old_enforcement = server.CONSTANTS.ENFORCE_TIME_CAP
    server.CONSTANTS.ENFORCE_TIME_CAP = True
    summaries = []
    try:
        for task_name, student_cls, dummy_classes, budgeted in (
            (
                "agent1",
                student.BiddingAgent1,
                (dummy1.BiddingAgent1, dummy2.BiddingAgent1, dummy3.BiddingAgent1),
                False,
            ),
            (
                "agent2",
                student.BiddingAgent2,
                (dummy1.BiddingAgent2, dummy2.BiddingAgent2, dummy3.BiddingAgent2),
                True,
            ),
        ):
            for seed in (20260722, 20260723, 20260724):
                random.seed(seed)
                agents = [student_cls()] + [cls() for cls in dummy_classes]
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    utilities = server.run_simulation(
                        agents, num_slots=4, T=3000, enforce_budget=budgeted
                    )
                output = stream.getvalue().lower()
                assert "disqualified" not in output, output
                assert "exceeded" not in output, output
                assert "raised an exception" not in output, output
                own_utility = utilities[TARGET.stem]
                assert math.isfinite(own_utility)
                summaries.append((task_name, seed, own_utility))
    finally:
        server.CONSTANTS.ENFORCE_TIME_CAP = old_enforcement
    return summaries


def main():
    static_checks()
    student = load_module("submission_under_test", TARGET)
    max_ms, mean_ms = edge_and_timing_checks(student)
    summaries = enforced_integration_checks(student)
    print("STATIC_IMPORTS_OK")
    print(f"DIRECT_CALLBACK_MS max={max_ms:.3f} mean={mean_ms:.3f}")
    for task_name, seed, utility in summaries:
        print(f"ENFORCED_SIM_OK task={task_name} seed={seed} utility={utility:.3f}")
    print("ALL_TESTS_OK")


if __name__ == "__main__":
    main()
