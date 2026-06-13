# sensor-and-comms.md — RealSense·video_degrade·sim-GPS·rosout·OG 토픽맵

GP 센서/통신 오케스트레이션. ROS↔웹·WebRTC·오디오·NavSatFix·rosout 일반
메커니즘은 [[ros2-architect]] `web-bridge-streaming.md`, OG 노드 일반은
[[isaac-sim-bridge]] `omnigraph-ros-bridge.md`. 여기는 **GP 배선·파라미터**.

## 목차
1. GP 토픽맵 (설계 §12 고정)
2. link_6 RealSense (K 행렬·depth)
3. OG 브리지 배선 (sensor_bridge)
4. video_degrade_node (5fps/JPEG)
5. sim-GPS node (world pose → NavSatFix)
6. rosout WARN 릴레이
7. 함정 체크리스트

---

## 1. GP 토픽맵 (절대 변형 금지 — 설계 §12)

| 토픽 | 타입 | QoS | 방향 |
|---|---|---|---|
| `/dsr01/joint_states` | sensor_msgs/JointState | RELIABLE d10 | OG→ROS (m0609) |
| `/robot/leg_joint_states` | sensor_msgs/JointState | RELIABLE d10 | OG→ROS (ANYmal) |
| `/cam/realsense/rgb` | sensor_msgs/Image | BEST_EFFORT d5 | OG→ROS |
| `/cam/realsense/depth` | sensor_msgs/Image | BEST_EFFORT d5 | OG→ROS |
| `/c2/video/compressed` | sensor_msgs/CompressedImage | BEST_EFFORT d5 | degrade→C2 |
| `/c2/depth/compressed` | sensor_msgs/CompressedImage | BEST_EFFORT d5 | degrade→C2 |
| `/robot/gps` | sensor_msgs/NavSatFix | RELIABLE d10 | gps_node |
| `/robot/odom` | nav_msgs/Odometry | RELIABLE d10 | locomotion |
| `/robot/state` | (custom) RobotState | RELIABLE d10 | locomotion |
| `/robot/nav/goal` | geometry_msgs/PoseStamped | RELIABLE d5 | C2→robot |
| `/robot/speaker/audio` | (custom) AudioChunk | RELIABLE d20 | C2→robot |
| `/rosout` | rcl_interfaces/Log | 기본 | level≥30 필터 |
| `/tf`,`/tf_static` | tf2_msgs/TFMessage | RELIABLE / +TRANSIENT_LOCAL | OG→ROS |

`ROS_DOMAIN_ID=130`. 영상 rgb 는 C2 에서 **WebRTC**(`/c2/webrtc/offer`),
`/c2/video/compressed` 는 저대역 MJPEG 폴백 겸 토픽. **영상은 DB 저장 안 함**.

## 2. link_6 RealSense (D4)

prim: `/World/Robot/m0609/link_6/realsense` (Camera + depth annotator).
K 행렬은 cobot3 `setup_cameras.py` 계산 재사용:

```
fx = focal_mm / h_aperture_mm * width_px
fy = focal_mm / v_aperture_mm * height_px
cx = width/2 ; cy = height/2
```

focal·aperture 를 prim 에 set → ROS2CameraHelper 가 camera_info 자동.
depth: annotator "distance_to_image_plane", 16UC1 또는 32FC1.

## 3. OG 브리지 배선 (`/World/Graphs/sensor_bridge`)

`OnPlaybackTick → ROS2Context →` 아래 노드(타입 점표기, 상세
[[isaac-sim-bridge]] `omnigraph-ros-bridge.md`):

- `ROS2PublishJointState`(m0609 articulation) → `/dsr01/joint_states`
- `ROS2PublishJointState`(anymal articulation) → `/robot/leg_joint_states`
- `IsaacCreateRenderProduct`(realsense) → `ROS2CameraHelper`(rgb) `/cam/realsense/rgb`
- 동 RP → `ROS2CameraHelper`(depth) `/cam/realsense/depth`
- `ROS2PublishTransformTree` → `/tf`,`/tf_static`

`/World/Graphs/cmd_bridge`: nav goal 은 노드측 rclpy 구독(c2_command/locomotion).

## 4. video_degrade_node (net-new, D8)

발행측 대역 절감. 메커니즘 일반은 [[ros2-architect]] `web-bridge-streaming.md`.
GP 파라미터:

```
sub /cam/realsense/rgb (BEST_EFFORT d5)   sub /cam/realsense/depth
  throttle → 5 fps                          throttle → 5 fps
  cv2.resize 1280x720 → 640x360             16bit→8bit scale
  cv2.imencode .jpg q=50                    .jpg/.png
  → pub /c2/video/compressed                → pub /c2/depth/compressed
```

- ≈ 원본의 수십분의 1 대역. 노드는 **프레임 생산만**, WebRTC 협상은
  C2 web_server(aiortc) 담당. 영상은 어떤 경로로도 **DB 저장 금지**.

## 5. sim-GPS node (net-new, D9)

Isaac 에 GPS 없음 → ANYmal base world pose 를 위경도로 환산.

```python
# 기준점(설정): LAT0, LON0, ALT0 ; sim 원점 = (0,0,0) = (LAT0,LON0)
x, y, z = base_world_xyz                 # robot.robot.get_world_pose()[0]
dlat = (y / 6378137.0) * (180/pi)
dlon = (x / (6378137.0*cos(radians(LAT0)))) * (180/pi)
NavSatFix(latitude=LAT0+dlat, longitude=LON0+dlon, altitude=ALT0+z)
# → pub /robot/gps (RELIABLE d10) ; /robot/odom 와 일관 유지
```

ENU(x=E, y=N) 가정. 평탄근사(소영역) 충분. `gps_track` 테이블에 적재.

## 6. rosout WARN 릴레이 (net-new)

`/rosout`(rcl_interfaces/Log) 구독, `msg.level >= 30`(WARN) 필터:
- level: DEBUG10 INFO20 **WARN30** ERROR40 FATAL50
- server-bridge 가 WS `/events` 로 `{type:"log",level,name,msg,ts}` 멀티캐스트
- `rosout_warn` 테이블 적재. 일반 패턴 [[ros2-architect]] `web-bridge-streaming.md`.

## 7. 함정 체크리스트

- [ ] 토픽명/QoS 가 §1 표와 정확히 일치(`/dsr01/joint_states` 등).
- [ ] 영상 데이터가 DB 적재 경로/스키마에 절대 없음.
- [ ] RealSense K = focal/aperture 기반(하드코딩 금지).
- [ ] OG 노드 타입 점표기(`isaacsim.ros2.bridge.*`).
- [ ] gps 기준점(LAT0/LON0) 설정값화, odom 과 좌표 일관.
- [ ] rosout 필터 level>=30(>가 아닌 >=). 변경 시 C2 로그 패널 영향 점검.
