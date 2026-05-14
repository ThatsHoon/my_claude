# Multi-Robot 시나리오와 두산 코드의 구조적 함정

이 문서는 **두산 ROS2 스택의 알려진 약점과 회피 전략** 을 정리한다. 단순한 known issues 보다
한 단계 더 들어가서, 왜 그렇게 됐고 어떻게 해결하는지를 다룬다.

## 1. multi-robot 미지원 — DSR_ROBOT2.py 의 빈 prefix

### 증상

같은 머신에서 두 m0609 로봇을 다루려고 하면 두 번째 로봇이 반응 안 함.

### 원인

`dsr_common2/imp/DSR_ROBOT2.py` line 39 근처:

```python
_srv_name_prefix = ''                    # ← 비어있음
_ros2_movej = g_node.create_client(MoveJoint, "dsr01/motion/move_joint")
_ros2_movel = g_node.create_client(MoveLine, "dsr01/motion/move_line")
# ... 나머지도 모두 dsr01/ 하드코딩
```

서비스 이름이 모듈 import 시점에 `dsr01/...` 로 박힌다. `_srv_name_prefix` 가 빈 문자열이라 다
른 로봇 (예: `dsr02`) 으로 바꿀 수 없다.

Python 의 모듈 캐싱 때문에 두 번째로 import 해도 같은 객체가 반환돼 인자도 의미 없다.

### 회피 전략 3가지

#### 전략 A — raw rclpy 직접 사용 (권장)

```python
import rclpy
from rclpy.node import Node
from dsr_msgs2.srv import MoveJoint

class TwoRobotController(Node):
    def __init__(self):
        super().__init__('two_robot_ctrl')
        self.movej1 = self.create_client(MoveJoint, '/dsr01/motion/move_joint')
        self.movej2 = self.create_client(MoveJoint, '/dsr02/motion/move_joint')

    def move_both(self, q1, q2):
        # ... 두 future 를 병렬로 spin
```

DSR_ROBOT2 wrapper 의 편의 함수는 못 쓰지만, namespace 가 깨끗하게 분리됨.

#### 전략 B — 프로세스 분리

각 로봇을 별도 Python 프로세스에서 실행. 각 프로세스가 자기 namespace 로 노드를 생성. 로봇 간
통신은 토픽으로. 가장 안정적이지만 멀티프로세스 동기화 복잡.

```bash
ROBOT_ID=dsr01 python3 robot1_main.py &
ROBOT_ID=dsr02 python3 robot2_main.py &
```

`DSR_ROBOT2.py` 를 패치해서 환경변수에서 namespace 를 읽도록:

```python
import os
_ROBOT_ID = os.environ.get('ROBOT_ID', 'dsr01')
_ros2_movej = g_node.create_client(MoveJoint, f"{_ROBOT_ID}/motion/move_joint")
```

이건 forward-compat 깨질 수 있으니 패치 사실을 README 에 명시.

#### 전략 C — `ROS_DOMAIN_ID` 분리

두 로봇 PC 가 별도 도메인 ID 라면 같은 LAN 에서 다른 그래프로 분리됨. 각 PC 에서:

```bash
ROS_DOMAIN_ID=25 ros2 launch dsr_bringup2 ... # 로봇 1
ROS_DOMAIN_ID=26 ros2 launch dsr_bringup2 ... # 로봇 2
```

다중 로봇이지만 사실상 독립 환경. 협업이 필요하면 cross-domain bridge 가 필요해 복잡.

## 2. service-call deadlock — `client.call()` 동기 호출의 함정

### 증상

콜백 안에서 `service_client.call(req)` 를 부르면 영원히 대기.

### 원인

rclpy 의 기본 spin 모델은 single-threaded executor + mutually-exclusive callback group. 한 콜
백이 실행 중이면 같은 노드의 다른 콜백 (service response 콜백 포함) 이 동시에 못 돈다. 즉
"내가 service 응답을 기다리는 콜백" 이 응답 콜백을 막아 자기 자신을 deadlock 한다.

### 해결

3가지 패턴 — `ros2-architect` 스킬의 `node-design.md §Executors` 와 동일.

**Fix 1**: `call_async` + done callback. 가장 간단.

**Fix 2**: `MultiThreadedExecutor` + `ReentrantCallbackGroup`.

**Fix 3**: `spin_until_future_complete(node, future)`. DSR_ROBOT2 가 내부적으로 이걸 쓴다. 다만
호출자가 이미 콜백 안이면 안 됨 — 외부 (메인 스레드) 에서만.

DSR_ROBOT2 의 motion 함수가 `spin_until_future_complete` 를 쓰기 때문에, 사용자 콜백 안에서
`movej(...)` 부르면 deadlock 가능성이 있다. 사용자 콜백에서 모션 호출 필요 시 → 별 스레드로
디스패치 (`executer.py` 의 Dispatcher/Worker 패턴, CLAUDE.md "멀티스레드 분리" 참고).

## 3. mode-locked at boot — virtual ↔ real 동적 전환 불가

### 증상

`SetRobotSystem(ROBOT_SYSTEM_REAL)` 을 런타임에 부르고 싶지만 controller 무응답.

### 원인

`dsr_hw_interface2.cpp:on_init()` 에서 `SetRobotSystem` 이 한 번 호출되고 끝. 이후 변경은
DRFL 이 거부하거나 무시. 모드 변경하려면 controller_manager 를 죽이고 다시 launch.

### 해결

mode 변경 = 전체 bringup 재시작. CI 에서 두 모드 모두 테스트하려면 launch group 을 분리:

```yaml
# matrix.yaml
test_matrix:
  - mode: virtual
  - mode: real
```

각 entry 마다 별도 process group 으로 launch + teardown.

## 4. 50ms 콜백 제약 — DRFL 콜백 안에서 무거운 일 금지

### 증상

비전/대용량 처리 코드를 DRFL 콜백 안에 넣으면 robot 이 멈추거나 응답 안 함.

### 원인

DRFL 라이브러리는 여러 모니터링 콜백을 자체 스레드에서 호출한다. 두산 문서가 **50ms 안에 반환
하라**고 명시 (dsr_controller2.cpp:105 주석에도 있음). 위반 시:

- 후속 콜백이 백업되어 데이터 stale.
- 심하면 DRFL 내부 watchdog 이 disconnection 을 발동.

### 해결

콜백 안에서는 **데이터 복사만** 하고, 처리는 별도 스레드 큐에서:

```cpp
// 콜백 — 빠르게 끝
void on_monitoring_data(const RobotData & data) {
  std::lock_guard<std::mutex> lk(mtx_);
  latest_data_ = data;     // 복사만
  data_ready_.store(true);
}

// 처리 스레드 — 무거운 일은 여기서
void worker() {
  while (running_) {
    if (data_ready_.exchange(false)) {
      RobotData copy;
      { std::lock_guard<std::mutex> lk(mtx_); copy = latest_data_; }
      // 무거운 처리...
    }
    std::this_thread::sleep_for(10ms);
  }
}
```

ROS 콜백 (subscription/timer) 도 같은 원칙. callback group 분리 + 무거운 일은 ReentrantGroup
의 별 timer 로 떠넘김.

## 5. M2.12 펌웨어 강제 — 다운그레이드 불가

### 증상

펌웨어가 오래된 컨트롤러 (M2.10 이하) 에 connect 시도 → "OnMonitoringDataCB 등록 실패" 류 에러.

### 원인

`dsr_hw_interface2.cpp:234-246` 에서 DRCF 버전 검사. M2.12 (121200) 미만이면 fail. graceful
degradation 안 함.

### 해결

펌웨어 업그레이드 외에 회피 없음. 두산 펜던트에서 M2.12+ 로 업데이트 후 재시도.

## 6. force/compliance 가 hardware_interface 경로로 노출 안 됨

### 증상

MoveIt 의 effort 컨트롤러 (`effort_controllers/JointGroupEffortController`) 가 동작 안 함.

### 원인

`dsr_hardware2` 가 `effort` command/state interface 를 export 안 함. `dsr_hw_interface2.cpp:
321,325` 에 TODO 명시.

### 해결

표준 ros2_control 경로를 우회하고 두산 force services 를 직접 호출:

```python
from dsr_msgs2.srv import TaskComplianceCtrl, SetDesiredForce

# 1) 강성 설정
node.create_client(TaskComplianceCtrl, '/dsr01/force/task_compliance_ctrl').call_async(...)

# 2) 목표 힘 인가
node.create_client(SetDesiredForce, '/dsr01/force/set_desired_force').call_async(...)
```

MoveIt 의 표준 effort 인터페이스를 기대하는 코드는 두산에서 동작 안 한다. 별 노드로 force
control 을 짜고, MoveIt 은 position trajectory 만 담당하게 분리.

## 7. RT 토픽 / RT 서비스가 virtual 에서 동작 안 함

### 증상

`mode:=virtual` 에서 `read_data_rt` 호출 → DR_Error 또는 무응답. `/rt_topic/<key>` 도 안 뜸.

### 원인

`dsr_hw_interface2.cpp:283-308` 의 RT setup 블록이 `if (mode != "virtual")` 조건 안에 있음. 따
라서 virtual 모드에서는:

- port 12347 connect 안 함.
- `start_rt_control` 호출 안 함.
- RT 데이터 자체가 갱신 안 됨.

### 해결

RT 가 필요한 코드는 real 모드에서만 테스트. virtual 모드는 motion service 시퀀스 검증용으로만
사용. CI 에 두 모드 분리.

## 8. coord_service 같은 서비스가 모션 중 무응답

### 증상

`get_current_posx()` 를 모션 중 호출 → 무한 대기.

### 원인

가상 컨트롤러 (emulator) 가 모션 실행 동안 service 요청을 처리할 thread 자원이 없는 듯. 실기
에서도 종종 발생.

### 해결

**좌표 폴링은 service call 대신 토픽 구독**:

- `/rt_topic/actual_tcp_position` 구독 (use_rt_topic_pub=true 필요)
- `tf2_ros.Buffer.lookup_transform('base_link', 'tool0', ...)` (robot_state_publisher 가 띄워
  주는 dynamic TF)
- `/dsr01/joint_states` + IK 자체 계산 (가벼움)

CLAUDE.md 의 "독립 대시형 서비스 노드" 섹션에 이 패턴이 정리돼 있다.

## 9. logger severity caching — 같은 라인에서 severity 변경 시 ValueError

### 증상

```python
log = self.get_logger().info if ok else self.get_logger().warn
log("status: %s" % msg)
```

→ `ValueError: Logger severity cannot be changed between calls`.

### 원인

rclpy 의 logger 가 (file, line) 으로 severity 를 캐시. 같은 라인에서 다른 severity 를 호출하면
캐시 충돌.

### 해결

severity 별로 라인 분리:

```python
if ok:
    self.get_logger().info(f'status: {msg}')
else:
    self.get_logger().warn(f'status: {msg}')
```

## 10. 다중 노드 cross-network DDS 부하

### 증상

서브 PC (현재 PC) 에서 메인노드 PC 의 `/joint_states` (100Hz), `/tf` (100Hz) 를 구독 → 메인PC 의
DSR service 응답이 느려짐.

### 원인

DDS 가 cross-network 로 100Hz 토픽을 fan-out 하면 multicast 패킷이 많아지고 메인 PC 의 ROS
graph 가 burst. service 응답 latency 증가.

### 해결

- `tf2_ros.Buffer` 의 lookup 주기를 10Hz 이하로 제한.
- 정말 빠르게 필요하면 같은 PC 에서 처리 (별도 노드).
- `ROS_LOCALHOST_ONLY=1` 또는 도메인 ID 분리 사용 검토.

## 11. DSR g_node 와 같은 executor 의 subscription 이 starve 되는 함정

### 증상

PyQt5 GUI 같은 long-running 프로세스에서 단일 노드에 (a) DSR_ROBOT2 g_node 등록 + (b)
`/dsr01/joint_states` subscription 을 함께 두고 `MultiThreadedExecutor.spin()` 을 돌리면,
`ros2 topic hz` 로는 publisher 가 100Hz 인데도 노드 측 콜백 카운터가 **0.3Hz** 정도만 증가한다.

진단 로그에서 정확히 **3 초마다 +1** 메시지 도착 패턴이 관찰됨 (= 모드 폴링 timer 주기와 일치).
20초 시연 기록에 7~9개 샘플만 적재되는 catastrophic data loss.

### 원인

DSR_ROBOT2.py 의 모든 service 호출은 다음 패턴:

```python
future = client.call_async(req)
rclpy.spin_until_future_complete(g_node, future)
```

`spin_until_future_complete` 는 글로벌 executor (= 우리 `MultiThreadedExecutor`) 의 spin lock 을
점유한다. 다른 thread 가 이미 `executor.spin()` 으로 spin 중이면 두 spin caller 가 같은 lock 을
경합 → subscription dispatch 가 starve. 모드 폴링 timer 가 3 초마다 service 호출을 끝낼 때마다
subscription 이 1 개씩만 빠져나오는 양상.

`callback_group=ReentrantCallbackGroup()` 으로 묶어도 효과 없음. spin lock 경합은 callback group
보다 상위 계층에서 발생하기 때문.

### 해결 (rclpy 공식 권장 패턴)

**subscription 을 별도 노드 + 별도 executor + 별도 thread 로 격리**.

```python
# DSR g_node 전용 (MultiThreadedExecutor, 글로벌)
class DsrNode(Node):                       # subscription 없음
    def __init__(self):
        super().__init__("dsr_node", namespace="dsr01")

# Subscription 전용 (SingleThreadedExecutor, 별도 thread)
class JointStateNode(Node):
    def __init__(self, on_joint):
        super().__init__("joint_state_listener", namespace="dsr01")
        qos = QoSProfile(depth=50,
                         reliability=ReliabilityPolicy.BEST_EFFORT,
                         history=HistoryPolicy.KEEP_LAST)
        self.create_subscription(JointState, "/dsr01/joint_states",
                                 lambda m: on_joint(m), qos)

# Thread 1: DSR g_node + 글로벌 MultiThreadedExecutor
ros_exec = MultiThreadedExecutor(num_threads=4)
rclpy.__executor = ros_exec               # DSR_ROBOT2 가 사용
ros_exec.add_node(DsrNode())
threading.Thread(target=ros_exec.spin, daemon=True).start()

# Thread 2: subscription 전용 SingleThreadedExecutor
js_exec = SingleThreadedExecutor()
js_exec.add_node(JointStateNode(on_joint=...))
threading.Thread(target=js_exec.spin, daemon=True).start()
```

→ DSR service 호출이 글로벌 executor 의 spin 자원을 점유해도 별도 executor 의 subscription
dispatch 는 무관 → 100Hz 정상 처리.

### 참고: QoS 도 BEST_EFFORT 권장

`joint_state_broadcaster` publisher 는 비표준적으로 **RELIABLE + TRANSIENT_LOCAL**. subscriber 가
RELIABLE 이면 ack 처리 지연이 누적되어 backpressure 가 동시 발생할 수 있음. `robot_state_publisher`
도 BEST_EFFORT + VOLATILE 로 받고 있으므로 동일 QoS 사용이 안전.

### 검증 방법

```bash
# publisher 발행률 (CLI 는 별도 프로세스 → 100Hz 가 정상)
ros2 topic hz /dsr01/joint_states

# 노드 측 실효 처리율을 알려면 subscription callback 카운터 추가
# (예: gui.py 의 JointStateNode.diag_snapshot 패턴)
```

ros2 topic hz 가 100Hz 인데 우리 노드는 0.3Hz 면 **무조건 이 함정**.

### 사례 — ros2_move_recoder

`/home/hoon/cobot_ws/src/ros2_move_recoder/ros2_move_recoder/gui.py` 의 `JointStateThread` /
`JointStateNode` / `RosSpinThread` / `MacroNode` 분리 구조가 이 패턴의 실제 적용 사례.
실측 0.3Hz → 100Hz 회복 확인됨 (2026-04-28).

### 비고

- `callback_group` 을 ReentrantCallbackGroup 으로 바꾸는 것만으로는 해결 안 됨 (실측 확인).
- `executor.spin_once(timeout)` loop 도 해결 안 됨 (단일 thread 처리율로 떨어짐, ≤10Hz).
- 같은 함정이 `realtime_scan/coord_service` 류와 동시 실행 시에도 발생 가능. 해당 서비스도
  `wait_for_motion_status` 같은 동기 호출을 갖고 있으면 같은 spin lock 경합.
- DSR_ROBOT2 vendor 코드 자체는 수정 불가 (executor 분리로 우회).

## 정리 — 이 함정들의 공통 교훈

1. **두산 ROS2 스택은 single-robot, single-process, single-mode 를 가정해 만들어졌다.** 그 가
   정을 벗어나면 워크어라운드가 필요하다.
2. **서비스보다 토픽을 우선시.** state 폴링, 좌표 조회, 상태 모니터링은 거의 다 토픽으로 가능.
   service 는 motion 같이 한 번만 호출하는 명령에만.
3. **콜백은 빠르게, 무거운 일은 별 스레드로.** ROS 2 콜백 모델 + DRFL 50ms 제약 두 군데서 같
   은 원칙이 강제된다.
4. **mode 결정은 boot 시점.** 런타임 변경 가정 금지.
5. **펌웨어 / DRCF 버전이 호환성의 기반.** M2.12 미만은 그냥 안 됨.

이 함정들은 CLAUDE.md "Known Issues" 섹션과 일관된 메시지를 보낸다. 코드 작성 전 이 두 문서를
함께 읽으면 90% 의 함정을 사전에 피할 수 있다.
