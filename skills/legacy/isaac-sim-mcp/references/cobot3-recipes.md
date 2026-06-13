# cobot3-recipes.md — MCP recipes for the cobot3 project

Project-specific recipes for the user's cobot3 workflow: **Doosan m0609 + RG2 gripper
+ YOLO + warehouse conveyor sorting + ROS 2 Humble + Supabase telemetry**.

These compose the patterns in `patterns.md` with concrete paths, names, and values
that match the user's setup.

For general Isaac Sim domain knowledge (USD/PhysX/OG concepts), see
[[isaac-sim-bridge]] — that skill's `warehouse-sorting-pipeline.md`,
`yolo-perception.md`, `sort-decision-logic.md`, `server-bridge.md`, and
`telemetry-supabase.md` are the authoritative references. This file is just the **MCP
control surface** for those patterns.

## Contents
1. Project paths and naming conventions
2. Fresh cobot3 scene from scratch
3. Spawn Doosan m0609 (custom USD, not `create_robot`)
4. Spawn RG2 gripper and attach to m0609 end-effector
5. Warehouse conveyor + bins (search vs explicit USD)
6. RGB camera over conveyor + ROS 2 image publish OG
7. YOLO in-process inference (call from `execute_script`)
8. Multi-robot namespace isolation
9. ROS 2 bridge debugging from MCP
10. Telemetry: emit a snapshot to Supabase from MCP
11. Fixing broken samples (PDF Section 8-style)

---

## 1. Project paths and naming conventions

```
~/dev_ws/cobot_ws/                       # ROS 2 workspace (Doosan + custom)
~/dev_ws/cobot_ws/src/doosan-robot2/     # Doosan ROS 2 source
~/dev_ws/cobot_ws/install/               # built install space
~/dev_ws/cobot3/                         # cobot3 project root
~/dev_ws/cobot3/scenes/                  # USD scenes (created on save)
~/dev_ws/cobot3/scripts/                 # Standalone Python scripts (use python.sh)
```

USD prim path convention (multi-robot):
```
/World/Sorter_01/
  ├── m0609                            # robot articulation root
  ├── m0609/rg2                        # gripper (child of EE link)
  ├── camera                           # RGB camera
  └── og                               # OmniGraph for ROS 2 bridge

/World/Sorter_02/  (same structure)
/World/Conveyor/                       # shared static conveyor
/World/Bins/                           # output bins
/World/Spawn/                          # incoming-package spawn zone
```

ROS 2 namespacing (one per robot):
```
/sorter_01/joint_states, /sorter_01/joint_command, /sorter_01/camera/image_raw
/sorter_02/joint_states, /sorter_02/joint_command, /sorter_02/camera/image_raw
/conveyor/...
```

`ROS_DOMAIN_ID=130` (per `~/.bashrc`).

---

## 2. Fresh cobot3 scene from scratch

The full startup sequence. Use this when starting work in a new session.

```
[Step 1] mcp__isaac-sim__get_scene_info()
         # confirm connection

[Step 2] # execute_script: empty stage
import omni.usd
import omni.timeline
omni.timeline.get_timeline_interface().stop()
omni.usd.get_context().new_stage()

[Step 3] mcp__isaac-sim__create_physics_scene(
            floor=True,
            gravity=[0, 0, -9.81],   # Z-up SI
            scene_name="cobot3_physics"
         )

[Step 4] # execute_script: spawn robots, conveyor, camera (see §3-6 below)
# ... composes patterns from §3, §4, §5, §6

[Step 5] # execute_script: build ROS 2 bridge OG (see §6 + patterns.md §10)

[Step 6] mcp__isaac-sim__get_scene_info()
         # final verification

[Step 7] # execute_script: start sim
import omni.timeline
omni.timeline.get_timeline_interface().play()
```

---

## 3. Spawn Doosan m0609

`create_robot` doesn't support Doosan. Use `add_reference_to_stage` via `execute_script`.

```python
# execute_script
from isaacsim.core.api import World
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.robots import Robot
import asyncio

M0609_USD = "/home/rokey/dev_ws/cobot_ws/install/dsr_description2/share/dsr_description2/usd/m0609.usd"

world = World.instance() or World()

add_reference_to_stage(usd_path=M0609_USD, prim_path="/World/Sorter_01/m0609")
robot = world.scene.add(Robot(
    prim_path="/World/Sorter_01/m0609",
    name="sorter_01_m0609",
    position=[0.0, 0.0, 0.0],
))

# Reset is required before reading state
asyncio.ensure_future(world.reset_async())
```

**If USD file doesn't exist**: `cobot_ws` may not be built. Tell user to:
```bash
cd ~/dev_ws/cobot_ws && colcon build --packages-select dsr_description2
```

**Verify joint setup** (run after reset completes, ~2 seconds later):
```python
from isaacsim.core.api import World
world = World.instance()
robot = world.scene.get_object("sorter_01_m0609")
print(f"num_dof: {robot.num_dof}")
print(f"dof_names: {robot.dof_names}")
# Expected: 6 DOF, names like joint1..joint6
```

If `num_dof` is wrong, the URDF importer didn't set up articulation correctly. See
[[isaac-sim-bridge]] `usd-from-urdf.md` §articulation.

---

## 4. Spawn RG2 gripper and attach

```python
# execute_script
from isaacsim.core.utils.stage import add_reference_to_stage
RG2_USD = "/home/rokey/dev_ws/cobot_ws/install/.../rg2.usd"  # update path

# Attach as child of m0609's end-effector link
add_reference_to_stage(
    usd_path=RG2_USD,
    prim_path="/World/Sorter_01/m0609/link6/rg2",
)
```

For programmatic grasp via SurfaceGripper (NVIDIA's suction simulation), use
[[isaac-sim-bridge]] `usd-from-urdf.md` §Surface-gripper. Mechanical 2-finger gripper
is more complex — usually handled via joint control + contact sensor.

---

## 5. Warehouse conveyor + bins

### Option A: Search NVIDIA catalog
```
mcp__isaac-sim__search_3d_usd_by_text(
    text_prompt="industrial conveyor belt",
    target_path="/World/Conveyor",
    position=[2.0, 0, 0.5],
    scale=[1, 1, 1]
)
```

### Option B: Use a specific NVIDIA Asset Library USD (preferred — deterministic)
```python
# execute_script
from isaacsim.core.utils.stage import add_reference_to_stage

CONVEYOR_USD = "omniverse://localhost/NVIDIA/Assets/Isaac/5.1/Props/ConveyorTrack/ConveyorTrack.usd"

add_reference_to_stage(usd_path=CONVEYOR_USD, prim_path="/World/Conveyor")

# Conveyor is static — remove RigidBody if importer auto-added it
from pxr import UsdPhysics
import omni.usd
stage = omni.usd.get_context().get_stage()
conveyor = stage.GetPrimAtPath("/World/Conveyor")
if conveyor.HasAPI(UsdPhysics.RigidBodyAPI):
    conveyor.RemoveAPI(UsdPhysics.RigidBodyAPI)
```

**Belt-surface velocity** (the right way to "move things on the conveyor" — don't
animate the mesh):
```python
from pxr import PhysxSchema
belt = stage.GetPrimAtPath("/World/Conveyor/Belt")
sva = PhysxSchema.PhysxSurfaceVelocityAPI.Apply(belt)
sva.GetSurfaceVelocityAttr().Set((0.3, 0.0, 0.0))   # 0.3 m/s along +X
sva.GetSurfaceVelocityEnabledAttr().Set(True)
```

### Bins
Three bins at known positions for class A/B/C sorting:
```python
from omni.physx.scripts import utils as physx_utils
from isaacsim.core.utils.prims import create_prim

for i, label in enumerate(["A", "B", "C"]):
    path = f"/World/Bins/bin_{label}"
    create_prim(
        prim_path=path,
        prim_type="Cube",
        position=(3.0, -1.0 + i * 1.0, 0.05),
        scale=(0.4, 0.4, 0.1),
    )
    physx_utils.setCollider(stage.GetPrimAtPath(path), approximationShape="boundingCube")
```

---

## 6. RGB camera + ROS 2 image publish OG

```python
# execute_script — create camera
from pxr import UsdGeom, Gf
import omni.usd

stage = omni.usd.get_context().get_stage()

# Create camera above conveyor looking down
camera_path = "/World/Sorter_01/camera"
cam = UsdGeom.Camera.Define(stage, camera_path)
cam.GetFocalLengthAttr().Set(24.0)
cam.GetHorizontalApertureAttr().Set(20.955)

xf = UsdGeom.Xformable(cam.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3f(2.0, 0, 2.0))      # 2m above conveyor
xf.AddRotateXYZOp().Set(Gf.Vec3f(0, -90, 0))         # look down (-Z)
```

```python
# execute_script — build OG to publish image
import omni.graph.core as og

keys = og.Controller.Keys
og.Controller.edit(
    {"graph_path": "/World/Sorter_01/og", "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("Tick", "omni.graph.action.OnPlaybackTick"),
            ("Context", "isaacsim.ros2.bridge.ROS2Context"),
            ("RP", "isaacsim.core_nodes.IsaacCreateRenderProduct"),
            ("PubImg", "isaacsim.ros2.bridge.ROS2CameraHelper"),
        ],
        keys.SET_VALUES: [
            ("Context.inputs:domain_id", 130),
            ("RP.inputs:cameraPrim", "/World/Sorter_01/camera"),
            ("RP.inputs:width", 640),
            ("RP.inputs:height", 480),
            ("PubImg.inputs:topicName", "/sorter_01/camera/image_raw"),
            ("PubImg.inputs:frameId", "sorter_01_camera"),
            ("PubImg.inputs:type", "rgb"),
        ],
        keys.CONNECT: [
            ("Tick.outputs:tick", "RP.inputs:execIn"),
            ("RP.outputs:execOut", "PubImg.inputs:execIn"),
            ("RP.outputs:renderProductPath", "PubImg.inputs:renderProductPath"),
            ("Context.outputs:context", "PubImg.inputs:context"),
        ],
    },
)
```

**Verify after Play**:
```bash
ros2 topic list | grep /sorter_01
ros2 topic hz /sorter_01/camera/image_raw
```

If no topic / no hz → see §9 below.

---

## 7. YOLO in-process inference

The cobot3 pipeline runs YOLO **inside Isaac Sim's Python** (not as a separate ROS
node) to avoid image copy overhead. Trigger from MCP:

```python
# execute_script — one-shot inference
# Prerequisite: pip install ultralytics inside Isaac Sim's bundled Python:
#   ~/dev_ws/isaac_sim/isaacsim/.../python.sh -m pip install ultralytics
#
# But for MCP-driven session, just import — Kit's Python has site-packages

import numpy as np
from ultralytics import YOLO

# Cached model? Reuse via stage-level dict
_state = globals().setdefault("_yolo_state", {})
if "model" not in _state:
    _state["model"] = YOLO("/home/rokey/dev_ws/cobot3/models/yolov8n.pt")

# Grab the latest frame from the render product (or via omni.replicator)
# Simplest: read from the camera's most recent frame via Replicator
import omni.replicator.core as rep
camera_prim = "/World/Sorter_01/camera"
rp = rep.create.render_product(camera_prim, resolution=(640, 480))
annotator = rep.AnnotatorRegistry.get_annotator("rgb")
annotator.attach([rp])

# Force one frame
import asyncio
asyncio.ensure_future(rep.orchestrator.step_async())

frame = annotator.get_data()    # numpy HxWx4 (RGBA)
img = frame[..., :3]            # drop alpha

results = _state["model"](img, verbose=False)
for box in results[0].boxes:
    cls = int(box.cls[0])
    conf = float(box.conf[0])
    xyxy = box.xyxy[0].cpu().numpy()
    print(f"class={cls} conf={conf:.2f} bbox={xyxy}")
```

For the **per-frame** version with publishing to `vision_msgs/Detection2DArray`, see
[[isaac-sim-bridge]] `yolo-perception.md` §publish.

---

## 8. Multi-robot namespace isolation

Two robots, two independent ROS 2 namespaces, zero topic collision.

The key: every OG node that publishes/subscribes to ROS 2 must have a **distinct
`topicName`** with the robot's namespace as prefix.

```python
# execute_script — build OG for sorter_02 (mirror of §6 with different paths/names)
import omni.graph.core as og

keys = og.Controller.Keys

for sorter_id in ["sorter_01", "sorter_02"]:
    og.Controller.edit(
        {"graph_path": f"/World/{sorter_id.capitalize()}/og", "evaluator_name": "execution"},
        {
            keys.CREATE_NODES: [
                ("Tick", "omni.graph.action.OnPlaybackTick"),
                ("Ctx", "isaacsim.ros2.bridge.ROS2Context"),
                ("PubJS", "isaacsim.ros2.bridge.ROS2PublishJointState"),
                ("SubJC", "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
                ("Ctrl", "isaacsim.core_nodes.IsaacArticulationController"),
            ],
            keys.SET_VALUES: [
                ("Ctx.inputs:domain_id", 130),
                ("PubJS.inputs:topicName", f"/{sorter_id}/joint_states"),
                ("PubJS.inputs:targetPrim", f"/World/{sorter_id.capitalize()}/m0609"),
                ("SubJC.inputs:topicName", f"/{sorter_id}/joint_command"),
                ("Ctrl.inputs:targetPrim", f"/World/{sorter_id.capitalize()}/m0609"),
            ],
            keys.CONNECT: [
                ("Tick.outputs:tick", "PubJS.inputs:execIn"),
                ("Tick.outputs:tick", "SubJC.inputs:execIn"),
                ("Ctx.outputs:context", "PubJS.inputs:context"),
                ("Ctx.outputs:context", "SubJC.inputs:context"),
                ("SubJC.outputs:jointNames", "Ctrl.inputs:jointNames"),
                ("SubJC.outputs:positionCommand", "Ctrl.inputs:positionCommand"),
            ],
        },
    )
```

**Verify**:
```bash
ros2 topic list | grep sorter
# /sorter_01/joint_command, /sorter_01/joint_states, ...
# /sorter_02/joint_command, /sorter_02/joint_states, ...
```

For more elaborate namespace separation (services, TF prefixes), see
[[isaac-sim-bridge]] `warehouse-sorting-pipeline.md` §namespace.

---

## 9. ROS 2 bridge debugging from MCP

Common: built the OG, but `ros2 topic list` is empty.

**Diagnose via MCP**:
```python
# execute_script — check OG state
import omni.graph.core as og
graph = og.get_graph_by_path("/World/Sorter_01/og")
print(f"Graph: {graph.get_path()}")
for node in graph.get_nodes():
    print(f"  Node: {node.get_prim_node().GetPath()}  state: {node.get_compute_count()}")
```

A node with `compute_count == 0` after a few seconds of Play means it never fired —
upstream tick or context isn't connected.

**Common fixes**:
- `Tick → execIn` not wired → node never fires
- `Context.outputs:context` not wired to publisher's `inputs:context` → ROS bridge not
  initialized for this graph
- `domain_id` mismatch with host `ROS_DOMAIN_ID` env var → topics exist but invisible

**Check host side** (Bash, not MCP):
```bash
echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
source /opt/ros/humble/setup.bash
ros2 topic list
```

For deeper bridge debugging see [[isaac-sim-bridge]] `omnigraph-ros-bridge.md`
§"Did the bridge actually publish?".

---

## 10. Telemetry snapshot to Supabase

Per [[isaac-sim-bridge]] `telemetry-supabase.md`, cobot3 logs events to a Postgres
DB. Emit a snapshot from MCP:

```python
# execute_script — log a cycle event
import os
from supabase import create_client
from datetime import datetime, timezone

# Connection — assumes env vars set in user's shell that launched Isaac Sim
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
if not (url and key):
    print("SUPABASE_URL / SUPABASE_ANON_KEY not in env. Skipping log.")
else:
    sb = create_client(url, key)
    sb.table("cycle_events").insert({
        "sorter_id": "sorter_01",
        "event_type": "pick_complete",
        "object_class": "B",
        "duration_s": 4.2,
        "ts": datetime.now(timezone.utc).isoformat(),
    }).execute()
    print("logged")
```

For schema details and batching see [[isaac-sim-bridge]] `telemetry-supabase.md`.

---

## 11. Fixing broken samples (PDF Section 8-style)

The PDF's `hello_world.py` ships in a broken mid-edit state (numpy not imported, refs
non-existent `fancy_robot`). When the user reports the resulting error:

```
NameError: name 'np' is not defined
```

**Don't fix the file via MCP** — files belong to disk, use `Edit`:
```
Edit tool on ~/dev_ws/isaac_sim/isaacsim/.../hello_world/hello_world.py
```

**Then** force Isaac Sim to reload via MCP:
```python
# execute_script — reload Python module
import importlib
import sys

mod_name = "isaacsim.examples.interactive.hello_world.hello_world"
if mod_name in sys.modules:
    importlib.reload(sys.modules[mod_name])
print("Module reloaded")
```

Or, simpler: ask user to restart Isaac Sim (extension changes require it anyway).

---

## Putting it all together — cobot3 single-robot mission via MCP

```
1.  get_scene_info                                    # connection check
2.  execute_script: stop timeline + new_stage         # clean slate
3.  create_physics_scene(floor=True, gravity=[0,0,-9.81])
4.  execute_script: §3 add m0609 to /World/Sorter_01
5.  execute_script: §5B add ConveyorTrack + remove RigidBody + surface velocity
6.  execute_script: §5 bins (A, B, C)
7.  execute_script: §6 camera + ROS image OG
8.  execute_script: §8 (single-robot variant) joint_state OG
9.  get_scene_info                                    # verify
10. execute_script: timeline.play()
11. (host shell)   ros2 topic list                    # verify ROS 2 topics
12. (host shell)   ros2 run yolo_node yolo_demo       # external YOLO consumer
                   OR §7 in-process YOLO
13. execute_script: read robot state, drive joints to grasp pose
14. §10 supabase log per cycle
```

This is a ~30 minute end-to-end demo. Each `execute_script` should be printed in chat
before sending, and verified with `get_scene_info` (or targeted `execute_script` read)
after.

See [[isaac-sim-bridge]] `warehouse-sorting-pipeline.md` for the full reference
architecture this implements.
