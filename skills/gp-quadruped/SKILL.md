---
name: gp-quadruped
description: Use for the cobot3 GP(경계초소) border-guard robot project — a Boston Dynamics Spot quadruped (Isaac Sim SpotFlatTerrainPolicy bundled RL locomotion, 12-DOF legs only, no arm), with front/rear body-mounted cameras, patrolling procedural mountainous terrain along a route to a fence, streaming degraded video (5fps JPEG front+rear) + sim-GPS + state + rosout to a separate C2 (command-and-control) PC via FastAPI+Next.js, with raycast weapon-fire simulation. Trigger on any of GP 경계근무 로봇, gp-quadruped, Spot 보행 정책, SpotFlatTerrainPolicy, 4족보행, waypoint follower, 절차적 산악 지형 + D2 클램프, sim-GPS / NavSatFix from world pose, video degrade 5fps, raycast 사격 + FireEvent, C2 지휘통제실 통신, gp-quadruped-system-design.md. Also trigger when implementing P0~P4 milestones of that design doc, or wiring the Spot scene via isaac-sim-mcp. Do NOT use for the original warehouse-sorting cobot3 (m0609+RG2+conveyor+bins) — that is the legacy scope; this skill is the border-guard pivot only.
---

# gp-quadruped — GP 경계근무 4족 로봇 프로젝트 플레이북

cobot3 의 **GP(경계초소) 경계근무 대체 로봇** 구현 전용 오케스트레이션 스킬.
설계 원본: `/home/rokey/dev_ws/isaac_sim/cobot3/dev-docs/gp-quadruped-system-design.md`
(권위 문서 — 충돌 시 그 문서가 우선).

**현재 로봇:** Boston Dynamics Spot (spot.usd, S3 에셋), SpotFlatTerrainPolicy.
**m0609 팔 없음.** 전방/후방 카메라 2개(기체 base 마운트).

이 스킬은 **프로젝트 고유 조합 패턴**만 담는다. 범용 능력은 위임:
- USD/PhysX/URDF→USD/OG/번들정책 메커니즘 → [[isaac-sim-bridge]]
- 라이브 Kit 제어·MCP 도구·워크어라운드 → [[isaac-sim-mcp]]
- ROS↔웹 브리지·WebRTC·오디오·GPS·rosout 릴레이 → [[ros2-architect]]

## 10 불변식 (내재화)

1. **보행은 실제 물리 RL 정책으로만.** 키프레임·`time.sleep`·루트 텔레포트 금지.
   Spot 번들 `SpotFlatTerrainPolicy` 를 physics callback 으로 구동
   (create→reset→initialize(set_gains=True, set_limits=True)→매 step `forward(dt,cmd)`).
   12-DOF 다리 레이아웃: `fl_/fr_/hl_/hr_` × `hx/hy/kn`. 메커니즘 상세는
   [[isaac-sim-bridge]] `bundled-locomotion-policy.md`, 프로젝트 조합은
   `references/locomotion-policy.md`.

2. **번들 정책은 flat terrain 학습본.** 험지를 "정책이 견디는 조건"으로 만든다
   (D2): 지형 국소 경사/진폭을 클램프. 우회가 아니라 *운용 조건 명시*.
   진짜 험지 보행은 P4 Isaac Lab 재학습(범위 밖, 명시만).

3. **영상은 DB 저장 안 함, 그 외 전부 psql.** 카메라 원본 프레임은
   WebRTC/토픽 전송 전용. GPS·상태·leg joint·rosout WARN·탐지 메타·
   FireEvent·순찰이벤트는 telemetry_logger → 로컬 Postgres.

4. **단일 적재·단일 도메인.** `ROS_DOMAIN_ID=130`, Main↔C2 LAN.
   prim 규약 `/World/Robot/base`, `/World/Robot/base/camera_front`,
   `/World/Robot/base/camera_rear`, `/World/{Terrain,Fence}`.
   토픽 `/robot/*`, `/c2/front/compressed`, `/c2/rear/compressed`. 절대 임의 변형 금지.

5. **OmniGraph ROS2 노드는 `render=True` 없이 동작하지 않는다.**
   `world.step(render=False)` 사용 시 `OnPlaybackTick` 펄스 미발생 → OG 전체 미동작.
   반드시 `world.step(render=True)` 로 타임라인 구동.

6. **MCP 라이브 작업은 검증 우선.** `execute_script` 래퍼 버그(성공해도
   validation 에러로 반환) → `/tmp` 파일 write 후 Bash read 로 확인.
   기동은 `setsid` 분리 + 로그 readiness 대기. 상세 [[isaac-sim-mcp]].

7. **모든 통신 노드는 계측 의무.** Isaac↔ROS↔degrade↔web_server↔브라우저
   는 다단 분산이라 "어디서 끊겼는지" 가 핵심 디버깅 정보다. 모든 노드/스크립트는
   ① 기동 시 **ENV 자가점검 덤프**(`ROS_DOMAIN_ID`/`RMW_IMPLEMENTATION`/
   `ROS_LOCALHOST_ONLY`, 기대값과 불일치 시 ⚠ 경고) ② **단계별 카운터 + 5초
   주기 헬스 로그**(수신/발행 건수, `count_publishers`/렌더프로덕트 등 원인
   힌트 포함) ③ web_server 는 진단을 **WS `type:"diag"` 이벤트로도 송출**해
   브라우저 콘솔에서 깔끔히 보이게(접두사 `[C2/...]`) — 를 반드시 포함한다.
   계측 없는 통신 코드는 미완성으로 간주. 상세 `references/debugging-instrumentation.md`.

8. **통신 모드는 환경으로 결정.** Isaac 번들 ROS2(py3.11) ↔ 시스템 ROS2
   (py3.10) 는 **같은 PC 에서 DDS 디스커버리 불통**(모든 표준 해법 검증 실패 —
   반복 금지). → **같은-PC 임시 검증 = D-확장 HTTP `/ingest` 우회**(ROS2
   미사용), **실배포 2-PC LAN = ROS2 정공**(`fastdds_no_shm.xml`, UDP-only).
   같은-PC 에서 ROS2 디스커버리 디버깅에 시간 쓰지 말 것. 상세
   `references/ros2-interop-and-bypass.md`.

9. **Foxglove 시각화는 자체호스팅 Lichtblick 전용.** 외부 SaaS
   (`app.foxglove.dev`) 임베드 금지 — 경계초소 데이터 비유출. 같은-PC(M1)
   `ros_bridge` 재발행은 `/ingest`·DB·WS 불변 **읽기 미러**(`C2_INGEST_
   REPUBLISH` 기본 OFF = 2-PC·대시보드 무영향). 토픽명 모드 무관 동일 →
   layout 재사용. 상세 `references/foxglove-telemetry-viz.md`.

10. **C2 웹 브리지 함정 3종.** C2 PC(FastAPI+Next.js) 작업 시 반드시 체크:
    - **Next.js SSR 동결:** 모듈 레벨 상수(`API_BASE = "..."`)는 SSR 시점에 `"localhost:8000"` 으로 고정됨. `"use client"` 컴포넌트에서도 `window` 없는 서버 사이드 평가 발생. **해결: `getApiBase()` 런타임 함수 패턴** (`if (_STATIC_BASE) return; return \`http://${window.location.hostname}:8000\``).
    - **uvicorn WebSocket:** `pip install uvicorn` 단독 설치는 WebSocket 미지원. `pip install "uvicorn[standard]" websockets` 필수. 증상: `/events` WS 연결 즉시 실패, 서버 로그 `WARNING: No supported WebSocket library detected`.
    - **rsync venv 오염:** rsync 로 C2 PC에 코드 배포 시 반드시 `--exclude='.venv'`. venv shebang 경로가 사용자별 절대경로(`/home/rokey/` vs `/home/hoon/`)라 덮어쓰면 C2 PC에서 모든 python 실행 파단.

## 라우터 — 작업별 참조

| 작업 | 참조 |
|---|---|
| Spot 정책 로드/init/physics-cb(SpotFlatTerrainPolicy), waypoint follower P제어, 12-DOF 중재 로직 | `references/locomotion-policy.md` |
| 절차적 볼록 heightfield(가우시안+ridged fBm), D2 클램프, 정적 삼각 collider, 제자리 메시 덮어쓰기 | `references/terrain-build.md` |
| link_6 RealSense K행렬·depth, video_degrade(5fps/JPEG), sim-GPS(NavSatFix), rosout WARN 릴레이, OG GP 토픽맵 | `references/sensor-and-comms.md` |
| raycast 히트판정 + 트레이서 prim + FireEvent + 명령불이행 타이머 | `references/weapon-fire.md` |
| 검증된 Isaac 소스/에셋/URDF 경로 인덱스 + 능력↔담당스킬 매핑 | `references/isaac-refs.md` |
| 통신 노드 계측 패턴(ENV 덤프·헬스 카운터·WS diag·브라우저 콘솔), 다단 파이프라인 단절 진단 절차 | `references/debugging-instrumentation.md` |
| 같은-PC Isaac↔호스트 ROS2 DDS 불통 결론, D-확장 HTTP `/ingest` 우회 패턴, 모드 선택(임시 vs 2-PC) | `references/ros2-interop-and-bypass.md` |
| C2(sub1_side) 사전요건(python3-venv·--system-site-packages·.venv uvicorn·멱등 SQL·rmw-cyclonedds·Node20·기동 헬퍼) | `references/sub1-side-setup.md` |
| Foxglove 시뮬레이터 상태 시각화 / 자체호스팅 Lichtblick `/debug` / M1·M2 모드 / 토픽→패널 매핑 / depth·FireEvent 패널 확장 | `references/foxglove-telemetry-viz.md` |

## 구현 단계 (설계 §15, 현행 기준 2026-05-19)

- **P0** ✅ 환경: `gp_scene.usd`(Spot ref), `ROS_DOMAIN_ID=130`, DB schema, Next.js scaffold
- **P1** ✅ (실행 핵심) 절차 볼록 지형 + Spot 물리 보행(SpotFlatTerrainPolicy) +
  waypoint follower P제어 + C2 goto. **넘어지지 않고 경로 완주 = 합격**
- **P2** ✅ 전/후방 카메라 OmniGraph + gps_node + video_degrade(5fps ×2) +
  C2 영상벽(WebRTC/MJPEG 폴백) + 서버측 YOLO (graceful skip)
  + Lichtblick /debug 패널(SpotSurroundView 3D + iframe)
- **P3** 양방향 음성 + 사격(raycast+트레이서+FireEvent) + rosout WARN +
  telemetry_logger 전체 + server-bridge 전 엔드포인트 + UI 완성
- **P4** 옵션: 열화상, rough-terrain Isaac Lab 학습, 실 DEM

> Foxglove `/debug`(자체호스팅 Lichtblick)는 Next.js UI 와 **병행** 운용자/
> 개발자 심화 모니터링 트랙: P2 에서 RealSense+video → Image/3D/Plot 패널,
> P3 에서 FireEvent 패널. 상세 `references/foxglove-telemetry-viz.md`.

## 보편 워크플로 (모든 비자명 작업)

1. 설계 문서 해당 절(S1~S7) + 이 스킬 라우터 ref 를 먼저 읽는다.
2. Isaac 라이브 작업이면 [[isaac-sim-mcp]] 보편 워크플로(get_scene_info →
   계획 → 가장 구체적 도구 → 1콜 → 검증) 적용.
3. 새 prim/토픽은 §5 규약·설계 §5.1/§12 와 grep 대조 후에만 추가.
4. 보행/결합 변경 시 불변식 1~3 위반 여부 자가검증 후 보고.
5. 변경이 다른 노드/단계에 주는 영향(연관 토픽·prim·단계) 점검 후 보고.

## 위임 경계 (이 스킬이 다루지 않음)

- URDF→USD 임포트 절차/조인트 드라이브 일반 → [[isaac-sim-bridge]] `usd-from-urdf.md`
- OG 노드 타입/QoS 매칭 일반 → [[isaac-sim-bridge]] `omnigraph-ros-bridge.md`
- 번들 PolicyController 내부 메커니즘 → [[isaac-sim-bridge]] `bundled-locomotion-policy.md`
- FastAPI/WebRTC/오디오/NavSatFix/rosout 일반 → [[ros2-architect]] `web-bridge-streaming.md`
- dsr_controller2/FollowJointTrajectory/m0609 리미트 → [[doosan-robotics]] `sim-integration.md`
- MCP 연결복구/실행 함정 → [[isaac-sim-mcp]] `debugging.md` `patterns.md`

## 스킬 출력 기대

- 보행 관련 코드는 **항상** physics callback 패턴(키프레임/sleep 0건)
- 지형 생성은 **항상** D2 클램프 포함, 정적 삼각 collider
- m0609 결합은 **항상** 질량경감+stow 완화 동반 명시
- prim/토픽은 **항상** 설계 §5/§12 규약과 일치
- MCP 변경 후 **항상** `/tmp` 파일 또는 get_scene_info 로 검증
- 영상 데이터는 **절대** DB 저장 코드/스키마에 넣지 않음
- Foxglove 작업은 **항상** M1/M2 모드 명시 + layout.json 패널 영향 + 자체
  호스팅 전용(외부 SaaS 0건) + 함정 체크리스트 통과 보고
