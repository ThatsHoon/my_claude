#!/usr/bin/env python3
"""qos_check.py — introspect a ROS 2 topic's publisher/subscriber QoS profiles
and flag mismatches that cause silent message drops.

Usage:
    python3 qos_check.py <topic_name>

Example:
    python3 qos_check.py /scan
    python3 qos_check.py /tf_static

Compatible with ROS 2 Humble / Iron / Jazzy / Kilted / Rolling.

Exit codes:
  0 — no issues found
  1 — incompatible QoS detected
  2 — runtime error (no ROS env, etc.)
"""
from __future__ import annotations
import sys
import time

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import (
        QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy)
except ImportError as e:
    print(f"error: rclpy not available — source your ROS 2 environment first ({e})",
          file=sys.stderr)
    sys.exit(2)


def reliability_name(r):
    return {
        QoSReliabilityPolicy.RELIABLE: 'RELIABLE',
        QoSReliabilityPolicy.BEST_EFFORT: 'BEST_EFFORT',
        QoSReliabilityPolicy.UNKNOWN: 'UNKNOWN',
        QoSReliabilityPolicy.SYSTEM_DEFAULT: 'SYSTEM_DEFAULT',
    }.get(r, str(r))


def durability_name(d):
    return {
        QoSDurabilityPolicy.VOLATILE: 'VOLATILE',
        QoSDurabilityPolicy.TRANSIENT_LOCAL: 'TRANSIENT_LOCAL',
        QoSDurabilityPolicy.UNKNOWN: 'UNKNOWN',
        QoSDurabilityPolicy.SYSTEM_DEFAULT: 'SYSTEM_DEFAULT',
    }.get(d, str(d))


def history_name(h):
    return {
        QoSHistoryPolicy.KEEP_LAST: 'KEEP_LAST',
        QoSHistoryPolicy.KEEP_ALL: 'KEEP_ALL',
        QoSHistoryPolicy.UNKNOWN: 'UNKNOWN',
        QoSHistoryPolicy.SYSTEM_DEFAULT: 'SYSTEM_DEFAULT',
    }.get(h, str(h))


def is_compatible(pub_reliability, sub_reliability, pub_durability, sub_durability):
    """Return (compatible, reason)."""
    # Subscriber RELIABLE requires publisher RELIABLE.
    if (sub_reliability == QoSReliabilityPolicy.RELIABLE
            and pub_reliability == QoSReliabilityPolicy.BEST_EFFORT):
        return False, ('reliability: subscriber requests RELIABLE '
                       'but publisher offers BEST_EFFORT')
    # Subscriber TRANSIENT_LOCAL requires publisher TRANSIENT_LOCAL.
    if (sub_durability == QoSDurabilityPolicy.TRANSIENT_LOCAL
            and pub_durability == QoSDurabilityPolicy.VOLATILE):
        return False, ('durability: subscriber requests TRANSIENT_LOCAL '
                       'but publisher offers VOLATILE')
    return True, ''


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    topic = sys.argv[1]

    rclpy.init()
    node = Node('qos_check_node')

    # Wait briefly for discovery.
    print(f"discovering peers for {topic} ...")
    time.sleep(1.5)

    pubs = node.get_publishers_info_by_topic(topic)
    subs = node.get_subscriptions_info_by_topic(topic)

    if not pubs and not subs:
        print(f"\nno publishers or subscribers found on '{topic}'.")
        print("   - is the topic name correct? `ros2 topic list -t` to list.")
        print("   - is the publishing node running?")
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(0)

    print(f"\n=== Publishers on {topic} ===")
    if not pubs:
        print("  (none)")
    for p in pubs:
        q = p.qos_profile
        print(f"  {p.node_namespace}{p.node_name}")
        print(f"    type        : {p.topic_type}")
        print(f"    reliability : {reliability_name(q.reliability)}")
        print(f"    durability  : {durability_name(q.durability)}")
        print(f"    history     : {history_name(q.history)} (depth={q.depth})")

    print(f"\n=== Subscribers on {topic} ===")
    if not subs:
        print("  (none)")
    for s in subs:
        q = s.qos_profile
        print(f"  {s.node_namespace}{s.node_name}")
        print(f"    type        : {s.topic_type}")
        print(f"    reliability : {reliability_name(q.reliability)}")
        print(f"    durability  : {durability_name(q.durability)}")
        print(f"    history     : {history_name(q.history)} (depth={q.depth})")

    # Compatibility check.
    issues = []
    for p in pubs:
        for s in subs:
            ok, reason = is_compatible(
                p.qos_profile.reliability, s.qos_profile.reliability,
                p.qos_profile.durability, s.qos_profile.durability)
            if not ok:
                issues.append((p, s, reason))

    print()
    if issues:
        print(f"⚠ Found {len(issues)} QoS mismatch(es):")
        for p, s, reason in issues:
            print(f"\n  pub: {p.node_namespace}{p.node_name}")
            print(f"  sub: {s.node_namespace}{s.node_name}")
            print(f"  problem: {reason}")
            print(f"  → messages will be silently dropped to this subscriber")
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(1)
    else:
        print("✓ All publisher/subscriber pairs are QoS-compatible.")
        node.destroy_node()
        rclpy.shutdown()
        sys.exit(0)


if __name__ == '__main__':
    main()
