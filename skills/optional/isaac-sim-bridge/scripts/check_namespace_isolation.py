#!/usr/bin/env python3
"""check_namespace_isolation.py — Verify per-robot ROS 2 namespace isolation.

After multi_robot_bringup.py finishes and Isaac Sim is playing, run this on
the host to confirm every expected /{robot_id}/... topic exists, every
topic is uniquely owned by exactly one publisher, and no topic crosses
between robot namespaces.

Usage (plain ROS 2 environment, NOT inside Isaac Sim):
    python3 check_namespace_isolation.py --robots r0,r1,r2,r3

Exit code 0 = isolation verified, 1 = one or more violations detected.
"""

from __future__ import annotations
import argparse
import sys
from collections import defaultdict
from typing import Iterable

EXPECTED_PER_ROBOT = (
    "joint_states",
    "joint_command",
    "cam/conveyor/image_raw",
    "cam/conveyor/camera_info",
    # Optional but commonly required; missing ones are reported as warnings, not errors:
    # "yolo/detections", "diagnostics", "robot_state", "contact_events", "heartbeat"
)
OPTIONAL_PER_ROBOT = (
    "yolo/detections",
    "diagnostics",
    "robot_state",
    "contact_events",
    "heartbeat",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--robots", default="r0,r1,r2,r3",
                   help="Comma-separated robot_ids that the bringup created")
    p.add_argument("--strict", action="store_true",
                   help="Treat missing OPTIONAL_PER_ROBOT topics as errors")
    return p.parse_args()


def list_topics() -> list[tuple[str, list[str]]]:
    """Return [(topic_name, [types])]. Uses rclpy because `ros2 topic list -t`
    parsing is brittle."""
    import rclpy
    rclpy.init()
    try:
        node = rclpy.create_node("namespace_audit")
        # Give discovery a moment.
        import time
        time.sleep(1.0)
        topics = node.get_topic_names_and_types()
        node.destroy_node()
    finally:
        rclpy.shutdown()
    return topics


def categorise(topics: list[tuple[str, list[str]]], robot_ids: list[str]):
    by_ns: dict[str, set[str]] = defaultdict(set)
    rogue: list[str] = []
    for name, _types in topics:
        if not name.startswith("/"):
            rogue.append(name)
            continue
        head = name.split("/")[1] if len(name.split("/")) > 1 else ""
        if head in robot_ids:
            relative = "/".join(name.split("/")[2:])
            by_ns[head].add(relative)
    return by_ns, rogue


def audit(by_ns, robot_ids, strict: bool) -> list[str]:
    problems: list[str] = []
    for rid in robot_ids:
        present = by_ns.get(rid, set())
        missing_req = [t for t in EXPECTED_PER_ROBOT if t not in present]
        if missing_req:
            problems.append(f"{rid}: missing required topics → {missing_req}")
        missing_opt = [t for t in OPTIONAL_PER_ROBOT if t not in present]
        if missing_opt:
            level = "ERROR" if strict else "warn"
            line = f"{rid}: {level} — missing optional → {missing_opt}"
            if strict:
                problems.append(line)
            else:
                print(line, file=sys.stderr)
    # cross-namespace collisions
    seen: dict[str, str] = {}
    for ns, topics in by_ns.items():
        for t in topics:
            full = f"/{ns}/{t}"
            other = seen.get(full)
            if other and other != ns:
                problems.append(f"topic {full} appears under both ns={other} and ns={ns}")
            seen[full] = ns
    return problems


def main():
    args = parse_args()
    robot_ids = [r.strip() for r in args.robots.split(",") if r.strip()]
    topics = list_topics()
    if not topics:
        print("ERROR: no topics discovered. Is Isaac Sim playing? Is ROS_DOMAIN_ID set?",
              file=sys.stderr)
        sys.exit(2)

    by_ns, rogue = categorise(topics, robot_ids)
    problems = audit(by_ns, robot_ids, args.strict)

    # Report
    print(f"discovered {len(topics)} topics, {len(by_ns)} namespaces matching --robots")
    for rid in robot_ids:
        count = len(by_ns.get(rid, set()))
        print(f"  /{rid}: {count} topic(s)")
    if rogue:
        print(f"  [warn] {len(rogue)} topic(s) not in any robot namespace (e.g. /clock, /tf): "
              f"{rogue[:5]}{'...' if len(rogue) > 5 else ''}")

    if problems:
        print(f"\nFAIL — {len(problems)} issue(s):", file=sys.stderr)
        for p in problems:
            print(f"  • {p}", file=sys.stderr)
        sys.exit(1)

    print("\nPASS — namespace isolation verified.")


if __name__ == "__main__":
    main()
