# sub1-side-setup.md — C2(sub1_side) 사전요건 체크리스트

GP C2 웹서버 측 기동 시 **실제로 막혔던** 사전요건. 일반 ROS↔웹 메커니즘은
[[ros2-architect]] `web-bridge-streaming.md` 위임 — 여기는 *이번에 발목 잡은
환경 의존성*만.

## 1. 사전 설치 (없으면 즉시 실패)

| 패키지 | 없을 때 증상 | 설치 |
|---|---|---|
| `python3.10-venv` (ensurepip) | `python3 -m venv .venv` 가 pip 부트스트랩 실패 → `.venv/bin/pip` 부재(127) | `apt install python3.10-venv python3-pip` |
| `ros-humble-rmw-cyclonedds-cpp` | (2-PC ROS2 경로) cyclone RMW 미존재 | `apt install ros-humble-rmw-cyclonedds-cpp` |
| Node 20 | Next.js 빌드 실패 | NodeSource 20 LTS |
| PostgreSQL 14 | DB 적재 불가 | 시스템 psql + `createdb cobot3` |

## 2. venv 는 `--system-site-packages` 필수

web_server 의 ros_bridge 는 시스템 rclpy 를 import 한다. 일반 venv 면 rclpy
미가시 → `--system-site-packages` 로 생성하고 **ROS 소싱 후** 그 venv python
실행:
```bash
python3 -m venv --system-site-packages .venv
./.venv/bin/pip install -r requirements.txt
# run.sh: source /opt/ros/humble/setup.bash → exec ./.venv/bin/uvicorn ...
```

## 3. uvicorn 은 PATH 의존 금지

`exec uvicorn` 은 PATH 에 없으면 `exec: uvicorn: not found`. run.sh 는
**`./.venv/bin/uvicorn` 명시**(없으면 `python3 -m uvicorn` 폴백).

## 4. SQL 멱등성 (반복 적용 안전)

`CREATE OR REPLACE FUNCTION` 은 **반환형이 다르면 실패**(`cannot change
return type of existing function`). schema.sql 은 함수 앞에
`DROP FUNCTION IF EXISTS cleanup_old_data();` 선행. 재적용 가능해야 함.

## 5. 빌드 산출물 = git 미추적, 클론 후 재생성

`.venv / node_modules / .next / __pycache__ / scenes/assets` 는 `.gitignore`.
클론/정리 후 §1~2 + `npm install` + `psql -f db/schema.sql` 로 재생성.
m0609 USD 는 camera_publisher 가 없으면 자동 임포트(또는 사전 임포트 —
`make_default_prim` 누락 시 무한 recompose, [[isaac-sim-bridge]]
`usd-from-urdf.md`).

## 6. 기동 헬퍼 (`~/.bashrc`)

- `cobot3-cobot3_web-restart_full` : C2 스택(web_server+web+db, +2-PC 시
  degrade) 일괄 종료·재기동. PostgreSQL 재시작(sudo) 포함.
- `isaac` / `isaac-mcp` : RMW·DOMAIN prefix 포함 Isaac 기동.
- 절대경로 하드코딩 → 클론 위치는 `/home/rokey/dev_ws/isaac_sim/cobot3` 고정
  (다르면 run 스크립트·bashrc 함수 경로 수정).

상세 환경/기동/트러블슈팅 전체: 프로젝트
`dev-docs/project_requirments.md`.
