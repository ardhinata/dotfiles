#!/usr/bin/env python3
"""A/B two embedding widths through AFT's own semantic lane.

The harness drives the real `aft` binary over its NDJSON stdin protocol, so
the numbers come from the production code path: the same chunker, the same
embed-text caps, the same query instruction, the same ranking, and the same
fused trigram+semantic lane the agent sees.

Each arm gets its own storage dir, its own config home, and its own proxy
port. AFT stores one semantic artifact per root, and the artifact key
includes the fingerprint (backend, model, base_url, dimension, chunking
version, embed-text caps), so two widths need two storage dirs.

Usage:
  aft_width_ab.py index  --root DIR --arm NAME --width N --port P --proxy-provider JSON
  aft_width_ab.py query  --root DIR --arm NAME --width N --port P --queries FILE
  aft_width_ab.py report --arms NAME=NAME,...

The queries file is JSON: [{"id": "...", "query": "...", "expect": "path/rel",
  "kind": "positive"}, ...]
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import IO, cast

WORK = Path(os.environ.get("AFT_AB_WORK", "/tmp/opencode/width-ab"))
MODEL = "qwen/qwen3-embedding-8b"
KEY_ENV = "OPENROUTER_API_OPENCODE_INDEX"


def find_aft_binary() -> Path:
    """Locate the native AFT binary that ships with the plugin.

    The plugin version directory changes on every plugin update, so the path
    is discovered rather than pinned.
    """
    override = os.environ.get("AFT_AB_BIN")
    if override:
        return Path(override)
    npm_root = Path(
        os.environ.get(
            "AFT_AB_NPM_ROOT",
            "/home/ardhinata/.cache/opencode/npm/@cortexkit",
        )
    )
    candidates = sorted(
        npm_root.glob("aft-opencode@*/**/aft-linux-x64/bin/aft"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise SystemExit("no AFT native binary found; set AFT_AB_BIN")
    return candidates[0]


AFT_NATIVE = find_aft_binary()


def arm_dir(arm: str) -> Path:
    return WORK / arm


def storage_dir(arm: str) -> Path:
    return arm_dir(arm) / "storage"


def config_home(arm: str) -> Path:
    return arm_dir(arm) / "config"


def salt(arm: str) -> str:
    # The salt is the identity segment in the endpoint URL. It changes the
    # AFT fingerprint, so each arm needs its own.
    return f"w{arm}"


def base_url(arm: str, port: int) -> str:
    return f"http://127.0.0.1:{port}/{salt(arm)}/v1"


def write_config(
    arm: str, port: int, root: Path, width: int, trigram: bool = True
) -> None:
    """Write the arm's user-tier AFT config.

    `semantic.base_url` and `index.roots` are user-tier-only keys in AFT, so
    they must live in the user config home, not in a project config.

    With trigram off, AFT has no lexical lane, so a query runs the semantic
    lane alone. That is how the semantic vector is measured on its own.
    """
    home = config_home(arm)
    (home / "cortexkit").mkdir(parents=True, exist_ok=True)
    config = {
        "semantic": {
            "backend": "openai_compatible",
            "model": MODEL,
            "base_url": base_url(arm, port),
            "api_key_env": KEY_ENV,
            "max_input_tokens": 480,
            "max_batch_size": 32,
            "query_instruction": "auto",
            # The default is 3000 ms. One remote query embedding can take
            # longer than that while a build shares the provider quota, and a
            # timed-out query drops the semantic lane for that request. The
            # lane then answers with lexical results only, which reads like a
            # width difference but is not one.
            "query_timeout_ms": 30000,
        },
        "indexes": {"trigram": trigram, "semantic": True, "callgraph": False},
        "index": {"roots": [{"path": str(root), "indexes": ["semantic"]}]},
    }
    (home / "cortexkit" / "aft.jsonc").write_text(json.dumps(config, indent=2))


def arm_env(arm: str, port: int) -> dict:
    env = dict(os.environ)
    env["XDG_CONFIG_HOME"] = str(config_home(arm))
    env["AFT_STORAGE_DIR"] = str(storage_dir(arm))
    env["HOME"] = str(arm_dir(arm) / "home")
    (arm_dir(arm) / "home").mkdir(parents=True, exist_ok=True)
    return env


def proxy_url(arm: str, port: int) -> str:
    return f"http://127.0.0.1:{port}/{salt(arm)}/v1/embeddings"


def embed(arm: str, port: int, texts: list) -> list:
    """Embed texts through the arm's proxy. One request per call."""
    key = os.environ[KEY_ENV]
    body = json.dumps({"model": MODEL, "input": texts}).encode()
    request = urllib.request.Request(
        proxy_url(arm, port),
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        payload = json.load(response)
    return [item["embedding"] for item in payload["data"]]


def index(arm: str, port: int, root: Path, width: int) -> None:
    """Build the arm's semantic index with the real AFT binary."""
    write_config(arm, port, root, width)
    env = arm_env(arm, port)
    storage_dir(arm).mkdir(parents=True, exist_ok=True)
    print(f"[{arm}] building semantic index at {width} dims", flush=True)
    started = time.time()
    result = subprocess.run(
        [str(AFT_NATIVE), "index"],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
        timeout=7200,
    )
    print(result.stdout[-4000:], flush=True)
    if result.returncode != 0:
        print(result.stderr[-4000:], file=sys.stderr, flush=True)
        raise SystemExit(f"[{arm}] index failed with {result.returncode}")
    print(f"[{arm}] done in {time.time() - started:.0f}s", flush=True)


class Bridge:
    """A minimal AFT NDJSON client: configure, then tool calls."""

    def __init__(self, arm: str, port: int, root: Path):
        self.arm = arm
        self.proc = subprocess.Popen(
            [str(AFT_NATIVE)],
            cwd=str(root),
            env=arm_env(arm, port),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.stdin = cast("IO[str]", self.proc.stdin)
        self.stdout = cast("IO[str]", self.proc.stdout)
        self.stderr = cast("IO[str]", self.proc.stderr)
        self.counter = 0

    def call(self, command: str, params: dict) -> dict:
        self.counter += 1
        request_id = str(self.counter)
        frame = {"id": request_id, "command": command, **params}
        self.stdin.write(json.dumps(frame) + "\n")
        self.stdin.flush()
        while True:
            line = self.stdout.readline()
            if not line:
                err = self.stderr.read()
                raise SystemExit(f"bridge closed: {err[-2000:]}")
            line = line.strip()
            if not line:
                continue
            response = json.loads(line)
            if response.get("id") == request_id:
                return response

    def configure(self, root: Path) -> dict:
        # The harness field is required by the configure payload. "runner" is
        # the neutral value for a non-plugin client that drives the binary
        # directly over NDJSON.
        #
        # cortexkit_user_config_path is how the plugin hands AFT its user-tier
        # config. Without it, configure reads no user tier, so the semantic
        # backend falls back to the fastembed default and the query vector
        # does not match the index vectors.
        return self.call(
            "configure",
            {
                "project_root": str(root),
                "harness": "runner",
                "cortexkit_user_config_path": str(
                    config_home(self.arm) / "cortexkit" / "aft.jsonc"
                ),
            },
        )

    def search(self, query: str, top_k: int = 20) -> dict:
        return self.call(
            "semantic_search", {"query": query, "topK": top_k}
        )

    def wait_semantic_ready(self, timeout_s: int = 900) -> bool:
        """Poll until the semantic lane reports ready.

        AFT answers a query during an index build with lexical results only,
        so a query issued too early measures the wrong lane.
        """
        deadline = time.time() + timeout_s
        probe = "warm up the semantic lane"
        while time.time() < deadline:
            response = self.search(probe, top_k=1)
            if response.get("semantic_status") == "ready":
                return True
            time.sleep(5)
        return False

    def close(self) -> None:
        try:
            self.stdin.close()
            self.proc.wait(timeout=30)
        except Exception:
            self.proc.kill()


def parse_results(response: dict) -> list:
    """Pull the ranked result rows out of an aft_search response.

    The response carries `results` at the top level, next to `status`,
    `semantic_status`, and `lanes`.
    """
    return response.get("results") or []


def expected_paths(item: dict) -> list:
    """The set of files that answer the query.

    A query can have several valid answers. A corpus that ships one file per
    platform has siblings like `parser-wasm.bun.ts` and `parser-wasm.node.ts`
    that are the same answer. Scoring only one of them as correct turns a
    correct result into a miss.
    """
    expect = item.get("expect")
    if not expect:
        return []
    if isinstance(expect, str):
        return [expect]
    return list(expect)


def rank_of(paths: list, wanted: list) -> int | None:
    """1-based rank of the first wanted path, or None when none matched."""
    if not wanted:
        return None
    for rank, path in enumerate(paths):
        for target in wanted:
            if target in path:
                return rank + 1
    return None


def query(
    arm: str,
    port: int,
    root: Path,
    width: int,
    queries: list,
    trigram: bool = True,
    label: str = "",
) -> dict:
    """Run every query against the arm and record the ranking."""
    write_config(arm, port, root, width, trigram=trigram)
    bridge = Bridge(arm, port, root)
    configured = bridge.configure(root)
    if configured.get("success") is False:
        print(json.dumps(configured)[:2000], file=sys.stderr)
        bridge.close()
        raise SystemExit(f"[{arm}] configure failed")
    print(f"[{arm}] configured", flush=True)
    if not bridge.wait_semantic_ready():
        print(f"[{arm}] semantic lane never became ready", file=sys.stderr)
        bridge.close()
        raise SystemExit(f"[{arm}] semantic lane not ready")
    print(f"[{arm}] semantic lane ready", flush=True)
    rows = []
    for item in queries:
        started = time.time()
        response = bridge.search(item["query"], top_k=20)
        elapsed = time.time() - started
        # A query whose semantic lane was not ready measures the wrong thing.
        # Fail loudly instead of scoring it as a miss.
        lane_state = (response.get("lanes") or {}).get("semantic") or {}
        if lane_state.get("status") not in ("ready", None):
            raise SystemExit(
                f"[{arm}] semantic lane not ready for {item['id']}: "
                f"{lane_state.get('status')} {lane_state.get('reason')}"
            )
        results = parse_results(response)
        paths = [r.get("file", "") for r in results]
        scores = [r.get("semantic_score", r.get("score")) for r in results]
        sources = [r.get("source") for r in results]
        wanted = expected_paths(item)
        hit = rank_of(paths, wanted)
        # Re-rank the same candidate set by the semantic score alone. The
        # fused lane can hide a width difference, so this isolates what the
        # semantic vector itself says.
        semantic_only = [
            (r.get("file", ""), r.get("semantic_score"))
            for r in results
            if r.get("semantic_score") is not None
        ]
        semantic_only.sort(key=lambda pair: pair[1], reverse=True)
        semantic_hit = rank_of([p for p, _ in semantic_only], wanted)
        rows.append(
            {
                "id": item["id"],
                "query": item["query"],
                "kind": item.get("kind", "positive"),
                "expect": item.get("expect"),
                "wanted": wanted,
                "hit_rank": hit,
                "paths": paths,
                "scores": scores,
                "sources": sources,
                "semantic_only_paths": [p for p, _ in semantic_only],
                "semantic_only_hit_rank": semantic_hit,
                "semantic_status": response.get("semantic_status"),
                "lanes": response.get("lanes"),
                "status": response.get("status"),
                "elapsed_ms": int(elapsed * 1000),
                "text": (response.get("text") or "")[:2000],
            }
        )
        print(
            f"[{arm}] {item['id']}: hit={hit} ({elapsed:.1f}s) top={paths[:2]}",
            flush=True,
        )
    bridge.close()
    out = arm_dir(arm) / (label or "results.json")
    out.write_text(json.dumps(rows, indent=2))
    print(f"[{arm}] wrote {out}", flush=True)
    return {"arm": arm, "width": width, "rows": rows}


def score(rows: list) -> dict:
    """Recall@k, MRR@10, and the negative-query behaviour."""
    positives = [r for r in rows if r["kind"] == "positive"]
    negatives = [r for r in rows if r["kind"] == "negative"]
    metrics = {}
    for k in (1, 5, 10):
        hits = sum(1 for r in positives if r["hit_rank"] and r["hit_rank"] <= k)
        metrics[f"recall_at_{k}"] = round(hits / len(positives), 4) if positives else None
    mrr = (
        sum(1 / r["hit_rank"] for r in positives if r["hit_rank"])
        / len(positives)
        if positives
        else None
    )
    metrics["mrr_at_10"] = round(mrr, 4) if mrr is not None else None
    metrics["positive_count"] = len(positives)
    metrics["negative_count"] = len(negatives)
    # A negative query has no ground truth, so the useful signal is how
    # confident the lane still is: the top score it returns.
    if negatives:
        tops = [
            r["scores"][0]
            for r in negatives
            if r["scores"] and r["scores"][0] is not None
        ]
        metrics["negative_top_score_mean"] = (
            round(sum(tops) / len(tops), 4) if tops else None
        )
        metrics["negative_top_score_max"] = round(max(tops), 4) if tops else None
    if positives:
        top_scores = [
            r["scores"][0]
            for r in positives
            if r["scores"] and r["scores"][0] is not None
        ]
        metrics["positive_top_score_mean"] = (
            round(sum(top_scores) / len(top_scores), 4) if top_scores else None
        )
    latencies = [r["elapsed_ms"] for r in rows]
    metrics["query_latency_p50_ms"] = (
        sorted(latencies)[len(latencies) // 2] if latencies else None
    )
    return metrics


def reciprocal_rank(row: dict) -> float:
    rank = row["hit_rank"]
    return 1.0 / rank if rank else 0.0


def semantic_reciprocal_rank(row: dict) -> float:
    rank = row.get("semantic_only_hit_rank")
    return 1.0 / rank if rank else 0.0


def semantic_only_metrics(rows: list) -> dict:
    """Recall and MRR over the semantic lane alone.

    The candidate set is the same one the fused lane returned, re-ranked by
    the semantic score. This shows what the vector itself says, which the
    fused ranking can hide.
    """
    positives = [r for r in rows if r["kind"] == "positive"]
    metrics: dict = {"semantic_only_count": len(positives)}
    if not positives:
        return metrics
    for k in (1, 5, 10):
        hits = sum(
            1
            for r in positives
            if r.get("semantic_only_hit_rank")
            and r["semantic_only_hit_rank"] <= k
        )
        metrics[f"semantic_only_recall_at_{k}"] = round(hits / len(positives), 4)
    mrr = sum(semantic_reciprocal_rank(r) for r in positives) / len(positives)
    metrics["semantic_only_mrr_at_10"] = round(mrr, 4)
    found = sum(1 for r in positives if r.get("semantic_only_hit_rank"))
    metrics["semantic_only_found_in_candidates"] = found
    return metrics


def paired_compare(left: list, right: list) -> dict:
    """Compare two arms on the SAME queries.

    An unpaired recall difference on 50 queries is inside the noise, so the
    comparison is paired: per query, one arm wins, loses, or ties. The sign
    test on those pairs is the evidence that a difference is real.
    """
    left_by_id = {r["id"]: r for r in left}
    right_by_id = {r["id"]: r for r in right}
    shared = [
        qid
        for qid in left_by_id
        if qid in right_by_id and left_by_id[qid]["kind"] == "positive"
    ]
    wins = losses = ties = 0
    deltas = []
    for qid in shared:
        a = reciprocal_rank(left_by_id[qid])
        b = reciprocal_rank(right_by_id[qid])
        deltas.append(a - b)
        if a > b:
            wins += 1
        elif a < b:
            losses += 1
        else:
            ties += 1
    n = wins + losses
    # Two-sided sign test p-value, exact binomial under p=0.5.
    if n == 0:
        p_value = 1.0
    else:
        k = min(wins, losses)
        tail = sum(
            math.comb(n, i) for i in range(0, k + 1)
        ) / (2**n)
        p_value = min(1.0, tail * 2)
    return {
        "shared_positive_queries": len(shared),
        "left_wins": wins,
        "left_losses": losses,
        "ties": ties,
        "sign_test_p_value": round(p_value, 4),
        "mrr_delta": round(sum(deltas) / len(deltas), 4) if deltas else None,
        "mean_mrr_left": round(
            sum(reciprocal_rank(left_by_id[q]) for q in shared) / len(shared), 4
        )
        if shared
        else None,
        "mean_mrr_right": round(
            sum(reciprocal_rank(right_by_id[q]) for q in shared) / len(shared), 4
        )
        if shared
        else None,
        "discordant_queries": [
            {
                "id": q,
                "left_rank": left_by_id[q]["hit_rank"],
                "right_rank": right_by_id[q]["hit_rank"],
            }
            for q in shared
            if reciprocal_rank(left_by_id[q]) != reciprocal_rank(right_by_id[q])
        ],
    }


def paired_compare_semantic_only(left: list, right: list) -> dict:
    """The same paired sign test, over the semantic lane alone."""
    left_by_id = {r["id"]: r for r in left}
    right_by_id = {r["id"]: r for r in right}
    shared = [
        qid
        for qid in left_by_id
        if qid in right_by_id
        and left_by_id[qid]["kind"] == "positive"
        and left_by_id[qid].get("semantic_only_hit_rank") is not None
        and right_by_id[qid].get("semantic_only_hit_rank") is not None
    ]
    wins = losses = ties = 0
    for qid in shared:
        a = semantic_reciprocal_rank(left_by_id[qid])
        b = semantic_reciprocal_rank(right_by_id[qid])
        if a > b:
            wins += 1
        elif a < b:
            losses += 1
        else:
            ties += 1
    n = wins + losses
    if n == 0:
        p_value = 1.0
    else:
        k = min(wins, losses)
        p_value = min(
            1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / (2**n)
        )
    return {
        "shared_queries": len(shared),
        "left_wins": wins,
        "left_losses": losses,
        "ties": ties,
        "sign_test_p_value": round(p_value, 4),
        "mean_mrr_left": round(
            sum(semantic_reciprocal_rank(left_by_id[q]) for q in shared) / len(shared), 4
        )
        if shared
        else None,
        "mean_mrr_right": round(
            sum(semantic_reciprocal_rank(right_by_id[q]) for q in shared) / len(shared), 4
        )
        if shared
        else None,
    }


def bootstrap_mrr_ci(rows: list, iterations: int = 2000) -> tuple:
    """Percentile bootstrap CI for MRR@10 over the positive queries."""
    import random

    positives = [r for r in rows if r["kind"] == "positive"]
    if not positives:
        return (None, None)
    values = [reciprocal_rank(r) for r in positives]
    rng = random.Random(1234)
    means = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(sum(sample) / len(sample))
    means.sort()
    low = means[int(0.025 * len(means))]
    high = means[int(0.975 * len(means))]
    return (round(low, 4), round(high, 4))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("index")
    p.add_argument("--root", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--width", type=int, required=True)
    p.add_argument("--port", type=int, required=True)

    p = sub.add_parser("query")
    p.add_argument("--root", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--width", type=int, required=True)
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--queries", required=True)
    p.add_argument(
        "--no-trigram",
        action="store_true",
        help="run the semantic lane alone, with the lexical lane off",
    )
    p.add_argument("--label", default="", help="results file name")

    p = sub.add_parser("report")
    p.add_argument("--arms", required=True, help="name=width,name=width")
    p.add_argument("--label", default="results.json")

    args = parser.parse_args()

    if args.cmd == "index":
        index(args.arm, args.port, Path(args.root), args.width)
    elif args.cmd == "query":
        queries = json.loads(Path(args.queries).read_text())
        query(
            args.arm,
            args.port,
            Path(args.root),
            args.width,
            queries,
            trigram=not args.no_trigram,
            label=args.label,
        )
    else:
        arms = []
        for pair in args.arms.split(","):
            name, width = pair.split("=")
            rows = json.loads((arm_dir(name) / args.label).read_text())
            metrics = score(rows)
            low, high = bootstrap_mrr_ci(rows)
            metrics["mrr_at_10_ci95"] = [low, high]
            metrics.update(semantic_only_metrics(rows))
            arms.append((name, int(width), metrics))
        print(json.dumps(arms, indent=2))
        if len(arms) == 2:
            left = json.loads((arm_dir(arms[0][0]) / args.label).read_text())
            right = json.loads((arm_dir(arms[1][0]) / args.label).read_text())
            print("\npaired comparison (first arm vs second arm):")
            print(json.dumps(paired_compare(left, right), indent=2))
            print("\npaired comparison, semantic lane only:")
            print(json.dumps(paired_compare_semantic_only(left, right), indent=2))


if __name__ == "__main__":
    main()
