'''HeadBook Influence Maximization — "Shield" file.

Contains:
  * Provided I/O + simulator functions (unchanged semantics).
  * Track A: evaluation, batch evaluator, penalty tuning loop.
  * Track B: risk-aware features, dynamic greedy with discounting, community cap,
    budget cleanup, improved swaps.

Allowed imports only: csv, os, random, networkx, pandas, numpy.
'''

import csv
import os
import random
import networkx as nx
import pandas as pd
import numpy as np


random.seed(21)
np.random.seed(21)

# ---------------------------------------------------------------------------
# Constants & hyperparameters
# ---------------------------------------------------------------------------

BUDGET = 1500
ROUNDS = 8

FRIENDSHIPS_FILENAME = 'HeadBook_friendships.csv'
PROBABILITIES_FILENAME = 'probabilities.csv'
COSTS_FILENAME = 'costs.csv'
EXAMPLE_INFLUENCERS_FILENAME = '000000000_000000000.csv'

# Pipeline hyperparameters. Override SMOKE=True for a fast end-to-end run.
SMOKE = False

CANDIDATE_POOL_SIZE = 80
GREEDY_TRIALS = 8
SWAP_TRIALS = 12
FINAL_TRIALS = 100
PENALTY_W = 2.5
DISCOUNT_FACTOR = 0.6
MAX_PER_COMMUNITY = 3
RANDOM_SEED = 42

# Output file used during development; rename to ID1_ID2.csv at submission time.
OUTPUT_FILENAME = '000000000_000000000.csv'


# ===========================================================================
# Provided I/O + simulator (semantics preserved)
# ===========================================================================

def read_graph(filename=FRIENDSHIPS_FILENAME):
    '''Reads the friendship graph from a CSV file.'''
    try:
        df = pd.read_csv(filename)
        graph = nx.from_pandas_edgelist(df, source='user', target='friend')
        print(f'Successfully read graph from {filename}')
        return graph
    except FileNotFoundError:
        print(f'Error: File not found - {filename}')
        return None
    except Exception as e:
        print(f'Error reading graph from {filename}: {e}')
        return None


def read_probabilities(filename=PROBABILITIES_FILENAME):
    '''Reads each user's personal reaction probabilities from a CSV file.'''
    probabilities = {}
    try:
        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            user_id = int(row['node'])
            probabilities[user_id] = {
                'p_plus':  float(row['p_plus']),
                'p_minus': float(row['p_minus']),
                'a_plus':  float(row['a_plus']),
                'a_minus': float(row['a_minus']),
            }
        print(f'Probabilities loaded for {len(probabilities)} users.')
        return probabilities
    except FileNotFoundError:
        print(f'Error: File not found - {filename}')
        return None
    except Exception as e:
        print(f'Error reading probabilities: {e}')
        return None


def read_costs(filename=COSTS_FILENAME):
    '''Reads influencer costs from a CSV file.'''
    costs = {}
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                user_id = int(row[0])
                cost = float(row[1])
                costs[user_id] = cost
        print(f'Successfully read costs from {filename}')
        return costs
    except FileNotFoundError:
        print(f'Error: File not found - {filename}')
        return None
    except Exception as e:
        print(f'Error reading costs from {filename}: {e}')
        return None


def simulate_influence(graph, initial_influencers, probabilities, rounds=ROUNDS):
    '''Runs one simulation of the influence cascade on Headbook.

    Returns net support = (number of Pro users) - (number of Anti users).
    Semantics: only newly-active nodes send messages; each sender sends once
    to every neighbor; ties leave the receiver Unaffected; states are permanent.
    '''
    states = {node: 'U' for node in graph.nodes()}

    for node in initial_influencers:
        if node not in states:
            continue
        states[node] = 'P'

    newly_active = {node: 'P' for node in initial_influencers if node in states}

    for _ in range(rounds):
        if not newly_active:
            break

        messages_received = {}
        for sender, msg_type in newly_active.items():
            for target in graph.neighbors(sender):
                if states[target] == 'U':
                    if target not in messages_received:
                        messages_received[target] = {'P': 0, 'A': 0}
                    messages_received[target][msg_type] += 1

        next_active = {}
        for node, msgs in messages_received.items():
            p = probabilities.get(node, {'p_plus': 0, 'p_minus': 0, 'a_plus': 0, 'a_minus': 0})
            X_P = 0
            X_A = 0
            for _ in range(msgs['P']):
                if random.random() < p['p_plus']:
                    X_P += 1
                if random.random() < p['p_minus']:
                    X_A += 1
            for _ in range(msgs['A']):
                if random.random() < p['a_plus']:
                    X_A += 1
                if random.random() < p['a_minus']:
                    X_P += 1

            if X_P > X_A:
                states[node] = 'P'
                next_active[node] = 'P'
            elif X_A > X_P:
                states[node] = 'A'
                next_active[node] = 'A'

        newly_active = next_active

    total_P = sum(1 for s in states.values() if s == 'P')
    total_A = sum(1 for s in states.values() if s == 'A')
    return total_P - total_A


def read_influencers_from_csv(filename, costs):
    '''Reads selected influencers from a CSV and validates them.'''
    selected_influencers = []
    total_cost = 0
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            if header != ['user_id']:
                print(f'Error: Invalid header in {filename}. Expected ["user_id"], got {header}.')
                return None

            seen_ids = set()
            for i, row in enumerate(reader):
                if len(row) != 1:
                    print(f'Error: Invalid row in {filename} line {i+2}: {row}.')
                    return None
                try:
                    user_id = int(row[0])
                except ValueError:
                    print(f'Error: Invalid user ID in {filename} line {i+2}: {row[0]}.')
                    return None
                if user_id not in costs:
                    print(f'Error: user {user_id} not in cost data.')
                    return None
                if user_id in seen_ids:
                    print(f'Error: Duplicate user {user_id}.')
                    return None
                selected_influencers.append(user_id)
                seen_ids.add(user_id)
                total_cost += costs[user_id]

        if total_cost > BUDGET:
            print(f'Error: cost {total_cost:.2f} exceeds budget {BUDGET}.')
            return None

        print(f'Validated {len(selected_influencers)} influencers from {filename}, cost {total_cost:.0f}/{BUDGET}.')
        return selected_influencers
    except FileNotFoundError:
        print(f'Error: File not found - {filename}')
        return None
    except Exception as e:
        print(f'Error reading influencers: {e}')
        return None


def submit_influencers(influencer_list, id1, id2, costs, filename=None):
    '''Validates an influencer list and writes the submission CSV. Returns bool.'''
    if filename is None:
        filename = f'{id1}_{id2}.csv'

    if not isinstance(influencer_list, list):
        print('Error: influencer_list must be a list.')
        return False
    if not (isinstance(id1, str) and id1 and isinstance(id2, str) and id2):
        print('Error: Student IDs must be non-empty strings.')
        return False
    if not influencer_list:
        print('Warning: The influencer list is empty.')

    validated = []
    seen = set()
    total_cost = 0.0
    for i, influencer in enumerate(influencer_list):
        try:
            influencer = int(float(influencer))
        except (ValueError, TypeError):
            print(f'Error: Item {i+1} is not a valid integer: {influencer}')
            return False
        if influencer not in costs:
            print(f'Error: user_id {influencer} does not exist.')
            return False
        if influencer in seen:
            print(f'Error: Duplicate user_id {influencer}.')
            return False
        seen.add(influencer)
        total_cost += costs[influencer]
        validated.append(influencer)

    if total_cost > BUDGET:
        print(f'Error: Total cost {total_cost:.0f} exceeds budget {BUDGET}.')
        return False

    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id'])
            for user_id in sorted(validated):
                writer.writerow([user_id])
        print(f'Submission saved to {filename} ({len(validated)} influencers, cost {total_cost:.0f}/{BUDGET}).')
        return True
    except Exception as e:
        print(f'Error writing file: {e}')
        return False


# ===========================================================================
# Track A: Evaluation, batch evaluator, tuning loop
# ===========================================================================

def total_cost(influencers, costs):
    return sum(costs[u] for u in influencers)


def evaluate_set(graph, influencers, probabilities, trials, base_seed=RANDOM_SEED):
    '''Run `trials` simulations of `influencers` using CRN seeds derived from base_seed.

    Common Random Numbers: identical trial indices use identical RNG seeds, so two
    candidate sets compared at the same step share the same randomness and the
    comparison has lower variance.
    '''
    scores = np.empty(trials, dtype=np.int64)
    for i in range(trials):
        random.seed(base_seed + i)
        np.random.seed(base_seed + i)
        scores[i] = simulate_influence(graph, influencers, probabilities)
    mean = float(scores.mean())
    std = float(scores.std(ddof=0))
    p10 = float(np.percentile(scores, 10))
    p90 = float(np.percentile(scores, 90))
    return mean, std, p10, p90, int(scores.min()), int(scores.max())


def batch_evaluator(graph, influencers, probabilities, trials=100, base_seed=10_000):
    '''Unbiased estimate using fresh (non-CRN) seeds. Returns (mean, std, ci95).'''
    scores = np.empty(trials, dtype=np.int64)
    for i in range(trials):
        random.seed(base_seed + i)
        np.random.seed(base_seed + i)
        scores[i] = simulate_influence(graph, influencers, probabilities)
    mean = float(scores.mean())
    std = float(scores.std(ddof=1)) if trials > 1 else 0.0
    ci95 = 1.96 * std / max(np.sqrt(trials), 1.0)
    return mean, std, float(ci95)


def tune_penalty(graph, costs, probabilities, weights=None, trials_per=30):
    '''Sweep PENALTY_W over `weights`, run the full pipeline for each, return DataFrame.'''
    if weights is None:
        weights = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

    rows = []
    for w in weights:
        print(f'\n=== Tuning PENALTY_W = {w} ===')
        selected = run_pipeline(graph, costs, probabilities, penalty_w=w)
        mean, std, ci95 = batch_evaluator(graph, selected, probabilities, trials=trials_per)
        rows.append({
            'penalty_w': w,
            'mean': mean,
            'std': std,
            'ci95': ci95,
            'n_selected': len(selected),
            'cost_used': total_cost(selected, costs),
            'score_adj': mean - 0.25 * std,
        })
        print(f'  -> n={len(selected)} cost={rows[-1]["cost_used"]:.0f} mean={mean:.2f} +/- {ci95:.2f}')

    df = pd.DataFrame(rows).sort_values('score_adj', ascending=False).reset_index(drop=True)
    return df


# ===========================================================================
# Track B: Risk-aware features, dynamic greedy, swaps
# ===========================================================================

def simple_pagerank(graph, damping=0.85, iterations=40):
    '''Pure-Python PageRank (no scipy needed).'''
    nodes = list(graph.nodes())
    n = len(nodes)
    rank = {node: 1.0 / n for node in nodes}
    base = (1.0 - damping) / n
    for _ in range(iterations):
        new_rank = {node: base for node in nodes}
        for node in nodes:
            degree = graph.degree(node)
            if degree == 0:
                share = damping * rank[node] / n
                for target in nodes:
                    new_rank[target] += share
            else:
                share = damping * rank[node] / degree
                for target in graph.neighbors(node):
                    new_rank[target] += share
        rank = new_rank
    return rank


def compute_node_features(graph, costs, probabilities, penalty_w=PENALTY_W):
    '''Per-node features including risk-adjusted local quality.

    Risk-adjusted local quality for a candidate v:
        average over neighbors u of v of
            (p_plus[u] + a_minus[u]) - penalty_w * (p_minus[u] + a_plus[u])
    This rewards neighbors who turn positive on positive messages and counter-boomerang
    on negative ones, and penalizes neighbors who flip negative (boomerang).
    '''
    pagerank = simple_pagerank(graph, damping=0.85, iterations=40)

    rows = []
    for node in graph.nodes():
        degree = graph.degree(node)
        cost = costs[node]
        neighbors = list(graph.neighbors(node))
        if neighbors:
            vals = []
            for u in neighbors:
                p = probabilities.get(u, {'p_plus': 0, 'p_minus': 0, 'a_plus': 0, 'a_minus': 0})
                vals.append((p['p_plus'] + p['a_minus']) - penalty_w * (p['p_minus'] + p['a_plus']))
            risk_quality = float(np.mean(vals))
        else:
            risk_quality = 0.0

        deg_per_cost = degree / cost if cost > 0 else 0.0
        pr_per_cost = pagerank[node] / cost if cost > 0 else 0.0
        heuristic = 0.45 * deg_per_cost + 0.30 * (pr_per_cost * 1000.0) + 0.25 * risk_quality

        rows.append({
            'user_id': node,
            'degree': degree,
            'cost': cost,
            'pagerank': pagerank[node],
            'deg_per_cost': deg_per_cost,
            'pr_per_cost': pr_per_cost,
            'risk_quality': risk_quality,
            'heuristic': heuristic,
        })

    return pd.DataFrame(rows)


def build_candidate_pool(features, pool_size=CANDIDATE_POOL_SIZE):
    '''Union of top-K from four rankings.'''
    per_method = max(8, pool_size // 4)
    rankings = [
        features.sort_values('heuristic', ascending=False),
        features.sort_values('degree', ascending=False),
        features.sort_values('deg_per_cost', ascending=False),
        features.sort_values('pr_per_cost', ascending=False),
    ]
    pool = []
    seen = set()
    for view in rankings:
        for uid in view.head(per_method)['user_id']:
            uid = int(uid)
            if uid not in seen:
                seen.add(uid)
                pool.append(uid)
    return pool[:pool_size]


def detect_communities(graph):
    '''Return {node: community_label}. Uses greedy modularity (ships with networkx).'''
    try:
        from networkx.algorithms.community import greedy_modularity_communities
        comms = list(greedy_modularity_communities(graph))
    except Exception as e:
        print(f'  community detection failed ({e}); falling back to connected components.')
        comms = list(nx.connected_components(graph))
    label = {}
    for i, comm in enumerate(comms):
        for node in comm:
            label[node] = i
    for node in graph.nodes():
        label.setdefault(node, -1)
    return label


def dynamic_greedy(graph, candidate_ids, costs, probabilities, communities,
                   greedy_trials=GREEDY_TRIALS, discount_factor=DISCOUNT_FACTOR,
                   max_per_community=MAX_PER_COMMUNITY):
    '''Greedy with neighbor-coverage discounting and community cap.

    Tolerance to avoid stopping on noise: 0.5 * std / sqrt(trials).
    '''
    selected = []
    selected_set = set()
    covered_count = {n: 0 for n in graph.nodes()}
    community_count = {}

    current_mean = 0.0
    current_std = 0.0

    print('\nDynamic greedy:')
    step = 0
    while True:
        remaining = BUDGET - total_cost(selected, costs)
        affordable = []
        for node in candidate_ids:
            if node in selected_set:
                continue
            if costs[node] > remaining:
                continue
            c_label = communities.get(node, -1)
            if community_count.get(c_label, 0) >= max_per_community:
                continue
            affordable.append(node)

        if not affordable:
            break

        # Use same CRN seed across all candidate evaluations this step (variance reduction).
        step_seed = RANDOM_SEED + step * 1000
        best_node = None
        best_adj_mean = -1e18
        best_raw_mean = -1e18
        best_std = 0.0

        for node in affordable:
            trial = selected + [node]
            mean, std, _, _, _, _ = evaluate_set(graph, trial, probabilities, greedy_trials, base_seed=step_seed)
            # Discount: degrade gain by how much this node's audience is already covered.
            neighbors = list(graph.neighbors(node))
            if neighbors:
                max_cov = max(covered_count[n] for n in neighbors)
            else:
                max_cov = 0
            adj_mean = mean * (discount_factor ** max_cov) if max_cov > 0 else mean

            if adj_mean > best_adj_mean:
                best_adj_mean = adj_mean
                best_raw_mean = mean
                best_std = std
                best_node = node

        tolerance = 0.5 * best_std / max(np.sqrt(greedy_trials), 1.0)
        if best_node is None or best_raw_mean <= current_mean - tolerance:
            break

        selected.append(best_node)
        selected_set.add(best_node)
        current_mean = best_raw_mean
        current_std = best_std
        c_label = communities.get(best_node, -1)
        community_count[c_label] = community_count.get(c_label, 0) + 1
        for n in graph.neighbors(best_node):
            covered_count[n] += 1

        cost_used = total_cost(selected, costs)
        print(f'  step {step+1:2d}: add {best_node:5d} | cost {cost_used:5.0f}/{BUDGET} | '
              f'mean {current_mean:8.2f} | std {current_std:6.2f} | community {c_label}')
        step += 1

    return selected


def budget_cleanup(graph, selected, candidate_ids, costs, probabilities,
                   greedy_trials=GREEDY_TRIALS):
    '''Spend leftover budget on cheap candidates that still improve mean.'''
    print('\nBudget cleanup:')
    selected = list(selected)
    selected_set = set(selected)
    current_mean, _, _, _, _, _ = evaluate_set(graph, selected, probabilities, greedy_trials,
                                                base_seed=RANDOM_SEED + 999_000)
    remaining = BUDGET - total_cost(selected, costs)
    cheap = sorted([u for u in candidate_ids if u not in selected_set and costs[u] <= remaining],
                   key=lambda u: costs[u])
    if not cheap:
        print('  no affordable cleanup candidates.')
        return selected

    seed = RANDOM_SEED + 999_000
    for u in cheap:
        if costs[u] > BUDGET - total_cost(selected, costs):
            continue
        trial = selected + [u]
        mean, _, _, _, _, _ = evaluate_set(graph, trial, probabilities, greedy_trials, base_seed=seed)
        if mean > current_mean:
            selected.append(u)
            selected_set.add(u)
            current_mean = mean
            print(f'  add cheap {u} | cost {total_cost(selected, costs):.0f}/{BUDGET} | mean {mean:.2f}')

    return selected


def improved_swaps(graph, selected, candidate_ids, costs, probabilities,
                   swap_trials=SWAP_TRIALS, max_passes=5):
    '''1-for-1, 1-for-2, 2-for-1 swaps under CRN. Accept only if mean improves > tolerance.'''
    print('\nImproved swaps:')
    best = list(selected)
    base_seed = RANDOM_SEED + 500_000
    best_mean, best_std, _, _, _, _ = evaluate_set(graph, best, probabilities, swap_trials, base_seed=base_seed)
    tolerance = 0.5 * best_std / max(np.sqrt(swap_trials), 1.0)

    cand_set = list(set(candidate_ids))

    for pass_i in range(max_passes):
        improved = False

        # 1-for-1
        best_swap = None
        for old in list(best):
            for new in cand_set:
                if new in best:
                    continue
                trial = [n for n in best if n != old] + [new]
                if total_cost(trial, costs) > BUDGET:
                    continue
                mean, _, _, _, _, _ = evaluate_set(graph, trial, probabilities, swap_trials, base_seed=base_seed)
                if mean > best_mean + tolerance:
                    if best_swap is None or mean > best_swap[0]:
                        best_swap = (mean, trial, f'1-for-1 {old}->{new}')
        if best_swap is not None:
            best_mean, best, msg = best_swap[0], best_swap[1], best_swap[2]
            print(f'  pass {pass_i+1}: {msg} | mean {best_mean:.2f}')
            improved = True
            continue

        # 1-for-2 (drop one, add two cheaper)
        best_swap = None
        for old in list(best):
            saved = costs[old]
            for i, n1 in enumerate(cand_set):
                if n1 in best or n1 == old:
                    continue
                if costs[n1] >= saved:
                    continue
                for n2 in cand_set[i+1:]:
                    if n2 in best or n2 == old:
                        continue
                    trial = [n for n in best if n != old] + [n1, n2]
                    if total_cost(trial, costs) > BUDGET:
                        continue
                    mean, _, _, _, _, _ = evaluate_set(graph, trial, probabilities, swap_trials, base_seed=base_seed)
                    if mean > best_mean + tolerance:
                        if best_swap is None or mean > best_swap[0]:
                            best_swap = (mean, trial, f'1-for-2 {old}->{n1}+{n2}')
        if best_swap is not None:
            best_mean, best, msg = best_swap[0], best_swap[1], best_swap[2]
            print(f'  pass {pass_i+1}: {msg} | mean {best_mean:.2f}')
            improved = True
            continue

        # 2-for-1 (drop two, add one)
        best_swap = None
        sel_list = list(best)
        for i, old1 in enumerate(sel_list):
            for old2 in sel_list[i+1:]:
                freed = costs[old1] + costs[old2]
                for new in cand_set:
                    if new in best:
                        continue
                    if costs[new] > freed + (BUDGET - total_cost(best, costs)):
                        continue
                    trial = [n for n in best if n != old1 and n != old2] + [new]
                    if total_cost(trial, costs) > BUDGET:
                        continue
                    mean, _, _, _, _, _ = evaluate_set(graph, trial, probabilities, swap_trials, base_seed=base_seed)
                    if mean > best_mean + tolerance:
                        if best_swap is None or mean > best_swap[0]:
                            best_swap = (mean, trial, f'2-for-1 {old1}+{old2}->{new}')
        if best_swap is not None:
            best_mean, best, msg = best_swap[0], best_swap[1], best_swap[2]
            print(f'  pass {pass_i+1}: {msg} | mean {best_mean:.2f}')
            improved = True
            continue

        if not improved:
            break

    return best


def run_pipeline(graph, costs, probabilities, penalty_w=PENALTY_W,
                 pool_size=CANDIDATE_POOL_SIZE, greedy_trials=GREEDY_TRIALS,
                 swap_trials=SWAP_TRIALS):
    '''End-to-end: features -> pool -> dynamic greedy -> cleanup -> swaps.'''
    features = compute_node_features(graph, costs, probabilities, penalty_w=penalty_w)
    pool = build_candidate_pool(features, pool_size=pool_size)
    communities = detect_communities(graph)
    selected = dynamic_greedy(graph, pool, costs, probabilities, communities,
                              greedy_trials=greedy_trials)
    selected = budget_cleanup(graph, selected, pool, costs, probabilities,
                              greedy_trials=greedy_trials)
    selected = improved_swaps(graph, selected, pool, costs, probabilities,
                              swap_trials=swap_trials)
    return selected


# ===========================================================================
# Main
# ===========================================================================

def main():
    print('--- HeadBook Influence Maximization ---')
    print('Loading data...')
    graph = read_graph()
    probabilities = read_probabilities()
    costs = read_costs()
    if graph is None or probabilities is None or costs is None:
        print('Error loading data. Exiting.')
        return

    print(f'Nodes: {graph.number_of_nodes()}, Edges: {graph.number_of_edges()}, Budget: {BUDGET}')

    if SMOKE:
        pool_size = 40
        greedy_trials = 3
        swap_trials = 4
        final_trials = 10
        print('\n(SMOKE mode: tiny pool/trials.)')
    else:
        pool_size = CANDIDATE_POOL_SIZE
        greedy_trials = GREEDY_TRIALS
        swap_trials = SWAP_TRIALS
        final_trials = FINAL_TRIALS

    if os.path.exists(EXAMPLE_INFLUENCERS_FILENAME):
        example = read_influencers_from_csv(EXAMPLE_INFLUENCERS_FILENAME, costs)
        if example is not None:
            mean, std, ci95 = batch_evaluator(graph, example, probabilities, trials=min(final_trials, 30))
            print(f'Example file mean over {min(final_trials, 30)}: {mean:.2f} +/- {ci95:.2f}')

    selected = run_pipeline(graph, costs, probabilities,
                            penalty_w=PENALTY_W, pool_size=pool_size,
                            greedy_trials=greedy_trials, swap_trials=swap_trials)

    print('\nFinal selection:')
    print(f'  influencers ({len(selected)}): {sorted(selected)}')
    print(f'  cost: {total_cost(selected, costs):.0f}/{BUDGET}')

    final_mean, final_std, final_ci = batch_evaluator(graph, selected, probabilities, trials=final_trials)
    print(f'  mean over {final_trials} trials: {final_mean:.2f} +/- {final_ci:.2f} (std {final_std:.2f})')

    submit_influencers(selected, 'solution', 'output', costs, filename=OUTPUT_FILENAME)


if __name__ == '__main__':
    main()
