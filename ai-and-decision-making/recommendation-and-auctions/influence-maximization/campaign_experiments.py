'''Experimental lab for HW1 — Influence Maximization.

Imports campaign_simulation as a read-only library. Adds:
  * compute_node_features_v2 — risk metric extended to 2-hop neighbors with decay.
  * celf_greedy             — lazy-evaluation greedy (CELF) using a max-heap.
  * run_experiment           — one end-to-end pipeline run returning a metrics dict.
  * grid_search              — sweeps hyperparameters, appends rows to CSV.

This file is NEVER part of the submission. Tomorrow we pick a winning knob
from experiments_best.csv and backport ONLY that change to the shield.
'''

import csv
import heapq
import itertools
import os
import time

import networkx as nx
import numpy as np
import pandas as pd

import influence_maximization as cs


# ---------------------------------------------------------------------------
# Lab knobs
# ---------------------------------------------------------------------------

SMOKE = False  # flip True for a one-combo dry run

LOG_PATH = 'experiments_log.csv'
BEST_PATH = 'experiments_best.csv'


# ---------------------------------------------------------------------------
# Multi-hop risk feature
# ---------------------------------------------------------------------------

def _per_neighbor_score(prob_dict, penalty_w):
    '''(p_plus + a_minus) - penalty_w * (p_minus + a_plus). Same as shield.'''
    return (prob_dict['p_plus'] + prob_dict['a_minus']) - penalty_w * (prob_dict['p_minus'] + prob_dict['a_plus'])


def compute_node_features_v2(
    graph, costs, probabilities,
    penalty_w=None,
    w_deg=0.45, w_pr=0.30, w_risk=0.25,
    hop2_decay=0.0,
    pagerank=None,
):
    '''Drop-in replacement for cs.compute_node_features with multi-hop risk + configurable weights.

    risk_quality(v) = mean_s(N1) + hop2_decay * mean_s(N2),
        where s(u) = (p_plus[u] + a_minus[u]) - penalty_w * (p_minus[u] + a_plus[u]).
    hop2_decay = 0 reproduces the shield's behavior.
    '''
    if penalty_w is None:
        penalty_w = cs.PENALTY_W
    if pagerank is None:
        pagerank = cs.simple_pagerank(graph, damping=0.85, iterations=40)

    default_p = {'p_plus': 0, 'p_minus': 0, 'a_plus': 0, 'a_minus': 0}
    node_score = {
        n: _per_neighbor_score(probabilities.get(n, default_p), penalty_w)
        for n in graph.nodes()
    }

    rows = []
    for node in graph.nodes():
        degree = graph.degree(node)
        cost = costs[node]

        if hop2_decay > 0:
            # BFS to depth 2; bucket by exact distance.
            dist = nx.single_source_shortest_path_length(graph, node, cutoff=2)
            n1 = [u for u, d in dist.items() if d == 1]
            n2 = [u for u, d in dist.items() if d == 2]
        else:
            n1 = list(graph.neighbors(node))
            n2 = []

        if n1:
            mean1 = float(np.mean([node_score[u] for u in n1]))
        else:
            mean1 = 0.0
        if n2:
            mean2 = float(np.mean([node_score[u] for u in n2]))
        else:
            mean2 = 0.0

        risk_quality = mean1 + hop2_decay * mean2

        deg_per_cost = degree / cost if cost > 0 else 0.0
        pr_per_cost = pagerank[node] / cost if cost > 0 else 0.0
        heuristic = w_deg * deg_per_cost + w_pr * (pr_per_cost * 1000.0) + w_risk * risk_quality

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


# ---------------------------------------------------------------------------
# CELF lazy greedy
# ---------------------------------------------------------------------------

def _evaluate_with_crn(graph, influencers, probabilities, base_seed, trials):
    '''Run `trials` simulations with the fixed scenario seeds [base_seed .. base_seed+trials-1].

    Identical to cs.evaluate_set but with a fixed seed set across the whole CELF run
    so marginal gains are comparable across iterations (key requirement for lazy greedy).
    Returns (mean, std).
    '''
    import random as _random
    scores = np.empty(trials, dtype=np.int64)
    for i in range(trials):
        _random.seed(base_seed + i)
        np.random.seed(base_seed + i)
        scores[i] = cs.simulate_influence(graph, influencers, probabilities)
    mean = float(scores.mean())
    std = float(scores.std(ddof=0))
    return mean, std


def celf_greedy(
    graph, candidate_ids, costs, probabilities, communities,
    greedy_trials=None,
    discount_factor=None,
    max_per_community=None,
    base_seed=None,
    verbose=True,
):
    '''Lazy-evaluation greedy with neighbor-coverage discount + community cap.

    Uses fixed scenario seeds across the whole run so popped upper-bound gains
    remain comparable as the selected set grows (approximate submodularity).
    '''
    if greedy_trials is None:
        greedy_trials = cs.GREEDY_TRIALS
    if discount_factor is None:
        discount_factor = cs.DISCOUNT_FACTOR
    if max_per_community is None:
        max_per_community = cs.MAX_PER_COMMUNITY
    if base_seed is None:
        base_seed = cs.RANDOM_SEED

    selected = []
    selected_set = set()
    covered_count = {n: 0 for n in graph.nodes()}
    community_count = {}

    # Initial gains vs empty set.
    heap = []
    for v in candidate_ids:
        mean, std = _evaluate_with_crn(graph, [v], probabilities, base_seed, greedy_trials)
        # last_step=0 means "computed against |selected|=0".
        heapq.heappush(heap, (-mean, v, 0, std))

    current_mean = 0.0

    if verbose:
        print('\nCELF greedy:')
    step = 0
    reevals = 0
    while heap:
        # Pop the candidate with the (currently) highest marginal-gain upper bound.
        try:
            neg_gain, v, last_step, last_std = heapq.heappop(heap)
        except IndexError:
            break

        if v in selected_set:
            continue
        remaining = cs.BUDGET - cs.total_cost(selected, costs)
        if costs[v] > remaining:
            continue
        c_label = communities.get(v, -1)
        if community_count.get(c_label, 0) >= max_per_community:
            continue

        if last_step == len(selected):
            # Gain is fresh — accept this candidate.
            fresh_gain = -neg_gain
            # Standard CELF stop: stop when the best marginal gain becomes non-positive.
            # Leftover budget is then filled by cs.budget_cleanup, which uses an
            # independent seed pool and behaves like a careful cost-aware greedy.
            if fresh_gain <= 0:
                if verbose:
                    print(f'  stop: best fresh gain {fresh_gain:.2f} <= 0')
                break

            selected.append(v)
            selected_set.add(v)
            community_count[c_label] = community_count.get(c_label, 0) + 1
            for n in graph.neighbors(v):
                covered_count[n] += 1
            current_mean += fresh_gain

            cost_used = cs.total_cost(selected, costs)
            if verbose:
                print(f'  step {step+1:2d}: add {v:5d} | cost {cost_used:5.0f}/{cs.BUDGET} | '
                      f'mean ~{current_mean:8.2f} | gain {fresh_gain:7.2f} | community {c_label} | reevals {reevals}')
            step += 1
            reevals = 0
        else:
            # Stale — re-evaluate against the current selection and push back.
            mean, std = _evaluate_with_crn(graph, selected + [v], probabilities, base_seed, greedy_trials)
            raw_gain = mean - current_mean
            # Apply neighbor-coverage discount.
            neighbors = list(graph.neighbors(v))
            if neighbors:
                max_cov = max(covered_count[n] for n in neighbors)
            else:
                max_cov = 0
            adj_gain = raw_gain * (discount_factor ** max_cov) if max_cov > 0 else raw_gain
            heapq.heappush(heap, (-adj_gain, v, len(selected), std))
            reevals += 1

    return selected


# ---------------------------------------------------------------------------
# One experiment + grid search
# ---------------------------------------------------------------------------

def build_pool_v2(features, pool_size, heuristic_only=False):
    '''Pool builder with optional 'heuristic-only' mode for proper multi-hop A/B.

    heuristic_only=True: take top `pool_size` by `heuristic` column only — so
    changes to risk_quality (and thus hop2_decay / w_risk) actually move the pool.
    heuristic_only=False: same as cs.build_candidate_pool (union of 4 rankings).
    '''
    if heuristic_only:
        view = features.sort_values('heuristic', ascending=False)
        return [int(u) for u in view.head(pool_size)['user_id']]
    return cs.build_candidate_pool(features, pool_size=pool_size)


_PAGERANK_CACHE = {}
_COMMUNITIES_CACHE = {}


def _cached_pagerank(graph):
    key = id(graph)
    if key not in _PAGERANK_CACHE:
        _PAGERANK_CACHE[key] = cs.simple_pagerank(graph, damping=0.85, iterations=40)
    return _PAGERANK_CACHE[key]


def _cached_communities(graph):
    key = id(graph)
    if key not in _COMMUNITIES_CACHE:
        _COMMUNITIES_CACHE[key] = cs.detect_communities(graph)
    return _COMMUNITIES_CACHE[key]


def run_experiment(graph, costs, probabilities, config):
    '''Run one combo end-to-end. Returns a flat dict with metrics + config echoed back.'''
    t0 = time.time()

    features = compute_node_features_v2(
        graph, costs, probabilities,
        penalty_w=config['penalty_w'],
        w_deg=config['w_deg'], w_pr=config['w_pr'], w_risk=config['w_risk'],
        hop2_decay=config['hop2_decay'],
        pagerank=_cached_pagerank(graph),
    )
    pool = build_pool_v2(features, pool_size=config['pool_size'],
                         heuristic_only=config.get('heuristic_only_pool', False))
    communities = _cached_communities(graph)

    selected = celf_greedy(
        graph, pool, costs, probabilities, communities,
        greedy_trials=config['greedy_trials'],
        discount_factor=config['discount_factor'],
        max_per_community=config['max_per_community'],
        verbose=False,
    )
    selected = cs.budget_cleanup(graph, selected, pool, costs, probabilities,
                                 greedy_trials=config['greedy_trials'])
    if config.get('use_swaps'):
        selected = cs.improved_swaps(graph, selected, pool, costs, probabilities,
                                     swap_trials=config['swap_trials'])

    mean, std, ci95 = cs.batch_evaluator(graph, selected, probabilities,
                                         trials=config['final_trials'])
    elapsed = time.time() - t0

    row = dict(config)  # echo config so each CSV row is self-describing
    row.update({
        'mean': mean,
        'std': std,
        'ci95': ci95,
        'n_selected': len(selected),
        'cost_used': cs.total_cost(selected, costs),
        'elapsed_s': round(elapsed, 2),
        'score_adj': mean - 0.25 * std,
        'selected': '|'.join(str(u) for u in sorted(selected)),
    })
    return row


def _append_csv_row(path, row):
    '''Append a single dict as a row; write header if file is new. Resumable.'''
    file_exists = os.path.exists(path) and os.path.getsize(path) > 0
    fieldnames = list(row.keys())
    with open(path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def grid_search(graph, costs, probabilities, grid, log_path=LOG_PATH, fixed=None):
    '''Sweep grid combos, write rows incrementally to log_path. Returns DataFrame of all rows.'''
    if fixed is None:
        fixed = {}

    keys = list(grid.keys())
    values = [grid[k] for k in keys]
    combos = list(itertools.product(*values))
    print(f'Grid: {len(combos)} combinations across {keys}')

    for i, combo in enumerate(combos, 1):
        config = dict(fixed)
        for k, v in zip(keys, combo):
            if k == 'weights':
                w_deg, w_pr, w_risk = v
                config['w_deg'] = w_deg
                config['w_pr'] = w_pr
                config['w_risk'] = w_risk
            else:
                config[k] = v

        print(f'\n--- combo {i}/{len(combos)} ---')
        for k in keys:
            print(f'    {k} = {config.get(k) if k != "weights" else (config["w_deg"], config["w_pr"], config["w_risk"])}')

        try:
            row = run_experiment(graph, costs, probabilities, config)
        except Exception as e:
            print(f'  ERROR: {e}')
            row = dict(config)
            row.update({'mean': float('nan'), 'std': float('nan'), 'ci95': float('nan'),
                        'n_selected': 0, 'cost_used': 0, 'elapsed_s': 0.0,
                        'score_adj': float('-inf'), 'selected': '', 'error': str(e)})
        _append_csv_row(log_path, row)
        print(f'  -> mean={row["mean"]} std={row["std"]} cost={row["cost_used"]} '
              f'n={row["n_selected"]} elapsed={row["elapsed_s"]}s')

    df = pd.read_csv(log_path)
    top = df.sort_values('score_adj', ascending=False).head(10)
    top.to_csv(BEST_PATH, index=False)
    print(f'\nWrote top 10 to {BEST_PATH}.')
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _smoke_unit_checks(graph, costs, probabilities):
    '''Quick sanity checks: multi-hop adds a non-zero 2-hop term; CELF vs shield overlap.'''
    print('\n[Smoke] Multi-hop risk check on a high-degree node:')
    high_deg_node = max(graph.nodes(), key=lambda n: graph.degree(n))
    f0 = compute_node_features_v2(graph, costs, probabilities, hop2_decay=0.0)
    f1 = compute_node_features_v2(graph, costs, probabilities, hop2_decay=0.5)
    r0 = float(f0.loc[f0['user_id'] == high_deg_node, 'risk_quality'].iloc[0])
    r1 = float(f1.loc[f1['user_id'] == high_deg_node, 'risk_quality'].iloc[0])
    print(f'  node {high_deg_node} (degree {graph.degree(high_deg_node)}): '
          f'risk_quality hop2_decay=0.0 -> {r0:.4f}; hop2_decay=0.5 -> {r1:.4f}; delta {r1 - r0:+.4f}')

    print('\n[Smoke] CELF vs cs.dynamic_greedy overlap check:')
    features = compute_node_features_v2(graph, costs, probabilities, hop2_decay=0.0)
    pool = cs.build_candidate_pool(features, pool_size=30)
    communities = _cached_communities(graph)
    sel_celf = celf_greedy(graph, pool, costs, probabilities, communities,
                           greedy_trials=4, discount_factor=0.6, max_per_community=3, verbose=False)
    sel_shield = cs.dynamic_greedy(graph, pool, costs, probabilities, communities,
                                   greedy_trials=4, discount_factor=0.6, max_per_community=3)
    s1, s2 = set(sel_celf), set(sel_shield)
    jacc = len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 1.0
    print(f'  CELF: {sorted(sel_celf)}')
    print(f'  shield: {sorted(sel_shield)}')
    print(f'  Jaccard overlap: {jacc:.2f}')


def main():
    print('--- Campaign Experiments Lab ---')
    print(f'SMOKE = {SMOKE}')

    graph = cs.read_graph()
    costs = cs.read_costs()
    probabilities = cs.read_probabilities()
    if graph is None or costs is None or probabilities is None:
        print('Could not load data. Exiting.')
        return

    if SMOKE:
        _smoke_unit_checks(graph, costs, probabilities)
        grid = {
            'discount_factor': [0.5],
            'max_per_community': [3],
            'weights': [(0.45, 0.30, 0.25)],
            'hop2_decay': [0.5],
        }
        fixed = {
            'penalty_w': cs.PENALTY_W,
            'pool_size': 30,
            'greedy_trials': 2,
            'swap_trials': 4,
            'final_trials': 10,
            'use_swaps': False,
        }
    else:
        grid = {
            'discount_factor': [0.4, 0.6, 0.7, 0.8],
            'penalty_w': [1.5, 2.5, 4.0],
            'weights': [
                (0.30, 0.20, 0.50),
                (0.45, 0.30, 0.25),
                (0.20, 0.30, 0.50),
                (0.50, 0.40, 0.10),
            ],
            'hop2_decay': [0.0, 0.5],
            'heuristic_only_pool': [False, True],
            'max_per_community': [3, 999],
        }
        fixed = {
            'pool_size': 120,
            'greedy_trials': 6,
            'swap_trials': 10,
            'final_trials': 80,
            'use_swaps': False,
        }

    grid_search(graph, costs, probabilities, grid, log_path=LOG_PATH, fixed=fixed)


if __name__ == '__main__':
    main()
