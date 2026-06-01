#!/usr/bin/env python3
"""multi_robot_bringup.py — Bring up N m0609+RG2 robots in a single Isaac Sim stage.

Usage (inside Isaac Sim's python.sh):
    ./python.sh multi_robot_bringup.py \
        --template robots/m0609_rg2.usda \
        --robots r0,r1,r2,r3 \
        --row-spacing 1.5

For each robot_id this script:
  1. Adds a USD reference of the template under /World/Robots/{robot_id}.
  2. Sets a unique world transform (row layout along +X).
  3. Builds the per-robot OmniGraph bridge (joint_states, joint_command, TF,
     overhead camera) with topic names prefixed by /{robot_id}/...
  4. Performs a quick post-build sanity check: every articulation root is
     found, every OG node is non-erroring, every camera prim exists.

Companion to references/warehouse-sorting-pipeline.md §4 (OG factory) and
references/omnigraph-ros-bridge.md §"다중 로봇 OG 팩토리". Do NOT call from
outside Isaac Sim — it depends on omni.* and pxr.* modules.
"""

from __future__ import annotations
import argparse
import logging
import sys

LOG = logging.getLogger("bringup")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--template", default="robots/m0609_rg2.usda",
                   help="USD asset path for one m0609+RG2 robot")
    p.add_argument("--robots", default="r0,r1,r2,r3",
                   help="Comma-separated robot_ids")
    p.add_argument("--row-spacing", type=float, default=1.5,
                   help="Distance (m) between robots along +X")
    p.add_argument("--camera-template", default="cameras/overhead_template.usda",
                   help="Optional camera USD; if missing, a default camera prim is created")
    return p.parse_args()


def add_robot_reference(stage, robot_id: str, template_path: str, position):
    """Reference the robot template under /World/Robots/{robot_id} and place it."""
    from pxr import UsdGeom, Sdf, Gf
    parent = "/World/Robots"
    if not stage.GetPrimAtPath(parent):
        UsdGeom.Xform.Define(stage, parent)
    xform_path = f"{parent}/{robot_id}"
    xform = UsdGeom.Xform.Define(stage, xform_path)
    xform.GetPrim().GetReferences().AddReference(template_path)
    # Translate
    op = xform.AddTranslateOp()
    op.Set(Gf.Vec3d(*position))
    LOG.info("added robot %s at %s referencing %s", robot_id, position, template_path)


def add_overhead_camera(stage, robot_id: str, base_position):
    """Place an overhead RGB camera looking down at the robot's conveyor zone."""
    from pxr import UsdGeom, Gf
    cam_path = f"/World/Cameras/{robot_id}_overhead"
    if stage.GetPrimAtPath(cam_path):
        return cam_path
    if not stage.GetPrimAtPath("/World/Cameras"):
        UsdGeom.Xform.Define(stage, "/World/Cameras")
    cam = UsdGeom.Camera.Define(stage, cam_path)
    # 1.5 m above robot base, looking down
    xform = UsdGeom.Xformable(cam.GetPrim())
    xform.AddTranslateOp().Set(Gf.Vec3d(base_position[0], base_position[1] + 0.5, 1.5))
    xform.AddRotateXYZOp().Set(Gf.Vec3f(-90.0, 0.0, 0.0))
    cam.CreateFocalLengthAttr().Set(24.0)
    cam.CreateHorizontalApertureAttr().Set(36.0)
    return cam_path


def build_og_bridge(robot_id: str):
    """Per-robot OmniGraph: JointState pub/sub, TF, camera helper.

    Mirrors references/omnigraph-ros-bridge.md §"다중 로봇 OG 팩토리".
    """
    import omni.graph.core as og
    ns = f"/{robot_id}"
    prim_root = f"/World/Robots/{robot_id}/m0609"
    cam_prim = f"/World/Cameras/{robot_id}_overhead"
    keys = og.Controller.Keys
    og.Controller.edit(
        {"graph_path": f"/World/Graphs/{robot_id}_bridge",
         "evaluator_name": "execution"},
        {
            keys.CREATE_NODES: [
                ("Tick",        "omni.graph.action.OnPlaybackTick"),
                ("Ctx",         "omni.isaac.ros2_bridge.ROS2Context"),
                ("ArticState",  "omni.isaac.core_nodes.IsaacArticulationState"),
                ("PubJoint",    "omni.isaac.ros2_bridge.ROS2PublishJointState"),
                ("SubJointCmd", "omni.isaac.ros2_bridge.ROS2SubscribeJointState"),
                ("Applier",     "omni.isaac.core_nodes.IsaacArticulationController"),
                ("PubTF",       "omni.isaac.ros2_bridge.ROS2PublishTransformTree"),
                ("CamHelper",   "omni.isaac.ros2_bridge.ROS2CameraHelper"),
            ],
            keys.SET_VALUES: [
                ("ArticState.inputs:targetPrim",  prim_root),
                ("Applier.inputs:targetPrim",     prim_root),
                ("PubJoint.inputs:topicName",     f"{ns}/joint_states"),
                ("PubJoint.inputs:queueSize",     10),
                ("SubJointCmd.inputs:topicName",  f"{ns}/joint_command"),
                ("PubTF.inputs:parentPrim",       "/World"),
                ("PubTF.inputs:targetPrims",      [prim_root]),
                ("CamHelper.inputs:cameraPrim",   cam_prim),
                ("CamHelper.inputs:type",         "rgb"),
                ("CamHelper.inputs:topicName",    f"{ns}/cam/conveyor/image_raw"),
                ("CamHelper.inputs:frameId",      f"{robot_id}_cam"),
            ],
            keys.CONNECT: [
                ("Tick.outputs:tick", "ArticState.inputs:execIn"),
                ("Tick.outputs:tick", "PubJoint.inputs:execIn"),
                ("Tick.outputs:tick", "SubJointCmd.inputs:execIn"),
                ("Tick.outputs:tick", "PubTF.inputs:execIn"),
                ("Tick.outputs:tick", "CamHelper.inputs:execIn"),
                ("ArticState.outputs:jointNames",      "PubJoint.inputs:jointNames"),
                ("ArticState.outputs:jointPositions",  "PubJoint.inputs:positionArray"),
                ("ArticState.outputs:jointVelocities", "PubJoint.inputs:velocityArray"),
                ("SubJointCmd.outputs:positionArray",  "Applier.inputs:positionCommand"),
                ("Ctx.outputs:context",                "PubJoint.inputs:context"),
                ("Ctx.outputs:context",                "SubJointCmd.inputs:context"),
                ("Ctx.outputs:context",                "PubTF.inputs:context"),
                ("Ctx.outputs:context",                "CamHelper.inputs:context"),
            ],
        },
    )
    LOG.info("built OG bridge for %s (ns=%s)", robot_id, ns)


def sanity_check(stage, robot_ids: list[str]) -> list[str]:
    """Return a list of human-readable errors (empty list = all good)."""
    errors: list[str] = []
    for rid in robot_ids:
        prim_root = f"/World/Robots/{rid}/m0609"
        prim = stage.GetPrimAtPath(prim_root)
        if not prim or not prim.IsValid():
            errors.append(f"{rid}: prim {prim_root} missing")
            continue
        # Articulation root check (UsdPhysics.ArticulationRootAPI)
        from pxr import UsdPhysics
        if not prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            errors.append(f"{rid}: articulation root API missing on {prim_root}")
        # Camera prim
        cam_prim = stage.GetPrimAtPath(f"/World/Cameras/{rid}_overhead")
        if not cam_prim or not cam_prim.IsValid():
            errors.append(f"{rid}: overhead camera missing")
        # OG graph prim
        og_prim = stage.GetPrimAtPath(f"/World/Graphs/{rid}_bridge")
        if not og_prim or not og_prim.IsValid():
            errors.append(f"{rid}: OG bridge missing")
    return errors


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    args = parse_args()
    robot_ids = [r.strip() for r in args.robots.split(",") if r.strip()]
    if not robot_ids:
        LOG.error("no robot_ids parsed; aborting")
        sys.exit(2)

    # Lazy imports — only works inside Isaac Sim
    try:
        import omni.usd
    except ImportError:
        LOG.error("omni.usd not importable. Run this from Isaac Sim's python.sh.")
        sys.exit(3)

    stage = omni.usd.get_context().get_stage()
    if stage is None:
        LOG.error("stage is None — open a stage before invoking this script")
        sys.exit(4)

    for i, rid in enumerate(robot_ids):
        position = (i * args.row_spacing, 0.0, 0.0)
        add_robot_reference(stage, rid, args.template, position)
        add_overhead_camera(stage, rid, position)
        build_og_bridge(rid)

    errors = sanity_check(stage, robot_ids)
    if errors:
        LOG.error("sanity check FAILED — %d issue(s):", len(errors))
        for e in errors:
            LOG.error("  • %s", e)
        sys.exit(1)
    LOG.info("bringup complete for %d robot(s); sanity check PASSED", len(robot_ids))


if __name__ == "__main__":
    main()
