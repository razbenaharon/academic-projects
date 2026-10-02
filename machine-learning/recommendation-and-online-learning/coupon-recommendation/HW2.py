import numpy as np
import pandas as pd
from pathlib import Path
from scipy import sparse
from scipy.sparse.linalg import lsqr, svds
# scipy may also be used according to the assignment instructions.
# Do not use sklearn or parallel-processing libraries.


# ============================================================
# Stage A: Computational models - Ramzi model and Shira model
# ============================================================

def solve_stage_a(train_path: str, test_path: str, coupon_info_path: str,
                  output_dir: str = "."):
    """
    Implement this function so that it creates the following files in output_dir:
    1. pred_rami.csv
    2. pred_shira.csv
    3. mse.txt

    train.csv columns: user_id,coupon_id,rating
    test.csv columns: user_id,coupon_id
    coupon_info.csv columns: coupon_id,category_id,cost,value

    Returning a value from this function is not required, but it is recommended
    to return:
    (mse_ramzi, mse_shira)
    """
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    coupon_info = pd.read_csv(coupon_info_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    ratings = train["rating"].to_numpy(dtype=float)
    r_avg = float(ratings.mean())

    # Work with compact consecutive indices: the IDs themselves need not be
    # consecutive (or even numeric).
    user_ids = pd.Index(train["user_id"].unique())
    coupon_ids = pd.Index(train["coupon_id"].unique())
    category_ids = pd.Index(coupon_info["category_id"].unique())
    user_index = {key: j for j, key in enumerate(user_ids)}
    coupon_index = {key: j for j, key in enumerate(coupon_ids)}
    category_index = {key: j for j, key in enumerate(category_ids)}

    info = coupon_info.set_index("coupon_id")
    train_categories = train["coupon_id"].map(info["category_id"])
    train_values = train["coupon_id"].map(info["value"])
    if train_categories.isna().any() or train_values.isna().any():
        raise ValueError("coupon_info.csv is missing a coupon used in train.csv")

    n_rows = len(train)
    n_users = len(user_ids)
    n_coupons = len(coupon_ids)
    n_categories = len(category_ids)
    eta_col = n_users + n_coupons + n_categories
    n_parameters = eta_col + 1

    row = np.arange(n_rows)
    u_cols = train["user_id"].map(user_index).to_numpy(dtype=int)
    i_cols = (n_users + train["coupon_id"].map(coupon_index)).to_numpy(dtype=int)
    c_cols = (n_users + n_coupons + train_categories.map(category_index)).to_numpy(dtype=int)
    log_values = np.log1p(train_values.to_numpy(dtype=float))

    design = sparse.coo_matrix(
        (
            np.concatenate((np.ones(n_rows), np.ones(n_rows),
                            np.ones(n_rows), log_values)),
            (
                np.concatenate((row, row, row, row)),
                np.concatenate((u_cols, i_cols, c_cols,
                                np.full(n_rows, eta_col, dtype=int))),
            ),
        ),
        shape=(n_rows, n_parameters),
    ).tocsr()

    # Augment the least-squares system with sqrt(lambda) * I.  This is
    # exactly the four differently weighted L2 penalties from the exercise.
    penalties = np.concatenate((
        np.full(n_users, 1.5),
        np.full(n_coupons, 2.0),
        np.full(n_categories, 0.7),
        np.array([0.2]),
    ))
    augmented_x = sparse.vstack(
        (design, sparse.diags(np.sqrt(penalties), format="csr")),
        format="csr",
    )
    augmented_y = np.concatenate((ratings - r_avg, np.zeros(n_parameters)))
    ramzi_parameters = lsqr(
        augmented_x, augmented_y, atol=1e-11, btol=1e-11,
        iter_lim=max(1000, 5 * n_parameters),
    )[0]
    ramzi_train_raw = r_avg + design @ ramzi_parameters
    mse_ramzi = float(np.mean((ratings - ramzi_train_raw) ** 2))

    def ramzi_prediction(frame):
        prediction = np.full(len(frame), r_avg, dtype=float)
        for pos, (user_id, coupon_id) in enumerate(
                frame[["user_id", "coupon_id"]].itertuples(index=False, name=None)):
            u = user_index.get(user_id)
            i = coupon_index.get(coupon_id)
            if u is not None:
                prediction[pos] += ramzi_parameters[u]
            if i is not None:
                prediction[pos] += ramzi_parameters[n_users + i]
            if coupon_id in info.index:
                category = info.at[coupon_id, "category_id"]
                c = category_index.get(category)
                if c is not None:
                    prediction[pos] += ramzi_parameters[n_users + n_coupons + c]
                prediction[pos] += ramzi_parameters[eta_col] * np.log1p(
                    float(info.at[coupon_id, "value"])
                )
        return prediction

    ramzi_test = np.clip(ramzi_prediction(test), 1.0, 10.0)

    # Shira's sparse rank-6 approximation. Missing entries remain implicit
    # zeros, as required by the assignment.
    centered = sparse.coo_matrix(
        (ratings - r_avg, (u_cols, train["coupon_id"].map(coupon_index).to_numpy(dtype=int))),
        shape=(n_users, n_coupons),
    ).tocsr()
    k = min(6, min(centered.shape) - 1)
    if k > 0:
        u_svd, singular_values, vt_svd = svds(
            centered, k=k, which="LM", random_state=0
        )
        # No dense rating matrix is formed. Predictions are individual dot
        # products of the compact factors.
        left = u_svd * singular_values
        shira_train_raw = r_avg + np.sum(
            left[u_cols] * vt_svd[:, train["coupon_id"].map(coupon_index).to_numpy(dtype=int)].T,
            axis=1,
        )
    else:
        left = np.zeros((n_users, 0), dtype=float)
        vt_svd = np.zeros((0, n_coupons), dtype=float)
        shira_train_raw = np.full(n_rows, r_avg, dtype=float)
    mse_shira = float(np.mean((ratings - shira_train_raw) ** 2))

    shira_test = np.full(len(test), r_avg, dtype=float)
    for pos, (user_id, coupon_id) in enumerate(
            test[["user_id", "coupon_id"]].itertuples(index=False, name=None)):
        u = user_index.get(user_id)
        i = coupon_index.get(coupon_id)
        if u is not None and i is not None:
            shira_test[pos] += float(left[u] @ vt_svd[:, i])
    shira_test = np.clip(shira_test, 1.0, 10.0)

    ramzi_output = test[["user_id", "coupon_id"]].copy()
    ramzi_output["rating"] = ramzi_test
    ramzi_output.to_csv(output / "pred_ramzi.csv", index=False)
    shira_output = test[["user_id", "coupon_id"]].copy()
    shira_output["rating"] = shira_test
    shira_output.to_csv(output / "pred_shira.csv", index=False)
    (output / "mse.txt").write_text(
        f"{mse_ramzi:.12g}\n{mse_shira:.12g}\n", encoding="utf-8"
    )
    return mse_ramzi, mse_shira


# ============================================================
# Stage B: Competitive part - Kochava's Coupon War
# ============================================================

class ShefaRecommender:
    def __init__(self, n_days: int, n_users: int, prices: np.ndarray,
                 values: np.ndarray, budget: int):
        """
        n_days: number of campaign days
        n_users: number of users/customers
        prices: daily activation cost of each coupon
        values: gross profit from each redeemed coupon
        budget: daily budget for activating coupons
        """
        self.n_days = n_days
        self.n_users = n_users
        self.prices = np.asarray(prices, dtype=int)
        self.values = np.asarray(values, dtype=float)
        self.budget = int(budget)
        self.n_coupons = len(self.prices)
        if self.n_coupons == 0 or len(self.values) != self.n_coupons:
            raise ValueError("prices and values must describe at least one coupon")

        # It is recommended to store the most recent recommendation so that
        # the update step can learn from the returned results.
        self.last_recommendation = None
        self.day = 0
        self.counts = np.zeros((n_users, self.n_coupons), dtype=np.int32)
        self.successes = np.zeros((n_users, self.n_coupons), dtype=float)
        self.global_counts = np.zeros(self.n_coupons, dtype=np.int64)
        self.global_successes = np.zeros(self.n_coupons, dtype=float)
        self.affordable = np.flatnonzero(self.prices <= self.budget)

        # A valid recommendation is mathematically impossible when no coupon
        # fits. Keep the required safest fallback nevertheless: recommend the
        # cheapest coupon rather than crashing.
        if len(self.affordable) == 0:
            self.affordable = np.array([int(np.argmin(self.prices))], dtype=int)

        # Explore the most promising coupons first. Only a brief forced sweep
        # is needed; the rest of the horizon is better spent letting the
        # adaptive policy refine its per-user estimates.
        order = np.argsort(-self.values[self.affordable], kind="stable")
        self.exploration_order = self.affordable[order]
        # Scale forced exploration smoothly with both the horizon and catalogue
        # size.  Forced exploration shows a single coupon to *every* user for a
        # whole day, so it is kept deliberately short (a few days) and the
        # adaptive UCB policy takes over quickly.  The two constants were
        # selected by grid search and re-checked on separate holdout seeds.
        n_explorable = len(self.exploration_order)
        exploration_denominator = 6.0 + 5.0 * n_explorable
        self.exploration_days = min(
            len(self.exploration_order),
            max(1, int(self.n_days // exploration_denominator)),
        )

        # For the small/medium coupon sets used by the simulator, enumerate
        # every feasible active set once. This makes the daily budget decision
        # exact. For larger catalogues, or pathological ones that yield a huge
        # number of maximal sets (e.g. many equally cheap coupons), a greedy
        # candidate builder is used instead so the per-day cost stays bounded.
        # The 2^n sweep stays sub-second through n = 16, and the count guard
        # keeps the daily scoring loop cheap regardless of the catalogue shape.
        self.feasible_sets = None
        max_feasible_sets = 2000
        if self.n_coupons <= 16:
            feasible = []
            for mask in range(1, 1 << self.n_coupons):
                chosen = np.flatnonzero(
                    (mask >> np.arange(self.n_coupons)) & 1
                )
                total_cost = int(self.prices[chosen].sum())
                if total_cost > self.budget:
                    continue

                # The objective cannot get worse when another affordable
                # coupon is added. Retaining only maximal feasible sets makes
                # exact daily scoring much cheaper without changing its best
                # attainable assignment.
                remaining = self.budget - total_cost
                unchosen = np.flatnonzero(
                    ((mask >> np.arange(self.n_coupons)) & 1) == 0
                )
                if len(unchosen) == 0 or np.all(self.prices[unchosen] > remaining):
                    feasible.append(chosen)
                    # Abort to the greedy fallback if enumeration explodes; the
                    # exact loop would otherwise dominate the daily runtime.
                    if len(feasible) > max_feasible_sets:
                        feasible = None
                        break
            self.feasible_sets = feasible if feasible else None

    def recommend(self) -> np.ndarray:
        """
        Called at the beginning of each day.
        Returns a NumPy array of length n_users, with dtype int.
        Each value is a coupon ID between 0 and n_coupons - 1.
        The set of distinct coupons appearing in the recommendation must satisfy
        the daily budget constraint.
        """
        # Warm-start with the most valuable affordable coupons. Each explored
        # coupon is shown to every user, yielding broad feedback at one
        # activation cost; large catalogues intentionally receive a partial sweep.
        if self.day < self.exploration_days:
            coupon = int(self.exploration_order[self.day])
            rec = np.full(self.n_users, coupon, dtype=int)
            self.last_recommendation = rec.copy()
            return rec

        global_mean = (self.global_successes + 1.0) / (
            self.global_counts + 2.0
        )
        # A moderate coupon-wide prior lets each user benefit from pooled
        # evidence without erasing their personal response history. Its weight
        # was grid-searched and validated on held-out seeds and catalogues.
        prior_weight = 3.0
        posterior_mean = (
            self.successes + prior_weight * global_mean[None, :]
        ) / (self.counts + prior_weight)
        confidence = np.sqrt(
            0.005 * np.log(self.day + 2.0) / (self.counts + prior_weight)
        )
        optimistic_profit = self.values[None, :] * np.minimum(
            1.0, posterior_mean + confidence
        )

        if self.feasible_sets is not None:
            best_set = None
            best_score = -np.inf
            for chosen in self.feasible_sets:
                score = float(np.max(optimistic_profit[:, chosen], axis=1).sum())
                if score > best_score:
                    best_score = score
                    best_set = chosen
        else:
            # Scalable fallback: greedily build sets from several promising
            # starting coupons. Trying multiple starts avoids committing the
            # entire budget to one attractive but expensive coupon.
            single_scores = optimistic_profit.sum(axis=0)
            ranked = self.affordable[
                np.argsort(-single_scores[self.affordable], kind="stable")
            ]
            seed_coupons = list(ranked[:min(5, len(ranked))])
            cheapest = int(self.affordable[np.argmin(self.prices[self.affordable])])
            if cheapest not in seed_coupons:
                seed_coupons.append(cheapest)

            best_set = None
            best_score = -np.inf
            for start in seed_coupons:
                start = int(start)
                selected = [start]
                remaining_budget = self.budget - int(self.prices[start])
                current = optimistic_profit[:, start].copy()
                while True:
                    candidates = np.array([
                        i for i in self.affordable
                        if i not in selected and self.prices[i] <= remaining_budget
                    ], dtype=int)
                    if len(candidates) == 0:
                        break
                    gains = np.maximum(
                        optimistic_profit[:, candidates] - current[:, None], 0.0
                    ).sum(axis=0)
                    ratios = gains / np.maximum(self.prices[candidates], 1)
                    pick_pos = int(np.argmax(ratios))
                    if gains[pick_pos] <= 0:
                        break
                    pick = int(candidates[pick_pos])
                    selected.append(pick)
                    remaining_budget -= int(self.prices[pick])
                    current = np.maximum(current, optimistic_profit[:, pick])

                candidate_score = float(current.sum())
                if candidate_score > best_score:
                    best_score = candidate_score
                    best_set = np.asarray(selected, dtype=int)

        rec = best_set[np.argmax(optimistic_profit[:, best_set], axis=1)].astype(int)
        self.last_recommendation = rec.copy()
        return rec

    def update(self, results: np.ndarray):
        """
        Called at the end of each day.
        results[i] = 1 if user i redeemed the coupon recommended to them that day,
        and 0 otherwise.
        """
        results = np.asarray(results, dtype=int)
        if results.shape != (self.n_users,) or self.last_recommendation is None:
            raise ValueError("results do not match the latest recommendation")
        users = np.arange(self.n_users)
        np.add.at(self.counts, (users, self.last_recommendation), 1)
        np.add.at(self.successes, (users, self.last_recommendation), results)
        np.add.at(self.global_counts, self.last_recommendation, 1)
        np.add.at(self.global_successes, self.last_recommendation, results)
        self.day += 1
