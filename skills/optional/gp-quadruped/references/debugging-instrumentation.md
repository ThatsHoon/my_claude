# debugging-instrumentation.md — 통신 노드 계측 & 다단 파이프라인 단절 진단

GP 시스템은 `Isaac OG → /cam/realsense/rgb → video_degrade → /c2/video/compressed
→ web_server(aiortc) → WebRTC → 브라우저` 처럼 **다단 분산**이라, 장애 시
"어느 hop 에서 끊겼나" 를 즉시 가려내는 계측이 디버깅의 핵심이다(불변식 7).

## 1. 모든 통신 노드 필수 계측 3종

### ① 기동 ENV 자가점검 덤프
노드/스크립트 시작 직후 무조건 출력:
```
ROS_DOMAIN_ID / RMW_IMPLEMENTATION / ROS_LOCALHOST_ONLY  (+ Isaac 은 GP_SCENE)
```
기대값(`130` / `rmw_cyclonedds_cpp`)과 다르면 `⚠` 경고 1줄. RMW 불일치는
Isaac↔C2 토픽 디스커버리 실패의 1순위 원인 — 가장 먼저 배제.

### ② 단계별 카운터 + 5초 주기 헬스
- 수신/발행 누적 카운터(`_rx`, `n_in/n_out`, `stepped N`).
- 5초 타이머로 `HEALTH rx=... publishers=...` 출력.
- **원인 힌트 포함**: 수신 0 일 때 `count_publishers(topic)` 로
  - publisher 0 → 상류 미발행/미재생/RMW·DOMAIN 불일치
  - publisher ≥1 인데 수신 0 → QoS/메시지타입 불일치 또는 상류 렌더프로덕트 미생성
- "첫 프레임 수신" 은 1회 명시 로그(통신 OK 마커).

### ③ web_server → 브라우저 콘솔(WS diag)
web_server 는 진단을 stdout 뿐 아니라 **WS `{"type":"diag", src, env, rx,
publishers, hint, warn, fatal}`** 로도 송출. Next.js `useEvents` 가 받아
`console.{debug|warn}("[C2/diag:src]", ...)` 로 깔끔히. WebRTC/WS 생명주기도
`[C2/ws]`,`[C2/webrtc]` 접두사로 콘솔에. → 담당자가 F12 만으로 단절 지점 파악.

## 2. 단절 지점 진단 절차 (위→아래 순서로 배제)

| # | 확인 | 명령/위치 | 끊김 판정 |
|---|---|---|---|
| 1 | Isaac 기동·RMW | kit `/proc/$PID/environ` `RMW_IMPLEMENTATION` | cyclone 아니면 → RMW 불일치 |
| 2 | OG 평가/렌더프로덕트 | camera_publisher `DIAG renderProduct=` | 비었으면 → cameraPrim/렌더 문제 |
| 3 | Isaac 발행 | `ros2 topic info /cam/realsense/rgb` (cyclone) | `Publisher count: 0` → Isaac 미발행 |
| 4 | degrade 수신 | `/tmp/cobot3_degrade.log` `in=N` | `in=0` + pub0 → 1·3 재확인 |
| 5 | degrade 발행 | `ros2 topic hz /c2/video/compressed` | 0 → degrade 입력 0 |
| 6 | web_server 수신 | server log `✓ 첫 영상 프레임` / WS diag `rx.video` | 0 → QoS/RMW |
| 7 | 브라우저 | F12 `[C2/webrtc] track 수신` | 없으면 → aiortc/SDP |

`ros2 topic list` 는 **publisher 0 이어도 구독자만으로 토픽이 보이므로** 단독
근거 불가 — 반드시 `ros2 topic info` 의 `Publisher count` 로 판정.

## 3. 자주 나오는 근본 원인 (이 프로젝트 실제 사례)

- **RMW 불일치**: Isaac 번들 FastDDS ↔ 시스템 — 동일 도메인이어도 디스커버리
  실패. 해결: Isaac·degrade·web_server·CLI **전부 `rmw_cyclonedds_cpp`**.
- **OG defaultPrim 누락**: URDF 임포트 `make_default_prim=False` → 참조
  `<defaultPrim>` 미해결 → 무한 recompose(CPU 폭주). 해결: dest USD 에
  defaultPrim 설정 후 참조.
- **standalone 에 ros2.bridge 미로드**: python.sh 앱은 자동 enable 안 됨 →
  `Could not find node type interface 'isaacsim.ros2.bridge.*'`. 해결:
  `enable_extension("isaacsim.ros2.bridge")` + app.update() 펌프 후 OG 생성.
- **OG 중복 생성**: 기존 그래프 위 `og.Controller.edit(CREATE_NODES)` →
  `Failed to wrap graph in node / graph already exists`. 해결: 기존
  `RemovePrim` 후 fresh 재생성(비기능 저장 OG 신뢰 금지).
- **타임라인 미재생**: OG `OnPlaybackTick` 미틱 → publisher 0. Play 필수.
- **`[json.exception.parse_error.101] ... last read: 's'` 스팸**: Isaac
  `isaac.sim.mcp_extension` 소켓 + stale Claude MCP relay 의 비-JSON 데이터.
  **무해 노이즈** — 파이프라인/발행과 무관, 무시(끄려면 mcp 확장 비활성/relay 정리).
- **같은-PC Isaac↔호스트 ROS2 미발견**: env 추측으로 못 푼다. 같은-PC 는
  D-확장 HTTP 우회, 2-PC LAN 은 ROS2 정공 — `ros2-interop-and-bypass.md` 참조.
- **기동 함정**: `setsid …&` 는 Bash 툴 종료 시 동반 종료 / GUI `isaac-sim.sh`
  는 harness 백그라운드에 DISPLAY 없어 exit 144 → 사용자 `!` 기동 / headless
  `python.sh` 는 tracked background 가능. 상세 [[isaac-sim-mcp]] `debugging.md`.

## 4. 코드 스니펫 규약

```python
# ENV 덤프 (노드 __init__ / 스크립트 head)
for k in ("ROS_DOMAIN_ID","RMW_IMPLEMENTATION","ROS_LOCALHOST_ONLY"):
    log(f"  {k}={os.environ.get(k,'<UNSET>')}")
if os.environ.get("RMW_IMPLEMENTATION") != "rmw_cyclonedds_cpp":
    log("  ⚠ RMW 불일치 — 디스커버리 실패 위험")

# 헬스(rclpy 노드): 5초 타이머
def _health(self):
    npub = self.count_publishers(IN_TOPIC)
    self.get_logger().info(f"rx={self._n} pub={npub}")
    if self._n == 0:
        self.get_logger().warn("⚠ "+("상류 미발행" if npub==0 else "QoS/RMW 의심"))
```

web_server diag 송출/브라우저 콘솔은 `sub1_side/server/ros_bridge.py` 의
`_health()` + `lib/api.ts` `useEvents` 의 `type==="diag"` 분기 참조(구현 기준).

## 5. 함정 체크리스트

- [ ] 모든 통신 노드에 ENV 덤프 + 5초 헬스 + 원인 힌트 존재
- [ ] web_server diag 가 WS 로 나가고 브라우저 콘솔 접두사(`[C2/...]`) 통일
- [ ] 단절 진단은 §2 표 순서(위→아래)로, `topic info` Publisher count 로 판정
- [ ] RMW/DOMAIN 은 **양쪽 프로세스 environ** 으로 확인(설정 파일 아님)
- [ ] 계측 추가가 핫패스 성능 해치지 않게(카운터 증가/5초 타이머 수준)
