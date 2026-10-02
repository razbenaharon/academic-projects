import numpy as np
from typing import Dict, List


class VectorIndex:
    """
    Dynamic exact vector index.

    The index keeps all active vectors packed in a dense matrix.
    Deletion is implemented by swapping the deleted row with the last active row.
    """

    def __init__(self, dim: int):
        self.dim = int(dim)
        self._cap = 0
        self._size = 0
        self._ids = np.empty(0, dtype=np.int64)
        self._vecs = np.empty((0, self.dim), dtype=np.float32)
        self._pos: Dict[int, int] = {}
        self._block = 512
        self._vec_block = 131072 

    def _ensure_capacity(self, need: int) -> None:
        if need <= self._cap:
            return
        new_cap = max(need, 1024 if self._cap == 0 else int(self._cap * 1.6))
        new_ids = np.empty(new_cap, dtype=np.int64)
        new_vecs = np.empty((new_cap, self.dim), dtype=np.float32)
        if self._size:
            new_ids[:self._size] = self._ids[:self._size]
            new_vecs[:self._size] = self._vecs[:self._size]
        self._cap, self._ids, self._vecs = new_cap, new_ids, new_vecs

    def insert(self, batch: Dict[int, np.ndarray]) -> Dict[str, List[int]]:
        succeeded, failed, new_ids, new_vecs = [], [], [], []
        for vid, vec in batch.items():
            vid = int(vid)
            if vid in self._pos:
                failed.append(vid)
            else:
                self._pos[vid] = self._size + len(new_ids)
                new_ids.append(vid)
                new_vecs.append(np.asarray(vec, dtype=np.float32))
                succeeded.append(vid)
        if new_ids:
            end = self._size + len(new_ids)
            self._ensure_capacity(end)
            self._ids[self._size:end] = np.asarray(new_ids, dtype=np.int64)
            self._vecs[self._size:end] = np.asarray(new_vecs, dtype=np.float32)
            self._size = end
        return {"succeeded": succeeded, "failed": failed}

    def delete(self, ids: np.ndarray) -> Dict[str, List[int]]:
        succeeded, failed = [], []
        for vid in np.asarray(ids, dtype=np.int64):
            vid = int(vid)
            row = self._pos.pop(vid, None)
            if row is None:
                failed.append(vid)
                continue
            last = self._size - 1
            if row != last:
                moved_id = int(self._ids[last])
                self._ids[row], self._vecs[row] = self._ids[last], self._vecs[last]
                self._pos[moved_id] = row
            self._size -= 1
            succeeded.append(vid)
        return {"succeeded": succeeded, "failed": failed}

    def search(self, queries: np.ndarray, k: int) -> np.ndarray:
        queries = np.asarray(queries, dtype=np.float32)
        n_q, k_eff = queries.shape[0], min(int(k), self._size)
        if k_eff <= 0: return np.empty((n_q, 0), dtype=np.int64)
        ids, vecs = self._ids[:self._size], self._vecs[:self._size]
        out = np.empty((n_q, k_eff), dtype=np.int64)
        for start in range(0, n_q, self._block):
            q = queries[start:start + self._block]
            score_parts, id_parts = [], []
            for v_start in range(0, self._size, self._vec_block):
                s = q @ vecs[v_start:v_start + self._vec_block].T
                kk = min(k_eff, s.shape[1])
                p = np.argpartition(-s, kth=kk - 1, axis=1)[:, :kk]
                score_parts.append(np.take_along_axis(s, p, axis=1));
                id_parts.append(ids[v_start + p])
            scores, block_ids = np.concatenate(score_parts, axis=1), np.concatenate(id_parts, axis=1)
            p = np.argpartition(-scores, kth=k_eff - 1, axis=1)[:, :k_eff]
            vals = np.take_along_axis(scores, p, axis=1)
            order = np.argsort(-vals, axis=1)
            out[start:start + self._block] = np.take_along_axis(block_ids, p, axis=1)[
                np.arange(q.shape[0])[:, None], order]
        return out