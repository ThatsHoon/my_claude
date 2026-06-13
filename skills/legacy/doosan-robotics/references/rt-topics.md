# RT Topics — 두산 컨트롤러의 실시간 데이터 푸시

`/rt_topic/<key>` 토픽 군과 `*_rt_stream` 토픽 군은 두산 ROS2 스택의 가장 강력하면서도 자주
오해되는 부분이다. 이 문서는 코드 (`dsr_controller2.cpp`, `dsr_realtime_control.cpp`) 의 실제
동작에 기반한다.

## 둘은 다른 것이다

| 패밀리 | 방향 | 발행자 | 용도 |
|---|---|---|---|
| `/rt_topic/<key>` | controller → 사용자 | dsr_controller2 (timer-driven) | **읽기** — RT 레이어의 실값 (joint pos/vel, TCP, torque, jacobian, ...) |
| `*_rt_stream` (servoj_rt_stream 등) | 사용자 → controller | 사용자 코드 | **쓰기** — 1kHz RT 명령 |

자주 헷갈리는 점: `torque_rt_stream` 은 **사용자가 publish 해서 컨트롤러에 토크 명령을 주는**
토픽이다. RT 토크 *상태* 를 읽으려면 `/rt_topic/actual_motor_torque` 같은 `/rt_topic/<key>` 를
구독한다.

## `/rt_topic/<key>` — 읽기 패밀리

### 활성화 방법

`dsr_controller2.yaml` 에서:

```yaml
dsr_controller2:
  ros__parameters:
    use_rt_topic_pub: true
    rt_timer_ms: 10                    # 10ms = 100Hz publish rate
    rt_topic_keys:
      - actual_joint_position          # /rt_topic/actual_joint_position (deg)
      - actual_tcp_position            # /rt_topic/actual_tcp_position (mm/deg ZYZ)
      - actual_joint_velocity
      - actual_tcp_velocity
      - external_tcp_force
      - external_joint_torque
      # ... 더 많은 키 가능
```

키 활성화는 동적이지 않다. yaml 수정 후 controller_manager 재시작 필요.

### 사용 가능한 모든 키 (`extract_field()` 함수 기준)

상태:
- `actual_joint_position` (deg, 6원소)
- `actual_joint_velocity` (deg/s, 6원소)
- `actual_motor_torque` (N·m, 6원소)
- `actual_joint_torque` (N·m, 6원소)
- `external_joint_torque` (N·m, 6원소)
- `actual_tcp_position` (mm/deg ZYZ, 6원소)
- `actual_tcp_velocity` (mm/s + deg/s, 6원소)
- `actual_flange_position` (mm/deg ZYZ, 6원소)
- `actual_flange_velocity`
- `external_tcp_force` (N + N·m, 6원소)
- `target_joint_position` (deg, 6원소)
- `target_tcp_position`

행렬 (6×6, 36원소로 평탄화):
- `jacobian_matrix`
- `mass_matrix`
- `coriolis_matrix`

기타:
- `time_stamp`
- `is_robot_connected`

### 메시지 타입과 구독 패턴

모든 `/rt_topic/<key>` 는 `std_msgs/Float32MultiArray`. 구독 코드:

```python
from std_msgs.msg import Float32MultiArray

def joint_pos_cb(msg):
    # msg.data 는 [j1, j2, j3, j4, j5, j6] (deg)
    print(msg.data[:6])

node.create_subscription(
    Float32MultiArray,
    '/rt_topic/actual_joint_position',
    joint_pos_cb,
    10  # depth
)
```

### `/joint_states` vs `/rt_topic/actual_joint_position` 차이

| 비교 | `/joint_states` | `/rt_topic/actual_joint_position` |
|---|---|---|
| 단위 | rad | **deg** |
| 발행자 | controller_manager 의 joint_state_broadcaster | dsr_controller2 자체 |
| 출처 | hardware_interface state_interfaces | DRFL `read_data_rt()` |
| QoS | RELIABLE | RELIABLE |
| 메시지 | sensor_msgs/JointState (이름·위치·속도·effort) | std_msgs/Float32MultiArray (값만) |
| 추천 용도 | tf2/RViz/MoveIt | 빠른 RT 폴링, 사용자 노드 자체 처리 |

`use_rt_topic_pub=false` (기본) 면 `/rt_topic/<key>` 자체가 안 뜬다. 이때는 `/joint_states` 또
는 `tf2_ros.TransformListener` 로 폴백.

### 모션 중에도 안전한가

그렇다. `/rt_topic` publish 는 `dsr_controller2` 의 별도 wall_timer 에서 동작한다. service 핸
들러 (motion service 처리) 와 분리돼 있어 모션 실행 중에도 갱신된다. 이게 `get_current_posx()`
서비스 호출이 모션 중 무응답이 되는 문제의 우회로다 (CLAUDE.md "Known Issues" 참고).

## `*_rt_stream` — 쓰기 패밀리 (1kHz 사용자 명령)

### 종류

| 토픽 | 메시지 | vel/acc 차원 |
|---|---|---|
| `/dsr01/servoj_rt_stream` | `dsr_msgs2/ServojRtStream` | 6원소 |
| `/dsr01/servol_rt_stream` | `dsr_msgs2/ServolRtStream` | 6원소 |
| `/dsr01/speedj_rt_stream` | `dsr_msgs2/SpeedjRtStream` | 6원소 |
| `/dsr01/speedl_rt_stream` | `dsr_msgs2/SpeedlRtStream` | 6원소 |
| `/dsr01/torque_rt_stream` | `dsr_msgs2/TorqueRtStream` | — |

대비: 비-RT 버전 (`/dsr01/servol_stream` 등) 은 vel/acc 가 [translation, rotation] **2원소** 벡
터다. 이거 헷갈려서 같은 이름인 줄 알고 잘못 채우는 게 가장 흔한 함정.

### 사전 조건

```python
# 1) RT 연결 (real 모드 전용)
from dsr_msgs2.srv import ConnectRtControl, SetRtControlOutput, StartRtControl
# ... 셋 다 호출 ...

# 2) RT 활성화 후
servoj_rt_pub = node.create_publisher(ServojRtStream, '/dsr01/servoj_rt_stream', 10)

# 3) 1kHz 타이머에서 발행
def tick():
    msg = ServojRtStream()
    msg.pos = [..., ..., ...]   # 6원소 deg
    msg.vel = [..., ..., ...]   # 6원소 deg/s
    msg.acc = [..., ..., ...]   # 6원소 deg/s²
    msg.time = 0.001
    servoj_rt_pub.publish(msg)

node.create_timer(0.001, tick)   # 1ms = 1kHz
```

### 1kHz 가 실제로 필요할 때만 써라

PREEMPT_RT 커널이 아닌 일반 Ubuntu 에서 wall_timer 의 jitter 는 수 ms 까지 튄다. 1kHz 를 약속
하지만 실제로는 ~100Hz 정도가 안정적인 한계. 과도한 publish rate 는 컨트롤러 큐를 오염시킨다.

대안: 일반 `*_stream` (servol_stream 등) 은 controller 가 내부 보간을 해주니 100Hz 만 발행해도
충분히 부드럽다. RT 가 필요하면 `dsr_realtime_control` C++ 패턴을 따라 멀티노드 + 수동 동기화
로 가라 (`codebase-architecture.md` §8 참고).

## 일반 stream — `*_stream` (1ms 보간 controller-side)

| 토픽 | 메시지 | 용도 |
|---|---|---|
| `/dsr01/servoj_stream` | `ServojStream` | 관절 위치 + vel/acc 보간 추종 |
| `/dsr01/servol_stream` | `ServolStream` | TCP 위치 + vel/acc 보간 |
| `/dsr01/speedj_stream` | `SpeedjStream` | 관절 속도 명령 |
| `/dsr01/speedl_stream` | `SpeedlStream` | TCP 속도 명령 |

이건 virtual / real 모두 동작. 100Hz 로 publish 하면 컨트롤러가 1ms 단위로 보간해 모터를 구
동. 우리에게는 가장 실용적인 비동기 모션 채널.

## alter_motion — 모션 중 경로 보정

비전이나 외력 측정 결과를 모션에 실시간 반영하는 채널.

```python
from dsr_msgs2.srv import EnableAlterMotion, DisableAlterMotion
from dsr_msgs2.msg import AlterMotionStream

# 1) enable
node.create_client(EnableAlterMotion, '/dsr01/motion/enable_alter_motion').call_async(...)

# 2) 메인 모션 시작 (예: amovel)
movel(target, vel=100, acc=200, _async=1)

# 3) 보정 stream publish
alter_pub = node.create_publisher(AlterMotionStream, '/dsr01/alter_motion_stream', 10)

def vision_cb(detection):
    # 외력/비전에서 받은 보정값 publish
    msg = AlterMotionStream()
    msg.delta = [dx, dy, dz, drx, dry, drz]
    alter_pub.publish(msg)

# 4) 모션 끝나면 disable
node.create_client(DisableAlterMotion, '/dsr01/motion/disable_alter_motion').call_async(...)
```

`enable_alter_motion` 호출이 빠지면 stream 발행해도 무시됨.

## 디버깅 — RT 토픽이 안 뜨는 6가지 이유

```bash
# 1) controller 가 use_rt_topic_pub=true 로 떴는지
ros2 param get /dsr_controller2 use_rt_topic_pub

# 2) yaml 의 rt_topic_keys 에 원하는 키가 있는지
ros2 param get /dsr_controller2 rt_topic_keys

# 3) 토픽 자체가 publish 되는지
ros2 topic hz /rt_topic/actual_joint_position

# 4) QoS 가 맞는지 (RELIABLE+VOLATILE 표준)
ros2 topic info /rt_topic/actual_joint_position --verbose

# 5) virtual 모드면 RT 자체가 동작 안 함 (real 모드만)
ros2 param get /dsr_controller2 mode

# 6) controller 라이프사이클 상태
ros2 lifecycle get /dsr_controller2
```

자주 나오는 증상:

- "actual_joint_position 만 뜨고 jacobian_matrix 가 안 뜸" → yaml 의 `rt_topic_keys` 리스트
  점검. 활성화한 키만 publish.
- "RT 가 처음엔 잘 되다가 어느 순간 끊김" → 네트워크/포트 12347 이슈. `connect_rt_control` 재
  호출 또는 controller 라이프사이클 재시작.
- "값이 NaN 또는 0 으로 옴" → mode=virtual 또는 real 모드 + RT 미활성. `start_rt_control` 호출
  여부 확인.

## 코드 인용

가장 가까운 RT 패턴: `dsr_example2/dsr_realtime_control/src/dsr_realtime_control.cpp`. 4-노드
구조 + std::mutex + std::atomic 으로 1kHz publish 를 구현했다. 같은 일을 Python 으로 하면
GIL 때문에 jitter 가 커져서 RT 의 의미가 사라진다.

`dsr_controller2.cpp:120-131, 146-299` 가 `/rt_topic/<key>` publisher 동적 생성과 timer 콜백
구현을 담고 있다. 새 키를 추가하고 싶으면 여기 `extract_field()` 의 case 를 늘리면 된다.
