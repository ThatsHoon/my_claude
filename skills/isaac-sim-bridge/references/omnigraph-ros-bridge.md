# omnigraph-ros-bridge.md — OmniGraph 기반 ROS 2 브리지

이 reference는 **Isaac Sim 의 센서/조인트/TF 를 ROS 2 토픽으로 노출하는 모든 방법**을 다룬다. OmniGraph (이하 OG) 노드 모델, Action Graph 작성, 각 sensor publisher 노드, QoS 매칭, 그리고 "토픽이 안 떠요" 디버깅.

> **선행 조건**: ROS 2 측 정석(QoS, lifecycle, executor, tf2)은 `ros2-architect` 스킬에서 다룬다. 이 파일은 **Isaac Sim 측에서 ROS 토픽을 발행/구독하는 그래프** 만 다룬다.

## Contents
1. OG vs rclpy: 어디에 뭘 쓰나
2. Bridge extension 활성화 & 검증
3. OmniGraph 의 노드/속성 모델
4. Action Graph (GUI) 로 첫 그래프 만들기
5. Python 으로 같은 그래프 만들기 (재현용)
6. Camera 퍼블리시
7. Lidar / RTX Lidar 퍼블리시
8. IMU 퍼블리시
9. JointState / TF 퍼블리시
10. Subscriber: TwistSubscriber → 모바일 베이스 구동
11. QoS 설정과 매칭 (ros2-architect 교차참조)
12. "Did the bridge actually publish?" 디버깅 체크리스트
13. 자주 발생하는 OG 함정

---

## 1. OG vs rclpy: 어디에 뭘 쓰나

| 무엇을 | Isaac Sim 내부 (OG) | 외부 ROS 노드 (rclpy/rclcpp) |
|---|---|---|
| 시뮬 카메라 → ROS 토픽 | ✓ Action Graph + `ROS2PublishCamera` | ✗ |
| 시뮬 joint → `/joint_states` | ✓ `ROS2PublishJointState` | ✗ |
| ROS `Twist` 명령 → 시뮬 베이스 | ✓ `ROS2SubscribeTwist` + `DifferentialController` | ✗ |
| 시뮬 USD prim 자세 → `/tf` | ✓ `ROS2PublishTransformTree` | ✗ |
| MoveIt 가 시뮬 robot 동작 시키기 | ✓ joint_states 만 OG 로 → MoveIt 는 외부 rclcpp | (외부) |
| 시뮬 외부에서 USD 변경 (예: env 추가) | ✗ | ✓ 외부 rclpy 노드가 시뮬에 service call |

**원칙**: **시뮬 안의 상태를 ROS 로 노출**하는 모든 작업은 OG. **ROS 로 시뮬을 외부 제어**하는 작업도 OG (subscribe). **시뮬 외부에서 알고리즘을 돌리고 결과를 시뮬로 보내는** 작업만 외부 rclpy.

## 2. Bridge extension 활성화 & 검증

`Window → Extensions` → 검색 `isaacsim.ros2.bridge` → ENABLED & AUTOLOAD.

검증:
```bash
# Isaac Sim 부팅 후 별도 셸에서
source /opt/ros/humble/setup.bash
ros2 node list           # /isaac_sim 노드가 떠 있어야 함 (없을 수도 있음)
ros2 topic list          # /tf, /tf_static, /clock 등 기본 토픽
ros2 param list /isaac_sim   # 파라미터
```

기본 토픽이 안 보이면:
- 호스트 ROS distro 와 Isaac Sim 내부 distro 일치? (`installation.md` §7)
- `RMW_IMPLEMENTATION` 통일?
- `ROS_DOMAIN_ID` 같음?

원본: `02-ros2-bridge/ros2_tutorials/ros2_landing_page.html`

## 3. OmniGraph 의 노드/속성 모델

OG 는 **노드 → 속성(in/out) → wire** 의 데이터플로 그래프. ROS 2 와 패러다임이 다르다:

- **Node**: 함수 단위. 예: `IsaacReadCamera`, `ROS2PublishCamera`, `OnPlaybackTick`, `Constant`.
- **Attribute**: 노드의 input/output 포트. 타입이 있음 (`token`, `float[3]`, `bundle`, `colorf[3][]`).
- **Wire**: 한 노드의 출력 attribute 를 다른 노드의 입력으로.
- **Execution edge** (별도): 회색 wire 가 아닌 **흰색 edge** 로 표시. 실행 순서를 강제.

매 시뮬 프레임마다:
1. `OnPlaybackTick` (또는 `OnSimulationStep`) 가 펄스 발사
2. 펄스가 execution edge 따라 전파
3. 각 노드는 자기 차례에 input 을 읽어 output 을 갱신
4. 마지막에 `ROS2Publish*` 가 토픽 발행

**중요**: data wire 만 있고 execution edge 가 없는 노드는 **절대 실행되지 않는다**. GUI 에서 노드 색이 흐릿하면 execution 미연결.

원본: `03-omnigraph/omnigraph/`

## 4. Action Graph (GUI) 로 첫 그래프 만들기

목표: Franka 의 왼쪽 카메라를 `/camera/rgb` 토픽으로 발행.

1. `Create → Visual Scripting → Action Graph` → `/World/CameraGraph` 생성.
2. Graph 에디터 열고 노드 추가:
   - `OnPlaybackTick`
   - `IsaacRunOneSimulationFrame` (선택, frame skip 시)
   - `IsaacCreateRenderProduct` — input: `cameraPrim` = `/World/Franka/panda_camera`
   - `ROS2CreateCameraInfoBuffers`
   - `ROS2CameraHelper` 또는 `ROS2PublishCamera` (6.0 이후)
3. Wire:
   - `OnPlaybackTick.outputs:tick` → 각 노드의 `inputs:execIn` (흰색 edge)
   - `IsaacCreateRenderProduct.outputs:renderProductPath` → `ROS2CameraHelper.inputs:renderProductPath`
4. `ROS2CameraHelper` 의 attributes:
   - `topicName: "/camera/rgb"`
   - `frameId: "panda_camera"`
   - `type: "rgb"` (또는 `"depth"`, `"semantic_segmentation"`)
   - `qosProfile: "default"` (또는 `"sensor_data"`, `"system_default"`)
5. Play 누르고 다른 터미널: `ros2 topic hz /camera/rgb` — 30~60 Hz 보이면 성공.

## 5. Python 으로 같은 그래프 만들기

소스 컨트롤 가능한 방식. Standalone 스크립트:

```python
import omni.graph.core as og

keys = og.Controller.Keys
(graph_handle, nodes, _, _) = og.Controller.edit(
    {"graph_path": "/World/CameraGraph", "evaluator_name": "execution"},
    {
        keys.CREATE_NODES: [
            ("OnTick", "omni.graph.action.OnPlaybackTick"),
            ("CreateRP", "isaacsim.core.nodes.IsaacCreateRenderProduct"),
            ("CamHelper", "isaacsim.ros2.bridge.ROS2CameraHelper"),
        ],
        keys.SET_VALUES: [
            ("CreateRP.inputs:cameraPrim", "/World/Franka/panda_camera"),
            ("CreateRP.inputs:width", 640),
            ("CreateRP.inputs:height", 480),
            ("CamHelper.inputs:topicName", "/camera/rgb"),
            ("CamHelper.inputs:frameId", "panda_camera"),
            ("CamHelper.inputs:type", "rgb"),
            ("CamHelper.inputs:qosProfile", "sensor_data"),
        ],
        keys.CONNECT: [
            ("OnTick.outputs:tick", "CreateRP.inputs:execIn"),
            ("CreateRP.outputs:execOut", "CamHelper.inputs:execIn"),
            ("CreateRP.outputs:renderProductPath", "CamHelper.inputs:renderProductPath"),
        ],
    },
)
```

이 코드는 Isaac Sim 부팅 후 한 번만 실행하면 USD 에 그래프가 영속화된다. 같은 stage 를 다시 열면 그래프가 살아 있다.

## 6. Camera 퍼블리시

`ROS2CameraHelper` 또는 분리된 `ROS2PublishCamera` + `ROS2PublishCameraInfo` 가 carry. 발행되는 토픽:

- `<topicName>/image` — `sensor_msgs/Image` (rgb 또는 depth)
- `<topicName>/camera_info` — `sensor_msgs/CameraInfo` (K, D, R, P)

depth 카메라:
```python
("CamHelper.inputs:type", "depth"),
# Topic 은 /camera/depth/image_raw 같이 변환됨
```

semantic / instance segmentation:
```python
("CamHelper.inputs:type", "semantic_segmentation"),
("CamHelper.inputs:enableSemanticLabels", True),
```

**주의**: 카메라 prim 의 `focalLength`, `horizontalAperture` 가 잘못되면 K 행렬이 깨진다. URDF 에서 안 들어오므로 USD 에서 직접 설정:
```python
camera_prim = stage.GetPrimAtPath("/World/Franka/panda_camera")
camera_prim.GetAttribute("focalLength").Set(24.0)        # mm
camera_prim.GetAttribute("horizontalAperture").Set(20.955)  # mm (1080p sensor)
```

## 7. Lidar / RTX Lidar 퍼블리시

두 종류:
- **Legacy raycast lidar** (`omni.isaac.range_sensor`): CPU, 단순, 노이즈 X
- **RTX Lidar** (`isaacsim.sensors.rtx`): GPU, 사실적, 반사·노이즈 모델 O — 권장

RTX Lidar 셋업:
```python
import omni.kit.commands
# RTX Lidar prim 생성
omni.kit.commands.execute(
    "IsaacSensorCreateRtxLidar",
    path="/World/Franka/lidar",
    parent="/World/Franka",
    config="OS1_REV6_128ch10hz1024res",   # Ouster, Velodyne 등 프리셋
    translation=(0, 0, 0.1),
)
```

OG 노드:
- `IsaacCreateRenderProduct` (lidar prim 지정)
- `ROS2RtxLidarHelper` → output: `/lidar/scan` (`sensor_msgs/LaserScan` 또는 `PointCloud2`)

`ROS2RtxLidarHelper.inputs:type`: `"laser_scan"` (2D 평면) 또는 `"point_cloud"` (3D).

원본: `02-ros2-bridge/sensors/`

## 8. IMU 퍼블리시

IMU 는 별도 OG 노드 없이 `IsaacReadIMU` + `ROS2PublishImu`:

```python
keys.CREATE_NODES: [
    ("OnTick", "omni.graph.action.OnPlaybackTick"),
    ("ReadIMU", "isaacsim.sensors.physics.IsaacReadIMU"),
    ("PubIMU", "isaacsim.ros2.bridge.ROS2PublishImu"),
],
keys.SET_VALUES: [
    ("ReadIMU.inputs:imuPrim", "/World/Robot/imu_link"),
    ("PubIMU.inputs:topicName", "/imu/data"),
    ("PubIMU.inputs:frameId", "imu_link"),
],
keys.CONNECT: [
    ("OnTick.outputs:tick", "ReadIMU.inputs:execIn"),
    ("ReadIMU.outputs:execOut", "PubIMU.inputs:execIn"),
    ("ReadIMU.outputs:linAcc", "PubIMU.inputs:linearAcceleration"),
    ("ReadIMU.outputs:angVel", "PubIMU.inputs:angularVelocity"),
    ("ReadIMU.outputs:orientation", "PubIMU.inputs:orientation"),
],
```

**노이즈는 시뮬레이터가 기본으론 안 넣는다.** 학습용이면 `replicator-sdg.md` §"센서 노이즈 랜덤화" 처방.

## 9. JointState / TF 퍼블리시

매니퓰레이터를 ROS 에서 모니터링하려면 둘 다 필수.

```python
keys.CREATE_NODES: [
    ("OnTick", "omni.graph.action.OnPlaybackTick"),
    ("PubJS", "isaacsim.ros2.bridge.ROS2PublishJointState"),
    ("PubTF", "isaacsim.ros2.bridge.ROS2PublishTransformTree"),
],
keys.SET_VALUES: [
    ("PubJS.inputs:targetPrim", "/World/Robot"),
    ("PubJS.inputs:topicName", "/joint_states"),
    ("PubTF.inputs:parentPrim", "/World"),
    ("PubTF.inputs:targetPrims", ["/World/Robot/base_link", "/World/Robot/end_effector"]),
    ("PubTF.inputs:topicName", "/tf"),
],
keys.CONNECT: [
    ("OnTick.outputs:tick", "PubJS.inputs:execIn"),
    ("OnTick.outputs:tick", "PubTF.inputs:execIn"),
],
```

`PubJS.inputs:targetPrim` 은 **articulation root** 를 가리켜야 한다 (`usd-from-urdf.md` §3). 가리키는 prim 이 articulation root 가 아니면 토픽은 발행되지만 position 이 전부 0.

`/tf` 발행 시 호스트의 `robot_state_publisher` 가 같은 URDF 로 동시 발행하면 충돌 → 둘 중 하나만. 통상 Isaac Sim 측에서 `/tf` 발행하고, 외부 노드는 `/joint_states` 만 받아 `tf2_ros::TransformListener` 로 변환.

## 10. Subscriber: TwistSubscriber → 모바일 베이스 구동

```python
keys.CREATE_NODES: [
    ("OnTick", "omni.graph.action.OnPlaybackTick"),
    ("SubTwist", "isaacsim.ros2.bridge.ROS2SubscribeTwist"),
    ("DiffCtrl", "isaacsim.wheeled_robots.DifferentialController"),
    ("ApplyVel", "isaacsim.core.nodes.IsaacArticulationController"),
],
keys.SET_VALUES: [
    ("SubTwist.inputs:topicName", "/cmd_vel"),
    ("DiffCtrl.inputs:wheelRadius", 0.06),
    ("DiffCtrl.inputs:wheelDistance", 0.3),
    ("ApplyVel.inputs:targetPrim", "/World/MobileBase"),
],
keys.CONNECT: [
    ("OnTick.outputs:tick", "SubTwist.inputs:execIn"),
    ("SubTwist.outputs:execOut", "DiffCtrl.inputs:execIn"),
    ("SubTwist.outputs:linearVelocity", "DiffCtrl.inputs:linearVelocity"),
    ("SubTwist.outputs:angularVelocity", "DiffCtrl.inputs:angularVelocity"),
    ("DiffCtrl.outputs:velocityCommand", "ApplyVel.inputs:velocityCommand"),
    ("DiffCtrl.outputs:execOut", "ApplyVel.inputs:execIn"),
],
```

`/cmd_vel` 에 `Twist` 보내면 베이스가 움직인다. 외부 노드:
```bash
ros2 topic pub /cmd_vel geometry_msgs/Twist "linear: {x: 0.2}" -1
```

## 11. QoS 설정과 매칭

`ROS2Publish*` 와 `ROS2Subscribe*` 노드의 `qosProfile` 옵션:

| Profile | reliability | durability | depth | 용도 |
|---|---|---|---|---|
| `system_default` | RELIABLE | VOLATILE | 10 | 일반 |
| `sensor_data` | BEST_EFFORT | VOLATILE | 5 | 고주파 센서 |
| `default` | RELIABLE | VOLATILE | 10 | system_default 와 동일 |
| `services_default` | RELIABLE | VOLATILE | 10 | 서비스용 |
| `parameters` | RELIABLE | VOLATILE | 1000 | 파라미터용 |

**핵심**: 외부 subscriber 의 QoS 와 일치해야 한다. Mismatch 증상은 `ros2 doctor` 에 `Incompatible QoS event`. 정석은 `ros2-architect/references/communication.md` §"QoS 정합성".

규칙 두 가지만 외우면 90%:
- **카메라/라이다/IMU** = `sensor_data` (BEST_EFFORT)
- **joint_states/tf** = `system_default` (RELIABLE)

원본: `02-ros2-bridge/ros2_tutorials/tutorial_ros2_camera.html` 등.

## 12. "Did the bridge actually publish?" 디버깅 체크리스트

토픽이 안 보이거나 echo 가 비어 있을 때 이 순서로:

1. **Bridge extension enabled?** `Window → Extensions` → `isaacsim.ros2.bridge` ENABLED.
2. **Play 눌렀나?** OG 의 `OnPlaybackTick` 은 simulation 이 play 중일 때만 발사. Pause 상태 → 발행 0.
3. **Stage 의 timecode 가 흐르나?** GUI 하단 timeline 이 움직이는지. 안 흐르면 `World.play()` 호출 필요 (헤드리스).
4. **Action Graph 에 red 노드 없나?** Window → Visual Scripting → Action Graph → 빨갛게 표시되는 노드는 evaluation 실패. 마우스 hover 로 에러 메시지 확인.
5. **Console 메시지 확인**: Window → Console. `[omni.graph]`, `[isaacsim.ros2.bridge]` prefix 의 ERROR/WARN.
6. **호스트 ROS distro 일치?** `installation.md` §7. 다른 distro 면 토픽 자체가 안 보임.
7. **`RMW_IMPLEMENTATION` 일치?** 두 셸에서 모두 `echo $RMW_IMPLEMENTATION` → 동일.
8. **`ROS_DOMAIN_ID` 일치?** 디폴트 0 이지만 동료가 바꿔놨을 수 있음.
9. **QoS 매칭?** `ros2 topic info -v /<topic>` 으로 publisher/subscriber 의 QoS 보기. RELIABLE ↔ BEST_EFFORT mismatch 면 메시지 0.
10. **방화벽 / 브리지 호스트 차이**: Docker 컨테이너 안의 Isaac Sim 과 host 의 외부 노드 → `--network=host` 필요.

체크리스트가 다 통과했는데도 안 되면, **다른 graph 가 같은 토픽으로 발행하지 않는지** 확인. 두 OG 가 같은 topicName 으로 publish 하면 둘이 경합 → 토픽은 보이지만 데이터가 깨질 수 있다.

## 13. 자주 발생하는 OG 함정

| 증상 | 원인 | 해결 |
|---|---|---|
| 노드가 회색 (실행 안 됨) | execution edge 누락 | 흰색 edge 로 `OnPlaybackTick → execIn` |
| 첫 한 번만 발행되고 멈춤 | `OnPlaybackTick` 대신 `OnLoaded` 썼음 | `OnPlaybackTick` 으로 교체 |
| 발행 주기가 60Hz 가 아닌 30Hz | render rate 와 physics rate 분리 | `IsaacRunOneSimulationFrame` 을 매 tick 마다 |
| 같은 OG 가 두 번 실행됨 | 그래프 복제됨 | Stage 에서 중복 그래프 prim 확인 후 삭제 |
| `targetPrim` 이 valid path 인데 noting happens | prim path 가 articulation root 가 아님 | `usd-from-urdf.md` §3 |
| Camera 토픽은 발행되는데 K 가 이상 | `focalLength` / `horizontalAperture` 미설정 | §6 의 sed 식 적용 |
| Subscribe 가 data 를 안 받음 | qos mismatch 또는 topic name typo | `ros2 topic info -v` |
| 그래프가 Stage 저장 후 사라짐 | `evaluator_name` 미지정 | edit() 호출 시 `evaluator_name: "execution"` |
| 노드 색이 노랑 (deprecated) | 6.0 에서 모듈 경로 변경 | `omni.isaac.ros2_bridge.*` → `isaacsim.ros2.bridge.*` |
| Python 에서 만든 그래프가 빈 화면 | Stage 가 아직 안 열림 | `omni.usd.get_context().new_stage_async()` 후 edit |

## See also

- `installation.md` §7 — ROS 2 distro 매트릭스
- `usd-from-urdf.md` §3 — articulation root (JointState publisher 가 가리킬 곳)
- `physx-tuning.md` §"Control rate" — 시뮬 rate 와 ROS 토픽 rate
- `isaac-ros-accel.md` §"NITROS zero-copy" — GPU 메시지로 OG → Isaac ROS 노드 직접 전달
- `ros2-architect` 스킬: `references/communication.md` (QoS), `references/tf2-urdf.md` (TF), `references/debugging.md` (ros2 doctor)
- 원문: `02-ros2-bridge/ros2_tutorials/`, `03-omnigraph/omnigraph/`
