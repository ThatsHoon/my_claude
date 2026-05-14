# Launch 와 모드 — virtual / real / sim 분기

`dsr_bringup2/launch/` 의 5개 launch 파일이 이 스택의 진입점이다. 이 문서는 각 모드가 어떻게
다르게 동작하는지, 어떤 함정이 있는지를 다룬다.

## 5개 launch 파일

| 파일 | 용도 |
|---|---|
| `dsr_bringup2_rviz.launch.py` | 가장 많이 쓰이는 표준 진입점. RViz 포함, mode 인자로 분기. |
| `dsr_bringup2_gazebo.launch.py` | Gazebo 시뮬레이션. ros2_control + gz_ros2_control plugin. |
| `dsr_bringup2_mujoco.launch.py` | MuJoCo 시뮬레이션. mj_ros2_control plugin. |
| `dsr_bringup2_moveit.launch.py` | MoveIt 노드 (move_group + RViz) 별도 기동. |
| `dsr_bringup2_spawn_on_gazebo.launch.py` | 이미 떠있는 Gazebo 에 robot spawn 만. |

세 모드 (virtual / real / sim) 는 launch arg `mode` 로 분기한다. 핵심 흐름:

```
launch arg (mode, host, port, model, ...)
    ↓
xacro evaluate (Command(['xacro ', ..., ' mode:=', mode, ...]))
    ↓
URDF 안의 <xacro:if value="...">  로 ros2_control snippet 선택
    ↓
controller_manager 가 적절한 hardware plugin 로드
```

## 모드별 차이

### virtual 모드

```bash
ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py \
    mode:=virtual host:=127.0.0.1 port:=12345 model:=m0609
```

내부 동작:

1. `dsr_bringup2/run_emulator` Python 노드 자동 spawn (launch.py:96-116). 이게 port 12345 에서
   DRCF 흉내를 낸다.
2. `dsr_hardware2` 가 `connect()` 시도 → emulator 응답.
3. `SetRobotSystem(ROBOT_SYSTEM_VIRTUAL)` 호출.
4. **RT setup 건너뜀** (`dsr_hw_interface2.cpp:283-308` 의 if 블록). 즉 port 12347 / RT 서비스
   는 동작 안 함.
5. controller 가 모든 일반 service 에 응답. motion 도 emulator 가 가짜 응답.

함정:
- `set_robot_mode(ROBOT_MODE_MANUAL)` 호출은 무한 대기. virtual 모드에서는 호출하지 마라
  (CLAUDE.md "Known Issues" 참고).
- `get_current_posx()` 같은 service 가 **모션 실행 중 응답 안 함**. 가상 컨트롤러의 한계. 좌표
  가 필요하면 `/rt_topic/actual_tcp_position` 구독 또는 coord_service 토픽 패턴 사용.

### real 모드

```bash
ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py \
    mode:=real host:=192.168.1.100 port:=12345 model:=m0609 rt_host:=192.168.1.100
```

내부 동작:

1. emulator 안 띄움.
2. `dsr_hardware2` 가 실제 컨트롤러 (192.168.1.100:12345) 에 connect. 20번 retry.
3. **DRCF 펌웨어 버전 검사 → ≥ M2.12 (121200)** 강제. 미달이면 fail (`dsr_hw_interface2.cpp:
   234-246`).
4. `SetRobotSystem(ROBOT_SYSTEM_REAL)`.
5. RT 채널 활성화: `connect_rt_control(rt_host, 12347)` → `set_rt_control_output()` →
   `start_rt_control()`. (`dsr_hw_interface2.cpp:283-308`)
6. 모드 자동 설정: `SetRobotMode(ROBOT_MODE_AUTONOMOUS)`.
7. controller 가 standby 상태로 진입. service 호출 가능.

함정:
- `rt_host` 가 host 와 다르면 DRCF 3.0~3.4 에서 강제로 host 와 같게 설정됨. 3.5+ 에서만 분리
  가능.
- 안전영역 위반/충돌 발생 시 `STATE_SAFE_STOP(5)` 진입. SetRobotControl(2) 로 리셋. E-Stop 은
  사람 개입 필요 (CLAUDE.md "정지·복구" 섹션).
- `change_collision_sensitivity` 를 너무 낮게 설정 (예: 5) 하면 정상 모션도 충돌로 판정 → 자
  주 SAFE_STOP. 기본값 (50~80) 권장.

### sim 모드 — Gazebo / MuJoCo

```bash
# Gazebo
ros2 launch dsr_bringup2 dsr_bringup2_gazebo.launch.py model:=m0609

# MuJoCo
ros2 launch dsr_bringup2 dsr_bringup2_mujoco.launch.py model:=m0609
```

내부 동작:

1. Gazebo (또는 MuJoCo) 가 별도 프로세스로 시작.
2. URDF 안의 `<gazebo>` (또는 `<mujoco>`) 태그가 활성화 → 시뮬레이터가 robot 을 visualize.
3. `gz_ros2_control` (또는 `mj_ros2_control`) plugin 이 controller_manager 의 hardware 역할.
   즉 dsr_hardware2 가 아니라 시뮬레이터의 fake hardware 를 쓴다.
4. **DRFL 호출 안 됨**. motion service 동작이 다르다 — 시뮬레이터 내부 모터로 위치 명령을 보
   냄. force/compliance 같은 두산 특유 service 는 동작 안 함.
5. `JointTrajectoryController` 가 표준 ros2_control 컨트롤러로 등장 (real/virtual 모드와 다름).

용도:
- 시각화 + MoveIt 통합 테스트에는 좋음.
- DRFL 특유의 force/compliance/RT 로직을 검증할 수는 없음. 그건 real 모드에서만.

## launch arg 표

| arg | 기본값 | 의미 |
|---|---|---|
| `mode` | `virtual` | virtual/real/sim |
| `host` | `127.0.0.1` | DRCF/emulator IP |
| `port` | `12345` | DRCF/emulator 포트 |
| `rt_host` | `host` 와 동일 | RT 채널 IP (보통 host 와 같음) |
| `model` | `m0609` | URDF/MoveIt config 선택 |
| `update_rate` | yaml 에서 읽음 | controller_manager update Hz |
| `name` | `dsr01` | 로봇 namespace |
| `color` | `white` | 메시 컬러 (white/blue) |
| `gripper` | (없음) | 그리퍼 종류 (있으면 URDF 에 attach) |
| `use_gazebo` | `false` | Gazebo 사용 |
| `use_mujoco` | `false` | MuJoCo 사용 |
| `use_rt_topic_pub` | yaml | `/rt_topic/<key>` 발행 활성 |
| `rt_timer_ms` | 10 | `/rt_topic` publish 주기 (10ms = 100Hz) |
| `rt_topic_keys` | yaml | 활성화할 RT 키 리스트 |

## URDF/xacro 분기 메커니즘

`dsr_description2/xacro/m0609.urdf.xacro` 의 핵심 (line 50-62 근방):

```xml
<xacro:if value="${use_gazebo}">
  <xacro:include filename="$(find dsr_description2)/xacro/m0609.gz_ros2_control.xacro"/>
</xacro:if>
<xacro:if value="${use_mujoco}">
  <xacro:include filename="$(find dsr_description2)/xacro/m0609.mj_ros2_control.xacro"/>
</xacro:if>
<xacro:unless value="${use_gazebo or use_mujoco}">
  <xacro:include filename="$(find dsr_description2)/xacro/m0609.ros2_control.xacro"/>
</xacro:unless>
```

이 세 ros2_control xacro 가 다른 hardware plugin 을 지정한다:

- `m0609.ros2_control.xacro`: `dsr_hardware2/SystemHardware`
- `m0609.gz_ros2_control.xacro`: `gz_ros2_control/GazeboSimSystem`
- `m0609.mj_ros2_control.xacro`: `mj_ros2_control/MuJoCoSystem`

따라서 같은 robot model 이라도 모드에 따라 controller_manager 가 다른 plugin 을 로드한다.

## 자주 나오는 launch 함정

1. **`source install/setup.bash` 누락** — 첫 빌드 후 새 터미널이면 항상 source.
2. **`build/setup.bash` 를 source** — 절대 금지. 항상 `install/`.
3. **여러 ROS 워크스페이스 source 순서** — `/opt/ros/humble` → `cobot_ws/install` 순. 거꾸로면
   underlay 의 dsr_msgs2 가 우선해 빌드 결과물이 무시됨.
4. **`mode:=real` 인데 host 미설정** — 기본값 `127.0.0.1` 로 시도하다가 connect 실패. 명시적
   으로 `host:=192.168.x.x` 지정.
5. **emulator 가 이미 떠 있는 상태에서 launch** — port 12345 점유 충돌. `pkill -f run_emulator`
   먼저.
6. **RViz 가 robot 을 안 보여줌** — `/robot_description` QoS 가 TRANSIENT_LOCAL 인데 RViz
   Display 의 `Description Topic > Durability Policy` 도 같이 맞췄는지 확인.
7. **launch 가 "ROS2 master not found" 비슷한 에러로 실패** — ROS 1 잔재. 깨끗한 터미널에서
   `humble` 만 source.

## 권장 launch 패턴 — bringup vs behavior 분리

**터미널 1 (bringup, 장기 실행):**
```bash
ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py mode:=virtual model:=m0609
```

**터미널 2 (behavior, 자주 재시작):**
```bash
ros2 run my_pkg my_motion_node
```

이유:

- bringup 은 controller_manager 라이프사이클 + 하드웨어 연결을 들고 있다. 재시작이 무겁다.
- behavior 는 사용자 코드. 빠른 iteration. ROS 2 그래프에 service client 만 만들어 붙으면 된다.
- 둘은 DDS 로만 연결. behavior 종료/재시작이 bringup 에 영향 없음.

CLAUDE.md "프로세스 분리" 섹션도 같은 패턴을 강조한다. 이건 두산만의 컨벤션이 아니라 **두산
launch 가 강제하는 구조** 다 (DSR_ROBOT2 모듈이 g_node 를 import 시점에 고정하기 때문).

## CI / 테스트에 적용

CI 환경에서는 GUI 없이 동작해야 하니:

```bash
# RViz 비활성, virtual 모드
ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py \
    mode:=virtual model:=m0609 rviz:=false &

# motion 코드 실행
ros2 run my_pkg my_test_node

# 종료
killall ros2 dsr_controller2 run_emulator
```

`rviz:=false` 는 모든 launch.py 가 표준으로 지원해야 하지만 일부 파일은 RViz 를 무조건 띄우니
확인 필요. 대안: `headless` 환경변수 + `IfCondition` 분기 추가.
