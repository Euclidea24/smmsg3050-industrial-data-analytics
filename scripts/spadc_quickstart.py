# -*- coding: utf-8 -*-
"""
spadc_quickstart.py
===================
在真实工业数据上跑一遍论文两条准则的"最小实现"：

  准则 1（一般依赖）：用**距离相关**给每个特征单独打分 d_i
  准则 2（多样性）  ：减去与已选特征的重复度（d_i 与 F_ij 的贪心版）

输出：只看相关的 Top-k  vs  加上多样性的 Top-k

用法：
    python spadc_quickstart.py --dataset secom --top 15
说明：
    这是"教学版"：真实 SpaDC 是把 max dᵀβ 与 βᵀFβ≤1、Σβ≤c 一起解成一个
    二次锥规划（论文式 (3)(4)）。这里用贪心近似，只为了让两条准则
    在真实数据上看得见差别。
"""
import argparse
import time

import numpy as np

from load_spadc_data import load

MAX_N = 400        # 距离表是 n×n，演示时下采样控制内存
MAX_P_PAIR = 100   # 计算 F_ij 时保留的特征数（按 d_i 预筛）


def _center(d):
    return d - d.mean(1, keepdims=True) - d.mean(0, keepdims=True) + d.mean()


def _norm_cols(X):
    X = X.astype(np.float64)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    return (X - mu) / sd


def centered_dist(a):
    """(n,) -> 中心化的 |a_i-a_j|，float32 省内存。"""
    d = np.abs(a[:, None] - a[None, :])
    return _center(d).astype(np.float32)


def run(dataset, top, seed=0):
    t0 = time.time()
    X, y, meta = load(dataset)
    rng = np.random.default_rng(seed)
    if X.shape[0] > MAX_N:
        idx = rng.choice(X.shape[0], MAX_N, replace=False)
        X, y = X[idx], y[idx]
    X = _norm_cols(X)

    B = centered_dist(y.astype(float)).astype(np.float64)
    dvar_b = float((B * B).mean())
    if dvar_b <= 0:
        raise ValueError("y 在抽样后是常数（dvar=0），换数据集或换 y")

    # ---- 准则 1：每个特征单独的距离相关
    d = np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        A = centered_dist(X[:, j]).astype(np.float64)
        dcov2 = float((A * B).mean())
        dvar_a = float((A * A).mean())
        if dvar_a > 0 and dcov2 > 0:
            d[j] = np.sqrt(dcov2 / np.sqrt(dvar_a * dvar_b))

    print("\n=== %s  (抽样 n=%d, p=%d, y=%s)"
          % (meta["name"], X.shape[0], X.shape[1], meta["target"]))
    print("d_i: max=%.3f  median=%.3f  接近 0 的特征数=%d  (用时 %.1fs)"
          % (d.max(), np.median(d), int((d < 1e-6).sum()), time.time() - t0))
    if d.max() <= 0:
        print("!! 所有 d_i 都是 0，检查 y 是否退化")
        return d, meta

    rank_corr = np.argsort(-d)[:top]

    # ---- 准则 2：加多样性（贪心），只对预筛出的候选算 F
    cand = np.argsort(-d)[:min(MAX_P_PAIR, X.shape[1])]
    A = np.stack([centered_dist(X[:, j]).astype(np.float64) for j in cand])  # (m,n,n)
    norms = np.sqrt((A * A).mean(axis=(1, 2)))
    norms[norms == 0] = 1.0
    m = len(cand)
    Fi = np.eye(m)
    for i in range(m):
        for j in range(i + 1, m):
            r = float((A[i] * A[j]).mean()) / (norms[i] * norms[j])
            Fi[i, j] = Fi[j, i] = max(r, 0.0)

    chosen = [int(np.argmax(d[cand]))]
    while len(chosen) < min(top, m):
        best, best_s = None, -1e9
        for k in range(m):
            if k in chosen:
                continue
            red = max(Fi[k, j] for j in chosen)
            score = d[cand[k]] * (1.0 - red)
            if score > best_s:
                best, best_s = k, score
        if best is None:
            break
        chosen.append(best)

    print("\n%-4s %-12s %-8s %-12s %-8s" % ("#", "只看相关", "d_i", "加多样性", "d_i"))
    for t in range(top):
        c1 = rank_corr[t] if t < len(rank_corr) else None
        c2 = cand[chosen[t]] if t < len(chosen) else None
        print("%-4d %-12s %-8.3f %-12s %-8.3f" % (
            t + 1,
            ("f%d" % c1) if c1 is not None else "-", d[c1] if c1 is not None else 0.0,
            ("f%d" % c2) if c2 is not None else "-", d[c2] if c2 is not None else 0.0))

    ov = len(set(rank_corr.tolist()) & set(cand[c] for c in chosen))
    print("\n两个名单重合 %d / %d → 差异越大，说明这个数据集里的冗余越严重" % (ov, top))
    print("总用时 %.1fs" % (time.time() - t0))
    return d, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="secom",
                    choices=["secom", "hydraulic", "steel", "wine_red",
                             "wine_white", "appliances", "gas"])
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    run(a.dataset, a.top)
