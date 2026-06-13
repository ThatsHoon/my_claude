# tool-reference.md — All 9 MCP tools

Exact signatures, semantics, and gotchas. Read the row for the tool you're about to
call, especially if it's been a while since you last used it.

## Contents
1. `get_scene_info`
2. `execute_script`
3. `create_robot`
4. `create_physics_scene`
5. `transform`
6. `omni_kit_command`
7. `search_3d_usd_by_text`
8. `generate_3d_from_text_or_image`
9. The implicit connection layer (no direct tool — but matters)

---

## 1. `get_scene_info`

```
mcp__isaac-sim__get_scene_info()  →  str (JSON)
```

**Purpose**: Health check + current stage summary. Always your first call.

**Returns**: JSON string with at least a status field. On success, includes scene state
that Isaac Sim's extension chose to expose (varies by version; usually includes prim
count, current stage URL, simulation state).

**Use when**:
- Starting a new task — confirm connection
- After any external GUI action (user clicked Reset, opened a new stage)
- Before mutating state in an unfamiliar scene
- After mutation, to verify result

**Failure mode**:
- `Connection refused` → Isaac Sim not running OR extension not loaded. See `debugging.md`.
- Timeout → Kit thread is busy (long simulation, big stage load). Wait and retry once,
  then escalate to user.

---

## 2. `execute_script` ⭐

```
mcp__isaac-sim__execute_script(code: str)  →  str
```

**Purpose**: Run arbitrary Python inside Kit's interpreter. The escape hatch for
anything the specific tools don't cover.

**Args**:
- `code`: A complete Python snippet. Imports allowed. Multi-line OK.

**Available imports inside the executed code**:
- `omni.usd`, `omni.kit.app`, `omni.kit.commands`, `omni.timeline`
- `pxr` (`Usd`, `UsdGeom`, `UsdPhysics`, `Sdf`, `Gf`, `PhysxSchema`, ...)
- `isaacsim.core.api.*` (`World`, `SimulationContext`, `Articulation`, `RigidObject`)
- `isaacsim.core.utils.*` (`prims`, `stage`, `nucleus`, `types`)
- `isaacsim.core.api.objects` (`DynamicCuboid`, `FixedCuboid`, `VisualCuboid`, ...)
- `omni.physx.scripts.utils` (`setRigidBody`, `setCollider`, ...)
- `omni.graph.core as og` (OmniGraph)
- `numpy as np`, `carb`

(All of these are available because the code runs *inside Kit* where these modules are
already importable.)

**Gotchas**:
- **No `print` to your console** — `print()` goes to Kit's stdout/log, not back to MCP.
  To return data, build a string and put it in a variable, then return via the last
  expression OR use the server's auto-return semantics.
- **Returns are limited** — typically a string log of execution. Don't expect to return
  large objects (numpy arrays, etc.). For inspection, save to a file or use
  `get_scene_info`.
- **No `time.sleep`** — blocks Kit's main thread, freezes GUI. Use
  `add_physics_callback` for timed behavior.
- **No long loops** — `for _ in range(10000): world.step()` will lock Kit for the whole
  duration. Use callbacks.
- **State is fresh per call** — variables don't persist across calls. The *USD stage*
  does. So `stage = omni.usd.get_context().get_stage()` works fine; rebuild your
  references each call.
- **Async functions need `asyncio.ensure_future`** — Isaac Sim has many `async def`
  APIs. Wrap them: `import asyncio; asyncio.ensure_future(world.reset_async())`.

**Convention**: Print the code in your chat reply *before* calling the tool. This
matches the server's docstring guidance and gives the user a chance to spot bugs.

**Example — load a robot, print joint count**:
```python
from isaacsim.core.api import World
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot

world = World.instance()
if world is None:
    world = World()

add_reference_to_stage(
    usd_path="/path/to/jetbot.usd",
    prim_path="/World/Jetbot",
)
robot = world.scene.add(Robot(prim_path="/World/Jetbot", name="jetbot"))
print(f"num_dof: {robot.num_dof}")
```

---

## 3. `create_robot`

```
mcp__isaac-sim__create_robot(robot_type: str = "g1", position: list = [0,0,0])  →  str
```

**Purpose**: One-shot spawn of a built-in NVIDIA robot.

**Args**:
- `robot_type`: one of `franka`, `jetbot`, `carter`, `g1` (default), `go1`
- `position`: `[x, y, z]` in stage units (meters by default)

**Use when**: You need one of the 5 supported robots and don't need custom
configuration.

**Don't use for**: Doosan m0609, UR series, Kinova, Sawyer, or any robot not in the
list. Those need `execute_script` with `add_reference_to_stage` + the appropriate USD
path.

**Prerequisite**: Server docstring says "call `create_physics_scene()` first". In
practice, if a PhysicsScene already exists in the stage, this works without
`create_physics_scene` — but if you're starting from a brand-new empty stage, run
`create_physics_scene` (or a manual `World()` init via `execute_script`) first.

**Doosan m0609 alternative** (cobot3 case — `create_robot` doesn't support it):
```python
# execute_script equivalent
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot

add_reference_to_stage(
    usd_path="/path/to/m0609.usd",  # local or omniverse:// URL
    prim_path="/World/m0609",
)
world.scene.add(Robot(prim_path="/World/m0609", name="m0609"))
```

---

## 4. `create_physics_scene`

```
mcp__isaac-sim__create_physics_scene(
    objects: list = [],
    floor: bool = True,
    gravity: list = [0, -0.981, 0],
    scene_name: str = "physics_scene"
)  →  dict
```

**Purpose**: Initialize a PhysicsScene + optional floor + primitive objects.

**Args**:
- `objects`: list of dicts. Each: `{"path": "/World/Cube", "type": "Cube", "size": 20,
  "position": [0, 100, 0]}`. Supported types: `Cube`, `Sphere`, `Cone`. Other shapes
  via `execute_script`.
- `floor`: adds a ground plane. Almost always `True`.
- `gravity`: defaults to `[0, -0.981, 0]` — note **Y-down gravity in cm units**, not
  the typical Z-up m/s². Adjust to `[0, 0, -9.81]` for Z-up SI units (the default Isaac
  Sim convention). The default in the tool is a quirk worth knowing.
- `scene_name`: cosmetic.

**Use when**: Brand-new stage, want a quick PhysX-ready playground with floor +
primitives.

**Don't use for**: Loading USD assets, robots, or complex scenes — use
`execute_script` with proper imports.

**Verify after**: `get_scene_info` and check that `/physicsScene` (or your
`scene_name`) prim exists and that `gravityDirection`/`gravityMagnitude` are what you
expect.

---

## 5. `transform`

```
mcp__isaac-sim__transform(
    prim_path: str,
    position: list = [0, 0, 50],
    scale: list = [10, 10, 10]
)  →  str
```

**Purpose**: Move/scale an existing prim.

**Args**:
- `prim_path`: must already exist in the stage.
- `position`: `[x, y, z]` in stage units.
- `scale`: `[x, y, z]`. Note **default is `[10, 10, 10]`** — passing no scale will
  10x the prim, surprising. Always pass an explicit scale.

**Use when**: One-off positioning of an existing prim.

**Don't use for**: Rotation (no rotation arg). For rotation, `execute_script`:
```python
from pxr import Gf, UsdGeom
prim = stage.GetPrimAtPath("/World/Robot")
xf = UsdGeom.Xformable(prim)
xf.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, 90))
```

**Don't use for**: Articulation joint positions (`transform` moves the whole prim,
not joints). For joint control, `execute_script` + `Articulation.apply_action`.

---

## 6. `omni_kit_command`

```
mcp__isaac-sim__omni_kit_command(command: str = "CreatePrim", prim_type: str = "Sphere")  →  str
```

**Purpose**: Run a built-in Kit command (the same things that show up in `Window →
Commands` panel).

**Args**:
- `command`: Kit command name (`CreatePrim`, `DeletePrim`, `ToggleVisibility`, ...).
- `prim_type`: argument for the command. Semantics depend on which command.

**Reality check**: This tool's surface is limited (mostly `CreatePrim` with a
hardcoded `prim_type` flow). For most uses, `execute_script` with
`omni.kit.commands.execute(...)` is more flexible:

```python
import omni.kit.commands
omni.kit.commands.execute(
    "CreatePrim",
    prim_type="Xform",
    prim_path="/World/MyGroup",
)
```

**Use when**: One of the 2 supported args fits exactly.

**Otherwise**: Skip to `execute_script`.

---

## 7. `search_3d_usd_by_text`

```
mcp__isaac-sim__search_3d_usd_by_text(
    text_prompt: str,
    target_path: str = "/World/my_usd",
    position: list = [0, 0, 50],
    scale: list = [10, 10, 10]
)  →  str
```

**Purpose**: Semantic search of NVIDIA's USD asset library by text description, then
auto-load the result into the scene at the given path.

**Args**:
- `text_prompt`: natural language ("warehouse shelving", "forklift", "industrial
  conveyor").
- `target_path`: where to place in the stage.
- `position`, `scale`: same as `transform` (note 10x default scale).

**Use when**: You need a generic environment asset (warehouse, office, factory floor,
prop) and don't have a specific USD path in mind.

**Don't use for**: Specific robots (use `create_robot` or `add_reference_to_stage`),
or assets you've already located by URL.

**Failure mode**: Returns task_id even for empty results. Always `get_scene_info` after
to confirm the prim was actually loaded.

---

## 8. `generate_3d_from_text_or_image`

```
mcp__isaac-sim__generate_3d_from_text_or_image(
    text_prompt: str = None,
    image_url: str = None,
    position: list = [0, 0, 50],
    scale: list = [10, 10, 10]
)  →  str
```

**Purpose**: AI-generate a fresh 3D asset (not from a library) and load it.

**Args**:
- One of `text_prompt` OR `image_url` (not both required).
- `position`, `scale`: same caveat as above.

**Use when**: You need a custom asset that doesn't exist in any library — e.g.,
"a damaged shipping box with one corner crushed", or generating from a reference photo.

**Don't use for**:
- Anything safety-critical (gen quality is variable)
- Anything that needs precise dimensions (you don't control the output mesh size)
- High-poly hero assets (gen is medium-poly)
- Anything you'd want consistent across runs (non-deterministic)

**Latency**: significantly slower than other tools (server-side generation). Set
expectations with the user.

---

## 9. The implicit connection layer

There is no direct tool for the connection itself, but it's a real failure surface.

**The MCP server (Python) opens a TCP socket to `localhost:8766`** on startup and on
the first `get_scene_info` call. If Isaac Sim is not running or extension not loaded,
the connection fails and every subsequent tool call returns an error.

**Symptoms of connection issues**:
| Symptom | Cause |
|---|---|
| `Connection refused: [Errno 111]` | Isaac Sim not running, OR extension not enabled |
| Tool returns but result is `None`/empty | Extension loaded but Kit busy (startup, big load) |
| Slow first call (~5-30s) then fast | Cold connection establishment. Normal on first call after restart |
| Repeated timeouts | Kit's main thread is stuck (long loop, modal dialog, crash) |

**Recovery**: See `debugging.md` §"Recovering connection".

**Multiple Isaac Sim instances**: The default port is 8766. If two instances are
running (one with `isaac-mcp`, one without), only the one with the extension and on
port 8766 is reachable. Confirm with `ss -tlnp | grep 8766`.

---

## Cross-tool patterns to remember

1. **`get_scene_info` is cheap; call it generously**. Cost is one round trip; benefit
   is knowing what's there.
2. **`create_robot` failing for Doosan/UR/etc. is expected** — fall back to
   `execute_script` with `add_reference_to_stage`. See `cobot3-recipes.md`.
3. **The `transform` tool's default scale `[10,10,10]` is a trap** — always pass
   explicit scale (often `[1,1,1]`).
4. **`create_physics_scene`'s default gravity is Y-down cm units, not Z-up SI**. Pass
   `[0, 0, -9.81]` if your stage is Z-up (which is Isaac Sim default).
5. **For anything not in this list, write `execute_script`** — and *print the code in
   your chat reply first*.

See also:
- `patterns.md` for multi-step workflows that combine these tools
- `debugging.md` for what to do when calls fail
- `cobot3-recipes.md` for Doosan/warehouse-specific recipes
