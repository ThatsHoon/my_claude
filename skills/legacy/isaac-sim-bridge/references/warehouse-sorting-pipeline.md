# Warehouse Conveyor Sorting Pipeline

**1문장 요지** — Isaac Sim 안에 다중(2~4대) m0609+RG2 로봇팔, 컨베이어, bin, spawn zone, RGB 카메라를 갖춘 warehouse 씬을 USD layer 로 구성하고, 각 로봇이 컨베이어 위 물체를 분류·이송하도록 namespace 분리된 ROS 2 인터페이스로 묶는 패턴을 정의한다.

> 이 파일은 시나리오의 **상위 아키텍처**를 다룬다. YOLO 추론은 `yolo-perception.md`, 의사결정/모션은 `sort-decision-logic.md`, 외부 통신은 `server-bridge.md`, 텔레메트리 적재는 `telemetry-supabase.md` 로 위임. URDF→USD 변환의 m0609+RG2 결합 세부는 `usd-from-urdf.md §m0609+RG2`.

---

## Contents

1. 시나리오 개요
2. USD 씬 컴포지션 (layer 전략)
3. 다중 로봇 namespacing 규약
4. OmniGraph 팩토리 패턴 (per-robot bringup)
5. 컨베이어 모델링 — kinematic vs animated rigid body
6. Spawn zone — Replicator 로 객체 흘려보내기
7. 충돌 zone 과 안전 영역
8. 병렬 운영 시 GPU/CPU 예산
9. 단계별 셋업 체크리스트
10. 안티패턴
11. 교차 참조

---

## 1. 시나리오 개요

```
              ┌──────────────────────────── Warehouse USD ────────────────────────────┐
              │                                                                        │
              │      [Spawn Zone]   ──→   [Conveyor Belt]   ──→   [End Buffer]        │
              │                                                                        │
              │                    [Camera r0]   [Camera r1]                          │
              │                        ▼               ▼                              │
              │      ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐            │
              │      │ Robot  │    │ Robot  │    │ Robot  │    │ Robot  │            │
              │      │  r0    │    │  r1    │    │  r2    │    │  r3    │  (선택)    │
              │      │ m0609  │    │ m0609  │    │ m0609  │    │ m0609  │            │
              │      │ + RG2  │    │ + RG2  │    │ + RG2  │    │ + RG2  │            │
              │      └────────┘    └────────┘    └────────┘    └────────┘            │
              │           │             │             │             │                 │
              │      [Bins r0]    [Bins r1]      [Bins r2]    [Bins r3]              │
              │                                                                        │
              └────────────────────────────────────────────────────────────────────────┘
```

- 컨베이어 양옆에 m0609 가 마주보거나 같은 쪽에 일렬로 배치 (zone 분할 방식에 따라).
- 각 로봇은 **고유 conveyor zone** 을 책임 — 같은 물체에 두 로봇이 동시에 손을 뻗는 상황을 시간/공간 분할로 회피.
- 카메라는 conveyor-수준 1대 또는 robot-수준 N대. zone 분할 시 robot 별 overhead RGB(+depth) 권장.
- 의사결정은 **hand-coded class→bin 매핑**. RL/IL 없음. cuMotion 또는 MoveIt2 로 plan.

> 이 시나리오는 **시뮬 우선** — 실기 m0609 에 옮기는 sim2real 은 별도 reference 자리. 다만 motion command/state topic 계약을 `dsr_controller2` 와 호환되게 유지해 swap 만으로 전환 가능하도록 둔다.

---

## 2. USD 씬 컴포지션 (layer 전략)

USD 의 핵심은 **여러 레이어를 composition arc 로 합성**하는 것. warehouse 씬도 단일 `.usd` 한 장에 모든 prim 을 박으면 안 되고, 다음과 같이 분리한다.

```
warehouse_main.usda                ← 루트 stage
├── (sublayer) layouts/floor.usda          → 바닥, 벽, 조명
├── (sublayer) layouts/conveyor.usda       → 컨베이어 articulation
├── (sublayer) layouts/bins.usda           → 분류함 prim 들
├── (reference) robots/m0609_rg2.usda      → 로봇 1대 (Variant 로 RG2 on/off)
│     └── 인스턴스 4개를 /World/Robots/r0..r3 로 배치
└── (sublayer) sensors/cameras.usda        → conveyor 상부 카메라
```

레이어 분리의 실익:
- **변경 단위 축소**: 로봇만 교체할 때 `robots/m0609_rg2.usda` 만 수정. 충돌 형상을 재계산해도 conveyor 는 무관.
- **버전 관리 친화**: `.usda` (텍스트) 로 둔 layer 는 git diff 가 의미 있게 보임.
- **인스턴싱**: 같은 m0609 USD 를 4번 reference 하면 mesh/material 은 1번만 로드되고 transform/joint state 만 4벌. 메모리 절약.

### 권장 prim path 규약

```
/World
  /Robots
    /r0   (Xform; references robots/m0609_rg2.usda)
      /m0609         (articulation root)
      /rg2           (articulation child)
    /r1, /r2, /r3
  /Conveyor
    /belt            (animated kinematic body)
    /surface_xform
  /Bins
    /r0_bin_red
    /r0_bin_blue
    ...
  /Cameras
    /r0_overhead
    /r1_overhead
    ...
  /SpawnZone
    /trigger_volume
```

이 path 들은 **OmniGraph 노드가 직접 가리키는 키**이기도 하다. 한 번 정한 뒤로는 절대 바꾸지 말 것 — 바꾸려면 OG 그래프와 launch 파라미터까지 모두 갱신.

---

## 3. 다중 로봇 namespacing 규약

ROS 2 측 namespace 와 USD prim path 는 **일대일 대응**되도록 정한다. 그래야 코드가 `robot_id = "r2"` 하나만 알면 prim path 도, ROS topic 도, supabase row 도 모두 인덱싱할 수 있다.

| 항목 | 규약 | 예시 |
|---|---|---|
| `robot_id` | `r{N}` (N=0,1,2,3) | `r0` |
| USD prim path | `/World/Robots/{robot_id}/m0609` | `/World/Robots/r0/m0609` |
| ROS namespace | `/{robot_id}` | `/r0` |
| Topic prefix | `/{robot_id}/...` | `/r0/joint_states` |
| Joint name | `{robot_id}_joint{1..6}` | `r0_joint1` (옵션, prefix-aware controller 일 때) |
| Supabase row | `robots.robot_id = '{robot_id}'` | `'r0'` |

### ROS_DOMAIN_ID 분리 vs 단일 도메인 + namespace

| 방식 | 장점 | 단점 | 권장 시나리오 |
|---|---|---|---|
| **단일 도메인 + namespace** (권장) | 모든 로봇이 한 도메인 → `ros2 topic list` 로 전체 가시화, server 가 토픽 하나만 받으면 됨 | 토픽 수가 N배로 증가, DDS discovery 부담 증가 | 본 시나리오 (서버가 모든 로봇 상태를 한꺼번에 조회해야 함) |
| **ROS_DOMAIN_ID 분리** | DDS discovery 완전 분리, 한 로봇의 멀티캐스트가 다른 로봇에 영향 안 줌 | 서버가 도메인 별 노드를 띄워야 하고 도메인 간 브리지가 별도 필요 | 로봇 간 완전 격리 + 서버 측 게이트웨이가 명시적으로 합치는 구조 |

본 스킬은 **단일 도메인 + namespace** 를 1차 권장. doosan-robotics `multi-robot-and-quirks.md` 의 패턴과 일관됨. 단 DDS partition 으로 sub-그룹화는 가능하니 필요 시 거기 참고.

```bash
# 셋업 예 — 4대 모두 ROS_DOMAIN_ID=42 공유
export ROS_DOMAIN_ID=42
# Isaac Sim 도, server bridge 도, 같은 도메인에서 띄움.
```

ros2-architect `references/communication.md §QoS 와 namespace` 와 교차참조.

---

## 4. OmniGraph 팩토리 패턴 (per-robot bringup)

같은 OG 템플릿을 N 대 로봇에 namespace 만 바꿔 인스턴스화한다. 사람이 GUI 에서 4번 클릭하지 말 것 — Python 으로 짠다.

```python
# scripts/multi_robot_bringup.py (요지)
import omni.graph.core as og
from omni.isaac.core.utils.stage import open_stage
from pxr import UsdGeom, Sdf

ROBOT_IDS = ["r0", "r1", "r2", "r3"]
TEMPLATE_USD = "robots/m0609_rg2.usda"


def add_robot_reference(stage, robot_id: str, base_pose):
    """USD reference 로 m0609+RG2 를 /World/Robots/{robot_id} 에 추가."""
    parent = "/World/Robots"
    xform_path = f"{parent}/{robot_id}"
    UsdGeom.Xform.Define(stage, xform_path)
    prim = stage.GetPrimAtPath(xform_path)
    prim.GetReferences().AddReference(TEMPLATE_USD)
    UsdGeom.Xformable(prim).AddTranslateOp().Set(base_pose)


def build_og_for_robot(robot_id: str):
    """Articulation, JointState, ROS bridge 노드를 동일 namespace 로 묶어 생성."""
    ns = f"/{robot_id}"
    keys = og.Controller.Keys
    og.Controller.edit(
        {"graph_path": f"/World/Graphs/{robot_id}_bridge", "evaluator_name": "execution"},
        {
            keys.CREATE_NODES: [
                ("Tick",            "omni.graph.action.OnPlaybackTick"),
                ("Context",         "omni.isaac.ros2_bridge.ROS2Context"),
                ("ArticState",      "omni.isaac.core_nodes.IsaacArticulationState"),
                ("PubJointState",   "omni.isaac.ros2_bridge.ROS2PublishJointState"),
                ("SubJointCmd",     "omni.isaac.ros2_bridge.ROS2SubscribeJointState"),
                ("ApplyArtic",      "omni.isaac.core_nodes.IsaacArticulationController"),
            ],
            keys.CONNECT: [
                ("Tick.outputs:tick",                "ArticState.inputs:execIn"),
                ("Tick.outputs:tick",                "PubJointState.inputs:execIn"),
                ("Tick.outputs:tick",                "SubJointCmd.inputs:execIn"),
                ("ArticState.outputs:jointNames",    "PubJointState.inputs:jointNames"),
                ("ArticState.outputs:jointPositions","PubJointState.inputs:positionArray"),
                ("SubJointCmd.outputs:positionArray","ApplyArtic.inputs:positionCommand"),
                ("Context.outputs:context",          "PubJointState.inputs:context"),
                ("Context.outputs:context",          "SubJointCmd.inputs:context"),
            ],
            keys.SET_VALUES: [
                ("ArticState.inputs:targetPrim",     f"/World/Robots/{robot_id}/m0609"),
                ("ApplyArtic.inputs:targetPrim",     f"/World/Robots/{robot_id}/m0609"),
                ("PubJointState.inputs:topicName",   f"{ns}/joint_states"),
                ("SubJointCmd.inputs:topicName",     f"{ns}/joint_command"),
                ("PubJointState.inputs:queueSize",   10),
            ],
        },
    )

# 메인 부트스트랩
for i, rid in enumerate(ROBOT_IDS):
    add_robot_reference(stage, rid, base_pose=(i * 1.5, 0, 0))
    build_og_for_robot(rid)
```

**중요**:
- `targetPrim` 은 `/World/Robots/{robot_id}/m0609` 만 가리킨다 — RG2 는 articulation child 로 자동 합류.
- `topicName` 은 항상 `/{robot_id}/...` prefix 로 출발. server bridge 가 prefix 만 보고 라우팅 가능.
- QoS 는 OG 노드 dropdown 으로 통일(`SystemDefaultsQoS` 또는 `SensorDataQoS`). ros2-architect `communication.md §QoS` 와 일치시킴.

검증: `scripts/check_namespace_isolation.py` 를 부트 후 1회 실행하여 토픽 충돌이 없는지 확인.

---

## 5. 컨베이어 모델링 — kinematic vs animated rigid body

| 방식 | 동작 | 장점 | 단점 |
|---|---|---|---|
| **Kinematic body + surface velocity** (1차 권장) | 컨베이어 표면 prim 에 `physxRigidBody:kinematicEnabled = True` + `physxMaterial:surfaceVelocity = (vx, 0, 0)` | 물리 안정, FPS 부담 최소, 위 물체가 마찰로 운반됨 | 정확한 위치 추정은 surface velocity × dt 로만 가능 |
| Animated rigid body (벨트 메쉬 자체 이동) | 메쉬 prim 에 keyframe / `omni.physx.scripts.physicsUtils.set_translate` 로 매 frame 이동 후 wrap-around | 시각적으로 가장 정확 | 매 frame 메쉬 transform 갱신 비용, mesh 길이 한계 |
| Conveyor Belt extension | NVIDIA 가 제공하는 omniverse extension (Isaac Sim 4.5+ 에서 가용) | 셋업 1줄 | extension 버전 의존, 커스터마이즈 시 우회 필요 |

권장 셋업 (kinematic + surface velocity):

```python
from pxr import UsdPhysics, PhysxSchema, Gf

belt_path = "/World/Conveyor/belt"
prim = stage.GetPrimAtPath(belt_path)
UsdPhysics.RigidBodyAPI.Apply(prim)
UsdPhysics.RigidBodyAPI(prim).CreateKinematicEnabledAttr().Set(True)

mat_api = PhysxSchema.PhysxMaterialAPI.Apply(prim)
mat_api.CreateSurfaceVelocityAttr().Set(Gf.Vec3f(0.3, 0, 0))   # 0.3 m/s along +X
mat_api.CreateDynamicFrictionAttr().Set(0.8)
mat_api.CreateStaticFrictionAttr().Set(0.9)
```

- 마찰을 너무 낮추면 물체가 미끄러져 분류 zone 진입 전에 zone 을 벗어남.
- 너무 높이면 robot 이 물체를 잡고 들었을 때 컨베이어가 물체를 끌어내려는 효과 (현실과 같지만 시뮬레이션 instability 의 원인).
- 권장 시작점: dynamic=0.7, static=0.8, surface velocity 0.2~0.4 m/s.

PhysX 솔버 파라미터는 `physx-tuning.md §Solver` 참조. 컨베이어 위에 가벼운 객체(0.05~0.5kg) 가 다수 있을 때 contact iterations 를 6 이상 권장.

---

## 6. Spawn zone — Replicator 로 객체 흘려보내기

컨베이어 진입 zone 에서 일정 주기로 객체를 spawn. Replicator 의 `with rep.trigger.on_time(...)` 또는 `omni.kit.script_editor` 에서 callback 으로 구현.

```python
import omni.replicator.core as rep

CLASS_USDS = {
    "box_red":  "assets/box_red.usda",
    "box_blue": "assets/box_blue.usda",
    "can_a":    "assets/can_a.usda",
    "reject":   "assets/scrap.usda",
}

with rep.new_layer():
    with rep.trigger.on_time(interval=2.0):              # every 2 s
        cls = rep.distribution.choice(list(CLASS_USDS.keys()))
        rep.create.from_usd(
            CLASS_USDS[cls],
            position=rep.distribution.uniform((-0.10, 1.0, 0.05), (0.10, 1.0, 0.05)),
            rotation=rep.distribution.uniform((0,0,0), (0,360,360)),
            semantics=[("class", cls)],
        )
```

- `semantics` 는 Replicator 의 라벨 시스템 — 이걸 활용하면 YOLO 학습 데이터 라이터(`replicator-sdg.md §컨베이어+YOLO`) 가 자동으로 COCO 라벨에 매핑한다.
- spawn 위치를 컨베이어 표면 바로 위 ~5cm 로 둬서 떨어뜨리는 효과로 자연스럽게 컨베이어에 안착.
- spawn 이벤트는 OG 의 `omni.replicator.core.OgnOnFrame` 콜백에서 ROS 토픽 `/conveyor/spawn` 으로 publish (id, class, ts, world_pose). 텔레메트리 시 detection ↔ ground truth 매칭에 쓰임.

---

## 7. 충돌 zone 과 안전 영역

PhysX contact reporter 로 다음 충돌을 별도 분류해 publish:

| 종류 | 의미 | 처리 |
|---|---|---|
| `gripper-object` | 정상 grasp 시도 | success 로 간주, telemetry 에 grasp 이벤트로 남김 |
| `arm_link-conveyor` | 로봇이 컨베이어와 충돌 | failure (plan_fail), 즉시 robot 정지 |
| `arm_link-other_robot_arm` | 다른 로봇 팔과 충돌 | 심각, 두 로봇 모두 정지 + alarm |
| `arm_link-bin` | 분류함 외벽과 접촉 | 경고 (grasp 시 부정확) |

설정:

```python
from omni.physx.scripts import physicsUtils
from pxr import PhysxSchema

# 충돌 보고를 켤 prim 에 ContactReportAPI 부착
for prim_path in ["/World/Robots/r0/m0609/link6", "/World/Conveyor/belt", ...]:
    prim = stage.GetPrimAtPath(prim_path)
    PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr().Set(1.0)  # N

# Python 콜백
import omni.physx
def on_contact(contact_headers, contact_data):
    for header in contact_headers:
        a = str(header.actor0)
        b = str(header.actor1)
        publish_contact_event(a, b, header.normal_force_magnitude)

omni.physx.get_physx_simulation_interface().subscribe_contact_report_events(on_contact)
```

publish 한 토픽은 `telemetry-supabase.md` 의 `collisions` 테이블로 들어가고, 심각 클래스(`arm_link-conveyor`, `arm_link-other_robot_arm`) 는 server bridge 의 WS `/events` 로도 push.

---

## 8. 병렬 운영 시 GPU/CPU 예산

4대 로봇 + 4대 카메라 + in-process YOLO 동시 가동 시 GPU 메모리 예산이 핵심 함정. 측정 예시 (RTX 4090 24GB 기준):

| 항목 | 추정 사용 (MB) |
|---|---:|
| Isaac Sim Kit + Omniverse | ~2,500 |
| PhysX GPU pipeline (4 robots × ~30 bodies) | ~600 |
| RTX rendering (4 cameras @ 1280×720, RTX-Real-Time) | ~5,000 |
| ultralytics YOLOv8m FP16 (1 model shared) | ~1,200 |
| TensorRT engine cache | ~500 |
| 여유 (replicator, log buffers) | ~2,000 |
| **합계** | ~11,800 (안전 한계 ≤ 70%) |

레퍼 (`isaac-ros-accel.md §GPU 예산`) 와 일관. 4090 24GB 면 4대까지 안정, 그 이상은:
- 카메라 해상도 720p → 540p 로 낮추기
- 카메라를 conveyor-수준 1대로 통합 (overhead 하나가 모든 zone 커버)
- YOLO 추론을 isaac_ros_yolov8 + NITROS 로 분리 (별도 GPU 가능 시)

CPU 측면: 단일 도메인 + namespace 일 때 DDS discovery 가 가장 부담. `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` 가 fastrtps 보다 다중 토픽에서 가볍게 동작 — ros2-architect `communication.md §RMW` 와 일치.

---

## 9. 단계별 셋업 체크리스트

1. **버전 고정**: Isaac Sim 4.5+ (Conveyor Belt extension), ROS 2 Humble/Iron, ROS_DOMAIN_ID=42, use_sim_time=true.
2. **USD 레이어 생성** (§2): `warehouse_main.usda` 를 빈 stage 로 만들고 sublayer/reference 등록.
3. **m0609+RG2 결합 USD** (`usd-from-urdf.md §m0609+RG2`): articulation root 와 mimic joint 확인 후 `robots/m0609_rg2.usda` 로 저장.
4. **컨베이어** (§5): kinematic body + surface velocity, 마찰 0.7/0.8.
5. **Bins/Cameras/SpawnZone** prim 생성 (§2 의 path 규약 그대로).
6. **OG 팩토리 실행** (§4 의 `scripts/multi_robot_bringup.py`): ROBOT_IDS 만 바꾸면 N대 확장.
7. **네임스페이스 검증** (`scripts/check_namespace_isolation.py`): 충돌 없으면 통과.
8. **server bridge / telemetry logger 기동** (각 reference).
9. **Spawn trigger 시작** (§6): 2초 주기로 컨베이어에 객체 흘리기.

---

## 10. 안티패턴

- ❌ 4번 GUI 클릭으로 로봇 4대 직접 배치 — 재현 불가, prim path 일관성 깨짐
- ❌ 같은 robot 의 OG 토픽을 다른 robot 의 articulation 에 연결 — 디버깅 지옥, 발견까지 며칠
- ❌ 컨베이어 메쉬에 `RigidBodyAPI` 만 적용하고 `kinematicEnabled` 미설정 → 물체가 컨베이어를 뚫고 들어감
- ❌ Replicator 의 spawn 이벤트를 GroundTruth 없이 발생시킴 → detection accuracy 검증 불가
- ❌ 4대 동시 운영 중 RTX-Real-Time + 4×1080p 카메라 → 즉시 OOM
- ❌ ROS_DOMAIN_ID 0 사용 (다른 노드와 충돌) — 반드시 명시적 ID 지정

---

## 11. 교차 참조

- `usd-from-urdf.md §m0609+RG2 결합 USD` — robot reference 의 원본 USD 만들기
- `omnigraph-ros-bridge.md §다중 로봇 OG 팩토리` — §4 의 더 깊은 OG 패턴
- `yolo-perception.md` — §6 spawn 이후 camera 프레임에서 YOLO 추론
- `sort-decision-logic.md` — detection → 모션 계획 → gripper 시퀀스
- `server-bridge.md` — 외부에서 namespace 별 robot 상태 조회
- `telemetry-supabase.md` — §7 의 충돌 / §6 의 spawn 을 Supabase 에 적재
- `replicator-sdg.md §컨베이어+YOLO 학습 데이터` — §6 의 spawn 을 학습 데이터로 변환
- `physx-tuning.md §Solver`, `§Contact` — §5/§7 의 PhysX 파라미터
- `isaac-ros-accel.md §GPU 예산` — §8 의 GPU 한계
- 외부: doosan-robotics `references/multi-robot-and-quirks.md`, ros2-architect `references/communication.md`
