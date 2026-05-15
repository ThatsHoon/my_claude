# debugging.md — When MCP tool calls fail

The failure modes for MCP calls cluster into a small set. This reference is a flat
diagnostic table → root cause → fix. Read the row matching your symptom first.

## Contents
1. Recovering connection
2. Reading Kit's log
3. Common error signatures
4. Stuck/frozen simulation
5. Stale state (yesterday's prims still there)
6. Wrong values silently accepted (USD/PhysX)
7. Multiple Isaac Sim instances
8. Permission denied / sandboxed errors

---

## 1. Recovering connection

**Symptom**: Every MCP tool returns `Connection refused: [Errno 111]` or similar.

**Diagnose in this order** (run via `Bash`, not MCP — MCP is the thing that's broken):

```bash
# 1. Is Isaac Sim running at all?
pgrep -af isaac-sim
# Expected: a process matching isaac-sim.sh + python.sh

# 2. Is the extension listening on 8766?
ss -tlnp 2>/dev/null | grep 8766
# Expected: LISTEN ... 127.0.0.1:8766

# 3. Did the MCP server (Python subprocess) start?
pgrep -af "isaac_mcp/server.py"
# Expected: one process running .venv/bin/python server.py
```

**Causes by what's missing**:

| Missing | Cause | Fix |
|---|---|---|
| Isaac Sim process | Not launched | Tell user: open terminal, run `isaac-mcp`, wait 1-2 min for boot |
| Isaac Sim running but no 8766 listener | Extension not loaded | `isaac-mcp` was launched without `--enable isaac.sim.mcp_extension`, or the extension itself failed to load. Tell user to check Isaac Sim's `Window → Console` for red errors mentioning `isaac.sim.mcp` |
| Both running but MCP server dead | Server crashed | Restart Claude Code session (the server is spawned by Claude on session start) |
| Everything running but still refused | Kit's main thread is blocked | Wait 10s and retry. If still failing, see §4 |

**The `isaac-mcp` alias** (set in `~/.bashrc`):
```bash
alias isaac-mcp='~/dev_ws/isaac_sim/isaacsim/_build/linux-x86_64/release/isaac-sim.sh \
  --ext-folder /home/rokey/dev_ws/isaac-sim-mcp/ \
  --enable isaac.sim.mcp_extension'
```

If the alias is missing or broken, the manual command above launches with extension.

---

## 2. Reading Kit's log

Kit writes a verbose log to `~/.nvidia-omniverse/logs/` and (for source builds) also
to `~/.local/share/ov/data/Kit/Apps/Isaac-Sim/<version>/kit_*.log`. The MCP server can
read these too.

**Tail the latest log via Bash**:
```bash
# Find the newest kit log
KIT_LOG=$(ls -t ~/.nvidia-omniverse/logs/Kit/*/kit_*.log 2>/dev/null | head -1)
[ -z "$KIT_LOG" ] && KIT_LOG=$(ls -t ~/.local/share/ov/data/Kit/Apps/Isaac-Sim/*/kit_*.log 2>/dev/null | head -1)
echo "Latest log: $KIT_LOG"

# Tail last 50 lines for errors
tail -50 "$KIT_LOG" | grep -iE "error|warning|exception|traceback" | tail -30
```

**Tail live during a test**:
```bash
tail -F "$KIT_LOG"
```

**What to look for**:
- `[Error] [omni.physx.plugin]` → PhysX setup issue (collider, articulation)
- `[Error] [asyncio] Task exception was never retrieved` → an `async def` raised but
  wasn't awaited. Often from BaseSample `setup_post_load` failures
- `[Error] [omni.usd] Stage opening or closing already in progress` → race condition
  on LOAD button (§5)
- `[Error] [omni.graph]` → OmniGraph node validation failure (red node)
- `[carb.graphics-vulkan]` → GPU/driver issue (rare on this user's RTX 5080)

After the first MCP `execute_script` call that crashes, **always** read the kit log
before retrying. The error printed to the MCP response is often a generic wrapper; the
real cause is in kit.log.

---

## 3. Common error signatures

### `NameError: name 'np' is not defined`
The `execute_script` snippet uses `np.` but didn't import numpy. Add
`import numpy as np` at the top.

### `AttributeError: 'NoneType' object has no attribute 'get_articulation_controller'`
`world.scene.get_object("name")` returned `None` because the prim doesn't exist OR the
robot wasn't added to the scene OR it wasn't reset yet. Fix:
```python
robot = world.scene.get_object("m0609")
if robot is None:
    print("ERROR: robot not in scene. Did you forget world.scene.add(Robot(...))?")
else:
    ctrl = robot.get_articulation_controller()
```

### `Exception: There is no stage currently opened`
Stage was closed (File → New, or unloaded). Open one first:
```python
import omni.usd
omni.usd.get_context().new_stage()
```
Or wait for the user to load a scene manually.

### `PhysX error: Supplied PxGeometry is not valid. Shape creation method returns NULL`
Mesh is degenerate (scale=0, empty, or perfectly flat for convex hull). See
[[isaac-sim-bridge]] `references/usd-from-urdf.md` §collision-fixes, then fix via
`execute_script`:
```python
from pxr import UsdGeom, Gf
prim = stage.GetPrimAtPath("/World/Cube_01")
# Diagnose: read scale and size
# Fix: set non-degenerate values
xf = UsdGeom.Xformable(prim)
for op in xf.GetOrderedXformOps():
    if op.GetOpName() == "xformOp:scale":
        op.Set(Gf.Vec3f(1, 1, 1))
```

### `setCollider: /...belt... is a part of a rigid body. Resetting approximation shape from none (trimesh) to convexHull`
**Warning, not error** — PhysX auto-fixed. Underlying issue: trimesh collider on a
dynamic body (PhysX forbids). Either remove RigidBodyAPI (conveyor should be static)
or accept the convex hull approximation. See `cobot3-recipes.md` §conveyor.

### `Task exception was never retrieved: ... NameError ...`
An `async def` in a BaseSample handler raised. The PDF's broken `hello_world.py`
exhibits this. See `cobot3-recipes.md` §"Fixing broken samples" or just rewrite the
handler.

---

## 4. Stuck/frozen simulation

**Symptom**: Viewport frozen, `get_scene_info` times out.

**Causes (most likely first)**:
1. **`time.sleep()` inside a physics callback or `execute_script`** — blocks Kit
   thread. Identify and remove.
2. **Tight loop in `execute_script`** — e.g., `for _ in range(1000): world.step()`.
   Same issue. Use `add_physics_callback` instead.
3. **Modal dialog stuck open in GUI** — user must dismiss it. Ask them to look at the
   GUI window.
4. **GPU hang** — rare, requires Isaac Sim restart.

**Recovery from MCP side**:
```python
# execute_script (may itself time out — try anyway)
import omni.timeline
omni.timeline.get_timeline_interface().stop()
```

If that fails, ask user to click `Stop` in viewport. If GUI also unresponsive →
restart Isaac Sim.

---

## 5. Stale state — yesterday's prims still there

**Symptom**: New session, you expect an empty stage, but `get_scene_info` shows prims
from a previous session.

**Cause**: Isaac Sim doesn't auto-clean stage between sessions. If a previous test
created `/World/Cube_01`, it's still there.

**Fix (always at the start of a fresh task)**:
```python
# execute_script
import omni.usd
omni.usd.get_context().new_stage()
```

Verify with `get_scene_info` — should be down to `/World` and `/Render`.

---

## 6. Wrong values silently accepted

USD and PhysX often accept invalid attribute values without raising. Examples:

- Setting `xformOp:scale` to `Gf.Vec3f(0, 1, 1)` — accepted, but the prim becomes
  degenerate. PhysX then fails downstream.
- Calling `prim.GetAttribute("nonExistent").Set(5)` — silently does nothing. No
  exception.
- Setting a typed attribute to wrong type — usually silent on USD side, blows up
  later.

**Defense**: After any `execute_script` that sets attributes, **read them back**:
```python
val = prim.GetAttribute("xformOp:scale").Get()
print(f"scale after set: {val}")
assert val[0] != 0, "scale.x is zero — refused or set wrong"
```

For typed APIs, use the typed wrappers when available:
```python
# Don't: prim.GetAttribute("...").Set(...)
# Do:    UsdGeom.Cube(prim).GetSizeAttr().Set(...)
```

---

## 7. Multiple Isaac Sim instances

If two Isaac Sim instances are running, only one has the extension listening on 8766
(the one started with `isaac-mcp`). MCP talks to that one.

**Confirm via Bash**:
```bash
pgrep -af isaac-sim
ss -tlnp | grep 8766
```

**If the user wants MCP to target a different instance**: the alternate instance must
have been launched with `--enable isaac.sim.mcp_extension`, and the port is allocated
sequentially (8766, 8767, ...). The MCP server connects to 8766 by default — to point
elsewhere, modify the server config (see `~/dev_ws/isaac-sim-mcp/isaac_mcp/server.py`
for the port).

---

## 8. Permission denied / sandboxed errors

Rare. If `execute_script` fails with file-system permission errors (e.g., writing to
`/etc/`), Kit runs with the user's permissions — if the user can't write there, Kit
can't either.

Common cases:
- Writing to `/etc/`, `/var/`, `/usr/` — needs sudo, which Kit doesn't have. Use
  `~/dev_ws/...` paths.
- Writing to a mounted read-only filesystem (e.g., NVIDIA's S3-mounted asset library)
  — use `omniverse://localhost/` (own Nucleus) or local paths.

---

## When in doubt — the universal diagnostic chain

1. `get_scene_info` via MCP — does it return? If no, §1.
2. If yes but result is unexpected: `execute_script` to dump prim list:
   ```python
   import omni.usd
   stage = omni.usd.get_context().get_stage()
   for p in stage.Traverse():
       print(p.GetPath(), p.GetTypeName())
   ```
3. Read latest kit.log (via Bash) for errors.
4. If error is PhysX-related, defer to [[isaac-sim-bridge]] `physx-tuning.md` and
   `usd-from-urdf.md`.
5. If error is OG-related, [[isaac-sim-bridge]] `omnigraph-ros-bridge.md`.
6. If nothing matches → ask the user to send screenshot of `Window → Console` red
   lines, plus the last 30 lines of `tail -F` on the kit log.
