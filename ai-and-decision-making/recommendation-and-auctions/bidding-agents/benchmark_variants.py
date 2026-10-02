"""Local paired benchmark for HW3 strategy variants (not a submission file)."""

import argparse
from collections import deque
import importlib.util
from pathlib import Path
import random
import statistics
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import server
from id_000000000_000000000 import BiddingAgent1, BiddingAgent2


def _load(module_name):
    path = ROOT / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DUMMY_MODULES = [_load(f"id_dummy_{i}") for i in range(1, 4)]


class FreshTopMixin:
    """Use only the current observable lower bound for a censored top bid."""

    def _learn_round(self, round_results):
        if round_results and round_results[0][0] != self.id:
            top_id = round_results[0][0]
            self._bid_estimate.pop(top_id, None)
        super()._learn_round(round_results)


class RecentWeightedMixin:
    """Give exponentially more weight to recent market snapshots."""

    def _metrics(self, candidates):
        snapshots = list(self._snapshots)
        if not snapshots:
            return [(0.0, 0.0) for _ in candidates]
        weights = [0.94 ** (len(snapshots) - 1 - i)
                   for i in range(len(snapshots))]
        total_weight = sum(weights)
        answer = []
        for bid in candidates:
            utility = 0.0
            spend = 0.0
            for opponents, weight in zip(snapshots, weights):
                rank = 0
                while rank < len(opponents) and opponents[rank] >= bid:
                    rank += 1
                if rank >= self.num_slots:
                    continue
                price = opponents[rank] if rank < len(opponents) else 0.0
                ctr = self.CTR_list[rank]
                spend += weight * ctr * price
                utility += weight * ctr * (self.value - price)
            answer.append((utility / total_weight, spend / total_weight))
        return answer


class LeanMixin:
    """Use fewer recent boundaries and observations for speed/generalization."""

    def _candidate_bids(self):
        if self.value <= 0.0:
            return (0.0,)
        candidates = {0.0, self.value}
        for k in range(1, 20):
            candidates.add(self.value * k / 20.0)
        for snapshot in list(self._snapshots)[-5:]:
            for threshold in snapshot[:self.num_slots]:
                if threshold < self.value:
                    candidates.add(min(self.value, threshold + 1e-5))
        return tuple(sorted(candidates))

    def _metrics(self, candidates):
        original = self._snapshots
        if len(original) > 30:
            self._snapshots = tuple(list(original)[-30:])
        try:
            return super()._metrics(candidates)
        finally:
            self._snapshots = original


class A1Current(BiddingAgent1):
    pass


class A1FreshTop(FreshTopMixin, BiddingAgent1):
    pass


class A1Weighted(RecentWeightedMixin, BiddingAgent1):
    pass


class A1FreshWeighted(FreshTopMixin, RecentWeightedMixin, BiddingAgent1):
    pass


class A1Short(BiddingAgent1):
    def start_simulation(self, *args):
        super().start_simulation(*args)
        self._snapshots = deque(maxlen=15)


class A1Lean(LeanMixin, BiddingAgent1):
    pass


class A1FreshLean(FreshTopMixin, LeanMixin, BiddingAgent1):
    pass


class A1Truth(BiddingAgent1):
    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        self.last_bid = self.value
        return self.last_bid


class A1Shade85(BiddingAgent1):
    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        self.last_bid = self.value * 0.85
        return self.last_bid


class A1Shade70(BiddingAgent1):
    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        self.last_bid = self.value * 0.70
        return self.last_bid


class A1Shade65(A1Shade70):
    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        self.last_bid = self.value * 0.65
        return self.last_bid


class A1Shade60(A1Shade70):
    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        self.last_bid = self.value * 0.60
        return self.last_bid


class A1Shade55(A1Shade70):
    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        self.last_bid = self.value * 0.55
        return self.last_bid


class A1Shade75(A1Shade70):
    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        self.last_bid = self.value * 0.75
        return self.last_bid


class FloorMixin:
    floor = 0.70

    def get_bid(self, current_budget_remaining):
        learned_bid = super().get_bid(current_budget_remaining)
        self.last_bid = max(learned_bid, self.value * self.floor)
        return self.last_bid


class A1Floor65(FloorMixin, BiddingAgent1):
    floor = 0.65


class A1Floor70(FloorMixin, BiddingAgent1):
    floor = 0.70


class A1Floor75(FloorMixin, BiddingAgent1):
    floor = 0.75


class A1Myopic(BiddingAgent1):
    def _metrics(self, candidates):
        original = self._snapshots
        if original:
            self._snapshots = (original[-1],)
        try:
            return super()._metrics(candidates)
        finally:
            self._snapshots = original


class A2Current(BiddingAgent2):
    pass


class A2FreshTop(FreshTopMixin, BiddingAgent2):
    pass


class A2Weighted(RecentWeightedMixin, BiddingAgent2):
    pass


class A2FreshWeighted(FreshTopMixin, RecentWeightedMixin, BiddingAgent2):
    pass


class A2Lean(LeanMixin, BiddingAgent2):
    pass


class A2FreshLean(FreshTopMixin, LeanMixin, BiddingAgent2):
    pass


class SpendTargetMixin:
    target_factor = 1.0

    def _paced_choice(self, candidates, metrics, spend_target):
        return super()._paced_choice(
            candidates, metrics, spend_target * self.target_factor)


class A2Target090(SpendTargetMixin, BiddingAgent2):
    target_factor = 0.90


class A2Target080(SpendTargetMixin, BiddingAgent2):
    target_factor = 0.80


class A2Target095(SpendTargetMixin, BiddingAgent2):
    target_factor = 0.95


class A2Target110(SpendTargetMixin, BiddingAgent2):
    target_factor = 1.10


class A2Target125(SpendTargetMixin, BiddingAgent2):
    target_factor = 1.25


class A2LeanTarget090(SpendTargetMixin, LeanMixin, BiddingAgent2):
    target_factor = 0.90


class A2LeanTarget095(SpendTargetMixin, LeanMixin, BiddingAgent2):
    target_factor = 0.95


class SimplePacingMixin:
    shade = 0.70

    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        rounds_left = max(1, self.T - self.current_round + 1)
        if self.total_budget <= 0.0:
            pacing_ratio = 0.0
        else:
            pacing_ratio = ((current_budget_remaining / self.total_budget) /
                            (rounds_left / self.T))
        self.last_bid = min(self.value,
                            current_budget_remaining,
                            self.value * self.shade * pacing_ratio)
        return max(0.0, self.last_bid)


class A2Simple60(SimplePacingMixin, BiddingAgent2):
    shade = 0.60


class A2Simple70(SimplePacingMixin, BiddingAgent2):
    shade = 0.70


class A2Simple80(SimplePacingMixin, BiddingAgent2):
    shade = 0.80


class PacingFloorMixin:
    floor = 0.60

    def get_bid(self, current_budget_remaining):
        learned_bid = super().get_bid(current_budget_remaining)
        rounds_left = max(1, self.T - self.current_round + 1)
        pacing_ratio = ((current_budget_remaining / self.total_budget) /
                        (rounds_left / self.T)) if self.total_budget > 0.0 else 0.0
        floor_bid = self.value * self.floor * pacing_ratio
        self.last_bid = min(self.value, current_budget_remaining,
                            max(learned_bid, floor_bid))
        return max(0.0, self.last_bid)


class A2Floor50(PacingFloorMixin, SpendTargetMixin, LeanMixin, BiddingAgent2):
    floor = 0.50
    target_factor = 0.95


class A2Floor40(PacingFloorMixin, SpendTargetMixin, LeanMixin, BiddingAgent2):
    floor = 0.40
    target_factor = 0.95


class A2Floor45(PacingFloorMixin, SpendTargetMixin, LeanMixin, BiddingAgent2):
    floor = 0.45
    target_factor = 0.95


class A2Floor55(PacingFloorMixin, SpendTargetMixin, LeanMixin, BiddingAgent2):
    floor = 0.55
    target_factor = 0.95


class A2Floor60(PacingFloorMixin, SpendTargetMixin, LeanMixin, BiddingAgent2):
    floor = 0.60
    target_factor = 0.95


class A2Floor70(PacingFloorMixin, SpendTargetMixin, LeanMixin, BiddingAgent2):
    floor = 0.70
    target_factor = 0.95


TASK1 = [A1Current, A1FreshTop, A1Weighted, A1FreshWeighted, A1Short,
         A1Lean, A1FreshLean, A1Truth, A1Shade85, A1Shade70, A1Myopic]
TASK1.extend([A1Shade55, A1Shade60, A1Shade65, A1Shade75,
              A1Floor65, A1Floor70, A1Floor75])
TASK2 = [A2Current, A2FreshTop, A2Weighted, A2FreshWeighted,
         A2Lean, A2FreshLean, A2Target080, A2Target090, A2Target095,
         A2Target110, A2Target125, A2LeanTarget090, A2LeanTarget095,
         A2Simple60, A2Simple70, A2Simple80,
         A2Floor40, A2Floor45, A2Floor50, A2Floor55, A2Floor60, A2Floor70]


def make_agents(cls, task):
    agents = [cls()]
    class_name = f"BiddingAgent{task}"
    agents.extend(getattr(module, class_name)() for module in DUMMY_MODULES)
    return agents


def benchmark(classes, task, simulations, rounds, seed, rotate_values=False):
    results = {}
    baseline_samples = None
    for cls in classes:
        samples = []
        margins = []
        by_agent = {"000000000_000000000": [], "dummy_1": [],
                    "dummy_2": [], "dummy_3": []}
        for sim in range(simulations):
            rotations = range(4) if rotate_values else range(1)
            fixed_values = [random.Random(seed + 100000 + sim * 4 + i).uniform(0, 100)
                            for i in range(4)]
            fixed_budgets = [random.Random(seed + 200000 + sim * 4 + i).gauss(10000, 750)
                             for i in range(4)]
            for rotation in rotations:
                random.seed(seed + sim)
                original_draw_value = server.draw_value
                original_gauss = random.gauss
                if rotate_values:
                    ordered = fixed_values[rotation:] + fixed_values[:rotation]
                    value_iterator = iter(ordered)
                    server.draw_value = lambda: next(value_iterator)
                    if task == 2:
                        ordered_budgets = (fixed_budgets[rotation:] +
                                           fixed_budgets[:rotation])
                        budget_iterator = iter(ordered_budgets)
                        gauss_calls = [0]
                        def controlled_gauss(mu, sigma):
                            gauss_calls[0] += 1
                            if gauss_calls[0] <= 2:
                                return original_gauss(mu, sigma)
                            return next(budget_iterator)
                        random.gauss = controlled_gauss
                try:
                    utilities = server.run_simulation(
                        make_agents(cls, task), 4, rounds,
                        enforce_budget=(task == 2))
                finally:
                    server.draw_value = original_draw_value
                    random.gauss = original_gauss
                ours = utilities["000000000_000000000"]
                samples.append(ours)
                for agent_id, utility in utilities.items():
                    by_agent[agent_id].append(utility)
                margins.append(ours - max(
                    utilities[f"dummy_{i}"] for i in range(1, 4)))
        results[cls.__name__] = (statistics.mean(samples),
                                 statistics.mean(margins),
                                 statistics.stdev(samples) / simulations ** 0.5)
        mean, margin, sem = results[cls.__name__]
        if baseline_samples is None:
            baseline_samples = samples
        paired_delta = statistics.mean(
            value - baseline for value, baseline in zip(samples, baseline_samples))
        dummy_means = [statistics.mean(by_agent[f"dummy_{i}"]) for i in range(1, 4)]
        print(f"{cls.__name__:18s} utility={mean:10.2f}  "
              f"paired_delta={paired_delta:8.2f}  "
              f"vs_mean_best={mean - max(dummy_means):9.2f}  "
              f"dummy_means={[round(x, 1) for x in dummy_means]}", flush=True)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int, choices=(1, 2), required=True)
    parser.add_argument("--simulations", type=int, default=100)
    parser.add_argument("--rounds", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--names", nargs="*",
                        help="Optional exact class names to benchmark")
    parser.add_argument("--rotate-values", action="store_true",
                        help="Rotate sampled values (and Task 2 budgets) across agents")
    args = parser.parse_args()
    classes = TASK1 if args.task == 1 else TASK2
    if args.names:
        wanted = set(args.names)
        classes = [cls for cls in classes if cls.__name__ in wanted]
    benchmark(classes, args.task, args.simulations, args.rounds, args.seed,
              rotate_values=args.rotate_values)


if __name__ == "__main__":
    main()
