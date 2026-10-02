'''Hyperparameter sweep wrapper for campaign_simulation.py.

Two modes:
  * driver (no args)              — loop the grid, launch a subprocess per combo
                                    with a 45-min wall-clock cap, skip combos
                                    already logged. At the end, copy the best
                                    selection to best_solution.csv.
  * worker (--run POOL SWAP SEED) — run a single combo end-to-end, append a row
                                    to optimize_log.csv, save its selection CSV.

Does not modify campaign_simulation.py.

Usage:
  python optimize_shield.py                 # run the whole grid
  python optimize_shield.py --run 80 12 42  # one combo (used by the driver)
'''

import csv
import os
import shutil
import subprocess
import sys
import time
import itertools


GRID_POOL = [80, 100, 120]
GRID_SWAP = [12, 20]
GRID_SEED = [42, 777]

LOG_PATH = 'optimize_log.csv'
BEST_PATH = 'best_solution.csv'
RUNS_DIR = 'runs'

PER_RUN_TIMEOUT_S = 45 * 60   # 45 minutes
FINAL_TRIALS = 100

FIELDNAMES = [
    'pool_size', 'swap_trials', 'seed',
    'mean', 'std', 'ci95', 'n_selected', 'cost_used',
    'elapsed_s', 'run_csv', 'selected', 'error',
]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _append_row(path, row):
    '''Append one dict row to a CSV. Writes header on first write.'''
    file_exists = os.path.exists(path) and os.path.getsize(path) > 0
    with open(path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction='ignore')
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def _read_completed():
    '''Return set of (pool, swap, seed) tuples with a non-NaN mean already in the log.'''
    done = set()
    if not os.path.exists(LOG_PATH):
        return done
    with open(LOG_PATH, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                pool = int(row['pool_size'])
                swap = int(row['swap_trials'])
                seed = int(row['seed'])
                mean = float(row['mean'])
                if mean == mean:  # not NaN
                    done.add((pool, swap, seed))
            except (ValueError, KeyError):
                continue
    return done


# ---------------------------------------------------------------------------
# Worker mode
# ---------------------------------------------------------------------------

def worker(pool_size: int, swap_trials: int, seed: int) -> int:
    '''Run one combo end-to-end. Imports cs lazily so driver startup stays fast.'''
    import influence_maximization as cs

    graph = cs.read_graph()
    costs = cs.read_costs()
    probabilities = cs.read_probabilities()
    if graph is None or costs is None or probabilities is None:
        _append_row(LOG_PATH, {
            'pool_size': pool_size, 'swap_trials': swap_trials, 'seed': seed,
            'mean': float('nan'), 'std': float('nan'), 'ci95': float('nan'),
            'n_selected': 0, 'cost_used': 0, 'elapsed_s': 0.0,
            'run_csv': '', 'selected': '', 'error': 'data_load_failed',
        })
        return 1

    cs.RANDOM_SEED = seed   # mutate shield's module-level constant

    t0 = time.time()
    try:
        selected = cs.run_pipeline(
            graph, costs, probabilities,
            penalty_w=cs.PENALTY_W,
            pool_size=pool_size,
            greedy_trials=cs.GREEDY_TRIALS,
            swap_trials=swap_trials,
        )
    except Exception as e:
        _append_row(LOG_PATH, {
            'pool_size': pool_size, 'swap_trials': swap_trials, 'seed': seed,
            'mean': float('nan'), 'std': float('nan'), 'ci95': float('nan'),
            'n_selected': 0, 'cost_used': 0, 'elapsed_s': round(time.time()-t0, 1),
            'run_csv': '', 'selected': '', 'error': f'pipeline:{e}',
        })
        return 1
    elapsed = time.time() - t0

    # Unbiased final score (fresh seeds, FINAL_TRIALS trials).
    mean, std, ci95 = cs.batch_evaluator(graph, selected, probabilities,
                                         trials=FINAL_TRIALS, base_seed=10_000)

    # Save the run's selection.
    os.makedirs(RUNS_DIR, exist_ok=True)
    run_csv = os.path.join(RUNS_DIR, f'pool{pool_size}_swap{swap_trials}_seed{seed}.csv')
    cs.submit_influencers(selected, f'pool{pool_size}', f'swap{swap_trials}_seed{seed}',
                          costs, filename=run_csv)

    _append_row(LOG_PATH, {
        'pool_size': pool_size,
        'swap_trials': swap_trials,
        'seed': seed,
        'mean': mean,
        'std': std,
        'ci95': ci95,
        'n_selected': len(selected),
        'cost_used': cs.total_cost(selected, costs),
        'elapsed_s': round(elapsed, 1),
        'run_csv': run_csv,
        'selected': '|'.join(str(u) for u in sorted(selected)),
        'error': '',
    })
    print(f'WORKER done: pool={pool_size} swap={swap_trials} seed={seed} '
          f'mean={mean:.2f} +/- {ci95:.2f} elapsed={elapsed:.1f}s')
    return 0


# ---------------------------------------------------------------------------
# Driver mode
# ---------------------------------------------------------------------------

def driver():
    grid = list(itertools.product(GRID_POOL, GRID_SWAP, GRID_SEED))
    done = _read_completed()
    todo = [combo for combo in grid if combo not in done]

    print(f'Grid size: {len(grid)} combos.')
    print(f'Already done: {len(done)}. Skipping those.')
    print(f'To run: {len(todo)} combos. Per-run cap: {PER_RUN_TIMEOUT_S//60} min.')

    for i, (pool, swap, seed) in enumerate(todo, 1):
        print(f'\n[{i}/{len(todo)}] pool={pool} swap={swap} seed={seed}')
        t0 = time.time()
        try:
            subprocess.run(
                [sys.executable, __file__, '--run', str(pool), str(swap), str(seed)],
                timeout=PER_RUN_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired:
            elapsed = time.time() - t0
            print(f'  TIMEOUT after {elapsed:.0f}s — logging NaN row.')
            _append_row(LOG_PATH, {
                'pool_size': pool, 'swap_trials': swap, 'seed': seed,
                'mean': float('nan'), 'std': float('nan'), 'ci95': float('nan'),
                'n_selected': 0, 'cost_used': 0, 'elapsed_s': PER_RUN_TIMEOUT_S,
                'run_csv': '', 'selected': '', 'error': 'timeout',
            })
        except Exception as e:
            print(f'  DRIVER ERROR: {e}')
            _append_row(LOG_PATH, {
                'pool_size': pool, 'swap_trials': swap, 'seed': seed,
                'mean': float('nan'), 'std': float('nan'), 'ci95': float('nan'),
                'n_selected': 0, 'cost_used': 0, 'elapsed_s': round(time.time()-t0, 1),
                'run_csv': '', 'selected': '', 'error': f'driver:{e}',
            })

    # Find best and copy.
    best = None
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'r', newline='') as f:
            for row in csv.DictReader(f):
                try:
                    mean = float(row['mean'])
                except ValueError:
                    continue
                if mean != mean:  # NaN
                    continue
                if best is None or mean > float(best['mean']):
                    best = row

    print('\n=== FINAL BEST ===')
    if best is None:
        print('  No successful runs.')
        return
    print(f'  pool={best["pool_size"]} swap={best["swap_trials"]} seed={best["seed"]}')
    print(f'  mean={best["mean"]} +/- {best["ci95"]}')
    print(f'  cost={best["cost_used"]}  n={best["n_selected"]}')
    print(f'  selection: {best["selected"]}')
    src = best['run_csv']
    if src and os.path.exists(src):
        shutil.copy(src, BEST_PATH)
        print(f'  copied {src} -> {BEST_PATH}')
    else:
        print(f'  WARN: best run_csv not found ({src}); cannot copy to {BEST_PATH}')


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) >= 5 and sys.argv[1] == '--run':
        pool = int(sys.argv[2])
        swap = int(sys.argv[3])
        seed = int(sys.argv[4])
        sys.exit(worker(pool, swap, seed))
    else:
        driver()


if __name__ == '__main__':
    main()
