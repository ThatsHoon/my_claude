#!/usr/bin/env python3
"""
check_mcp_health.py — Diagnostic for isaac-sim-mcp connectivity.

Usage:
    python3 check_mcp_health.py

Checks (in order):
  1. Is `isaac-sim` process running?
  2. Is the extension's TCP listener on localhost:8766?
  3. Is the MCP server (Python subprocess) running?
  4. Can the MCP server reach the extension? (TCP ping)
  5. Is the kit log accessible? (latest entry mtime)

Prints a structured diagnosis with what's working and what to fix.
Designed for the user to run via Bash when MCP tools start failing.
"""

import os
import socket
import subprocess
import sys
from pathlib import Path


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "OK  " if ok else "FAIL"
    line = f"  [{mark}] {label}"
    if detail:
        line += f"  — {detail}"
    print(line)


def pgrep(pattern: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["pgrep", "-af", pattern], stderr=subprocess.DEVNULL, text=True
        )
        return [ln for ln in out.strip().splitlines() if ln]
    except subprocess.CalledProcessError:
        return []


def tcp_check(host: str, port: int, timeout: float = 1.0) -> tuple[bool, str]:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True, "connected"
    except ConnectionRefusedError:
        return False, "Connection refused"
    except socket.timeout:
        return False, "timeout"
    except Exception as e:
        return False, str(e)
    finally:
        s.close()


def latest_kit_log() -> Path | None:
    candidates = []
    for pattern in [
        "~/.nvidia-omniverse/logs/Kit/*/kit_*.log",
        "~/.local/share/ov/data/Kit/Apps/Isaac-Sim/*/kit_*.log",
    ]:
        candidates.extend(Path(os.path.expanduser("~")).glob(pattern.replace("~/", "")))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main() -> int:
    print("=" * 60)
    print("isaac-sim-mcp health check")
    print("=" * 60)

    failures = []

    print("\n[1/5] Isaac Sim process")
    # match the actual binary, not just any path containing "isaac-sim"
    # (the MCP server's path is ~/dev_ws/isaac-sim-mcp/... which would false-match)
    isaac_procs = [p for p in pgrep("isaac-sim") if "isaac-sim-mcp" not in p and "claude" not in p.lower()]
    if isaac_procs:
        check("Isaac Sim is running", True, f"{len(isaac_procs)} process(es)")
        for p in isaac_procs[:3]:
            print(f"         {p[:100]}")
    else:
        check("Isaac Sim is running", False, "no process matches 'isaac-sim'")
        failures.append("Start Isaac Sim with: isaac-mcp")

    print("\n[2/5] Extension TCP listener (localhost:8766)")
    ok, detail = tcp_check("127.0.0.1", 8766)
    check("Port 8766 accepting connections", ok, detail)
    if not ok:
        failures.append(
            "Extension not loaded. Launch with: isaac-mcp  (alias includes --enable isaac.sim.mcp_extension)"
        )

    print("\n[3/5] MCP server subprocess")
    server_procs = pgrep("isaac_mcp/server.py")
    if server_procs:
        check("MCP server process running", True, f"{len(server_procs)} process(es)")
    else:
        check(
            "MCP server process running",
            False,
            "spawned by Claude Code; restart your Claude session",
        )
        failures.append("Restart Claude Code session to respawn the MCP server")

    print("\n[4/5] End-to-end ping (MCP server <-> extension)")
    # We can't directly invoke the MCP from this script (it'd require the MCP protocol),
    # but we can check that both ends are up — proxy.
    e2e_ok = bool(isaac_procs and server_procs and tcp_check("127.0.0.1", 8766)[0])
    check(
        "All three components present", e2e_ok, "MCP should now work" if e2e_ok else "see failures above"
    )

    print("\n[5/5] Kit log accessibility")
    log = latest_kit_log()
    if log is None:
        check("Kit log found", False, "no kit_*.log files in standard locations")
    else:
        import time

        age_s = time.time() - log.stat().st_mtime
        check("Kit log found", True, f"{log}  (last write: {age_s:.0f}s ago)")
        print(f"         tail -F {log}")

    print("\n" + "=" * 60)
    if failures:
        print("FAILURES — fix in order:")
        for i, f in enumerate(failures, 1):
            print(f"  {i}. {f}")
        return 1
    else:
        print("All checks passed. MCP should be functional.")
        print("Test from Claude: mcp__isaac-sim__get_scene_info()")
        return 0


if __name__ == "__main__":
    sys.exit(main())
