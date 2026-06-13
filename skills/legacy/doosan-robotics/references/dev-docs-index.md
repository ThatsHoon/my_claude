# Dev-Docs Index — `/home/hoon/Documents/services` 와 `/home/hoon/Documents/topics`

이 두 디렉토리는 **두산 서비스/토픽 161개 전체에 대한 1차 레퍼런스**다. 코드를 작성할 때마다
먼저 여기를 열어 정확한 Python 래퍼 이름, 인자 타입, 제약, 활용 예를 확인하라. 안 그러면 사
람 손으로 추측하다 함정에 빠진다.

## 빠른 사용법

```
서비스가 필요한 동작 → 카테고리 결정 → 해당 카테고리 디렉토리 열람 → md 파일 확인
```

예: "movej 인자가 정확히 뭐였지?"
1. 카테고리 = motion (동작 지령)
2. `/home/hoon/Documents/services/motion/move_joint.md` 열람
3. 5개 섹션 확인 (다음 §섹션 구조)

## 디렉토리 구조

```
/home/hoon/Documents/services/
├── aux_control/    # 18 — 현재/목표 위치·속도·토크 조회
├── drl/            #  5 — DRL 스크립트 시작/정지/일시정지/상태
├── force/          # 23 — 컴플라이언스, 힘제어, 좌표계 변환
├── io/             # 10 — 디지털/아날로그 I/O
├── modbus/         #  4 — Modbus 신호 등록/입출력
├── motion/         # 26 — movej/movel/movec/jog/blending/spiral/periodic/spline/alter
├── realtime/       # 16 — RT control, read_data_rt, set_*_rt
├── system/         # 14 — 모드, 상태, 안전, 알람, 충돌감도
├── tcp/            #  4 — TCP 설정 add/delete/current/get
└── tool/           #  5 — 툴 설정 add/delete/current/get + add_modbus

/home/hoon/Documents/topics/    # 18 — 모두 stream/state 토픽
├── alter_motion_stream.md
├── dsr_controller2_transition_event.md
├── dynamic_joint_states.md
├── jog_multi.md
├── joint_state_broadcaster_transition_event.md
├── joint_states.md
├── robot_description.md
├── servoj_rt_stream.md
├── servoj_stream.md
├── servol_rt_stream.md
├── servol_stream.md
├── speedj_rt_stream.md
├── speedj_stream.md
├── speedl_rt_stream.md
├── speedl_stream.md
├── tf.md
├── tf_static.md
└── torque_rt_stream.md
```

## md 파일의 표준 5섹션

각 서비스 md 는 다음 구조다 (확인된 표준):

1. **개요**: 서비스 이름·기능 한 줄 설명
2. **구조 (호출 패턴)**: srv 원본 + Python 래퍼 시그니처
3. **인자 상세**: 각 필드 의미·타입·제약·기본값
4. **활용 예시**: Python 짧은 코드 (DSR_ROBOT2 import 가정)
5. **비고**: 알려진 제약, deprecated 여부, 호환성, 함정

이 5섹션이 일관되므로 grep 으로 빠르게 추출 가능하다.

## 카테고리별 핵심 서비스 (외울 가치 있는 것들)

### motion (26개)

| Python 래퍼 | srv 이름 | 용도 |
|---|---|---|
| `movej`, `amovej` | `MoveJoint` | 관절공간 PTP, 동기/비동기 |
| `movel`, `amovel` | `MoveLine` | 직교공간 직선 |
| `movec`, `amovec` | `MoveCircle` | 원호 |
| `movejx`, `amovejx` | `MoveJointx` | 직교 목표를 관절공간으로 |
| `moveb`, `amoveb` | `MoveBlending` | 블렌딩 시퀀스 (최대 50 segments) |
| `movesj`, `amovesj` | `MoveSplineJoint` | 관절 스플라인 |
| `movesx`, `amovesx` | `MoveSplineTask` | 직교 스플라인 |
| `move_spiral`, `amove_spiral` | `MoveSpiral` | 나선 |
| `move_periodic`, `amove_periodic` | `MovePeriodic` | 주기 모션 (위빙/연마용) |
| `jog`, `jog_multi` | `Jog`, `JogMulti` | 수동 이송 |
| `enable_alter_motion`, `disable_alter_motion` | `EnableAlterMotion`, `DisableAlterMotion` | 동적 경로 보정 |
| `wait` | (Python 자체 sleep) | **service 가 아님 — 단순 time.sleep** |
| `move_pause`, `move_resume`, `move_stop` | `MovePause`, `MoveResume`, `MoveStop` | **Python 래퍼 없음 — raw rclpy 필요** |

함정:
- `wait()` 은 `time.sleep` 일 뿐. **모션 완료 대기가 아니다**. 동기 모션은 이미 반환 시 완료된
  상태. 비동기 모션 완료를 기다리려면 `mwait()` 를 쓴다.
- `radius` 가 0 이 아닌 movej/movel/movec 호출에 `_async=1` 을 넣으면 radius 가 강제로 0 이
  된다. 블렌딩이 필요하면 동기 호출만.

### realtime (16개)

| Python 래퍼 | srv 이름 | 용도 |
|---|---|---|
| `connect_rt_control`, `disconnect_rt_control` | `ConnectRtControl`, `DisconnectRtControl` | RT 소켓 연결 (port 12347) |
| `start_rt_control`, `stop_rt_control` | `StartRtControl`, `StopRtControl` | RT 스트림 활성화 |
| `read_data_rt` | `ReadDataRt` | 최신 RT 데이터 한 번 읽기 |
| `write_data_rt` | `WriteDataRt` | RT 데이터 쓰기 (커스텀 필드) |
| `set_velj_rt`, `set_accj_rt`, `set_velx_rt`, `set_accx_rt` | `SetVeljRt` 등 | RT 모션의 속도/가속도 설정 |
| `set_rt_control_input`, `set_rt_control_output` | `SetRtControlInput`, `SetRtControlOutput` | RT 데이터 필드 선택 |
| `get_rt_control_input_data_list` 등 | `Get*` | 사용 가능한 RT 필드 enum |

함정:
- realtime 서비스의 `period` 인자는 반드시 `float`. `int` 넘기면 `DR_Error`.
- virtual 모드에서는 모든 RT 서비스가 무응답. real 모드 전용.

### system (14개)

| Python 래퍼 | srv 이름 | 용도 |
|---|---|---|
| `get_robot_state` | `GetRobotState` | 16개 코드 (STANDBY/MOVING/SAFE_STOP/...) |
| `set_robot_mode`, `get_robot_mode` | `SetRobotMode`, `GetRobotMode` | AUTONOMOUS/MANUAL/MEASURING |
| `set_robot_system`, `get_robot_system` | `SetRobotSystem`, `GetRobotSystem` | REAL/VIRTUAL — **부팅 후 변경 불가** |
| `change_collision_sensitivity` | `ChangeCollisionSensitivity` | 1~100, 클수록 민감 |
| `set_robot_speed_mode`, `get_robot_speed_mode` | 속도 모드 | NORMAL/REDUCED |
| `get_last_alarm` | `GetLastAlarm` | 최근 알람 1건 |
| `set_robot_control` | `SetRobotControl` | **Python 래퍼 없음** — SAFE_STOP/SAFE_OFF 복구 시 raw rclpy |
| `servo_off` | `ServoOff` | **Python 래퍼 없음** |

`set_robot_control` 의 값:

| 값 | 전이 | 용도 |
|---|---|---|
| 2 | SAFE_STOP → STANDBY | 노란 LED 리셋 (소프트웨어만) |
| 3 | SAFE_OFF → STANDBY | 빨간 LED 해제 후 서보 On (사람 개입 필요 + 약 3초 대기) |

복구 절차는 CLAUDE.md 의 "정지·복구 시퀀스" 섹션 참고.

### force (23개)

| Python 래퍼 | srv 이름 | 용도 |
|---|---|---|
| `task_compliance_ctrl`, `release_compliance_ctrl` | `TaskComplianceCtrl`, `ReleaseComplianceCtrl` | 강성 기반 순응 제어 |
| `set_desired_force`, `release_force` | `SetDesiredForce`, `ReleaseForce` | 목표 힘/토크 인가 |
| `set_stiffnessx` | `SetStiffnessx` | 6축 강성 (Translation/Rotation) |
| `check_force_condition` | `CheckForceCondition` | 힘 임계 조건 비동기 체크 |
| `check_position_condition` | `CheckPositionCondition` | 위치 임계 조건 |
| `parallel_axis1`, `parallel_axis2`, `align_axis1`, `align_axis2` | (1/2 분기 srv) | 평행/정렬 보조 |
| `set_user_cart_coord1/2/3`, `overwrite_user_cart_coord`, `get_user_cart_coord` | (분기) | 사용자 좌표계 |
| `get_workpiece_weight`, `reset_workpiece_weight` | `GetWorkpieceWeight`, `ResetWorkpieceWeight` | 워크피스 무게 보상 |

함정:
- `parallel_axis1` vs `parallel_axis2` 는 srv 이름이 같고 `_nType`/`_cmd_type` 인자로 분기. 문
  서의 Python 함수명을 정확히 사용해야 의도한 서비스 호출.
- 특이점 영역에서는 force/compliance 가 동작 안 함. CLAUDE.md "특이점 처리" 섹션 참고.

### io (10개) / modbus (4개)

| Python 래퍼 | srv 이름 | 용도 |
|---|---|---|
| `set_digital_output(idx, val=None, time=None, val2=None)` | (분기 service) | DI 1~16 ON/OFF/Pulse |
| `get_digital_input` | (service) | DI 1~16 read |
| `set_analog_output_*`, `get_analog_input_*` | (services) | AI/AO V/A 모드 |
| `set_mode_analog_input` | `SetCtrlBoxAnalogInputType` | **래퍼명 ↔ srv명 다름** |
| `add_modbus_signal`, `read_modbus_signal`, `write_modbus_signal` | `ConfigCreateModbus`, `ReadModbusSignal`, `WriteModbusSignal` | Modbus 신호 등록·통신 |

함정:
- `set_digital_output(-3)` 은 `index=3, val=OFF` 와 동일. 음수 index = 양수 ON 의 반전.
- `add_modbus_signal` ↔ `ConfigCreateModbus` 처럼 **Python 함수명과 srv 이름이 다른 케이스**가
  많다. 항상 md 의 "Python 호출 패턴" 섹션을 우선시.

## topics 인덱스 (18개)

| 토픽 | QoS | 발행자 | 용도 |
|---|---|---|---|
| `/dsr01/joint_states` | RELIABLE+VOLATILE | dsr_controller2 | 6축 관절 상태 (sensor_msgs/JointState) |
| `/dynamic_joint_states` | RELIABLE+VOLATILE | controller_manager | ros2_control 표준 |
| `/robot_description` | RELIABLE+TRANSIENT_LOCAL (latched) | robot_state_publisher | URDF 문자열 |
| `/tf`, `/tf_static` | 표준 | tf2 broadcaster | 좌표 트리 |
| `/dsr01/servoj_stream`, `/dsr01/servol_stream`, `/dsr01/speedj_stream`, `/dsr01/speedl_stream` | RELIABLE | 사용자 발행 → controller 수신 | 비동기 스트림 모션 명령 |
| `/dsr01/servoj_rt_stream`, `/dsr01/servol_rt_stream`, `/dsr01/speedj_rt_stream`, `/dsr01/speedl_rt_stream`, `/dsr01/torque_rt_stream` | RELIABLE | 사용자 발행 → controller RT layer | 1kHz RT 명령 (real 모드만) |
| `/dsr01/alter_motion_stream` | RELIABLE | 사용자 발행 | 동작 중 경로 보정 (alter_motion enable 후) |
| `/dsr01/jog_multi` | RELIABLE | 사용자 발행 | 다축 jog 명령 |
| `/dsr_controller2/transition_event`, `/joint_state_broadcaster/transition_event` | TRANSIENT_LOCAL | controller_manager | 라이프사이클 전이 이벤트 |
| `/rt_topic/<key>` | RELIABLE | dsr_controller2 (use_rt_topic_pub=true 시) | RT 데이터 push (Float32MultiArray) |

`*_stream` 과 `*_rt_stream` 차이:
- `*_stream` (예: servol_stream): 일반 컨트롤 경로. vel/acc 가 [translation, rotation] **2원소**
  벡터.
- `*_rt_stream` (예: servol_rt_stream): RT 경로. vel/acc 가 6축 **6원소** 벡터. real 모드 + RT
  활성 시에만 동작.

## md 파일 한 번에 검색하는 패턴

질문 → 빠른 grep:

```bash
# 함수 이름으로 검색 — 시그니처 + 예제 즉시 찾기
grep -rl "movej\|MoveJoint" /home/hoon/Documents/services/motion/

# 카테고리 전체에서 특정 키워드 — 함정/제약 찾기
grep -ri "deprecated\|virtual 모드\|raw rclpy" /home/hoon/Documents/services/

# topic QoS 확인
grep -i "qos\|durability\|best_effort" /home/hoon/Documents/topics/*.md
```

## 자동 갱신 규칙

- 문서와 실제 동작이 다르면 → 해당 md 의 **§5 비고** 섹션을 즉시 갱신.
- 새 서비스를 작성/관찰하면 → 해당 카테고리 디렉토리에 새 md 추가 (5섹션 표준 따름).
- Python wrapper 없는 서비스를 발견하면 → 해당 md 의 §2 에 "Python wrapper 없음 — raw rclpy 필
  요" 명시.

이 인덱스가 SKILL.md 의 함수별 상세보다 우선한다. SKILL.md 는 의도와 패턴 가이드, 이 docs 는
서명·인자·예제의 진실 소스다.
