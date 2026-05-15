# patterns.md — Common MCP workflow sequences

Pre-baked sequences for the most frequent tasks. Each is a *recipe*: a small set of
MCP calls in a specific order, with verification. Copy → adapt → execute.

## Contents
1. Sanity-check on connect (always)
2. Empty the stage (fresh start)
3. Add a built-in robot
4. Add a custom USD asset (Doosan, UR, etc.)
5. Modify an existing prim (position, scale, property)
6. Add/remove physics on a prim
7. Set up a simple physics playground
8. Run a timed action sequence (no `time.sleep`)
9. Inspect a prim's full state
10. Build an OmniGraph (Action Graph for ROS 2 bridge)
11. Save the current stage to a USD file
12. Recover from a stuck simulation

---

## 1. Sanity-check on connect

Run this first in every new task. Confirms connection + tells you what's in the scene.

```
[1] mcp__isaac-sim__get_scene_info()
```

If returns `Connection refused` → stop, go to `debugging.md` §1.

If returns scene data → note what's there. Common starting states:
- Empty stage (just `/World` and maybe `/Render`)
- One of the example scenes (Hello World, Hello Robot)
- A previous user session left over (don't assume what's there)

---

## 2. Empty the stage

Before adding new content, decide: *do I want a fresh stage or to add to the existing
one?* Most cobot3 tasks want a known starting point — empty.

```python
# execute_script
import omni.usd
omni.usd.get_context().new_stage()
```

**Verify**: `get_scene_info` → should show only `/Render` and `/World` (or just
`/World`).

**Gotcha**: If a simulation is playing, `new_stage` may not work cleanly. Stop first:
```python
import omni.timeline
omni.timeline.get_timeline_interface().stop()
omni.usd.get_context().new_stage()
```

---

## 3. Add a built-in robot

Best case — Franka, Jetbot, Carter, G1, Go1.

```
[1] mcp__isaac-sim__create_physics_scene(floor=True, gravity=[0, 0, -9.81])
    # Z-up gravity. Default tool value is Y-down cm units — pass explicit value.

[2] mcp__isaac-sim__create_robot(robot_type="jetbot", position=[0, 0, 0])

[3] mcp__isaac-sim__get_scene_info()
    # Verify: prim list should now include /World/jetbot or similar
```

---

## 4. Add a custom USD asset (Doosan m0609, UR10, etc.)

`create_robot` doesn't support these. Use `execute_script`.

```python
# Print this code in chat, then execute_script
from isaacsim.core.api import World
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot

world = World.instance() or World()

# Local USD file or omniverse:// URL
M0609_USD = "/home/rokey/dev_ws/cobot_ws/src/doosan-robot2/urdf/m0609_isaac_sim/m0609_isaac_sim.usd"

add_reference_to_stage(usd_path=M0609_USD, prim_path="/World/m0609")
world.scene.add(Robot(prim_path="/World/m0609", name="m0609"))

# Need to call reset before any state read
import asyncio
asyncio.ensure_future(world.reset_async())
```

**Verify after** (separate `execute_script` call, because reset is async):
```python
from isaacsim.core.api import World
world = World.instance()
robot = world.scene.get_object("m0609")
print(f"num_dof: {robot.num_dof}")
print(f"dof_names: {robot.dof_names}")
```

If `num_dof` is `None`, the reset hasn't completed yet — wait a few seconds and retry.

---

## 5. Modify an existing prim

### Position only
```
mcp__isaac-sim__transform(prim_path="/World/m0609", position=[1.0, 0, 0], scale=[1, 1, 1])
```
**Always** pass explicit `scale=[1,1,1]` — the tool default is `[10,10,10]`.

### Rotation, attribute set, or anything else
```python
# execute_script
from pxr import Usd, UsdGeom, Gf
import omni.usd

stage = omni.usd.get_context().get_stage()
prim = stage.GetPrimAtPath("/World/m0609")

xf = UsdGeom.Xformable(prim)
# clear existing transform ops first if you want to fully replace
xf.ClearXformOpOrder()
xf.AddTranslateOp().Set(Gf.Vec3f(1.0, 0, 0))
xf.AddRotateXYZOp().Set(Gf.Vec3f(0, 0, 90))
xf.AddScaleOp().Set(Gf.Vec3f(1, 1, 1))
```

---

## 6. Add/remove physics on a prim

### Quick: RigidBody + Collider preset (one prim)
```python
from omni.physx.scripts import utils as physx_utils
import omni.usd

stage = omni.usd.get_context().get_stage()
prim = stage.GetPrimAtPath("/World/MyCube")
physx_utils.setRigidBody(prim, approximationShape="convexHull", kinematic=False)
```

### Remove RigidBody (make a prim static — typical for conveyor frames)
```python
from pxr import UsdPhysics
prim = stage.GetPrimAtPath("/World/ConveyorTrack_06")
prim.RemoveAPI(UsdPhysics.RigidBodyAPI)
```

### Change collider approximation (e.g., thin belt mesh fails as convexHull)
```python
from pxr import UsdPhysics
mesh_prim = stage.GetPrimAtPath("/World/ConveyorTrack_06/Belt/SM_Belt_01")
collision_api = UsdPhysics.MeshCollisionAPI.Apply(mesh_prim)
collision_api.CreateApproximationAttr().Set("boundingCube")  # or "convexDecomposition"
```

---

## 7. Simple physics playground (Cube falling on ground)

```
[1] mcp__isaac-sim__create_physics_scene(
        floor=True,
        gravity=[0, 0, -9.81],   # Z-up SI
        objects=[
            {"path": "/World/Cube", "type": "Cube", "size": 0.1,
             "position": [0, 0, 1.0]},
        ]
    )

[2] # Press Play (timeline)
    # execute_script:
    import omni.timeline
    omni.timeline.get_timeline_interface().play()

[3] # After ~2 seconds, verify cube landed
    mcp__isaac-sim__get_scene_info()
```

---

## 8. Run a timed action sequence (no `time.sleep`)

The wrong way (don't do this — blocks Kit):
```python
self.controller.apply_action(...)
time.sleep(3)  # ❌ freezes GUI
self.controller.apply_action(...)
```

The right way — `step_size` accumulation in a physics callback:
```python
# execute_script — register a callback that uses elapsed_time
from isaacsim.core.api import World
from isaacsim.core.utils.types import ArticulationAction
import numpy as np

world = World.instance()
robot = world.scene.get_object("m0609")

# Stash state on the world so the callback can read it
world._elapsed = 0.0

def mission(step_size):
    world._elapsed += step_size
    if world._elapsed < 3.0:
        v = np.array([-5.0, -5.0])      # 3s reverse
    elif world._elapsed < 8.0:
        v = np.array([0.0, 0.0])         # 5s stop
    elif world._elapsed < 12.0:
        v = np.array([2.0, 5.0])         # 4s left turn
    elif world._elapsed < 15.0:
        v = np.array([5.0, 5.0])         # 3s forward
    else:
        v = np.array([0.0, 0.0])         # stop

    robot.get_articulation_controller().apply_action(
        ArticulationAction(joint_velocities=v)
    )

world.add_physics_callback("mission", callback_fn=mission)
```

The callback runs every physics step (60 Hz default), independent of MCP calls.
After registering, *return from `execute_script`* and let Kit's event loop run.

---

## 9. Inspect a prim's full state

```python
# execute_script
from pxr import Usd, UsdPhysics
import omni.usd

stage = omni.usd.get_context().get_stage()
prim_path = "/World/Cube_01"
prim = stage.GetPrimAtPath(prim_path)

print(f"Type: {prim.GetTypeName()}")
print(f"Applied schemas: {prim.GetAppliedSchemas()}")
print(f"Has RigidBodyAPI: {prim.HasAPI(UsdPhysics.RigidBodyAPI)}")
print(f"Has CollisionAPI: {prim.HasAPI(UsdPhysics.CollisionAPI)}")
print(f"Has ArticulationRootAPI: {prim.HasAPI(UsdPhysics.ArticulationRootAPI)}")
print("Properties:")
for prop in prim.GetProperties():
    name = prop.GetName()
    try:
        val = prop.Get() if hasattr(prop, "Get") else "(rel)"
    except Exception as e:
        val = f"<error: {e}>"
    print(f"  {name} = {val}")
```

The `print` output goes to Kit's stdout, which the MCP server tails — you'll get the
result back as part of the tool return.

---

## 10. Build an OmniGraph for ROS 2 bridge

Wire a Jetbot to publish JointState + subscribe to /cmd_vel.

```python
# execute_script
import omni.graph.core as og

keys = og.Controller.Keys
og.Controller.edit(
    {"graph_path": "/World/RosGraph", "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("Tick", "omni.graph.action.OnPlaybackTick"),
            ("Context", "isaacsim.ros2.bridge.ROS2Context"),
            ("PubJS", "isaacsim.ros2.bridge.ROS2PublishJointState"),
        ],
        keys.SET_VALUES: [
            ("Context.inputs:domain_id", 130),       # match user's ROS_DOMAIN_ID
            ("PubJS.inputs:topicName", "joint_states"),
            ("PubJS.inputs:targetPrim", "/World/jetbot"),
        ],
        keys.CONNECT: [
            ("Tick.outputs:tick", "PubJS.inputs:execIn"),
            ("Context.outputs:context", "PubJS.inputs:context"),
        ],
    },
)
```

**Verify**: in another terminal, `ros2 topic list` should show `/joint_states` after
pressing Play in Isaac Sim. If not, see `cobot3-recipes.md` §"ROS 2 bridge debugging".

See [[isaac-sim-bridge]] `references/omnigraph-ros-bridge.md` for full sensor patterns
(camera, lidar, TF, IMU).

---

## 11. Save the current stage

```python
# execute_script
import omni.usd
ctx = omni.usd.get_context()
# Save to a new path (does not change which stage is open)
ctx.save_as_stage("/home/rokey/dev_ws/cobot3/scenes/snapshot.usda")
# Or save in place (only works if the stage has a file backing — not for new stages)
# ctx.save_stage()
```

**`.usda`** for human-readable, **`.usd`** for binary (smaller).

---

## 12. Recover from a stuck simulation

Symptoms: viewport frozen, `get_scene_info` times out, GUI sluggish.

```python
# execute_script — first try graceful stop
import omni.timeline
omni.timeline.get_timeline_interface().stop()
```

If still stuck:
```python
# Reset world
from isaacsim.core.api import World
import asyncio
world = World.instance()
if world is not None:
    asyncio.ensure_future(world.reset_async())
```

If `execute_script` itself times out, ask the user to manually click `Stop` in the
viewport. If that also fails, restart Isaac Sim (`isaac-mcp` from a fresh terminal).

---

## Pattern composition

These patterns combine. A typical cobot3 startup looks like:

```
1.  get_scene_info                                    # connection check
2.  execute_script: new_stage()                        # clean slate
3.  create_physics_scene(floor=True, gravity=[0,0,-9.81])
4.  execute_script: add Doosan m0609 + RG2 (§4)
5.  execute_script: add conveyor + bins from search_3d_usd_by_text or local USD
6.  execute_script: build OG ROS 2 bridge (§10)
7.  get_scene_info                                    # final verification
8.  execute_script: timeline.play()                    # start sim
```

See `cobot3-recipes.md` for the fleshed-out version of this with actual paths and
values.
