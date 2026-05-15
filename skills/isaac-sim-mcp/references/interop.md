# interop.md — When to use MCP vs other tools

The user has many ways to make changes happen — MCP, Bash, Edit, Write, `python.sh`,
existing skills. Pick the right one. Using MCP where it doesn't fit is a common
beginner mistake.

## Contents
1. MCP vs Bash
2. MCP vs Edit / Write
3. MCP vs standalone `python.sh`
4. MCP vs the GUI (Script Editor / Examples Browser)
5. Working with `isaac-sim-bridge` skill (domain knowledge)
6. Working with `ros2-architect` / `doosan-robotics` skills
7. Decision flowchart

---

## 1. MCP vs Bash

| Task | Tool |
|---|---|
| Anything inside Isaac Sim (USD, OG, articulation) | **MCP** |
| File system (mkdir, cp, ls) | Bash |
| Package install (apt, pip, ros2 packages) | Bash |
| ROS 2 commands (`ros2 topic`, `ros2 run`, `colcon build`) | Bash |
| Start/stop Isaac Sim itself | Bash (or user manually) |
| Check ports, processes, system state | Bash |
| Tail kit.log | Bash |
| Run a `.py` script outside Kit | Bash (`python.sh script.py`) |

**Rule**: If the action affects state **inside the running Kit process**, use MCP. If
it affects the OS or files outside Kit, use Bash.

**Example — kit.log reading**: Bash, because the log is a file on disk and Bash is
simpler than `execute_script` doing file I/O.

**Example — checking topic list**: Bash with `ros2 topic list`. Don't try to call ROS 2
introspection from MCP — Kit's `rclpy` is its own context.

---

## 2. MCP vs Edit / Write

Both write files. The difference is **where they take effect**.

| Edit/Write | MCP `execute_script` |
|---|---|
| Modifies the `.py` file on disk | Mutates the live Kit stage/runtime |
| Effect: next time the module is imported (or Isaac Sim restarts) | Effect: immediate |
| Persists across Isaac Sim restarts | Only persists if you save the stage |
| Targets `~/dev_ws/...py` | Targets `/World/...` (USD paths) |

**When changes need to survive restart** (extension code, scene templates, mission
scripts): `Edit`/`Write` to disk + restart Isaac Sim.

**When changes are throwaway experiments** (try this physics value, see if this prim
loads correctly): MCP `execute_script`.

**Common mistake**: Editing a `.py` file with `Edit`, then expecting the running Kit
to pick up the change. It won't — Python modules are cached. Either restart Kit, or
force `importlib.reload` via `execute_script`.

---

## 3. MCP vs standalone `python.sh`

```
isaac-sim.sh                       <—— GUI Kit instance, port 8766, MCP target
python.sh script.py                <—— headless Kit instance, no GUI, no MCP
```

These spawn **separate Kit processes**. State doesn't share.

| Use case | Tool |
|---|---|
| Interactive development, "see what happens" | MCP (GUI Kit) |
| Headless data generation (SDG) | Bash + `python.sh` |
| RL training (Isaac Lab) | Bash + `python.sh` |
| CI test — does this scene load? | Bash + `python.sh` |
| Quick interactive bug fix | MCP |
| Producing repeatable artifacts | Bash + `python.sh` (script committed to git) |

**Hybrid pattern**: Develop interactively in MCP. When the workflow is stable, dump it
to a `.py` script (using `Write`) and verify with `python.sh`. Then commit the script.

```python
# A reproducible scene-build script
# Run with: python.sh build_cobot3_scene.py

from isaacsim import SimulationApp
app = SimulationApp({"headless": True})

# ... same code you tested via execute_script
from isaacsim.core.api import World
from isaacsim.core.utils.stage import add_reference_to_stage
# ...

# Save the result
import omni.usd
omni.usd.get_context().save_as_stage("/home/rokey/dev_ws/cobot3/scenes/cobot3_base.usda")

app.close()
```

---

## 4. MCP vs the GUI (Script Editor / Examples Browser)

| GUI | MCP |
|---|---|
| User clicks/types directly | Claude drives via tool calls |
| Good for: human-visual debugging | Good for: automation, repeatable, AI-driven |
| `Window → Script Editor` + Python | `execute_script` |
| `Window → Examples → Robotics Examples` | n/a (no MCP equivalent) |

Both run in the same Kit Python interpreter, so anything that works in Script Editor
works in `execute_script`. The difference is **who's at the keyboard**.

**Prefer MCP** when:
- Claude is generating the code
- You want a record of what was done (MCP calls are logged)
- The user wants iteration without context switching

**Prefer GUI** when:
- The user wants to explore visually
- A modal dialog needs to be handled (file picker, etc.)
- Inspecting transient state (Articulation Inspector slider)

---

## 5. Working with `isaac-sim-bridge` skill

`isaac-sim-bridge` is the **domain skill** — it knows USD, PhysX, OG, Isaac Lab, etc.
This skill (`isaac-sim-mcp`) is the **interface skill** — it knows the MCP tool API.

Pair them. Decision rule:

```
"What should the code do?"      → consult isaac-sim-bridge
"How do I send it to Isaac Sim?" → this skill
```

Example — "fix the broken Cube_01 with scale=0":

1. **isaac-sim-bridge** tells you: a degenerate scale makes PhysX fail; fix by setting
   `xformOp:scale` to a non-zero `Gf.Vec3f`; verify with bbox check.
2. **isaac-sim-mcp** (this skill) tells you: send the fix via `execute_script` with
   `print(scale)` for verification; use `transform` tool if you only need position;
   re-verify with `get_scene_info`.

The bridge skill has these references that often pair with MCP work:
- `usd-from-urdf.md` — URDF import settings, articulation root rules
- `physx-tuning.md` — Drive gains, contact/friction, solver settings
- `omnigraph-ros-bridge.md` — OG patterns for sensor publishing
- `replicator-sdg.md` — Synthetic data
- `isaaclab-rl.md` — RL training (uses `python.sh`, not MCP)
- `warehouse-sorting-pipeline.md`, `yolo-perception.md` — cobot3 architecture

---

## 6. Working with `ros2-architect` / `doosan-robotics`

Two other domain skills relevant to cobot3:

**`ros2-architect`** — ROS 2 middleware (rclpy, QoS, launch, executors, lifecycle).
- Used when: writing host-side ROS 2 nodes/launch files (separate from Kit)
- This skill handles: the OG side (`isaacsim.ros2.bridge.*` nodes inside Kit)
- Boundary: any topic crossing Kit ↔ host involves both. The OG node is here; the
  subscriber/publisher on host is in `ros2-architect`.

**`doosan-robotics`** — Doosan SDK (DSR_ROBOT2, dsr_controller2, DRL, 161 service/
topic specs).
- Used when: driving real m0609 from ROS 2, mode transitions, DRL scripts
- This skill handles: simulating m0609 inside Kit, generating ROS 2 joint commands
- Boundary: the simulated m0609 (Kit) and real m0609 (Doosan) should accept the same
  joint commands. `doosan-robotics` defines the interface; MCP delivers commands in
  the sim side via OG `ROS2SubscribeJointState` → `IsaacArticulationController`.

Don't try to handle ROS 2 host-side debugging or Doosan SDK quirks from MCP — wrong
tool. Defer to those skills.

---

## 7. Decision flowchart

```
User asks for a change. Where does the change need to take effect?

├── In the live Kit process (USD stage, OG, articulation)
│       → MCP. Pick tool per tool-reference.md §3.
│
├── On disk (Python source, USD file, JSON config)
│       → Edit or Write. Restart Kit if module reload is needed.
│
├── In the OS (install, processes, ROS 2 commands)
│       → Bash.
│
├── In a headless Kit run (CI, training, data gen)
│       → Write the script + Bash `python.sh`.
│
└── In another Kit instance (separate GUI)
        → MCP can't reach it (only one extension on 8766). Either:
          • Restart with extension on different port (advanced)
          • Use Bash to drive that instance differently
```

---

## Anti-pattern: doing everything in `execute_script`

A common failure mode is reaching for `execute_script` for every task. Symptoms:
- `execute_script` shelling out to subprocess — that should be Bash
- `execute_script` writing to files outside Kit's domain — should be Edit/Write
- `execute_script` doing string manipulation that didn't need Kit at all

If your `execute_script` doesn't actually touch `omni.*`, `pxr`, `isaacsim.*`, or Kit
state, it shouldn't be `execute_script`. Use Bash or Python directly.

---

## When in doubt — ask the user

If you're not sure whether a change should persist or be throwaway, ask:
> "Should this be a one-off experiment in the current session (I'll use MCP) or a
> permanent change to the project files (I'll edit on disk)?"

Better to clarify than to commit to the wrong tool and have to redo work.
