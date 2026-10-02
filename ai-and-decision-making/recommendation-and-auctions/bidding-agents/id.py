"""Adaptive bidding agents for the two HW3 GSP environments.

Only Python's standard library is used.  The calculations in ``get_bid`` are
bounded by a small rolling window, so their running time does not grow with T.
"""

from collections import deque
import random


_AGENT_ID = "000000000_000000000"
_EPSILON = 1e-7


class _MarketLearner:
    """Reconstruct recent opponent bids from the public GSP outcomes."""

    def _start_market(self, num_agents, num_slots, CTR_list, value, T, window):
        self.num_agents = num_agents
        self.num_slots = num_slots
        self.CTR_list = tuple(CTR_list)
        self.value = max(0.0, float(value))
        self.T = T
        self.current_round = 0
        self.last_bid = 0.0
        self._bid_estimate = {}
        self._snapshots = deque(maxlen=window)

    def _candidate_bids(self):
        """Bids worth considering: a grid plus observed rank boundaries."""
        if self.value <= 0.0:
            return (0.0,)

        candidates = {0.0, self.value}
        # The grid makes the learner robust before all opponents are observed.
        for k in range(1, 20):
            candidates.add(self.value * k / 20.0)

        # In a GSP auction utility changes only when a bid crosses an opponent.
        # Only recent boundaries are useful in a changing market.  This also
        # keeps every callback comfortably below the strict time limit.
        # A short boundary horizon reacts quickly and avoids fitting isolated
        # old bids.  The utility estimator below still uses a longer window.
        recent = list(self._snapshots)[-5:]
        for snapshot in recent:
            for threshold in snapshot[: self.num_slots]:
                if threshold < self.value:
                    candidates.add(min(self.value, threshold + 1e-5))
        return tuple(sorted(candidates))

    def _metrics(self, candidates):
        """Return empirical (expected utility, expected spend) per candidate."""
        # Thirty observations were more stable in local paired benchmarks than
        # replaying the entire window, while also cutting callback time.
        snapshots = list(self._snapshots)[-30:]
        if not snapshots:
            return [(0.0, 0.0) for _ in candidates]

        n = float(len(snapshots))
        answer = []
        for bid in candidates:
            utility = 0.0
            spend = 0.0
            for opponents in snapshots:
                rank = 0
                # Candidate bids are placed just above learned thresholds.
                while rank < len(opponents) and opponents[rank] >= bid:
                    rank += 1
                if rank >= self.num_slots:
                    continue
                price = opponents[rank] if rank < len(opponents) else 0.0
                ctr = self.CTR_list[rank]
                spend += ctr * price
                utility += ctr * (self.value - price)
            answer.append((utility / n, spend / n))
        return answer

    def _learn_round(self, round_results):
        """Build a counterfactual opponent-bid snapshot from public results."""
        if not round_results:
            return

        winners = [(agent_id, int(slot), float(price))
                   for agent_id, slot, price in round_results]

        # Every non-top winner's bid is exactly the price of the slot above it.
        for rank in range(1, len(winners)):
            agent_id = winners[rank][0]
            if agent_id != self.id:
                self._bid_estimate[agent_id] = max(0.0, winners[rank - 1][2])

        top_id = winners[0][0]
        if top_id != self.id:
            lower_bound = max(0.0, winners[0][2]) + 1e-5
            if self.id not in (item[0] for item in winners):
                # Our bid also lost to the top bidder.
                lower_bound = max(lower_bound, self.last_bid + 1e-5)
            old = self._bid_estimate.get(top_id, lower_bound)
            self._bid_estimate[top_id] = max(old, lower_bound)

        opponent_bids = []
        for rank, (agent_id, _slot, _price) in enumerate(winners):
            if agent_id == self.id:
                continue
            if rank == 0:
                bid = self._bid_estimate.get(agent_id, winners[0][2] + 1e-5)
            else:
                bid = winners[rank - 1][2]
            opponent_bids.append(max(0.0, bid))

        # With more agents than slots, the last price is the highest losing bid.
        # It is needed when counterfactually removing ourselves from the winners.
        if self.num_agents > self.num_slots and len(winners) == self.num_slots:
            losing_bid = max(0.0, winners[-1][2])
            self_won = any(item[0] == self.id for item in winners)
            self_is_loser_at_margin = (not self_won and
                                      abs(losing_bid - self.last_bid) <= 1e-6)
            if self_won or not self_is_loser_at_margin:
                opponent_bids.append(losing_bid)

        opponent_bids.sort(reverse=True)
        self._snapshots.append(tuple(opponent_bids))


class BiddingAgent1(_MarketLearner):
    """No-budget agent: empirical best response to recent market bids."""

    def __init__(self):
        self.id = _AGENT_ID

    def start_simulation(self, num_agents, num_slots, CTR_list, value,
                         total_budget, T):
        self._start_market(num_agents, num_slots, CTR_list, value, T, window=60)

    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        if not self._snapshots:
            bid = self.value  # One safe exploratory round reveals the market.
        else:
            candidates = self._candidate_bids()
            metrics = self._metrics(candidates)
            # Prefer the lower bid on a statistical tie.
            best = max(range(len(candidates)),
                       key=lambda i: (metrics[i][0], -candidates[i]))
            bid = max(candidates[best], self.value * 0.65)
        self.last_bid = max(0.0, min(self.value, bid))
        return self.last_bid

    def notify_round_results(self, round_results):
        self._learn_round(round_results)

    def get_id(self):
        return self.id


class BiddingAgent2(_MarketLearner):
    """Budgeted agent using empirical utility and a pacing shadow price."""

    def __init__(self):
        self.id = _AGENT_ID

    def start_simulation(self, num_agents, num_slots, CTR_list, value,
                         total_budget, T):
        self._start_market(num_agents, num_slots, CTR_list, value, T, window=40)
        self.total_budget = max(0.0, float(total_budget))
        self.budget_remaining = self.total_budget
        self._last_spend = 0.0

    def _paced_choice(self, candidates, metrics, spend_target):
        """Choose a point on the empirical utility/spend frontier.

        A Lagrange multiplier prices budget.  Binary search finds the two
        frontier actions bracketing the desired average spend, and randomized
        interpolation prevents systematic under-use of the budget.
        """
        if not candidates:
            return 0.0

        def best_at(shadow_price):
            return max(range(len(candidates)),
                       key=lambda i: (metrics[i][0] - shadow_price * metrics[i][1],
                                      -candidates[i]))

        unconstrained = best_at(0.0)
        if metrics[unconstrained][1] <= spend_target:
            return candidates[unconstrained]

        low_lambda = 0.0
        high_lambda = 1.0
        low_action = unconstrained
        high_action = best_at(high_lambda)
        while metrics[high_action][1] > spend_target and high_lambda < 65536.0:
            high_lambda *= 2.0
            high_action = best_at(high_lambda)

        for _ in range(20):
            middle = (low_lambda + high_lambda) * 0.5
            action = best_at(middle)
            if metrics[action][1] > spend_target:
                low_lambda, low_action = middle, action
            else:
                high_lambda, high_action = middle, action

        costly_spend = metrics[low_action][1]
        cheap_spend = metrics[high_action][1]
        if costly_spend <= cheap_spend + _EPSILON:
            return candidates[high_action]

        probability_costly = ((spend_target - cheap_spend) /
                              (costly_spend - cheap_spend))
        if random.random() < max(0.0, min(1.0, probability_costly)):
            return candidates[low_action]
        return candidates[high_action]

    def get_bid(self, current_budget_remaining):
        self.current_round += 1
        self.budget_remaining = max(0.0, float(current_budget_remaining))
        rounds_left = max(1, self.T - self.current_round + 1)

        if self.budget_remaining <= 0.0 or self.value <= 0.0:
            self.last_bid = 0.0
            return 0.0

        if not self._snapshots:
            # Spend at most a small fraction of the budget while learning.
            bid = min(self.value, self.budget_remaining / rounds_left * 3.0)
        else:
            candidates = self._candidate_bids()
            metrics = self._metrics(candidates)
            # A small reserve corrects optimistic empirical spend estimates;
            # the target is recomputed every round, so unused reserve can still
            # be released automatically near the end of the simulation.
            target = 0.95 * self.budget_remaining / rounds_left
            bid = self._paced_choice(candidates, metrics, target)

        self.last_bid = max(0.0, min(self.value, self.budget_remaining, bid))
        return self.last_bid

    def notify_round_results(self, round_results):
        self._learn_round(round_results)

    def get_id(self):
        return self.id
