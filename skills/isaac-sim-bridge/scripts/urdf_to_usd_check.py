#!/usr/bin/env python3
"""urdf_to_usd_check.py — URDF→USD 임포트 후 sanity check.

usd-from-urdf.md §11 참조. Isaac Sim 의 bundled python.sh 로 실행:

    ~/.local/share/ov/pkg/isaac-sim-*/python.sh urdf_to_usd_check.py /path/to/robot.usd

검사 항목:
  1. PhysicsArticulationRootAPI 가 정확히 1개의 prim 에만 적용되어 있는가
  2. 모든 PhysicsJoint 가 articulation root 의 자손인가
  3. 모든 link (Xform) 의 mass > 0 인가
  4. visual mesh 대비 collision mesh 의 폴리곤 비율이 1:10 이하인가
  5. drive (stiffness/damping) 가 0 이 아닌 joint 개수
  6. joint limit 이 정의된 joint 개수

실패 항목이 있으면 exit code 1.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main(usd_path: str) -> int:
    # Isaac Sim 의 SimulationApp 부팅 후에만 USD API 접근 가능
    from isaacsim import SimulationApp

    app = SimulationApp({"headless": True})

    try:
        from pxr import Usd, UsdGeom, UsdPhysics

        stage = Usd.Stage.Open(usd_path)
        if not stage:
            print(f"[FAIL] Cannot open USD at {usd_path}", file=sys.stderr)
            return 1

        # 1. Articulation root count
        roots = []
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
                roots.append(prim.GetPath())
        if len(roots) == 0:
            print("[FAIL] No PhysicsArticulationRootAPI found — robot will not move")
            return 1
        if len(roots) > 1:
            print(f"[FAIL] Expected 1 articulation root, got {len(roots)}: {roots}")
            return 1
        root_path = roots[0]
        print(f"[OK ] Articulation root: {root_path}")

        # 2. Every PhysicsJoint inside the articulation root subtree
        all_joints = []
        orphan_joints = []
        for prim in stage.Traverse():
            if prim.IsA(UsdPhysics.Joint):
                all_joints.append(prim.GetPath())
                if not str(prim.GetPath()).startswith(str(root_path)):
                    orphan_joints.append(prim.GetPath())
        if orphan_joints:
            print(f"[FAIL] {len(orphan_joints)} joints outside articulation root:")
            for p in orphan_joints[:5]:
                print(f"       {p}")
            return 1
        print(f"[OK ] {len(all_joints)} joints, all under articulation root")

        # 3. Link mass > 0
        zero_mass_links = []
        link_count = 0
        for prim in stage.Traverse():
            if prim.HasAPI(UsdPhysics.MassAPI):
                link_count += 1
                mass_attr = prim.GetAttribute("physics:mass")
                if mass_attr and mass_attr.HasValue():
                    m = mass_attr.Get()
                    if m is not None and m <= 0:
                        zero_mass_links.append((prim.GetPath(), m))
        if zero_mass_links:
            print(f"[FAIL] {len(zero_mass_links)} links with mass <= 0:")
            for path, m in zero_mass_links[:5]:
                print(f"       {path}: mass={m}")
            return 1
        print(f"[OK ] {link_count} links, all with mass > 0")

        # 4. Visual vs collision mesh polygon ratio
        visual_faces = 0
        collision_faces = 0
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                face_count_attr = prim.GetAttribute("faceVertexCounts")
                if face_count_attr and face_count_attr.HasValue():
                    n_faces = len(face_count_attr.Get())
                    if prim.HasAPI(UsdPhysics.CollisionAPI):
                        collision_faces += n_faces
                    else:
                        visual_faces += n_faces
        if collision_faces > 0:
            ratio = collision_faces / max(visual_faces, 1)
            verdict = "[OK ]" if ratio <= 0.1 else "[WARN]"
            print(
                f"{verdict} Collision/visual mesh face ratio: "
                f"{collision_faces}/{visual_faces} = {ratio:.3f}"
            )
            if ratio > 0.1:
                print("       Consider convex decomposition (V-HACD / CoACD)")
        else:
            print("[WARN] No collision meshes detected — robot may not collide")

        # 5. Drive count
        drives_enabled = 0
        zero_drives = 0
        for joint_path in all_joints:
            prim = stage.GetPrimAtPath(joint_path)
            for axis in ("angular", "linear"):
                drive = UsdPhysics.DriveAPI.Get(prim, axis)
                if drive:
                    stiff = drive.GetStiffnessAttr().Get() or 0.0
                    damp = drive.GetDampingAttr().Get() or 0.0
                    if stiff > 0 or damp > 0:
                        drives_enabled += 1
                    else:
                        zero_drives += 1
        print(
            f"[OK ] Drives enabled: {drives_enabled}, "
            f"zero stiffness/damping: {zero_drives}"
        )
        if zero_drives > 0:
            print("       (zero-drive joints will not respond to position commands)")

        # 6. Joint limit count
        limited = 0
        unlimited = 0
        for joint_path in all_joints:
            prim = stage.GetPrimAtPath(joint_path)
            joint = UsdPhysics.Joint(prim)
            lower = joint.GetLowerLimitAttr().Get() if joint.GetLowerLimitAttr() else None
            upper = joint.GetUpperLimitAttr().Get() if joint.GetUpperLimitAttr() else None
            if lower is not None and upper is not None and lower < upper:
                limited += 1
            else:
                unlimited += 1
        print(f"[OK ] Joints with limits: {limited}, unlimited: {unlimited}")
        if unlimited > 0:
            print("       (unlimited joints may rotate infinitely under drive)")

        print()
        print("All checks passed.")
        return 0

    finally:
        app.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: urdf_to_usd_check.py <path/to/robot.usd>", file=sys.stderr)
        sys.exit(2)
    usd_path = sys.argv[1]
    if not Path(usd_path).exists():
        print(f"File not found: {usd_path}", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(usd_path))
