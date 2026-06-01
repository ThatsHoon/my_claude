# Sort Decision Logic — Hand-coded mapping + cuMotion / MoveIt2

**1문장 요지** — YOLO detection 결과로부터 class→bin 매핑을 lookup 하고, bbox+depth 로 grasp pose 를 산출한 뒤, cuMotion 또는 MoveIt2 로 trajectory 를 plan, dsr_controller2 와 호환되는 FollowJointTrajectory 인터페이스로 execute 하는 hand-coded behavior FSM 패턴을 정의한다.

> 본 스킬의 의사결정은 **hand-coded** — RL/IL 정책은 의도적으로 범위 밖. 학습 기반으로 가려면 별도 reference 자리 (`sim2real-deployment.md` 등). FSM 의 상태 전환 자체는 BehaviorTree.CPP 로 옮길 수 있지만, 본 스킬은 단순 Python FSM 으로 시작.

---

## Contents

1. class→bin 매핑 config (YAML)
2. Behavior FSM — 7 단계
3. Grasp pose 산출
4. cuMotion vs MoveIt2 — 선택 기준
5. cuMotion 직접 호출 패턴
6. MoveIt2 plan 호출 패턴 (대안)
7. Plan retry / fallback 정책
8. Multi-robot 시간/공간 분리 (zone allocator)
9. Abort / preempt 처리
10. dsr_controller2 호환 인터페이스 보존
11. 안티패턴
12. 교차 참조

---

## 1. class→bin 매핑 config (YAML)

config 는 단순한 YAML 1장. 하드코딩하지 말고 launch param 또는 yaml 로 분리.

```yaml
# config/sort_mapping.yaml
robots:
  r0:
    zone_x_range: [0.0, 1.0]          # 컨베이어 x 좌표 (m), r0 가 책임지는 zone
    bins:
      box_red:    {prim: /World/Bins/r0_bin_red,    pose: [0.6, -0.3, 0.30]}
      box_blue:   {prim: /World/Bins/r0_bin_blue,   pose: [0.6, -0.5, 0.30]}
      can_a:      {prim: /World/Bins/r0_bin_can,    pose: [0.8, -0.3, 0.30]}
      reject:     {prim: /World/Bins/r0_bin_reject, pose: [0.4, -0.3, 0.30]}
  r1:
    zone_x_range: [1.0, 2.0]
    bins:
      box_red:    {prim: /World/Bins/r1_bin_red,    pose: [1.6, -0.3, 0.30]}
      ...

# detection conf 임계
confidence_threshold: 0.5

# unknown class 처리
default_bin: reject
```

로드:

```python
import yaml
with open("config/sort_mapping.yaml") as f:
    SORT_CFG = yaml.safe_load(f)

def resolve_bin(robot_id: str, class_name: str) -> dict | None:
    bins = SORT_CFG["robots"][robot_id]["bins"]
    return bins.get(class_name, bins[SORT_CFG["default_bin"]])
```

장점: 새 class 추가 시 yaml 한 줄, 시뮬 재시작도 launch param reload 만으로 가능.

---

## 2. Behavior FSM — 7 단계

```
                ┌────────────────────┐
                │  IDLE              │  (대기, conveyor 감시)
                └─────────┬──────────┘
                          │ detection received & zone match
                          ▼
                ┌────────────────────┐
                │  PLAN              │  (grasp pose 산출 + plan)
                └─────────┬──────────┘
                          │ plan ok
                          ▼
                ┌────────────────────┐
                │  REACH_PRE_GRASP   │  (안전 pre-grasp 자세로 이동)
                └─────────┬──────────┘
                          │ trajectory completed
                          ▼
                ┌────────────────────┐
                │  GRASP             │  (서서히 내려가 gripper 닫기)
                └─────────┬──────────┘
                          │ gripper closed + contact force OK
                          ▼
                ┌────────────────────┐
                │  LIFT              │  (수직 상승)
                └─────────┬──────────┘
                          │ lift complete
                          ▼
                ┌────────────────────┐
                │  CARRY_TO_BIN      │  (target bin 위로 이동)
                └─────────┬──────────┘
                          │ at bin
                          ▼
                ┌────────────────────┐
                │  RELEASE           │  (gripper open + lift)
                └─────────┬──────────┘
                          │ done
                          ▼
                ┌────────────────────┐
                │  RETURN_HOME       │  (home 자세 복귀)
                └─────────┬──────────┘
                          ▼
                        IDLE
```

각 상태 전환 시점에 `cycle_events` 테이블에 row 추가 (telemetry-supabase.md §D4). 실패 (plan_fail, grasp_slip, timeout) 는 `failures` 테이블 + cycles.success=false.

### Python 골격

```python
from enum import Enum, auto

class S(Enum):
    IDLE = auto(); PLAN = auto(); REACH_PRE_GRASP = auto(); GRASP = auto()
    LIFT = auto(); CARRY_TO_BIN = auto(); RELEASE = auto(); RETURN_HOME = auto()
    FAIL = auto()

class SortFSM:
    def __init__(self, robot_id, planner, controller, logger):
        self.robot_id = robot_id
        self.state = S.IDLE
        self.planner = planner          # cuMotion or MoveIt2 wrapper
        self.controller = controller    # FollowJointTrajectory action client
        self.logger = logger            # telemetry sink
        self.cycle_id: int | None = None
        self.detection = None

    def on_detection(self, det):
        if self.state != S.IDLE:
            return                        # 이미 사이클 중
        if det.confidence < SORT_CFG["confidence_threshold"]:
            return
        if not self.in_zone(det.world_pose):
            return
        self.detection = det
        self.cycle_id = self.logger.begin_cycle(self.robot_id, det)
        self.transition(S.PLAN)

    def transition(self, next_state):
        self.logger.cycle_event(self.cycle_id, str(next_state))
        self.state = next_state
        getattr(self, f"do_{next_state.name.lower()}")()
    ...
```

`do_plan`, `do_grasp` 등은 §3~§7 참조.

---

## 3. Grasp pose 산출

`yolo-perception.md §6` 의 `bbox_to_world_pose` 를 활용해 detection 의 월드 좌표를 얻은 뒤, **단순화된 top-down grasp** 가정 — RG2 는 평행 그리퍼이고 컨베이어 위 객체는 평면 자세.

```python
def compute_grasp(det_world_pose: np.ndarray, object_height: float = 0.05) -> dict:
    """grasp pose: bbox center 위 +Z 0.10m 의 pre-grasp, -Z 로 0.05m 내려가서 잡기."""
    x, y, z = det_world_pose
    pre_grasp = pose(x, y, z + object_height + 0.10, rpy=(np.pi, 0, 0))
    grasp     = pose(x, y, z + object_height * 0.5, rpy=(np.pi, 0, 0))
    lift      = pose(x, y, z + 0.30, rpy=(np.pi, 0, 0))
    return {"pre_grasp": pre_grasp, "grasp": grasp, "lift": lift}
```

- `rpy=(pi, 0, 0)` — gripper 가 아래를 향하도록 (TCP frame 의 z 가 -Z world)
- `object_height` 는 class 별로 yaml 에서 조회 가능 (`bins.box_red.height: 0.05`)
- 실패 케이스 (IK fail) 시 yaw 를 ±π/4 회전해 재시도 (§7 fallback)

3D pose 가 NaN 이거나 신뢰도 낮으면 즉시 reject:

```python
if not np.all(np.isfinite(det_world_pose)):
    self.logger.log_failure("invalid_pose")
    return None
```

---

## 4. cuMotion vs MoveIt2 — 선택 기준

| 항목 | cuMotion | MoveIt2 |
|---|---|---|
| 위치 | GPU (NITROS) | CPU |
| 평균 plan 시간 (m0609) | ~10ms | ~100~500ms |
| 환경 충돌 회피 | curobo 의 voxel grid (GPU) | OctoMap (CPU, 비용↑) |
| 통합 난도 | NVIDIA Isaac ROS 컨테이너 권장 | 표준 ROS 2 패키지, doosan-robotics 와 직접 호환 |
| Constraint 표현 | 직진성, end effector orientation 직접 지원 | OMPL constraint planner 까지 풀 |

**1차 권장**: 본 시나리오 (4대 동시, 0.5초 cycle 목표) 에서는 **cuMotion**. MoveIt2 는 plan latency 가 cycle 시간 대비 크다. 단, doosan-robotics 의 표준 MoveIt2 구성을 이미 쓰는 워크스페이스라면 동일 인터페이스 (FollowJointTrajectory) 라 swap 만으로 전환 가능 — 이 swap 가능성을 §10 에서 다룸.

---

## 5. cuMotion 직접 호출 패턴

cuRobo 의 Python API 를 사용. 자료실 `/home/hoon/isaac-sim-skill-research/10-gap-fills/curobo/repo/`.

```python
from curobo.types.base import TensorDeviceType
from curobo.types.robot import RobotConfig
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig

class CurobePlanner:
    def __init__(self, robot_cfg_path: str):
        tensor_args = TensorDeviceType()
        robot_cfg = RobotConfig.from_dict(load_yaml(robot_cfg_path))  # m0609 cfg
        cfg = MotionGenConfig.load_from_robot_config(
            robot_cfg,
            world_cfg=None,                # 정적 환경 voxel 은 후속 load
            interpolation_dt=0.02,
        )
        self.gen = MotionGen(cfg)
        self.gen.warmup(enable_graph=True)

    def plan(self, q_current: np.ndarray, target_pose: np.ndarray, world_obs: list) -> "Result":
        self.gen.update_world(world_obs)   # voxel grid 갱신
        return self.gen.plan_single(
            start_state=q_current,
            goal_pose=target_pose,
            plan_config=...,
        )

    def to_trajectory(self, result) -> JointTrajectory:
        # cuMotion 결과 (interpolated) 를 ros2 trajectory_msgs/JointTrajectory 로 변환
        ...
```

장점: 한 번 warmup 한 뒤 plan_single 호출이 ms 단위. 다중 로봇 시 robot 마다 별도 `MotionGen` 인스턴스 (모델 가중치는 다르지 않으면 공유 가능).

`isaac-ros-accel.md §cuRobo` 의 더 깊은 셋업과 교차.

---

## 6. MoveIt2 plan 호출 패턴 (대안)

doosan-robotics 가 이미 m0609 MoveIt2 config 를 제공 (`~/cobot_ws/src/doosan-robot2/...`). 그대로 재사용 가능:

```python
from rclpy.action import ActionClient
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, Constraints, ...

class MoveItPlanner:
    def __init__(self, node, planning_group="manipulator"):
        self.client = ActionClient(node, MoveGroup, f"/{robot_ns}/move_action")

    async def plan_to_pose(self, target_pose):
        goal = MoveGroup.Goal()
        goal.request.group_name = "manipulator"
        # PositionConstraint + OrientationConstraint 설정
        ...
        result = await self.client.send_goal_async(goal)
        return result.trajectory
```

장점: doosan-robotics `references/launch-and-modes.md` 의 bringup 그대로 + ros2_control `joint_trajectory_controller` 와 매끄럽게 연결.

단점: plan latency 가 cuMotion 대비 10~50배. 4대 동시 cycle 시 plan 이 직렬화되며 bottleneck.

권장: **cuMotion 1차 + MoveIt2 fallback** — cuMotion 이 fail 했을 때 (예: world voxel grid 가 불완전) MoveIt2 로 1회 재시도.

---

## 7. Plan retry / fallback 정책

```python
def plan_with_fallback(robot_id, target):
    for yaw in (0, np.pi/4, -np.pi/4, np.pi/2, -np.pi/2):
        rotated = rotate_pose_yaw(target, yaw)
        r = curobo_planner.plan(q_now(robot_id), rotated)
        if r.success:
            return r.trajectory
    # cuMotion 5회 fail → MoveIt2 로 1회 더
    return moveit_planner.plan(target)
```

- yaw 후보 5개 (0, ±45°, ±90°) — 평행 그리퍼 RG2 는 yaw 자유도가 있음
- 모두 fail 시 `failures` 테이블에 `category='plan_fail'` 로 기록하고 cycle 종료 (success=false), 그 detection 은 다음 cycle 에서 skip

**timeout** — plan 1회 시도는 100ms 한도. 그 이상 걸리면 environment voxel 갱신을 의심 (curobo `update_world` 가 stuck) → 워밍업 재실행.

---

## 8. Multi-robot 시간/공간 분리 (zone allocator)

같은 detection 에 두 로봇이 동시 손을 뻗는 상황은 충돌 / 실패의 큰 원인.

**1차 권장: 공간 분할** — `sort_mapping.yaml` 의 `zone_x_range` 로 robot 별 conveyor 책임 zone 을 미리 정함. r0 는 x∈[0,1], r1 은 [1,2] 처럼. 같은 zone 안에서 detection 이 발생해도 다른 robot 은 응답하지 않음.

```python
def in_zone(self, world_pose):
    lo, hi = SORT_CFG["robots"][self.robot_id]["zone_x_range"]
    return lo <= world_pose[0] <= hi
```

**보조: 시간 분할** — 같은 zone 안에서 다중 detection 이 시간차로 도착하면 robot 이 한 cycle 마치고 IDLE 로 돌아오면 다음 받는 식. 이는 FSM 의 `IDLE` 상태에서만 detection 수락하는 정책으로 자동 보장.

**고급 (선택)**: 중앙 broker 노드가 모든 detection 을 받아 가장 가까운 idle robot 에 할당. 본 스킬 1차 범위 밖.

---

## 9. Abort / preempt 처리

server bridge 의 `POST /robots/{id}/preempt` (E5) → ROS service `/{robot_ns}/motion/abort` (B4) 호출:

```python
class SortFSM:
    def abort(self):
        # 1) 현재 trajectory action 을 cancel
        self.controller.cancel_current_goal()
        # 2) gripper 가 닫혀 있다면 open (객체 들고 있을 가능성)
        if self.gripper_state == "closed":
            self.controller.open_gripper()
        # 3) home 으로 복귀하지 말 것 — 사용자가 직접 결정
        self.state = S.IDLE
        self.logger.log_failure(category="aborted", message="user preempt")
```

- 충돌 이벤트 (`/contact_events` 의 심각 클래스, `warehouse-sorting-pipeline.md §7`) 가 들어와도 같은 abort 경로.
- abort 후 robot 은 `IDLE` 로 복귀하되 외부 명령 (`/{robot_ns}/mode/set: 'maintenance'`) 으로 잠금 가능. doosan-robotics `references/launch-and-modes.md §mode` 패턴.

---

## 10. dsr_controller2 호환 인터페이스 보존

본 시나리오는 시뮬 우선이지만, **추후 동일 워크스페이스를 실기로 옮길 때 코드가 swap 만으로 동작**해야 가치가 크다. 이를 위해 본 스킬은 다음 인터페이스 계약을 strictly 따른다.

| 인터페이스 | 본 스킬 (sim) | doosan-robotics (real) | 차이 |
|---|---|---|---|
| Trajectory execute | action `/{ns}/joint_trajectory_controller/follow_joint_trajectory` (control_msgs/FollowJointTrajectory) | 동일 | 동일 |
| JointState publish | `/{ns}/joint_states` 60Hz | 동일 | 동일 |
| TF tree | base→link6→tcp | 동일 | 동일 |
| Gripper | action `/{ns}/gripper/command` (control_msgs/GripperCommand) | 동일 (doosan_gripper_controller 또는 RG2 driver) | 동일 |
| Mode | service `/{ns}/mode/set` | doosan-robotics 의 mode service | doosan-robotics 가 sim/real/virtual 3-mode 가짐 → 본 스킬은 sim mode 만 |

**core principle**: planner (cuMotion/MoveIt2) 의 출력은 `JointTrajectory` 이고, 실행 측은 `FollowJointTrajectory` 액션. 이 사이 어떤 변환도 sim/real 분기로 두지 말 것 — 그래야 swap 가능.

doosan-robotics `references/multi-robot-and-quirks.md` 와 `references/launch-and-modes.md` 가 실기 측 표준. 본 스킬은 그것과 직접 호환되도록 OG 토픽명, action name, joint name 을 모두 일치시킴.

---

## 11. 안티패턴

- ❌ class 이름을 Python 코드에 하드코딩 — yaml 분리 안 함
- ❌ grasp pose 의 yaw 를 단일 값으로 시도 — IK fail 률 ↑
- ❌ cuMotion plan 결과를 검증 없이 controller 로 push — collision 체크 누락
- ❌ FSM 의 모든 상태를 `IDLE` 로 reset 없이 진행 — race condition, 잘못된 detection 에 반응
- ❌ trajectory 실행 도중 새 detection 으로 cycle 재시작 — 두 cycle 이 동시 진행
- ❌ MoveIt2 의 plan 을 직접 sim 의 articulation controller 로 write — controller manager 를 우회하면 추후 실기 swap 불가
- ❌ zone 분리 없이 다중 로봇 → 같은 객체에 두 로봇이 동시 접근

---

## 12. 교차 참조

- `yolo-perception.md §6` — detection 의 월드 좌표 추정 (이 reference 의 입력원)
- `warehouse-sorting-pipeline.md §3, §7` — namespacing 과 충돌 분류
- `telemetry-supabase.md §D3, §D4, §D7` — cycle / event / failure 적재
- `omnigraph-ros-bridge.md §다중 로봇 OG 팩토리` — JointState/JointCommand 토픽 셋업
- `physx-tuning.md §Articulation Drive` — joint drive P/D 매핑, RG2 mimic joint
- `isaac-ros-accel.md §cuMotion vs MoveIt2` — 본 §4 의 깊은 비교
- 외부: doosan-robotics `references/multi-robot-and-quirks.md`, doosan-robotics `references/launch-and-modes.md`
