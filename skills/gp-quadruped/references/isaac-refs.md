# isaac-refs.md — 구현 능력 ↔ 담당 스킬 매핑 + 검증된 Isaac 참조자료

GP 프로젝트 구현에 필요한 **통신 연결 방법 + Isaac Sim 기능 구현** 전체 목록과,
각각을 어느 스킬/ref 가 담당하는지의 단일 인덱스. 모든 Isaac 경로는 실재
검증됨(발명 금지 — 인용만).

## A. 능력 ↔ 담당 매핑

### A1. Isaac Sim 기능 구현

| 능력 | 담당 |
|---|---|
| 번들 보행정책 메커니즘(PolicyController/Anymal/Spot, obs/forward/init) | [[isaac-sim-bridge]] `bundled-locomotion-policy.md` |
| ANYmal-C 정책 구동·waypoint·m0609 stow 조합 | 본 스킬 `locomotion-policy.md` |
| 절차적 볼록 heightfield + D2 클램프 + 정적 collider | 본 스킬 `terrain-build.md` |
| m0609 URDF→USD, 조인트 드라이브 일반 | [[isaac-sim-bridge]] `usd-from-urdf.md` |
| m0609 payload 결합·stow·FollowJointTrajectory·리미트 | [[doosan-robotics]] `sim-integration.md` |
| RealSense K행렬·OG 카메라/joint/tf 발행 일반 | [[isaac-sim-bridge]] `omnigraph-ros-bridge.md` |
| GP OG 배선·토픽맵·RealSense 파라미터 | 본 스킬 `sensor-and-comms.md` |
| raycast 사격·트레이서·FireEvent | 본 스킬 `weapon-fire.md` |
| 라이브 Kit 제어·execute_script 함정·setsid 기동 | [[isaac-sim-mcp]] `debugging.md` `patterns.md` |
| 텔레메트리 스키마(GP 적응) | [[isaac-sim-bridge]] `telemetry-supabase.md` |

### A2. 통신 연결 방법

| 능력 | 담당 |
|---|---|
| 멀티호스트 DDS(ROS_DOMAIN_ID, discovery, peers) | [[ros2-architect]] `communication.md` |
| ROS↔웹 브리지(FastAPI+WS), WebRTC(aiortc) vs MJPEG 폴백 | [[ros2-architect]] `web-bridge-streaming.md` |
| 양방향 오디오(Opus/PCM 청크) over ROS/WS | [[ros2-architect]] `web-bridge-streaming.md` |
| 영상 fps/화질 스로틀 + QoS | [[ros2-architect]] `web-bridge-streaming.md` + 본 스킬 `sensor-and-comms.md`(GP 파라미터) |
| NavSatFix/GPS 토픽 규약 + sim-GPS 환산 | [[ros2-architect]] `web-bridge-streaming.md` + 본 스킬 `sensor-and-comms.md` |
| rosout(rcl_interfaces/Log) level≥30 필터·릴레이 | [[ros2-architect]] `web-bridge-streaming.md` + 본 스킬 `sensor-and-comms.md` |
| GP 토픽맵·QoS 고정표 | 본 스킬 `sensor-and-comms.md` §1 |

## B. 검증된 Isaac Sim 참조자료 (인용 전용, 수정 금지)

### B1. 번들 보행정책 소스

베이스: `~/dev_ws/isaac_sim/isaacsim/source/extensions/isaacsim.robot.policy.examples/isaacsim/robot/policy/examples/`

| 파일 | 핵심 |
|---|---|
| `controllers/policy_controller.py` | `PolicyController.__init__(name,prim_path,root_path,usd_path,position,orientation)`; `load_policy(pt,yaml)` → torch.jit + `_decimation,_dt,render_interval`; `initialize(physics_sim_view,effort_modes="force",control_mode="position",set_gains,set_limits,set_articulation_props)`; `_compute_action`(torch.no_grad); `post_reset` |
| `robots/anymal.py` | `AnymalFlatTerrainPolicy`; usd 기본 `anymal_c.usd`; `load_policy(anymal_policy.pt, anymal_env.yaml)`; obs 48 (lin3/ang3/grav3/cmd3/jpos12/jvel12/prevact12); `forward(dt,command)` action_scale 0.5 → `_actuator_network.compute_torques` → `set_joint_efforts`; `initialize` → `super().initialize(control_mode="effort")` + `LstmSeaNetwork.setup(sea_net_jit2.pt, default_pos)` + reset |
| `robots/spot.py` | `SpotFlatTerrainPolicy`; usd `spot.usd`; **position 제어**(actuator net 없음), action_scale 0.2, `set_joint_positions` |
| `utils/actuator_network.py` | `LstmSeaNetwork.setup(path,default_pos)`, `reset()`, `compute_torques(jpos,jvel,actions)`→(torque[-80,80], state) |

표준 루프: `~/dev_ws/isaac_sim/isaacsim/source/standalone_examples/api/isaacsim.robot.policy.examples/{anymal_standalone.py,spot_standalone.py}`
인터랙티브: `.../isaacsim.examples.interactive/isaacsim/examples/interactive/quadruped/quadruped_example.py`

### B2. 에셋 경로 (assets_root = `get_assets_root_path()`)

- 로봇: `/Isaac/Robots/ANYbotics/anymal_c/anymal_c.usd` (Spot: `/Isaac/Robots/BostonDynamics/spot/spot.usd`)
- 정책: `/Isaac/Samples/Policies/Anymal_Policies/{anymal_policy.pt,anymal_env.yaml,sea_net_jit2.pt}`
  (Spot: `/Isaac/Samples/Policies/Spot_Policies/{spot_policy.pt,spot_env.yaml}`)

### B3. m0609 URDF

`/home/rokey/dev_ws/isaac_sim/src/doosan-robot2/urdf/m0609_isaac_sim.urdf`
- links: `base, base_link, link_1..link_6, tool0`
- joints: `joint_1..joint_6` (+ `base_link-base`, `joint_6-tool0` fixed)
- 플랜지 = `link_6` (RealSense 부착), tool0 = 툴 마운트

### B4. OG 노드 타입 (점 표기 — 밑줄 아님)

- `omni.graph.action.OnPlaybackTick`
- `isaacsim.core.nodes.*` (IsaacCreateRenderProduct, IsaacArticulation* 등)
- `isaacsim.ros2.bridge.*` (ROS2Context, ROS2PublishJointState,
  ROS2CameraHelper, ROS2PublishTransformTree, ROS2SubscribeTwist 등)

### B5. 설계 권위 문서

`/home/rokey/dev_ws/isaac_sim/cobot3/dev-docs/gp-quadruped-system-design.md`
(D1~D11 결정, S1~S7 서브시스템, §12 토픽/QoS, §13 스키마, §15 P0~P4 —
충돌 시 항상 이 문서 우선)

## C. 갱신 규약

새 검증 경로 발견 시 B 에 추가하고, 새 능력은 A 매핑에 먼저 등재한 뒤
담당 ref 작성. 경로는 반드시 실재 확인 후 기재(추정 금지).
