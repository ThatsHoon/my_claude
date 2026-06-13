# ros2-interop-and-bypass.md — 같은-PC Isaac↔호스트 ROS2 불통 & D-확장 우회

GP 프로젝트에서 가장 비싸게 배운 것. 범용 메커니즘은 [[isaac-sim-bridge]]
`installation.md`(같은-호스트 DDS 한계·scrub), [[isaac-sim-mcp]] `debugging.md`
(기동 라이프사이클) 위임 — 여기는 **이 프로젝트의 결론·우회 패턴**.

## 1. 결론 (반복 금지 — 이미 다 해봤다)

Isaac Sim 5.1 번들 내부 ROS2(Python **3.11**) ↔ 시스템 ROS 2 Humble
(Python **3.10**) 가 **같은 호스트에서 DDS 디스커버리 안 됨**. Isaac 측은
정상 발행(OG·render product·timeline OK, 내부 rclpy loaded)하나 외부
`ros2 topic info` 의 Publisher 가 항상 0.

**전부 시도했고 전부 실패**(같은-호스트 한정 병리):
- cyclone 통일(양측 `rmw_cyclonedds_cpp` + `CYCLONEDDS_URI` localhost peer)
- `LD_LIBRARY_PATH` 에 Isaac 번들 `exts/isaacsim.ros2.bridge/humble/lib`
- 시스템 ROS env scrub(→ Isaac 내부 rclpy 정상 로드되지만 여전히 미발견)
- FastDDS UDP-only 프로파일(= NVIDIA 공식 `IsaacSim-ros_workspaces/humble_ws/
  fastdds.xml` 과 동일 내용)
- 공식 `clock.py` 예제도 같은 환경에서 호스트 미발견(테스트는 단명이라
  inconclusive 했지만, 장수 publisher 인 camera_publisher 가 모든 설정에서
  0 인 것이 누적 증거)

→ **같은-PC 는 ROS2 로 풀려고 하지 말 것.** 머신 분리(2-PC LAN)면 DDS 와이어
프로토콜은 ABI·Python버전 무관이라 NVIDIA 지원 경로(같은 도메인 +
`fastdds_no_shm.xml`). 즉 한계는 *같은-호스트*에 국한.

## 2. 모드 선택 (불변식)

- **실배포 2-PC LAN** → 설계 본문 ROS2 정공(같은 `ROS_DOMAIN_ID=130` +
  `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` + `FASTRTPS_DEFAULT_PROFILES_FILE=
  .../cobot3/fastdds_no_shm.xml`, `ROS_LOCALHOST_ONLY=0`).
- **같은-PC(임시 검증)** → **D-확장 HTTP 우회**(§3). ROS2 손대지 말 것.

## 3. D-확장 패턴 (검증 완료 — 같은-PC 영상+텔레메트리 웹 수신)

Isaac 은 단일 프로세스 → ROS2 가 나르려던 데이터 거의 전부 in-process
Python API 로 접근 가능. camera_publisher 한 곳에서 캡처해 web_server 로
한 홉 HTTP POST(DDS 완전 우회).

### 3.1 송신측 (`main_side/camera_publisher.py`)
```
세팅(once, world.reset+play 후):
  import omni.replicator.core as rep
  rgb  = rep.AnnotatorRegistry.get_annotator("rgb")
  dep  = rep.AnnotatorRegistry.get_annotator("distance_to_image_plane")
  rgb.attach([render_product_path]); dep.attach([render_product_path])
       # render_product_path = OG CreateRP.outputs:renderProductPath (지연 attach)
  from isaacsim.core.prims import Articulation
  m0609 = Articulation("/World/Robot/m0609"); m0609.initialize()
  anymal= Articulation("/World/Robot/anymal"); anymal.initialize()
  xc = UsdGeom.XformCache()                    # base pose → sim-GPS

매 ~12 step (≈5Hz):
  tele = {arm_q: m0609.get_joint_positions()[:6],
          leg_q: anymal.get_joint_positions()[:12],
          odom : XformCache(/World/Robot/anymal).translation,
          gps  : enu→LLHA(odom, LAT0,LON0,ALT0)}
  frame= resize_RGB_640x360(rgb.get_data())    # numpy 스트라이드(cv2 불요)
  queue.put_nowait((frame, tele))              # 비차단

백그라운드 스레드(urllib, Kit 루프 비차단):
  POST {C2}/ingest/telemetry  (json)
  POST {C2}/ingest/frame?w=640&h=360&enc=rgb  (raw bytes)
```
- **Kit 루프에 sleep/blocking 금지** — 큐 적재만, POST 는 별도 스레드.
- 프레임 인코딩 의존성 회피: Isaac python 에 cv2/PIL 없을 수 있어 **raw RGB
  numpy 스트라이드 다운샘플(640×360)** 전송, JPEG 인코딩은 web_server(cv2)에서.
- 런처(`run_camera_pub.sh`/`_gui.sh`)는 ROS env scrub + Isaac 번들 ROS2 격리
  포함. GUI 는 harness 백그라운드 불가(DISPLAY) → 사용자 `!` 기동.

### 3.2 수신측 (`sub1_side/server/app.py`) — 기존 UI 무변경
| 엔드포인트 | 처리 |
|---|---|
| `POST /ingest/frame` | RGB→BGR, (선택)YOLO 오버레이, `ros._set_video_frame`(WebRTC/MJPEG 그대로 소비), `ros.ingest_ts` |
| `POST /ingest/telemetry` | `ros.latest` 갱신 + WS state/gps + DB(gps_track/joint_snapshots/robot_state_log/rosout_warn), `ros.ingest_ts` |
| `GET /ingest/stats` | `{frame,tele}` 누적 |
- ingest 는 **rclpy 불요**(ros_bridge 독립). ros_bridge `_health` 는
  `ingest_ts` 인지 → 최근 ingest 시 구 ROS2 video WARN 대신
  `ingest=LIVE` INFO(거짓경보 억제).
- 영상 **DB 저장 금지**(불변식 4 유지).

## 4. 함정 체크리스트
- [ ] 같은-PC 에서 ROS2 디스커버리 디버깅에 시간 쓰지 말 것 — D-확장으로.
- [ ] 영상 캡처는 OG render product 에 annotator attach(첫 rp 확보 후 지연).
- [ ] POST 는 백그라운드 스레드(Kit thread 비차단).
- [ ] `robot_state` mode/battery/waypoint 는 보행 FSM 미구현 → 빈 값(정상).
- [ ] 2-PC 로 갈 땐 D-확장 끄고 ROS2 정공 + `fastdds_no_shm.xml`.
