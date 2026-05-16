# usd-from-urdf.md — URDF/MJCF/OnShape → USD 변환

이 reference는 **로봇 모델을 Isaac Sim 에 올리는 모든 단계**를 다룬다. URDF Importer, MJCF Importer, articulation root 설정, joint drive 튜닝, collision mesh 분리, 그리고 매니퓰레이터별(UR / Franka / Doosan) 함정.

## Contents
1. URDF → USD 의 전체 흐름
2. URDF Importer 사용법 (GUI + Python)
3. Articulation root 결정과 검증
4. Joint drive (P/D) 설정
5. Collision mesh 분리 및 convex decomposition
6. MJCF Importer 차이점
7. OnShape Importer 차이점
8. 매니퓰레이터별 노트 — UR
9. 매니퓰레이터별 노트 — Franka
10. 매니퓰레이터별 노트 — Doosan m0609
11. 임포트 후 sanity check 스크립트
12. 자주 발생하는 임포트 실패

---

## 1. URDF → USD 의 전체 흐름

URDF 는 **`<link>` + `<joint>` + `<material>` + (선택) `<gazebo>`** 정의다. Isaac Sim 의 URDF Importer 는 이를 읽어 다음 USD prim 들을 생성한다:

```
<robot_root>/                    Xform (root)
├── joints/                      Scope (joint definitions)
│   ├── joint1                   PhysicsRevoluteJoint
│   └── joint2                   PhysicsPrismaticJoint
├── link0/                       Xform (base link)
│   ├── visuals/...              Mesh / GeomSubset
│   └── collisions/...           Mesh + PhysicsCollisionAPI
├── link1/                       Xform with PhysicsArticulationRootAPI (자동/수동)
│   └── ...
└── ...
```

**핵심**: 임포트가 끝나면 URDF 는 **참조용일 뿐**, 모든 후속 작업은 USD 위에서 한다 (SKILL.md §Core mental model #2 참조).

원본 가이드: `04-urdf-usd/importer_exporter/`

## 2. URDF Importer 사용법

### GUI

`File → Import` → `.urdf` 선택 → Import 다이얼로그에서:

- **Merge Fixed Joints**: 권장 ON. fixed joint 가 articulation count 를 깎는다.
- **Convex Decomposition**: 복잡한 mesh 면 ON, 박스/실린더면 OFF (느려짐).
- **Self Collision**: 기본 OFF, 충돌 디버깅 필요할 때만 ON.
- **Default Drive Type**: `Position` 권장 (대부분의 실 로봇 컨트롤러가 위치 제어).
- **Default Drive Strength**: 1e7 (위치제어 시 기본 stiffness). 너무 작으면 중력으로 처짐.
- **Default Position Drive Damping**: 1e5.

### Python (재현 가능)

```python
import omni.kit.commands
from isaacsim.asset.importer.urdf import _urdf

cfg = _urdf.ImportConfig()
cfg.merge_fixed_joints = True
cfg.convex_decomp = True
cfg.fix_base = True            # 매니퓰레이터: True, 모바일 베이스: False
cfg.make_default_prim = True
cfg.self_collision = False
cfg.create_physics_scene = True
cfg.import_inertia_tensor = True   # URDF 의 <inertial> 사용
cfg.default_drive_type = _urdf.UrdfJointTargetType.JOINT_DRIVE_POSITION
cfg.default_drive_strength = 1e7
cfg.default_position_drive_damping = 1e5
cfg.distance_scale = 1.0       # URDF 가 m 단위면 1.0

result, prim_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path="/home/me/robot.urdf",
    import_config=cfg,
    dest_path="/home/me/robot.usd",   # 저장 경로
)
print(f"Imported at {prim_path}")
```

`fix_base=True` 누락 → 매니퓰레이터가 중력으로 추락. `import_inertia_tensor=False` → 모든 link inertia 가 자동 계산되어 실 로봇과 다름.

## 3. Articulation root 결정과 검증

USD 의 articulation 은 **단 하나의 prim** 에만 `PhysicsArticulationRootAPI` 가 적용되어야 한다. 이 prim 의 자손에 있는 모든 PhysicsJoint 가 하나의 articulation tree 로 묶인다.

URDF Importer 는 `fix_base=True` 면 base link 위에, `False` 면 root Xform 에 자동 부여한다.

### 검증 (GUI)

`/Robot/base_link` 같은 prim 클릭 → Property panel → `Add` → `Physics → Articulation Root` 가 이미 있어야 함. 없으면 임포터가 root 를 다른 곳에 붙였다는 의미 → 수동으로 추가하고 잘못된 위치는 제거.

### 검증 (Python)

```python
from pxr import UsdPhysics
from isaacsim.core.utils.stage import get_current_stage

stage = get_current_stage()
roots = []
for prim in stage.Traverse():
    if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
        roots.append(prim.GetPath())
assert len(roots) == 1, f"Expected 1 articulation root, got {len(roots)}: {roots}"
print(f"Articulation root: {roots[0]}")
```

**여러 개면 motion 이 비결정적** (마지막에 적용된 게 이긴다). 0개면 robot 이 아예 안 움직인다.

### 모바일 매니퓰레이터 (mobile manipulator)

베이스가 floating + 팔이 articulated 인 경우, articulation root 는 **베이스 위**에 둬야 팔/베이스가 한 트리. 베이스를 floating 으로 두려면:
- `fix_base=False` 로 임포트
- Root 는 base prim 에
- Base 가 wheel 이면 wheel joint 도 articulation 안에

## 4. Joint drive (P/D) 설정

각 joint 에 `PhysicsDriveAPI` 가 붙어 있고, `drive:angular` (revolute) 또는 `drive:linear` (prismatic) 의 attribute 로:

| Attribute | 의미 | 단위 |
|---|---|---|
| `targetPosition` | 목표 위치 | rad / m |
| `targetVelocity` | 목표 속도 | rad/s / m/s |
| `stiffness` | P gain | N·m/rad / N/m |
| `damping` | D gain | N·m·s/rad / N·s/m |
| `maxForce` | 토크 한계 | N·m / N |

**적용 토크 모델** (PhysX 5):
```
τ = stiffness * (targetPosition - currentPosition)
  + damping * (targetVelocity - currentVelocity)
clamped to [-maxForce, +maxForce]
```

### 권장 초기값 (실 로봇 컨트롤러 모방)

```python
from pxr import UsdPhysics

joint = stage.GetPrimAtPath("/Robot/joints/joint1")
drive = UsdPhysics.DriveAPI.Get(joint, "angular")
drive.GetStiffnessAttr().Set(4e6)    # 강한 위치제어
drive.GetDampingAttr().Set(2e5)
drive.GetMaxForceAttr().Set(87.0)    # joint 의 spec
drive.GetTargetPositionAttr().Set(0.0)
```

너무 높으면 진동, 너무 낮으면 중력에 처짐. 실 로봇 datasheet 의 max torque 를 maxForce 로, stiffness/damping 은 PD 튜닝 (`physx-tuning.md` §"Drive 수식과 튜닝" 참조).

### Drive 끄기 (토크 직접 제어)

RL 에서 torque control 하려면:
```python
drive.GetStiffnessAttr().Set(0.0)
drive.GetDampingAttr().Set(0.0)
# 매 스텝마다 articulation_view.set_joint_efforts(...)
```

## 5. Collision mesh 분리 및 convex decomposition

URDF 의 `<visual>` 과 `<collision>` 이 같은 mesh 를 쓰면, 임포터는 visual mesh 를 그대로 collision 에도 쓴다. **3D 스캔된 복잡한 visual mesh 가 collision 으로 쓰이면 PhysX 가 매 contact 마다 수만 개의 폴리곤 검사 → 시뮬레이션이 50ms+ 까지 늘어진다.**

### 자동 convex decomposition

임포트 다이얼로그에서 `Convex Decomposition: ON`. 내부적으로 V-HACD 사용, 메시당 5~30 hulls 로 쪼갠다.

### 수동 (CoACD 권장, 더 좋은 품질)

```bash
# CoACD 설치
pip install coacd

# URDF 의 mesh 를 사전 분해
python3 -c "
import coacd, trimesh
m = trimesh.load('/path/to/visual.obj')
mesh = coacd.Mesh(m.vertices, m.faces)
parts = coacd.run_coacd(mesh, threshold=0.05)
# parts 를 별도 obj 파일로 저장 후 URDF <collision> 에 참조
"
```

URDF:
```xml
<link name="finger">
  <visual>
    <geometry><mesh filename="finger_visual.obj"/></geometry>
  </visual>
  <collision>
    <geometry><mesh filename="finger_collision_decomposed.obj"/></geometry>
  </collision>
</link>
```

### 박스 / 캡슐로 단순화

손가락, 그리퍼 패드처럼 단순한 모양은 `<box>` / `<cylinder>` 로 손코딩이 최선. 폴리곤 0개 검사 → 가장 빠름.

원본: `04-urdf-usd/openusd_tuning_tutorials/`

## 6. MJCF Importer 차이점

MuJoCo 의 `.xml` 을 import. Isaac Lab 의 일부 환경(humanoid 등)이 MJCF 기반.

차이:
- MJCF 는 contact / friction / actuator 가 **로봇 정의 안에** 들어 있음 → 임포트 시 그대로 옮겨짐 (URDF 는 별도 작업)
- `<actuator>` 는 USD 의 `PhysicsDriveAPI` 로 변환
- `<sensor>` 는 변환 안 됨 → Isaac Sim 측 OG 노드로 따로 셋업

```python
import omni.kit.commands
omni.kit.commands.execute(
    "MJCFCreateAsset",
    mjcf_path="/path/to/humanoid.xml",
    import_config=...,  # MJCFImportConfig
    dest_path="/path/to/humanoid.usd",
)
```

## 7. OnShape Importer 차이점

OnShape (CAD) 에서 직접 import. URDF 단계 없이 곧장 USD. 산업용 매니퓰레이터 CAD 가 OnShape 에 있을 때만 가치 있음.

`Window → Extensions → onshape.importer` enable. API key 필요.

## 8. 매니퓰레이터별 노트 — Universal Robots (UR5, UR10, UR16e)

**소스**: `10-gap-fills/manipulators/ur/Universal_Robots_ROS2_Description/`

함정:
- UR 의 공식 URDF 는 `xacro` 매크로 → 먼저 펼쳐야 함:
  ```bash
  ros2 run xacro xacro \
    Universal_Robots_ROS2_Description/urdf/ur.urdf.xacro \
    name:=ur5 ur_type:=ur5 > ur5_expanded.urdf
  ```
- joint limit 이 `<safety_controller>` 태그로 들어 있어 임포터가 무시 → URDF 의 `<limit>` 만 사용. 안전 마진 별도 적용.
- visual mesh 가 `dae` (Collada) → Isaac Sim 6.0 부터 자동 변환되지만 5.x 면 obj 로 사전 변환 필요.
- TCP frame 이 URDF 에 없음 → 임포트 후 USD 에서 `tool0` 자식으로 빈 Xform 추가.

권장 drive:
- `stiffness=1e7`, `damping=1e5`, `maxForce=150` (어깨), `87` (팔꿈치), `40` (손목).

## 9. 매니퓰레이터별 노트 — Franka Panda / FR3

**소스**: `10-gap-fills/manipulators/franka/franka_ros2/`, `09-github-repos/IsaacLab/source/isaaclab_assets/isaaclab_assets/` (Franka config)

가장 잘 지원되는 로봇. Isaac Lab 기본 매니퓰레이터.

함정:
- Panda 와 FR3 는 인터페이스 같지만 spec 다름 (FR3 는 페이로드/속도 ↑) → URDF 분리 필수.
- 그리퍼는 별도 articulation 으로 관리해도 됨 (open/close 만 쓰면).
- `franka_description` 의 visual mesh 는 사이즈 큼 → 게임용 LOD 가 아니므로 RTX-Real-Time 에서 무겁다.

권장 drive:
- 7 joints: `stiffness=400, damping=80` (URDF 기본을 그대로 사용해도 됨, Isaac Lab 의 `FRANKA_PANDA_CFG` 참조).

## 10. 매니퓰레이터별 노트 — Doosan m0609

**소스**: `10-gap-fills/manipulators/doosan/doosan-robot2/dsr_description2/`

NVIDIA 공식 USD 라이브러리에 m0609 가 **없다**. 직접 import 해야 함.

```bash
# 1. xacro 펼침
cd ~/cobot_ws/src/doosan-robot2/dsr_description2/xacro
ros2 run xacro xacro m0609.urdf.xacro > /tmp/m0609.urdf

# 2. mesh 경로를 절대경로로 변환 (URDF Importer 가 package:// 못 풀음)
sed -i 's|package://dsr_description2|/home/hoon/cobot_ws/install/dsr_description2/share/dsr_description2|g' /tmp/m0609.urdf

# 3. Isaac Sim 에서 import (GUI or Python — §2 참조)
```

함정:
- `dsr_description2` 의 mesh 는 `.dae` + 텍스처. 임포트 후 텍스처 경로가 깨지면 USD 에서 `material:binding` 직접 수정.
- m0609 의 joint 1, 2, 3 은 가장 강하고 (`maxForce=200+`), 4, 5, 6 은 약함 (`maxForce=50` 정도). 같은 stiffness 쓰면 손목이 진동.
- TCP / tool flange frame: URDF 에 `tool0` 으로 정의되어 있음. m0609 는 사용자가 add_tcp 로 정의한 TCP 가 따로 있는데 (vendor SDK), USD 에는 자동 반영 안 됨 → 시뮬에서도 같은 변환을 수동 적용해야 sim/real 일치.
- **두산의 dsr_controller2 와 함께 쓰려면** vendor 측 mode 가 `virtual` (시뮬레이션 모드) 여야 한다. 자세한 건 `doosan-robotics` 스킬의 `references/launch-and-modes.md` 참조.

호출 사이드의 ROS 토픽/서비스 이름은 두산 스킬과 동일해야 함 (`/dsr01/joint_states` 등). USD 임포트 시 link 이름이 두산 표준과 일치하는지 확인 (`base_0`, `link1`, ..., `link6`, `tool0`).

## 11. 임포트 후 sanity check 스크립트

`scripts/urdf_to_usd_check.py` 가 이 스킬에 포함되어 있다. 사용:

```bash
~/.local/share/ov/pkg/isaac-sim-6.0.0/python.sh \
  ~/.claude/skills/isaac-sim-bridge/scripts/urdf_to_usd_check.py \
  /path/to/robot.usd
```

검사 항목:
1. articulation root prim 정확히 1개
2. 모든 PhysicsJoint 가 articulation 안에 있음
3. 모든 link 의 mass > 0
4. visual / collision mesh 폴리곤 비율 (collision 이 visual 의 1/10 이하 권장)
5. drive stiffness/damping 이 0 이 아닌 joint 개수

실패 항목이 있으면 구체적 prim path 를 출력.

## 12. 자주 발생하는 임포트 실패

| 증상 | 원인 | 해결 |
|---|---|---|
| 임포트 후 robot 이 무한 추락 | `fix_base=False` + 매니퓰레이터 | `fix_base=True` 재임포트 |
| 임포트는 됐는데 안 움직임 | articulation root 0개 또는 위치 잘못 | §3 검증 |
| Drive 가 안 먹음 | DriveAPI 가 angular/linear 잘못 | revolute → "angular", prismatic → "linear" |
| 일부 joint 만 응답 | 그 joint 가 articulation tree 밖 | 모두 같은 root 자손인지 확인 |
| collision 이 visual 보다 큼 | convex hull 이 mesh 를 둘러싸도록 | 수동 `<collision>` 정의 |
| import 시 segfault | URDF 의 mesh 경로 못 찾음 | 절대경로로 변환 (§10 의 sed) |
| joint limit 이 무시됨 | URDF `<limit>` 누락 | URDF 에 `<limit lower="..." upper="..." effort="..." velocity="..."/>` 명시 |
| material 색이 회색 | `.dae` 텍스처 경로 깨짐 | USD 에서 `material:binding` 수정 또는 mesh 를 `.usd` 로 사전 변환 |
| 임포트 후 GUI 가 멈춤 | mesh 폴리곤 수 100만+ | Decimate (Blender) 후 재임포트 |
| 두 번째 임포트 시 prim 충돌 | 같은 prim path 에 덮어쓰기 | dest_path 를 다르게 또는 기존 stage 비우기 |

## 13. m0609 + RG2 결합 USD 만들기 (warehouse 시나리오)

warehouse 컨베이어 분류 시나리오 (`warehouse-sorting-pipeline.md`) 는 m0609 팔과 OnRobot RG2 그리퍼를 합친 단일 USD asset 을 N대 인스턴스화. 결합 절차:

### 13.1 원본 URDF 확보

- m0609 URDF: 자료실 `/home/hoon/isaac-sim-skill-research/10-gap-fills/manipulators/doosan/doosan-robot2/dsr_description2/urdf/m0609.urdf.xacro` 또는 `~/cobot_ws/src/doosan-robot2/...` 의 동일 파일
- RG2 URDF: `/home/hoon/isaac-sim-skill-research/11-warehouse-sorting/rg2-gripper/onrobot_community/` 또는 `ros2_robotiq_gripper/` 의 mimic-joint URDF

### 13.2 결합 (xacro 또는 URDF concat)

가장 단순한 방법은 m0609 의 마지막 link (`link6` 또는 `tcp`) 에 `fixed joint` 로 RG2 base 를 붙이는 wrapper xacro:

```xml
<?xml version="1.0"?>
<robot name="m0609_rg2" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:include filename="$(find dsr_description2)/urdf/m0609.urdf.xacro"/>
  <xacro:include filename="$(find rg2_description)/urdf/rg2.urdf.xacro"/>

  <xacro:m0609 prefix=""/>
  <xacro:rg2 prefix="rg2_"/>

  <joint name="m0609_to_rg2" type="fixed">
    <parent link="link6"/>
    <child  link="rg2_base"/>
    <origin xyz="0 0 0.030" rpy="0 0 0"/>   <!-- 30mm flange offset, 모델에 맞춰 조정 -->
  </joint>
</robot>
```

xacro → URDF:

```bash
ros2 run xacro xacro m0609_rg2.urdf.xacro -o m0609_rg2.urdf
```

### 13.3 URDF Importer 로 변환

§2 의 Python 패턴 그대로. 핵심 옵션:

```python
from omni.importer.urdf import _urdf

cfg = _urdf.ImportConfig()
cfg.merge_fixed_joints = False             # rg2 mimic joint 보존
cfg.import_inertia_tensor = True
cfg.fix_base = False                       # 베이스는 world 와 fixed joint 로 별도 묶음
cfg.self_collision = False                 # RG2 mimic joint 가 self_collision 으로 false alarm 다발
cfg.distance_scale = 1.0                   # URDF 가 meter 단위라 가정
cfg.density = 0.0                          # URDF inertia 사용
_, stage_path = _urdf.create_from_urdf(
    "m0609_rg2.urdf", dest_path="/World/Robots/template/m0609_rg2", config=cfg)
```

`merge_fixed_joints=False` 가 중요 — True 면 RG2 의 `rg2_base→rg2_finger_link1` 등 fixed/mimic 구조가 손실됨.

### 13.4 Mimic joint 처리

RG2 의 두 finger 는 한 actuator 로 mirroring. URDF `<mimic joint="rg2_finger_joint1" multiplier="1.0" offset="0.0"/>` 가 있어도 Isaac Sim 의 URDF importer 는 mimic 을 직접 따르지 않는다. 후처리:

```python
from pxr import UsdPhysics
finger2 = stage.GetPrimAtPath("/World/Robots/template/m0609_rg2/joints/rg2_finger_joint2")
# Drive 를 끄고, 별도 OG 노드 또는 Python script 가 finger1 의 position 을 읽어 finger2 에 mirror 적용
UsdPhysics.DriveAPI.Get(finger2, "linear").GetTargetPositionAttr().Set(0.0)
# 또는 PhysxArticulationAPI 의 mimic constraint (Isaac Sim 6.x 가 일부 지원)
```

대안: gripper command 가 들어오면 OG 의 JointCommand 가 두 finger 모두 같은 target 으로 publish — 가장 단순.

### 13.5 Articulation root 검증

§3 의 검증을 그대로 적용:
- articulation root 는 m0609 base (`base_0` 또는 `link0`) 에만 1개
- RG2 base 는 child link 로만 존재, 별도 articulation 아님
- `scripts/urdf_to_usd_check.py` 가 자동으로 검사

### 13.6 TCP 정의

m0609 의 마지막 link 가 아닌 RG2 의 두 finger 중간점을 TCP 로 정의해야 정확한 grasp pose 계산 가능:

```python
from pxr import UsdGeom, Gf
tcp_path = "/World/Robots/template/m0609_rg2/rg2_tcp"
xform = UsdGeom.Xform.Define(stage, tcp_path)
# rg2_base 기준 z=+0.14, y=0, x=0 (모델에 맞춰)
xform.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.14))
# 부모를 rg2_base 로
```

`sort-decision-logic.md §3` 의 grasp pose 계산이 이 TCP 를 활용.

### 13.7 저장 (재사용용)

```python
stage.Export("robots/m0609_rg2.usda", args={"format": "usda"})
```

`.usda` (text) 로 저장 — `warehouse-sorting-pipeline.md §2` 가 reference 로 가져갈 1차 자산.

### 13.8 자주 발생하는 함정

| 증상 | 원인 | 처방 |
|---|---|---|
| Gripper 가 안 닫힘 | mimic joint 미설정 + 단일 finger 만 command | OG 가 두 finger 동시에 publish 또는 §13.4 의 constraint |
| Gripper 가 닫혀도 객체 안 잡힘 | finger 의 surface 마찰 너무 낮음 | `PhysxMaterial:dynamicFriction`/`staticFriction` 0.9+ |
| 팔이 진동 | RG2 의 finger collision 이 self-collision 으로 잡힘 | `self_collision=False` 또는 finger pair 만 disable |
| TCP 가 wrong 위치 | flange offset (`m0609_to_rg2` joint origin) 부정확 | RG2 datasheet 의 base→TCP 길이로 보정 |

## See also

- `physx-tuning.md` §"Drive 수식과 튜닝" — drive gain 의 수학과 안정성
- `omnigraph-ros-bridge.md` §"JointState 퍼블리시" — 임포트한 robot 을 ROS 로 노출
- `isaaclab-rl.md` §"Asset 등록" — USD 를 Isaac Lab env 에 연결
- `warehouse-sorting-pipeline.md §2` — 결합한 USD 를 N대로 인스턴스화
- `sort-decision-logic.md §3` — TCP 기준 grasp pose
- `doosan-robotics` 스킬: `references/launch-and-modes.md` — m0609 mode 와 TCP 정의
- 원문: `04-urdf-usd/robot_setup/`, `04-urdf-usd/importer_exporter/`, `10-gap-fills/manipulators/doosan/`, `11-warehouse-sorting/rg2-gripper/`

---

## §M0609-PAYLOAD — 매니퓰레이터를 다른 로봇에 페이로드로 결합 (GP)

m0609(또는 임의 팔)을 4족 등 베이스 로봇에 얹어 운반시키는 패턴.
대표 사용처: gp-quadruped (ANYmal-C 등에 m0609 결합). 보행 정책과의
상호작용은 [[gp-quadruped]] `locomotion-policy.md`, m0609 조인트/리미트는
`doosan-robotics` `sim-integration.md` 위임.

**1. URDF→USD**: `m0609_isaac_sim.urdf`
(links `base,base_link,link_1..link_6,tool0`; joints `joint_1..joint_6`)
→ `/World/Robot/m0609`. fixed base, position drive, self-collision off,
collider convexHull (이 reference 상단 일반 절차 동일).

**2. 베이스 결합 (fixed joint)**: m0609 `base_link` ↔ 베이스 로봇 link 사이
`UsdPhysics.FixedJoint`(body0=베이스 로봇 마운트 link, body1=m0609
base_link). 베이스 로봇은 자기 articulation(보행 정책), m0609 은 자기
articulation(position drive)을 유지하고 fixed joint 로만 연결.

**3. CoM 외란 완화 (근본 대응, 우회 금지)**: 팔을 얹으면 베이스 CoM 이
이동해 보행 정책이 불안정해질 수 있다. 항상 3종 동반:
- (a) m0609 각 링크 mass 를 페이로드 수준으로 스케일(관성텐서 동반 조정)
- (b) 보행 중 6축을 **stow 자세**로 position drive hold(동적 토크 외란 제거)
- (c) 그래도 불안정 시 페이로드 포함 정책 재학습(Isaac Lab) — 명시적 단계
땜질(키프레임 보정 등) 금지. stow posj 값/리미트는 `doosan-robotics`
`sim-integration.md`.

**4. 센서 플랜지 부착**: RealSense 등은 `link_6`(플랜지) 자식 prim 으로.
OG 발행은 `omnigraph-ros-bridge.md` §REALSENSE-DSR01.

함정: 두 articulation 을 fixed 로 잇기 → articulation root/조인트 트리
충돌 주의(베이스 로봇 articulation 에 m0609 를 흡수시키지 말 것). 결합 후
베이스 보행 안정성 반드시 재검증(넘어짐 테스트).
