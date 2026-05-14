# Doosan-Robot2 Codebase Architecture (Code-Grounded)

이 문서는 `~/cobot_ws/src/doosan-robot2/` 의 실제 코드를 분석한 결과다. SKILL.md 의 일반 함수
레퍼런스가 *어떻게 호출되는가* 를 다룬다면, 이 문서는 *왜 그렇게 동작하는가* 를 다룬다. 모든
주장은 파일 경로와 라인 번호로 추적 가능하다.

## TOC

1. 4계층 구조 다시 보기 — 코드 위치
2. dsr_controller2 — 표준 ros2_control 가 아닌 이유
3. dsr_hardware2 — 흔치 않은 hardware_interface 패턴
4. dsr_bringup2 launch — 모드 분기와 xacro 전파
5. dsr_msgs2 — 161개 인터페이스 카탈로그
6. dsr_common2 / DSR_ROBOT2.py — Python 래퍼 내부
7. DRFLEx — vendor C++ API 의 이상한 부분
8. dsr_realtime_control — 1kHz C++ 패턴 분해
9. dsr_moveit2 / dsr_description2 — m0609 변형 처리
10. 알려진 TODO 및 구조적 약점

## 1. 4계층 구조 다시 보기 — 코드 위치

| 계층 | 디렉토리 | 진입점 |
|---|---|---|
| Python 사용자 코드 | (사용자 작성) | `import DSR_ROBOT2` 직후 g_node 사용 |
| **DSR_ROBOT2.py** | `dsr_common2/imp/DSR_ROBOT2.py` | 모듈 import 시점에 ~100개 service client 생성 |
| **dsr_controller2** (controller plugin) | `dsr_controller2/src/dsr_controller2.cpp` | controller_manager 가 동적 로드 |
| **dsr_hardware2** (hardware plugin) | `dsr_hardware2/src/dsr_hw_interface2.cpp` | controller_manager 가 동적 로드 |
| **DRFL** (vendor C++) | `dsr_common2/lib/libdsr*.so` (binary), `dsr_common2/include/DRFLEx.h` | dsr_controller2/dsr_hardware2 가 직접 호출 |
| **DRCF** (펌웨어/에뮬레이터) | 별도 프로세스, port 12345 | TCP 연결 |

이 그림에서 가장 의외인 점: **dsr_controller2 는 ros2_control 의 표준 컨트롤러가 아니다**. 다음
섹션에서 설명한다.

## 2. dsr_controller2 — 표준 ros2_control 가 아닌 이유

`dsr_controller2/src/dsr_controller2.cpp` 의 진실:

- `command_interface_configuration()` 와 `state_interface_configuration()` 가 **빈 벡터를 반환**
  한다 (line ~89-95). 즉 ros2_control 의 standard interface 시스템을 거의 사용하지 않는다.
- 컨트롤러가 직접 DRFL 객체(`Drfl`, dsr_controller2.cpp:30-31, extern 전역)에 접근해 모션 서비
  스를 호출한다. 표준이라면 `read()/write()` 사이클에서 command/state interface 만 만지고 끝나
  야 한다.
- 결과: **모든 모션이 service-driven** 이다. controller_manager 의 1kHz update loop 에 motion
  실행이 들어가지 않는다. update loop 은 거의 비어있다.

**왜 이렇게 했는가** (추정): DRFL 이 자체적으로 motion blending, trajectory generation, force
control 같은 고수준 기능을 갖고 있어서 ros2_control 에 다시 구현할 가치가 없다. controller_
manager 는 단지 "이 plugin 을 로드하고 라이프사이클을 관리해주는 셸" 정도로 쓰인다.

**우리에게 주는 의미**:

- m0609 에 쓸 때는 표준 `JointTrajectoryController` 와 같은 기대를 갖지 마라. 모션은 service
  call (`/dsr01/motion/move_joint` 등) 로 보낸다.
- ros2_control 의 `controller_manager` CLI (`ros2 control list_controllers`) 는 동작하지만, 그
  결과가 우리가 익숙한 의미와는 다르다. 두산 controller 는 "loaded, active" 여도 별도 동작이
  필요 없다.
- MoveIt2 와 통합할 때만 표준 `JointTrajectoryController` 가 별도로 등장한다 (`dsr_controller2
  /dsr_joint_trajectory_plugin.xml` 참고).

### dsr_controller2 가 라이프사이클에서 하는 일

`on_configure()` (dsr_controller2.cpp:75-143) 에서:

1. `Drfl` 전역에 모드/호스트/포트 설정.
2. **DRFL 콜백 10개 등록** (line 105-118):
   - `set_on_tp_initializing_completed` — 컨트롤러 초기화 완료
   - `set_on_monitoring_data_ex` — 30Hz 주기 모니터링 데이터
   - `set_on_monitoring_ctrl_io` — DI/DO 변경 이벤트
   - `set_on_monitoring_state` — STATE_STANDBY/MOVING/SAFE_STOP 등 전이
   - `set_on_log_alarm` — 알람 메시지
   - `set_on_monitoring_modbus`
   - `set_on_disconnected`, `set_on_program_stopped` 등
3. 콜백은 DRFL 내부 스레드에서 호출되며 **50ms 안에 반환해야 한다**. 무거운 처리는 큐로 넘겨야
   안전 (코드 주석에 명시).
4. `use_rt_topic_pub` 파라미터가 true 면 `/rt_topic/<key>` Float32MultiArray 퍼블리셔를 동적으
   로 생성 (line 120-131, 146-299).

`on_activate()` 에서 100Hz `wall_timer` 로 `read_data_rt()` 호출 → RT 토픽 publish. 이게 RT
publishing 의 실제 메커니즘이다.

## 3. dsr_hardware2 — 흔치 않은 hardware_interface 패턴

`dsr_hardware2/src/dsr_hw_interface2.cpp`:

- `on_init()` (line 47-) 에서 host/port/mode/model/update_rate 를 `hardware_parameters` 로 받는
  다 (URDF 의 `<param>` 에서 옴, ROS 파라미터 아님).
- DRFL 에 20번 0.5초 간격 retry 로 연결 (line 138-146).
- **virtual 모드**: `SetRobotSystem(ROBOT_SYSTEM_VIRTUAL)` 후 RT setup 건너뜀 (line 270-308).
  emulator (port 12345) 와 일반 control 만 가능, RT 서비스 (port 12347) 는 동작 안 함.
- **real 모드**: DRCF 버전 확인 → `connect_rt_control(rt_host, 12347)` → `set_rt_control_output()`
  → `start_rt_control()` 순서. 이 셋이 빠지면 `read_data_rt`/`servoj_rt_stream` 등이 무응답.
- `read()` / `write()` **오버라이드가 보이지 않는다** (line 313-329). 즉 hardware_interface 가
  표준 update cycle 을 돌지 않는다.
- `export_command_interfaces()` 는 position/velocity 만 export, **effort 는 TODO** (line 321,325).
  Force control 은 controller services 로 가능하나 hardware_interface 경로는 막혀있다.

### 우리에게 주는 의미

- **mode 는 부팅 시 결정되고 바뀌지 않는다.** real → virtual 동적 전환 불가. CI 에서 virtual
  로 테스트하려면 launch 시 `mode:=virtual` 로 시작.
- **DRCF 펌웨어 버전 ≥ M2.12** 가 강제다. 미달이면 `OnMonitoringDataCB` (구식) 가 없어서
  callback 등록 실패. 다운그레이드 불가능한 hard dependency.
- `rt_host` 는 보통 `host` 와 같지만, DRCF 3.0~3.4 에서는 강제로 같게 설정된다 (line 284-286).
  3.5+ 라면 분리 가능.
- effort 컨트롤이 필요하면 controller services (`task_compliance_ctrl`, `set_desired_force`) 를
  쓰고, MoveIt 의 effort 인터페이스 기대는 버려라.

## 4. dsr_bringup2 launch — 모드 분기와 xacro 전파

`dsr_bringup2/launch/dsr_bringup2_gazebo.launch.py` 가 가장 복잡한 진입점. 핵심:

- **launch arg → xacro 인자 → URDF**: `Command(['xacro ', urdf_path, ' host:=', host, ' port:=',
  port, ' mode:=', mode, ...])` (line 61-81). xacro 는 mode 에 따라 `m0609.ros2_control.xacro`,
  `m0609.gz_ros2_control.xacro`, `m0609.mj_ros2_control.xacro` 중 하나를 include.
- **emulator 자동 기동**: `mode == 'virtual'` 이면 `dsr_bringup2/run_emulator` Python 노드를 함
  께 spawn (line 96-116). 이게 port 12345 에서 DRCF 흉내를 낸다.
- **gazebo / mujoco / 실기**: `use_gazebo`, `use_mujoco` 별도 플래그. 각각 다른 ros2_control
  xacro 가 들어감.
- **namespace 통일**: 모든 노드가 `LaunchConfiguration('name')` (default `dsr01`) 아래 묶임.
  `joint_states` 는 `/dsr/joint_states` 로 remap (line 89).

### 표준 launch 명령

```bash
# 가상 모드 (emulator + DRFL on localhost:12345)
ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py \
    mode:=virtual host:=127.0.0.1 port:=12345 model:=m0609

# 실기 모드 (실제 컨트롤러 IP 192.168.1.100)
ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py \
    mode:=real host:=192.168.1.100 port:=12345 model:=m0609
```

이 두 줄은 CLAUDE.md 에도 있지만, 그 뒤에서 어떤 모드 분기가 일어나는지는 위 분석으로 확인.

## 5. dsr_msgs2 — 161개 인터페이스 카탈로그

`/home/hoon/cobot_ws/src/doosan-robot2/dsr_msgs2/{srv,msg,action}/` 에 정의됨. 카테고리별 srv 디
렉토리 구조가 그대로 `/home/hoon/Documents/services/<category>/` 와 일치. 즉:

```
dsr_msgs2/srv/motion/MoveJoint.srv      → /home/hoon/Documents/services/motion/move_joint.md
dsr_msgs2/srv/realtime/ReadDataRt.srv   → /home/hoon/Documents/services/realtime/read_data_rt.md
```

Documents 의 md 파일은 이 srv 파일의 사용 설명서다. 어떻게 쓰는지는 `dev-docs-index.md` 참고.

### 카테고리별 개수 (확정)

| 카테고리 | srv 개수 | 용도 |
|---|---|---|
| motion | 26 | movej/movel/movec/spline/jog/blending/spiral/periodic/alter |
| force | 23 | compliance/desired_force/parallel/align/user_cart_coord |
| aux_control | 18 | get_current_*, get_desired_*, joint/external_torque |
| realtime | 16 | read_data_rt, set_v*_rt, connect/start/stop_rt_control |
| system | 14 | robot_mode/system/state/safety/control |
| io | 10 | digital/analog input/output |
| drl | 5 | drl_start/stop/pause/resume, get_drl_state |
| tool | 5 | add/delete tool, current/get tool |
| tcp | 4 | add/delete tcp, current/get tcp |
| modbus | 4 | add/delete modbus signal, read/write |
| **합계 srv** | **143** | |
| msg | 18 | RobotState, *Stream, *RtStream, AlterMotionStream |
| action | 3 | MovejH2r, MovelH2r, JogH2r |

### 메시지/액션의 위치

- **18개 msg** 는 거의 다 stream 류. ServojStream/ServolStream 등은 토픽으로 publish 하는 비
  동기 모션 명령. RobotState/RobotError 는 컨트롤러가 publish 하는 상태.
- **3개 action** 은 H2R (Hand to Robot) 동작용. 사람이 이끄는 시연 학습 같은 패턴.

## 6. dsr_common2 / DSR_ROBOT2.py — Python 래퍼 내부

`dsr_common2/imp/DSR_ROBOT2.py` 의 핵심 패턴 (line 30-150):

```python
# 모듈 최상단 — import 즉시 실행
g_node = DR_init.__dsr__node          # 이 시점의 노드 영구 고정
_srv_name_prefix = ''                 # ← 이게 빈 문자열인 게 multi-robot 버그
_ros2_movej = g_node.create_client(MoveJoint, "dsr01/motion/move_joint")
# ... 100여 개 클라이언트 같은 노드에 등록
```

`movej(...)` 호출 시:

```python
def movej(pos, vel, acc, ...):
    req = MoveJoint.Request()
    req.pos = pos
    # ... fill request ...
    future = _ros2_movej.call_async(req)
    rclpy.spin_until_future_complete(g_node, future)   # 타임아웃 없음, 무한 블록 가능
    return future.result()
```

### 우리에게 주는 의미

- DSR_ROBOT2 import **이전에** `DR_init.__dsr__node = node` 를 반드시 설정. 안 그러면 `g_node`
  가 None 이 되어 모든 호출 실패.
- 호출은 항상 blocking. asyncio 와 호환 안 됨. 멀티스레드 노드라면 `g_node` 를 별도 executor
  에 넣지 말고 `spin_until_future_complete` 가 자체 스핀하게 두라 (CLAUDE.md 의 "DSR 실행 모
  델" 섹션 참고).
- ★ **`g_node` 와 같은 executor 에 sensor topic subscription 을 넣지 마라.** `spin_until_future_complete`
  가 글로벌 executor 의 spin lock 을 점유하여 같은 executor 의 subscription dispatch 가 starve
  되는 함정이 있다 (실측: 100Hz topic 이 0.3Hz 처리). 해결은 subscription 전용 별도 노드 +
  별도 `SingleThreadedExecutor` + 별도 thread 로 격리. 자세한 내용은 `multi-robot-and-quirks.md`
  §11 참조.
- **multi-robot 전혀 지원 안 함.** `_srv_name_prefix = ''` 가 모듈 전역. 같은 프로세스에서 두
  로봇을 다루려면 모듈을 두 번 import 해야 하는데 Python 에서는 그냥 캐싱돼 두 번째는 의미가
  없다. **다중 로봇 시나리오면 raw rclpy 를 직접 쓰는 게 깔끔하다**. (`multi-robot.md` 참고)
- 응답에서 `success` 같은 필드를 검사 안 한다. service call 이 성공해도 로봇은 거절했을 수
  있는데 wrapper 는 알려주지 않는다. 신뢰성 필요한 코드는 raw rclpy 로 호출 후 응답 검사.

### Python wrapper 가 빠뜨린 함수 (raw rclpy 필요)

코드 grep 결과 다음은 wrapper 함수가 없다:

- `servo_off`
- `set_robot_control` (SAFE_STOP/SAFE_OFF 복구)
- `move_pause`, `move_resume`, `move_stop`
- 일부 modbus 서비스
- 모든 lifecycle 서비스 (configure/activate/deactivate)

이런 건 `node.create_client(SrvType, "/dsr01/motion/move_pause")` 로 직접 만든다.

## 7. DRFLEx — vendor C++ API 의 이상한 부분

`dsr_common2/include/DRFLEx.h` 만 읽어도 알 수 있는 점:

- **Deprecated/new API 가 공존**: `_GetRobotState()` (PascalCase) vs `_get_robot_state()`
  (snake_case). 옛 호출은 매크로로 deprecated 마킹돼 있지만 컴파일은 된다 (line 68-75).
- **콜백이 std::function 이 아니라 raw function pointer typedef**. lambda 캡처 어려움.
- **포트 12345/12347 분리**: 12345 는 일반 control, 12347 은 RT data. RT 가 필요하면 별도
  `connect_rt_control(host, 12347)` 호출.
- 기본 IP 192.168.137.100 이 hardcoded 이지만 ROS 2 launch 에서 host 인자로 override 가능.
- **에러 처리 없음**: 함수 대부분 bool 반환만. 실패 원인 알려면 별도 `get_last_error()` 같은
  걸 호출하거나, OnLogAlarm 콜백을 미리 등록해 둬야 한다.

## 8. dsr_realtime_control — 1kHz C++ 패턴 분해

`dsr_example2/dsr_realtime_control/src/dsr_realtime_control.cpp` 가 RT 패턴의 정석. 노드 구조:

| 노드 | 역할 | 주기 | 메커니즘 |
|---|---|---|---|
| ReadDataRtNode | `read_data_rt` 서비스를 폴링해서 RT state 갱신 | ~3 kHz busy-loop | std::thread, while(rclpy.ok()) |
| TorqueRtNode | `/dsr01/torque_rt_stream` publish | 1 kHz | wall_timer(1000us) |
| ServojRtNode | `/dsr01/servoj_rt_stream` publish | 1 kHz | wall_timer(1000us) |
| ServolRtNode | `/dsr01/servol_rt_stream` publish | 1 kHz | wall_timer(1000us) |

상태 공유: `g_stRTState` 전역 + `std::mutex mtx` + `std::atomic_bool first_get`. 사용자가 직접
동기화. (line 9-11)

### 우리에게 주는 의미

- **RT 패턴은 "여러 노드 + 수동 동기화" 가 정석**이다. 한 노드 안에서 timer 로 다 처리하려 하
  지 마라. context switch 비용이 더 크다.
- timer 주기를 1ms 미만으로 설정하지 마라. wall_timer 정밀도가 OS 스케줄러에 의존. PREEMPT_RT
  커널이 아니면 jitter 가 커서 의미 없음.
- ReadDataRtNode 가 busy-loop 인 이유: `read_data_rt` 자체가 service call 이라 latency 가 있어
  서, polling 으로 최신 state 를 잡는다. timer 로 하면 service round-trip 시간만큼 stale 해짐.
- 100ms 보다 짧은 주기면 보통 std::mutex 보다 std::atomic 으로 끝나는 lock-free 패턴이 낫다
  (코드는 mutex 사용, 개선 여지).

## 9. dsr_moveit2 / dsr_description2 — m0609 변형 처리

```
dsr_moveit2/dsr_moveit_config_m0609/    # MoveIt 설정 — m0609 전용
dsr_moveit2/dsr_moveit_config_m1013/    # 다른 모델
dsr_moveit2/dsr_moveit_config_a0509/
...                                       # 10개 모델 모두 별도 패키지
```

각 패키지 안:

- `config/*.yaml` — kinematics, planning groups, controllers
- `launch/move_group.launch.py`, `moveit_rviz.launch.py` — 표준 MoveIt 부팅
- 차이는 거의 URDF/SRDF 만. 코드는 거의 동일.

URDF 진입점: `dsr_description2/xacro/m0609.urdf.xacro`. 매크로 분리:

- `m0609.white.xacro` / `m0609.blue.xacro` — 색상별 메시
- `m0609.ros2_control.xacro` / `m0609.gz_ros2_control.xacro` / `m0609.mj_ros2_control.xacro` —
  실기/Gazebo/MuJoCo 별 ros2_control 스니펫
- xacro args (line 4-16): `color`, `gripper`, `namespace`, `use_gazebo`, `use_mujoco`, `host`,
  `port`, `mode`, `model`, `update_rate`, `rt_host`

**우리에게 주는 의미**: 다른 모델(m1013) 로 옮기려면 패키지 이름만 `dsr_moveit_config_m1013` 으
로 바꾸면 거의 끝. 그러나 `ROBOT_MODEL = "m0609"` 으로 고정하라는 CLAUDE.md 지침이 있으므로
이번 프로젝트에선 m0609 만 다룬다.

## 10. 알려진 TODO 및 구조적 약점

| 위치 | 이슈 | 심각도 |
|---|---|---|
| `dsr_hardware2.cpp:321,325` | effort interface 미구현 | 중 — force 는 service 로만 가능 |
| `dsr_hw_interface2.cpp:284-286` | DRCF 3.0~3.4 에서 rt_host=host 강제 | 저 — 알려진 워크어라운드 |
| `DSR_ROBOT2.py:39` | `_srv_name_prefix = ''` — multi-robot 미지원 | 고 — 멀티봇 시나리오 블로커 |
| `dsr_realtime_control.cpp:26-33` | context-switch 측정 코드 주석 처리됨 | 저 — 디버깅 도구 손실 |
| `dsr_tests/test_cli_dsr_system.py` | 다수 TODO: real 모드 미테스트, alter_motion 미커버 | 중 — 테스트 신뢰도 |
| `dsr_controller2.cpp:20-23` | g_node 추출용 dead code 주석 처리됨 | 저 — 영향 없음 |

## 코드 인용 시 우선순위

새 코드를 작성할 때, 비슷한 일을 하는 기존 코드를 먼저 찾아 패턴을 따르는 게 안전하다. 추천
인용 순서:

1. `dsr_example2/dsr_example/` — 기본 motion sequence 의 reference
2. `dsr_example2/dsr_realtime_control/` — 1kHz C++ 패턴
3. `dsr_example2/dsr_visualservoing/` — 비전 + alter_motion 패턴
4. `dsr_bringup2/launch/dsr_bringup2_rviz.launch.py` — 표준 launch composition
5. `dsr_controller2/src/dsr_controller2.cpp` — service 핸들러 등록 패턴 (직접 작성보다는 참고용)
