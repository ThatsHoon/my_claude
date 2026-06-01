#!/usr/bin/env python3
"""replay_telemetry.py — Pull cycle telemetry from Supabase and replay offline.

Reads cycles + joint_snapshots + cycle_events + failures for a single robot
over a time window and renders:
  • per-cycle joint trajectory traces (one subplot per joint)
  • cycle outcome (success/fail) markers
  • failure annotations from `failures` table
  • optional histogram of cycle durations

Useful for post-mortem debugging — "what did r2 do during 14:30~14:45 yesterday
when the failure rate spiked?". Companion to references/telemetry-supabase.md
§"운영 쿼리 예시".

Environment:
    SUPABASE_DB_URL   postgres://user:pwd@host:5432/db  (read-only role OK)

Usage:
    python3 replay_telemetry.py --robot r2 --since "2026-05-14T14:30:00Z" \
                                --until "2026-05-14T14:45:00Z" \
                                --out /tmp/r2_replay.png
"""

from __future__ import annotations
import argparse
import os
import sys
from datetime import datetime, timezone


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--robot", required=True, help="robot_id, e.g. r2")
    p.add_argument("--since", required=True, help="ISO8601 UTC start, inclusive")
    p.add_argument("--until", required=True, help="ISO8601 UTC end, exclusive")
    p.add_argument("--out", default="-", help="png path, or - for live show()")
    p.add_argument("--db-url", default=os.environ.get("SUPABASE_DB_URL"),
                   help="Postgres connection URL")
    p.add_argument("--hist", action="store_true",
                   help="Also draw cycle-duration histogram")
    return p.parse_args()


def fetch(conn, robot: str, since: datetime, until: datetime):
    """Return (cycles, joint_rows, failures) as lists of dicts."""
    cycles = conn.execute("""
        SELECT id, detection_id, start_ts, pick_ts, place_ts, end_ts,
               success, fail_reason
          FROM cycles
         WHERE robot_id = $1 AND start_ts >= $2 AND start_ts < $3
         ORDER BY start_ts
    """, robot, since, until).fetchall()

    joints = conn.execute("""
        SELECT cycle_id, ts, q, qd
          FROM joint_snapshots
         WHERE robot_id = $1 AND ts >= $2 AND ts < $3
         ORDER BY ts
    """, robot, since, until).fetchall()

    fails = conn.execute("""
        SELECT cycle_id, ts, category, message
          FROM failures
         WHERE robot_id = $1 AND ts >= $2 AND ts < $3
         ORDER BY ts
    """, robot, since, until).fetchall()

    return cycles, joints, fails


def plot(cycles, joints, fails, robot: str, out: str, hist: bool):
    import matplotlib
    if out != "-":
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    # m0609 has 6 joints. Compose a figure with 6 stacked subplots + optional histogram row.
    n_joints = 6
    nrows = n_joints + (1 if hist else 0)
    fig, axs = plt.subplots(nrows, 1, figsize=(14, 2.0 * nrows), sharex=False)
    if nrows == 1:
        axs = [axs]

    # Build per-joint time series from joint snapshots.
    import numpy as np
    ts_arr = [r["ts"] for r in joints]
    q_arr = np.asarray([r["q"] for r in joints]) if joints else np.empty((0, n_joints))

    for j in range(n_joints):
        ax = axs[j]
        if q_arr.size > 0:
            ax.plot(ts_arr, q_arr[:, j], lw=0.7, label=f"joint{j+1}")
        ax.set_ylabel(f"j{j+1} [rad]")
        ax.grid(True, alpha=0.3)
        if j == 0:
            ax.set_title(f"replay  robot={robot}  cycles={len(cycles)}  "
                         f"successes={sum(1 for c in cycles if c['success'])}  "
                         f"failures={sum(1 for c in cycles if c['success'] is False)}")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        # Overlay cycle boundaries
        for c in cycles:
            color = "green" if c["success"] else ("red" if c["success"] is False else "gray")
            ax.axvspan(c["start_ts"], c["end_ts"] or c["start_ts"], alpha=0.05, color=color)
        # Annotate failures (only on j0 subplot to avoid clutter)
        if j == 0:
            for f in fails:
                ax.annotate(f["category"], xy=(f["ts"], ax.get_ylim()[1]),
                            xytext=(0, -15), textcoords="offset points",
                            fontsize=6, color="red")

    if hist and cycles:
        ax = axs[-1]
        durs_ms = [(c["end_ts"] - c["start_ts"]).total_seconds() * 1000
                   for c in cycles if c["end_ts"] is not None]
        if durs_ms:
            ax.hist(durs_ms, bins=20, color="#4488cc", alpha=0.8)
        ax.set_xlabel("cycle duration [ms]")
        ax.set_ylabel("count")
        ax.set_title("cycle duration distribution")
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    if out == "-":
        plt.show()
    else:
        fig.savefig(out, dpi=120)
        print(f"saved {out}")


def main():
    args = parse_args()
    if not args.db_url:
        print("ERROR: --db-url or SUPABASE_DB_URL required", file=sys.stderr)
        sys.exit(2)
    try:
        import psycopg
    except ImportError:
        print("ERROR: pip install psycopg[binary]", file=sys.stderr)
        sys.exit(3)

    since = datetime.fromisoformat(args.since.replace("Z", "+00:00")).astimezone(timezone.utc)
    until = datetime.fromisoformat(args.until.replace("Z", "+00:00")).astimezone(timezone.utc)

    with psycopg.connect(args.db_url, row_factory=psycopg.rows.dict_row) as conn:
        cycles, joints, fails = fetch(conn, args.robot, since, until)
    print(f"fetched cycles={len(cycles)} joint_rows={len(joints)} failures={len(fails)}")
    if not cycles and not joints:
        print("nothing to plot — exiting", file=sys.stderr)
        sys.exit(0)
    plot(cycles, joints, fails, args.robot, args.out, args.hist)


if __name__ == "__main__":
    main()
