---
name: isaac-sim-mcp
description: >
  Use this skill whenever the user works with the running Isaac Sim instance through the
  isaac-sim-mcp server — that is, whenever Claude itself needs to read or modify USD
  stage, articulation state, OmniGraph, physics, or sensors in a live Isaac Sim Kit
  process (port 8766) rather than just writing Python to a file. Triggers on any of:
  the user says "MCP", "execute_script", "controll Isaac Sim from Claude", "live MCP
  control", "let Claude drive Isaac Sim", or "fix this in the running scene"; the user
  pastes a Python snippet and asks to run it in Isaac Sim; the user asks to add a
  prim/robot/light/camera while Isaac Sim is open; the user shares an Isaac Sim
  screenshot and asks to modify what's visible; the user reports a runtime error from
  Isaac Sim's Console / kit_*.log and wants it fixed without restarting; the user says
  "Cube_01 scale is 0, fix it" or any equivalent live-edit request. Also trigger when
  the user is in a cobot3 / Doosan m0609 / warehouse-sorting workflow and Isaac Sim is
  running — virtually all such tasks benefit from MCP over writing standalone scripts.
  This skill is the *playbook* for the 9 MCP tools (`get_scene_info`, `execute_script`,
  `create_robot`, `create_physics_scene`, `transform`, `omni_kit_command`,
  `search_3d_usd_by_text`, `generate_3d_from_text_or_image`, and the implicit
  connection layer); it tells Claude which tool to pick first, what order to call them
  in, how to verify changes via `get_scene_info` + kit log, and how to recover from
  connection failures. Complements `isaac-sim-bridge` (which is the Isaac Sim *domain*
  skill — USD/PhysX/OG concepts) — this skill is the *interface* skill. Do not use this
  skill when Isaac Sim is not running (no MCP target), or when the task is purely
  authoring standalone `.py` files for `python.sh` (no live Kit) — those go to plain
  Bash/Edit + `isaac-sim-bridge`.
---

# isaac-sim-mcp — MCP playbook for live Isaac Sim control

You have **9 MCP tools** that let you directly read and modify a running Isaac Sim
instance. This skill is the decision router + mental model for using them well.

Pairs with [[isaac-sim-bridge]] — that skill provides USD/PhysX/OG **domain knowledge**;
this skill provides **MCP usage knowledge**. Read both for non-trivial Isaac Sim work.

## Core mental model — 6 things to internalize

### 1. The MCP server is a relay, not a runtime

The architecture has 3 hops, and knowing where state lives prevents 90% of confusion:

```
You (Claude)
   │  MCP tool call (JSON-RPC via stdio)
   ▼
isaac-sim-mcp server (Python subprocess, started by Claude Code)
   │  TCP socket to localhost:8766
   ▼
isaac.sim.mcp_extension (loaded inside Isaac Sim Kit process)
   │  same-process Python call
   ▼
omni.usd / omni.kit / pxr — actual Kit runtime
```

Implications:
- **All Python you submit runs inside Kit's interpreter** — `omni.usd.get_context()` works, `from pxr import Usd` works, `omni.isaac.core.World()` works
- **You do NOT need `python.sh`** — that's for standalone scripts. MCP scripts run *in-process*
- **State persists between calls** — a variable you create in `execute_script` survives only within that one call (it's a fresh exec scope), but the **USD stage state persists** across all calls
- **If Isaac Sim is not running**, every call returns `Connection refused`. Always check first

### 2. `get_scene_info` is your `pwd` — call it first

Before doing anything that depends on stage state, call `get_scene_info`. It does two
jobs:
- Confirms the MCP↔Kit connection is alive (most common failure mode)
- Tells you what's currently in the stage (prims, simulation state)

If `get_scene_info` returns `Connection refused` or an error, **stop and report to the
user** — Isaac Sim isn't running, or extension didn't load. Don't keep calling tools
in the dark.

```python
# Always your first call in a fresh task
mcp__isaac-sim__get_scene_info()
```

### 3. Pick the right tool — `execute_script` is powerful but rarely the right first choice

The 9 tools form a hierarchy of specificity. **Prefer the most specific tool that
fits**, because:
- Specific tools have validated argument schemas (catches typos)
- They handle setup that `execute_script` users often forget (PhysicsScene, drives, defaults)
- They return cleaner results

Decision table:

| Task | First-choice tool |
|---|---|
| "What's in the scene?" | `get_scene_info` |
| Add a built-in robot (Franka, Jetbot, Carter, G1, Go1) | `create_robot` |
| Set up physics + primitives + floor | `create_physics_scene` |
| Move/scale an existing prim | `transform` |
| Run a built-in Kit command (e.g., CreatePrim) | `omni_kit_command` |
| Search NVIDIA asset catalog for a USD | `search_3d_usd_by_text` |
| Generate a fresh 3D asset from text/image | `generate_3d_from_text_or_image` |
| **Anything else** (custom Doosan/m0609, OmniGraph, attribute tweaks, debugging) | `execute_script` |

`execute_script` is the fallback for arbitrary Python. It's the right tool for
**~70% of cobot3 work** (Doosan-specific, OG bridge, physics tuning) because the
specific tools don't cover Doosan/warehouse-sorting scenarios.

### 4. Verify after every write — Kit doesn't fail loudly

PhysX, OG, and USD often **fix silently** instead of erroring (PhysX auto-converts
trimesh→convexHull for dynamic bodies; OG ignores invalid wires; USD accepts attribute
sets on wrong types). To catch this:

1. After `execute_script` that mutates state, call `get_scene_info` again
2. Or `execute_script` a verification snippet (`stage.GetPrimAtPath(...).IsValid()`)
3. For physics issues, tail `kit_*.log` — the server can read it (see §debugging.md)

The pattern is **write → verify → next step**, never write → write → write blind.

### 5. Don't fight the event loop — one call at a time

Kit's main thread runs the event loop. Each MCP call enqueues work; the next call
won't be processed until the previous one returns. Don't:
- Send 10 rapid-fire `execute_script` calls expecting them to interleave
- Put `time.sleep(N)` inside `execute_script` — it blocks the Kit thread, freezes
  GUI, can corrupt OG state
- Run a "long simulation loop" inside `execute_script` (e.g., `for _ in range(1000):
  world.step()`) — it locks Kit for that duration

Do:
- One MCP call per logical step
- For multi-step simulation, set up callbacks (`add_physics_callback`) and let Kit's
  loop run; verify state in a *separate* `execute_script` call
- For timed sequences, use `step_size` accumulation in a callback, not sleeps

### 6. Standalone `python.sh` and MCP are different worlds

The user has both:
- `python.sh` for headless scripts (RL training, CI, batch SDG) — runs its own Kit
  instance, no GUI
- MCP for the **live GUI Kit instance** — interactive, visible in viewport

Don't try to mix them. If the user wants to "test this in headless then deploy", that's
two separate workflows — one with `Bash` running `python.sh`, one with MCP. This skill
covers the MCP side only.

## Decision router

Pick the row matching the task and read the listed reference(s).

| Task | Reference |
|---|---|
| "Which tool should I use for X?" — full tool signatures and gotchas | `references/tool-reference.md` |
| Common workflow sequences (load scene, add robot + sensors, run mission, sanity-check) | `references/patterns.md` |
| Connection refused, kit log reading, recovering from stale state | `references/debugging.md` |
| cobot3 specifics — Doosan m0609 + ROS 2 bridge + warehouse sorting via MCP | `references/cobot3-recipes.md` |
| When to use MCP vs `Bash`/`Edit`/`python.sh`, working with sibling skills | `references/interop.md` |

For domain knowledge (USD prim/property, PhysX articulation, OG nodes, sim2real), defer
to [[isaac-sim-bridge]].

## Universal workflow — apply to every non-trivial MCP task

1. **Confirm connection.** `get_scene_info`. If error → diagnose with §debugging before
   doing anything else. Tell the user, don't silently retry.
2. **Plan in your head.** What prims will exist after this is done? What attributes
   will be set? Write the target state explicitly. This is the equivalent of a unit
   test mental model.
3. **Pick most-specific tool.** Walk the §3 table from top to bottom.
4. **For `execute_script` only:** print the code in your reply *before* sending it,
   so the user can sanity-check. The server.py docstring requests this explicitly.
5. **Send.** One call.
6. **Verify.** `get_scene_info` or a targeted `execute_script` read. Confirm target
   state was achieved.
7. **If it failed**, don't retry blindly. Read §debugging — usually the kit log has
   the real reason.

## When this skill should defer

- **USD/PhysX/OG concept questions** (what's a prim? convex hull vs decomp? articulation
  root rules?) → [[isaac-sim-bridge]]. This skill assumes that domain knowledge.
- **ROS 2 middleware** (rclpy, QoS, launch files) → `ros2-architect` skill.
- **Doosan motion API** (DSR_ROBOT2, dsr_controller2, DRL) → `doosan-robotics` skill.
- **Pure file-system or shell work** (creating dirs, editing config) → use `Bash`/`Edit`
  directly, not MCP.
- **Standalone `python.sh` scripts** (RL training, CI, headless SDG) — write the file
  with `Edit`, run with `Bash`. MCP is for the live Kit instance only.

## Skill output expectations

When this skill is active, MCP usage should:

- **Always** call `get_scene_info` before mutating state in an unfamiliar scene
- **Always** print `execute_script` code in the chat reply *before* sending the tool
  call, so the user sees what's about to run
- **Always** verify after mutation (re-query `get_scene_info` or targeted read)
- **Prefer** `create_robot` / `create_physics_scene` / `transform` over hand-written
  `execute_script` when a built-in tool fits
- **Never** use `time.sleep` inside `execute_script` (blocks Kit thread). For timed
  behavior use `add_physics_callback` with `step_size` accumulation
- **Never** chain 5+ rapid `execute_script` calls without verification between them —
  bugs compound silently
- **Never** call MCP tools when `get_scene_info` reports `Connection refused` — first
  ask the user to start Isaac Sim with `isaac-mcp` (the alias) and wait for "Listening
  on localhost:8766"

## Local context — this user's setup

| Item | Value |
|---|---|
| Isaac Sim version | 5.1.0-rc.19 (source build at `~/dev_ws/isaac_sim/isaacsim/`) |
| Launch alias | `isaac-mcp` (in `~/.bashrc`) — passes `--ext-folder` and `--enable isaac.sim.mcp_extension` |
| MCP server path | `~/dev_ws/isaac-sim-mcp/isaac_mcp/server.py` |
| MCP server venv | `~/dev_ws/isaac-sim-mcp/.venv/bin/python` |
| Port | `localhost:8766` |
| Project | cobot3 — Doosan m0609 + RG2 gripper + YOLO + warehouse sorting |
| Sibling skills | `isaac-sim-bridge` (domain), `web-slide` (slides), `code-simplifier` etc. |

## Related references in this skill

```
isaac-sim-mcp/
├── SKILL.md                          ← you are here
├── references/
│   ├── tool-reference.md             ← 9 tools: signatures, args, gotchas, examples
│   ├── patterns.md                   ← Common task sequences (sanity-check, add robot,
│   │                                   run mission, save USD, reset stage)
│   ├── debugging.md                  ← Connection refused, kit log tailing, stale
│   │                                   state recovery, common error signatures
│   ├── cobot3-recipes.md             ← Doosan m0609 + RG2 + warehouse + YOLO + ROS 2
│   │                                   bridge OG via MCP
│   └── interop.md                    ← MCP vs Bash vs Edit vs python.sh; how this
│                                       skill works with isaac-sim-bridge, ros2-architect,
│                                       doosan-robotics
└── scripts/
    └── check_mcp_health.py           ← Standalone diagnostic (run via Bash):
                                        does MCP server connect to Isaac Sim?
```

Each reference is self-contained. Read the matching one before sending non-trivial
tool calls.
