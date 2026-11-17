"""Build the upload queue with duplicate protection (no upload happens here).

    python tools/upload_queue.py [--first N] [--dashboard uploads/dashboard-names.json]

For each outfit in uploads/plan.csv (in order), each half is:
  already uploaded      logged in uploads/log.csv with an asset ID (or the spec says uploaded: true)
  on dashboard, unlogged  a group item with the same name exists but is not in the log: NOT uploaded;
                        it is added to the log (asset ID from the dashboard snapshot) and reported
  to upload             otherwise
Outfits with one half done are queued for the missing half only. Writes uploads/queue.csv.
"""
import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clothing import ROOT   # noqa: E402

UP = ROOT / "uploads"
LOG = UP / "log.csv"
LOG_FIELDS = ["outfit_id", "garment", "file", "asset_id", "name", "price", "fee_paid", "time", "moderation_status"]


def read_log():
    if not LOG.exists():
        return []
    with LOG.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_log(row):
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in LOG_FIELDS})


def spec_by_id():
    out = {}
    for p in (ROOT / "specs").glob("*.yaml"):
        if p.name.startswith("_"):
            continue
        s = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        out[s.get("id") or p.stem] = (p, s)
    return out


def build(first=None, dashboard=None):
    plan = list(csv.DictReader((UP / "plan.csv").open(encoding="utf-8")))
    log = read_log()
    logged = {(r["outfit_id"], r["garment"]): r for r in log if r.get("asset_id")}
    logged_names = {r["name"]: r for r in log if r.get("asset_id")}
    dash = json.loads(Path(dashboard).read_text(encoding="utf-8")) if dashboard and Path(dashboard).exists() else {}
    specs = spec_by_id()
    rows, found_unlogged = [], []
    for r in plan[: first or len(plan)]:
        oid = r["outfit"]
        spec = specs.get(oid, (None, {}))[1]
        up = spec.get("upload") or {}
        for g in ("shirt", "pants"):
            name = r[f"{g}_name"]
            status, aid = "to upload", ""
            if (oid, g) in logged or name in logged_names:
                status, aid = "already uploaded", (logged.get((oid, g)) or logged_names[name])["asset_id"]
            elif spec.get("uploaded") and up.get(f"{g}_asset_id"):
                status, aid = "already uploaded", str(up[f"{g}_asset_id"])
            elif name in dash:
                status, aid = "on dashboard, not in log: skipped and logged", str(dash[name])
                found_unlogged.append((oid, g, name, aid))
                append_log({"outfit_id": oid, "garment": g, "file": r[f"{g}_file"], "asset_id": aid, "name": name,
                            "price": "?", "fee_paid": "unknown (found on dashboard)",
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "moderation_status": "found on dashboard, not uploaded by this run"})
            rows.append({"n": r["n"], "outfit": oid, "garment": g, "file": r[f"{g}_file"], "name": name,
                         "description": r[f"{g}_description"], "price": 5, "status": status, "asset_id": aid})
    for oid in {x["outfit"] for x in rows}:
        halves = [x for x in rows if x["outfit"] == oid]
        todo = [x for x in halves if x["status"] == "to upload"]
        if len(todo) == 1:
            todo[0]["status"] = "to upload (missing half only)"
    with (UP / "queue.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    return rows, found_unlogged


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--first", type=int)
    ap.add_argument("--dashboard", default=str(UP / "dashboard-names.json"))
    a = ap.parse_args()
    rows, found = build(a.first, a.dashboard)
    for x in rows:
        print(f"{x['n']:>3} {x['outfit']:<28} {x['garment']:<6} {x['status']:<45} {x['asset_id']:<16} {x['name']}")
    if found:
        print("\nFOUND ON DASHBOARD BUT NOT IN LOG (not uploaded, now logged):")
        for f in found:
            print("  ", *f)
    print("\nto upload:", sum(1 for x in rows if x["status"].startswith("to upload")), "items")


if __name__ == "__main__":
    main()
