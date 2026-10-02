"""Compare the three submitted TREC runs against each other.

The competition graded on MAP against held-out relevance judgements we never
received, so this script deliberately computes no effectiveness metric - it
would have nothing to compute one against. What the run files *can* answer is
how differently the three models actually rank, which is the question that
matters when deciding whether a hybrid earned its complexity: two models that
return nearly the same ordering are not really two models.

Usage:
    pip install matplotlib
    python analyze_runs.py

Writes assets/run_agreement.png and prints the same numbers as a table.
"""
from __future__ import annotations

import collections
import pathlib

RUNS = {
    "1 · Hybrid (BM25 + Dirichlet PRF expansion)": "run_1.res.txt",
    "2 · Dirichlet + PRF": "run_2.res.txt",
    "3 · BM25 baseline": "run_3.res.txt",
}
CUTOFFS = (10, 100, 1000)
HERE = pathlib.Path(__file__).parent


def load(path: pathlib.Path) -> dict[str, list[str]]:
    """qid -> doc ids ordered by the rank column."""
    rows: dict[str, list[tuple[int, str]]] = collections.defaultdict(list)
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) < 5:
                continue
            qid, _, docid, rank = parts[0], parts[1], parts[2], int(parts[3])
            rows[qid].append((rank, docid))
    return {qid: [d for _, d in sorted(items)] for qid, items in rows.items()}


def mean_overlap(a: dict[str, list[str]], b: dict[str, list[str]], k: int) -> float:
    """Mean fraction of a query's top-k documents that both runs return."""
    shared = sorted(set(a) & set(b))
    if not shared:
        return 0.0
    total = 0.0
    for qid in shared:
        top_a, top_b = set(a[qid][:k]), set(b[qid][:k])
        denominator = max(len(top_a), 1)
        total += len(top_a & top_b) / denominator
    return total / len(shared)


def main() -> None:
    runs = {}
    for label, filename in RUNS.items():
        runs[label] = load(HERE / filename)
        depths = {len(v) for v in runs[label].values()}
        print(f"{label:46} {len(runs[label]):3} queries, "
              f"depth {min(depths)}-{max(depths)}")

    labels = list(RUNS)
    print()
    header = f"{'pair':<52}" + "".join(f"{'top-'+str(k):>10}" for k in CUTOFFS)
    print(header)
    print("-" * len(header))

    results: dict[tuple[int, int], list[float]] = {}
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            values = [mean_overlap(runs[labels[i]], runs[labels[j]], k)
                      for k in CUTOFFS]
            results[(i, j)] = values
            pair = f"{labels[i].split(' · ')[0]} vs {labels[j].split(' · ')[0]}"
            name = f"{pair}  ({labels[i].split(' · ')[1][:18]} / " \
                   f"{labels[j].split(' · ')[1][:18]})"
            print(f"{name:<52}" + "".join(f"{v:>9.1%}" for v in values))

    _plot(labels, results)


def _plot(labels: list[str], results: dict[tuple[int, int], list[float]]) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not installed - skipping the figure)")
        return

    fig, ax = plt.subplots(figsize=(9, 4.6))
    width = 0.25
    colors = ("#3b7dd8", "#d98c3b", "#5aa469")
    for offset, ((i, j), values) in enumerate(results.items()):
        positions = [x + (offset - 1) * width for x in range(len(CUTOFFS))]
        pair = f"run {i+1} vs run {j+1}"
        bars = ax.bar(positions, values, width, label=pair, color=colors[offset])
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.015,
                    f"{value:.0%}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(range(len(CUTOFFS)))
    ax.set_xticklabels([f"top-{k}" for k in CUTOFFS])
    ax.set_ylabel("mean overlap between the two runs")
    ax.set_ylim(0, 1.05)
    ax.set_title("How differently do the three submitted runs rank?\n"
                 "Mean per-query document overlap across 199 test queries",
                 fontsize=11)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    out = HERE / "assets"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "run_agreement.png", dpi=150)
    print(f"\nwrote {out / 'run_agreement.png'}")


if __name__ == "__main__":
    main()
