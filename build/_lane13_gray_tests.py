"""Within-city-demeaned pooled-z test: gray calls_per_1k vs murder_rate arcs (mirrors lane12 machinery)."""
import json, math, collections

def statistics_mean(v):
    return sum(v) / len(v)

B = "C:/Users/J"
rows = json.load(open(f"{B}/gray_safety_lane_panel_v1.json"))

def pooled_within_z(rows, xkey, ykey):
    """Per city: demean x and y, pool city-demeaned pairs, Pearson r + t approx (no p-values over-claim)."""
    by_city = collections.defaultdict(list)
    for r in rows:
        if r.get(xkey) is not None and r.get(ykey) is not None:
            by_city[r["city"]].append((r[xkey], r[ykey]))
    pooled_x, pooled_y = [], []
    used = {}
    for city, pts in by_city.items():
        if len(set(p[1] for p in pts)) < 2:
            continue
        mx = statistics_mean([p[0] for p in pts]); my = statistics_mean([p[1] for p in pts])
        for x, y in pts:
            pooled_x.append(x - mx); pooled_y.append(y - my)
        used[city] = len(pts)
    n = len(pooled_x)
    if n < 6 or len(used) < 2:
        return {"n_city_years": n, "cities": used, "verdict": "too-thin"}
    mx = sum(pooled_x) / n; my = sum(pooled_y) / n
    sxx = sum((x - mx) ** 2 for x in pooled_x)
    syy = sum((y - my) ** 2 for y in pooled_y)
    sxy = sum((x - mx) * (y - my) for x, y in zip(pooled_x, pooled_y))
    if sxx == 0 or syy == 0:
        return {"n_city_years": n, "cities": used, "verdict": "degenerate"}
    r = sxy / math.sqrt(sxx * syy)
    t = r * math.sqrt((n - 2) / max(1e-12, 1 - r * r)) if n > 2 else None
    return {"r": round(r, 3), "t_approx": round(t, 2) if t is not None else None,
            "n_city_years": n, "cities": used}

tests = {}
tests["calls_per1k_t_vs_murder_rate_t0"] = pooled_within_z(rows, "calls_per_1k", "murder_rate_t0")
tests["calls_per1k_t_vs_murder_rate_t+1"] = pooled_within_z(rows, "calls_per_1k", "murder_rate_t+1")
tests["calls_per1k_t_vs_murder_rate_t+2"] = pooled_within_z(rows, "calls_per_1k", "murder_rate_t+2")
# the reverse arc: calls next year AFTER murder this year (does murder volume pull enforcement?)
tests["murder_rate_t0_vs_calls_per1k_t+1"] = pooled_within_z(rows, "murder_rate_t0", "calls_per1k_t+1")
# per-city sign table at t0
per_city = {}
by_city = collections.defaultdict(list)
for r in rows:
    if r.get("calls_per_1k") is not None and r.get("murder_rate_t0") is not None:
        by_city[r["city"]].append((r["year"], r["calls_per_1k"], r["murder_rate_t0"]))
def pearson(pairs):
    n = len(pairs)
    if n < 3:
        return None
    mx = sum(p[1] for p in pairs) / n; my = sum(p[2] for p in pairs) / n
    sxx = sum((p[1] - mx) ** 2 for p in pairs); syy = sum((p[2] - my) ** 2 for p in pairs)
    sxy = sum((p[1] - mx) * (p[2] - my) for p in pairs)
    return round(sxy / math.sqrt(sxx * syy), 3) if sxx > 0 and syy > 0 else None
for c, pts in by_city.items():
    per_city[c] = {"n": len(pts), "within_city_r_raw": pearson(pts)}
print(json.dumps(tests, indent=1))
print(json.dumps(per_city, indent=1))
json.dump({"tests": tests, "per_city": per_city}, open(f"{B}/gray_safety_lane_tests_v1.json", "w"), indent=1)
print("SAVED tests")
