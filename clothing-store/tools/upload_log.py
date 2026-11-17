"""Record upload progress (called right after each step succeeds, so an interrupted run leaves an accurate log).

    python tools/upload_log.py item <outfit_id> <shirt|pants> <asset_id> <fee_paid> <status>
    python tools/upload_log.py status <asset_id> <status> [<fee_add>]     update an existing row (e.g. after publishing)
    python tools/upload_log.py done <spec_path> <shirt_asset_id> <pants_asset_id>   mark the outfit uploaded in its spec
"""
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from upload_queue import LOG, LOG_FIELDS, append_log   # noqa: E402
from clothing import ROOT                              # noqa: E402


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def main():
    cmd = sys.argv[1]
    if cmd == "item":
        oid, g, aid, fee, status = sys.argv[2:7]
        plan = {r["outfit"]: r for r in csv.DictReader((ROOT / "uploads" / "plan.csv").open(encoding="utf-8"))}
        r = plan[oid]
        append_log({"outfit_id": oid, "garment": g, "file": r[f"{g}_file"], "asset_id": aid, "name": r[f"{g}_name"],
                    "price": "5", "fee_paid": fee, "time": now(), "moderation_status": status})
    elif cmd == "status":
        aid, status = sys.argv[2:4]
        add = sys.argv[4] if len(sys.argv) > 4 else None
        rows = list(csv.DictReader(LOG.open(encoding="utf-8")))
        for r in rows:
            if r["asset_id"] == aid:
                r["moderation_status"] = status
                if add:
                    r["fee_paid"] = f"{r['fee_paid']} + {add}"
                r["time"] = f"{r['time']} / {now()}"
        with LOG.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=LOG_FIELDS)
            w.writeheader(); w.writerows(rows)
    elif cmd == "done":
        spec, sid, pid = sys.argv[2:5]
        p = Path(spec)
        s = p.read_text(encoding="utf-8")
        if "\nuploaded: true" not in s:
            s += (f"\n# upload record (set after the pair went live; validate.py refuses to queue it again)\nuploaded: true\n"
                  f"upload:\n  shirt_asset_id: {sid}\n  pants_asset_id: {pid}\n  date: {datetime.now():%Y-%m-%d}\n")
            p.write_text(s, encoding="utf-8")
    print("logged", sys.argv[1:])


if __name__ == "__main__":
    main()
