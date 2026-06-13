# foxglove-telemetry-viz.md — Foxglove(자체호스팅 Lichtblick) 시뮬레이터 상태 시각화

GP 운용자/개발자용 심화 모니터링(기존 Next.js UI 와 별개). 범용
foxglove_bridge/SDK·ROS↔웹 일반은 [[ros2-architect]] `web-bridge-streaming.md`
위임 — 여기는 **GP 조합·제약·layout·확장 패턴만**. 발행측 토픽맵은
`references/sensor-and-comms.md`, 같은-PC 우회 토대(불변식 8)는
`references/ros2-interop-and-bypass.md`. 권위 런북:
`/home/rokey/dev_ws/isaac_sim/cobot3/sub1_side/FOXGLOVE.md`.

## 목차
1. 원칙/제약 (hard — 먼저 읽을 것)
2. 2-모드 아키텍처 (M1 같은-PC / M2 2-PC)
3. 토픽 → Lichtblick 렌더 매핑 (bridge 네이티브)
4. foxglove_bridge 런처
5. Lichtblick 자체호스팅 + layout + /debug iframe
6. 핵심 확장 패턴 (depth+CameraCalibration / FireEvent 무기 패널)
7. 검증
8. 함정 체크리스트

> 로봇 = `spot_with_arm` 단일 아티큘레이션(설계 2026-05-17 로봇 스왑).
> **토픽 계약은 로봇 불문 불변** — 본 문서는 prim 이 아닌 토픽 기준.

---

## 1. 원칙/제약 (hard)

- **외부 SaaS(`app.foxglove.dev`) 임베드 금지.** 경계초소 데이터 외부 유출.
  **자체호스팅 Lichtblick(:8080) 전용** — 어느 모드든.
- **republish 는 읽기 미러.** 같은-PC(M1)에서 `ros_bridge.py` 의
  `/ingest`→ROS2 재발행은 `/ingest`·DB·WS 를 **건드리지 않는다**.
  `C2_INGEST_REPUBLISH` 미설정(기본)이면 종전과 바이트 동일(2-PC·대시보드
  무영향). 토대는 불변식 8 (`references/ros2-interop-and-bypass.md`).
- **Foxglove 는 USD 를 못 읽는다.** 1단계 3D 로봇 메시 생략 — `/tf`+
  `/robot/odom` 축 + JointState Plot 으로 본다. Spot URDF/glTF 메시는
  후속(§6 비고, `asset_uri_allowlist` 경유).

## 2. 2-모드 아키텍처

토픽명은 두 모드 동일 → **layout.json 무변경**(모드 무관 재사용).

### M1 — 같은-PC 임시 (`C2_INGEST_REPUBLISH=1`)
```
Isaac camera_publisher(py3.11) ─HTTP /ingest─▶ web_server :8000 (py3.10)
   C2_INGEST_REPUBLISH=1 → ros_bridge 10Hz 재발행:
     /robot/{state,gps,odom} /tf /dsr01/joint_states
     /robot/leg_joint_states /c2/video/compressed
   ─시스템 ROS2(py3.10, 동일구현·같은-PC OK)─▶
   foxglove_bridge :8765 ─ws─▶ Lichtblick :8080 ─iframe─▶ /debug
```
Isaac↔시스템 DDS 홉을 HTTP 가 대체(불변식 8). 유일 DDS 홉(web_server→
bridge)은 동일 py3.10·같은-PC 라 정상.

### M2 — 2-PC 정식 (재발행 OFF, 기본·공개)
`C2_INGEST_REPUBLISH` 미설정 → `ros_bridge.py` 종전대로 Isaac 실토픽
구독, C2 PC 의 foxglove_bridge 가 LAN 으로 Isaac 토픽 직접 노출. 공개는
Cloudflare Access(동일 정책 — 디버그=전상태 노출), `FOXGLOVE.md §2-PC`.

## 3. 토픽 → Lichtblick 렌더 매핑 (bridge 네이티브)

**핵심**: `foxglove_bridge` 는 ROS 타입을 그대로 광고하고 Lichtblick 이
**네이티브 렌더**한다 — 직접 스키마 변환 불필요. 우측 열은 SDK 직결
(`foxglove.start_server`) 시의 등가 Foxglove well-known 스키마(참고용; GP 는
bridge 경로).

| GP 토픽 | ROS 타입 (bridge 네이티브) | Lichtblick 패널 | (SDK 직결 등가 스키마) |
|---|---|---|---|
| `/cam/realsense/rgb` | sensor_msgs/Image (rgb8) | Image | RawImage |
| `/cam/realsense/depth` | sensor_msgs/Image (32FC1) | Image | RawImage |
| `/cam/realsense/camera_info` | sensor_msgs/CameraInfo | (Image 오버레이) | CameraCalibration |
| `/c2/video/compressed` | sensor_msgs/CompressedImage (jpeg) | Image | CompressedImage |
| `/dsr01/joint_states` | sensor_msgs/JointState | Plot (arm) | JointStates |
| `/robot/leg_joint_states` | sensor_msgs/JointState | Plot (leg) | JointStates |
| `/robot/odom` | nav_msgs/Odometry | 3D | Odometry |
| `/robot/gps` | sensor_msgs/NavSatFix | Map | LocationFix |
| `/robot/state` | std_msgs/String(JSON) | RawMessages | (generic JSON Channel) |
| `/tf`,`/tf_static` | tf2_msgs/TFMessage | 3D (좌표축) | FrameTransforms |

정본 토픽맵/QoS 는 `references/sensor-and-comms.md §1`. **임의 토픽명 금지
(불변식 5)** — 변경은 `server/config.py` TOPICS 와 대조 후에만.

## 4. foxglove_bridge 런처

`sub1_side/run_foxglove_bridge.sh` (생성됨):
`ros2 launch foxglove_bridge foxglove_bridge_launch.xml port:=8765
address:=0.0.0.0 use_compression:=false`. **화이트리스트 없음**(전 토픽
노출 → layout 모드 무관). domain130·`rmw_fastrtps_cpp`·`site.sh` FastDDS
프로파일 정합(`FASTDDS.md §3`). 설치: `sudo apt install -y
ros-humble-foxglove-bridge`(3.3.0 검증).

- `use_compression` 은 로보틱스에서 비권장(기본 false 유지).
- 후속 Spot URDF/glTF 3D 메시 도입 시: `asset_uri_allowlist` 에 `package://
  …(dae|glb|gltf|stl|urdf)` 허용 추가 + Lichtblick 에 자산 서빙. 1단계는 불요.

## 5. Lichtblick 자체호스팅 + layout + /debug

docker `ghcr.io/lichtblick-suite/lichtblick:latest`(Caddy :8080 정적 SPA).
entrypoint 가 `/lichtblick/default-layout.json` 바인드마운트를 읽어 레이아웃
주입(검증됨):
```bash
sudo docker rm -f cobot3-lichtblick 2>/dev/null
sudo docker run -d --name cobot3-lichtblick --restart unless-stopped -p 8080:8080 \
  -v /home/rokey/dev_ws/isaac_sim/cobot3/sub1_side/lichtblick/layout.json:/lichtblick/default-layout.json:ro \
  ghcr.io/lichtblick-suite/lichtblick:latest
```
`sub1_side/lichtblick/layout.json` 패널: 3D[`/tf`,`/robot/odom`] ·
RawMessages[`/robot/state`] · Plot[arm `/dsr01/joint_states`] · Plot[leg
`/robot/leg_joint_states`] · Image[`/c2/video/compressed`].

표시 = 기존 Next.js `app/debug/page.tsx` 전체화면 iframe, 데이터소스 자동:
`?ds=foxglove-websocket&ds.url=ws://localhost:8765`. `app/page.tsx`·
`layout.tsx` 무수정. env `NEXT_PUBLIC_LICHTBLICK_URL`(기본
`http://localhost:8080`) 빌드타임 주입 — 변경 시 `next dev` 재시작/재빌드.

## 6. 핵심 확장 패턴 (net-new)

### 6.1 RealSense depth + CameraCalibration 패널
- depth 발행은 이미 OG 에 있음(`/cam/realsense/depth`,
  `distance_to_image_plane`, `references/sensor-and-comms.md §2`). Lichtblick
  layout 에 **Image 패널 1개 추가**(topic=`/cam/realsense/depth`).
  encoding 은 **`32FC1`**(16UC1 이면 mm 정수) — 패널 색맵/range 설정.
- `/cam/realsense/camera_info`(sensor_msgs/CameraInfo, OG ROS2CameraHelper
  자동) 를 같은 Image 패널의 calibration 소스로 연결 → 왜곡/투영 정합.
- 발행측 OG 확장이 필요하면 `references/sensor-and-comms.md` 위임(여기서
  새 OG 노드 설계하지 말 것).

### 6.2 FireEvent 무기 패널
`references/weapon-fire.md` 의 `FireEvent {ts,operator,target_ref,hit,
hit_prim,distance_m}` 를 Foxglove 로 노출. **GP 패턴**: `/robot/state` 와
동일하게 **`std_msgs/String(JSON)` 토픽으로 발행**(커스텀 msg 타입 등록
불요 → bridge·Lichtblick 즉시 표시). 절차:

1. 토픽 계약 먼저 등재: `server/config.py` TOPICS + `references/
   sensor-and-comms.md §1` 표에 `/robot/weapon/fire_event`
   (std_msgs/String JSON, RELIABLE) 추가 — **임의 추가 금지(불변식 5)**,
   사격 명령 service `/robot/weapon/fire` 와 별개(이벤트 로그용).
2. `fire_events` psql 적재는 그대로(불변식 4 — 영상만 DB 금지).
3. Lichtblick layout 에 **RawMessages 패널**(topic=위 토픽) 추가.
4. (옵션) 3D 패널에 히트 시각화: hit_pos·트레이서 선분을 SceneUpdate(또는
   `visualization_msgs/Marker`) 1회성 발행 → 3D 패널이 origin→hit 라인/
   포인트 표시. 트레이서 prim 자체는 `references/weapon-fire.md §4`.

## 7. 검증

**M1(재발행 ON)**: Isaac `run_camera_pub.sh`→Play → `curl -s
localhost:8000/ingest/stats` frame/tele 증가 → `ROS_DOMAIN_ID=130 ros2
topic list` 에 §3 토픽 + `ros2 node info /c2_web_server` 가 이들을
**publisher** → `/tmp/cobot3_foxglove.log` `listening on 0.0.0.0:8765` →
`http://localhost:3000/debug` 패널 스트림(3D 축 이동·State·Plot·Image).

**M2 회귀(재발행 OFF 기본)**: `C2_INGEST_REPUBLISH` 없이 기동 →
`ros2 node info /c2_web_server` 가 구독+업링크 pub 만, **신규 publisher/
타이머 0** → 텔레메트리 버스트 후 DB 중복행 0, WS 중복 0.

## 8. 함정 체크리스트

- [ ] M1 인데 `C2_INGEST_REPUBLISH=1` 미설정 → Foxglove 토픽 0.
- [ ] 토픽 보이나 0 메시지 → ingest >10s 끊김(재발행 정지). Isaac uplink·
      `/ingest/stats` 확인.
- [ ] 2-PC 인데 재발행 ON → DB·WS 중복(불변식: 기본 OFF 유지).
- [ ] 외부 SaaS(`app.foxglove.dev`) 임베드 시도 0건 — 자체호스팅만.
- [ ] prod https 오리진 + http Lichtblick iframe → 혼합콘텐츠 차단
      (임시 localhost http 통일, 정식 Cloudflare wss).
- [ ] `NEXT_PUBLIC_*` 변경 후 web 재빌드/재시작 누락 없음.
- [ ] docker 그룹 미반영 시 임시 런북은 `sudo docker`.
- [ ] depth Image encoding `32FC1`(또는 16UC1 mm) 명시 — 빈 패널 방지.
- [ ] FireEvent 는 토픽 계약(config.py TOPICS·sensor-and-comms §1) 등재
      후에만 — 임의 토픽명 금지(불변식 5). 영상 외 데이터 psql(불변식 4).
- [ ] layout.json 패널 추가/변경 시 두 모드 토픽명 동일 확인.
