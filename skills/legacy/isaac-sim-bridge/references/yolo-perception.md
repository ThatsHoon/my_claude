# YOLO Perception inside Isaac Sim

**1문장 요지** — Isaac Sim 안에서 컨베이어 위 물체를 분류하기 위해 ultralytics YOLOv8 모델을 in-process 로 호출, 카메라 프레임을 numpy/torch tensor 로 받아 추론하고 결과를 `vision_msgs/Detection2DArray` 로 publish 하는 패턴을 정의한다. GPU 자원 공유, 학습 데이터 생성, sim2real gap 처방까지 다룬다.

> 본 스킬의 1차 권장은 **in-process YOLO** (시뮬 프로세스 안에서 호출). 추론 부하가 PhysX 와 충돌하기 시작하면 isaac_ros_yolov8 + NITROS 로 분리 — 그 결정 매트릭스와 분리 시점은 §1, `isaac-ros-accel.md §isaac_ros_yolov8 사용 결정` 교차참조.

---

## Contents

1. 결정 매트릭스 — 어디서 추론할 것인가
2. In-process YOLO 구현 (omni.isaac.core CameraSensor → ultralytics)
3. GPU 공유 함정 — PhysX + RTX + TensorRT
4. 카메라 intrinsic 일관성 (Replicator camera writer ↔ camera_info)
5. Detection2DArray publish 와 namespace
6. bbox → 3D pose 추정
7. 학습 데이터 생성 (Replicator + COCO writer)
8. 도메인 랜덤화 — sim2real gap 줄이기
9. 모델 로딩 / FP16 / TensorRT export
10. 안티패턴
11. 교차 참조

---

## 1. 결정 매트릭스 — 어디서 추론할 것인가

| 옵션 | 장점 | 단점 | 권장 시나리오 |
|---|---|---|---|
| **In-process (ultralytics in Isaac Sim Python)** ✅ 1차 | 셋업 단순 (단일 프로세스), 카메라 tensor 를 zero-copy 로 받음 (`isaac.core.sensors.Camera.get_rgba`), 별도 ROS 노드/컨테이너 불필요 | GPU 메모리/연산 자원이 PhysX·RTX 와 경쟁, 추론 burst 가 sim FPS 를 낮춤 | 카메라 ≤ 4대, GPU ≥ 16GB, sim FPS 30+ 가 우선순위 |
| isaac_ros_yolov8 (NITROS) | NVMM zero-copy 로 sim ↔ inference 간 메모리 복사 최소화, 추론 노드가 별도 컨테이너 → 자원 격리 | 셋업 복잡 (CUDA, TensorRT, Isaac ROS 컨테이너), ros bridge 의 image_raw publish 단계가 추가 비용 | 카메라 ≥ 4대 또는 sim FPS < 30 로 떨어질 때 분리 |
| 외부 Python/FastAPI 서비스 | 가장 격리, 다른 머신에 GPU 분산 가능 | 이미지 직렬화 비용 큼, 레이턴시 50ms+ | 시뮬 호스트가 GPU 가 작고 별도 inference 서버가 있는 환경 |

**분리 시점 trigger** (in-process → isaac_ros_yolov8):
1. GPU mem 사용률 > 80% 지속
2. Isaac Sim FPS < 30 지속 (목표 60)
3. 추론 latency > 1.5 × 기대치 (예: YOLOv8m 16ms 기대 → 24ms 초과)

이때 다음 reference 로 넘어감: `isaac-ros-accel.md §isaac_ros_yolov8 사용 결정`.

---

## 2. In-process YOLO 구현

### 2.1 카메라 prim 등록

먼저 USD 에 카메라 prim 이 있어야 한다 (`warehouse-sorting-pipeline.md §2` 의 `/World/Cameras/r0_overhead`).

```python
from omni.isaac.sensor import Camera
import numpy as np

cam = Camera(
    prim_path="/World/Cameras/r0_overhead",
    resolution=(1280, 720),
    frequency=30,
)
cam.initialize()
cam.add_distance_to_image_plane_to_frame()   # depth 도 필요하면
```

`frequency=30` 은 카메라 갱신 주기 — sim step (보통 60Hz) 의 1/2 정도면 충분.

### 2.2 YOLO 모델 로드 (1회만)

ultralytics 의 `YOLO` 객체는 **글로벌 1회 로드**해 재사용. Action Graph 매 tick 마다 로드하면 GPU 가 즉시 죽는다.

```python
from ultralytics import YOLO

_yolo_singleton: YOLO | None = None

def get_yolo(weights: str = "yolov8m.pt", device: str = "cuda:0"):
    global _yolo_singleton
    if _yolo_singleton is None:
        _yolo_singleton = YOLO(weights)
        _yolo_singleton.to(device)
        _ = _yolo_singleton.predict(np.zeros((720, 1280, 3), dtype=np.uint8), verbose=False)  # warmup
    return _yolo_singleton
```

워밍업 1회 호출은 CUDA kernel 컴파일을 미리 마쳐 첫 실프레임 latency 폭증을 막는다.

### 2.3 추론 + Detection2DArray publish

`rclpy` 노드 또는 OG Python script node 안에서 카메라 프레임을 읽어 추론:

```python
import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose, BoundingBox2D

class YoloNode(Node):
    def __init__(self, robot_id: str):
        super().__init__(f"yolo_{robot_id}")
        self.pub = self.create_publisher(Detection2DArray, f"/{robot_id}/yolo/detections", 10)
        self.cam = Camera(prim_path=f"/World/Cameras/{robot_id}_overhead", resolution=(1280, 720))
        self.cam.initialize()
        self.yolo = get_yolo()
        self.timer = self.create_timer(1.0/30.0, self.tick)

    def tick(self):
        rgba = self.cam.get_rgba()                # H×W×4 uint8 torch tensor (RGBA)
        if rgba is None or rgba.size == 0:
            return
        rgb = rgba[..., :3].cpu().numpy()         # 또는 .cuda() 유지 시 GPU 직접 추론 가능
        results = self.yolo.predict(rgb, verbose=False, conf=0.4)
        self.publish_detections(results[0])

    def publish_detections(self, r):
        msg = Detection2DArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "conveyor_camera"
        for b, conf, cls in zip(r.boxes.xywh.cpu().numpy(),
                                r.boxes.conf.cpu().numpy(),
                                r.boxes.cls.cpu().numpy()):
            d = Detection2D()
            d.bbox = BoundingBox2D()
            d.bbox.center.position.x = float(b[0])
            d.bbox.center.position.y = float(b[1])
            d.bbox.size_x = float(b[2])
            d.bbox.size_y = float(b[3])
            h = ObjectHypothesisWithPose()
            h.hypothesis.class_id = str(int(cls))
            h.hypothesis.score = float(conf)
            d.results.append(h)
            msg.detections.append(d)
        self.pub.publish(msg)
```

**GPU-resident 추론** (faster): `cam.get_rgba()` 는 GPU torch tensor 를 반환 가능. CPU 왕복을 생략하고 `self.yolo.predict(rgba_gpu, ...)` 가능 (ultralytics 8.0+ 에서 torch tensor 직접 지원).

다중 로봇 시: `YoloNode(robot_id="r0")` 를 `r0..r3` 각각 인스턴스화. 모델은 글로벌 싱글톤이므로 가중치 메모리는 1번만 차지. carry 비용은 카메라 메모리뿐.

---

## 3. GPU 공유 함정 — PhysX + RTX + TensorRT

Isaac Sim 안에서 YOLO 를 돌리면 같은 GPU 메모리가 세 사용자(PhysX, RTX, ultralytics/TensorRT) 에 분할된다. 측정 예 (RTX 4090 24GB, m0609 4대):

| 사용자 | 단위 | 4대 합 |
|---|---|---:|
| Isaac Sim Kit + Omniverse 기본 | ~2,500 MB | 2,500 |
| PhysX (joints×bodies×envs) | ~150 MB / 로봇 | 600 |
| RTX-Real-Time @ 1280×720 카메라 | ~1,200 MB / 카메라 | 4,800 |
| YOLOv8m FP16 가중치 | ~85 MB | 85 |
| TensorRT engine + activation | ~700 MB | 700 |
| 추론 burst 시 임시 buffer | ~1,000 MB | 1,000 |
| 여유 | — | ~3,000 |
| **합계** | — | ~12,685 (24GB 의 53%) |

여유가 사라지는 trigger:
- 카메라 해상도 1080p (×2.25) → 합계 ~17 GB
- YOLOv8x (×3 가중치) + activation → 추가 ~3 GB
- Replicator SDG 가 백그라운드로 같이 돌 때 (Replicator camera 추가)

처방:
- **카메라 해상도 720p, conf threshold 0.4 이상** — confidence 가 낮은 detection 은 어차피 결정 로직에서 제외됨
- **YOLOv8m 권장** (~52M params); 작은 객체 검출이 필요하면 v8s+SAHI tiling 으로 우회
- **TensorRT export 후 FP16 로 사용**: `YOLO("yolov8m.pt").export(format="engine", half=True, dynamic=False, imgsz=720)` → `.engine` 파일, 이후 `YOLO("yolov8m.engine")` 로드 시 메모리/latency 둘 다 ↓
- **RTX-Real-Time 끄기**: 학습용 SDG 가 아니라 perception 인 경우 `PathTracing` 도 불필요. `RTX Real-Time` 만 사용하면서도 `samples_per_pixel=1` 로 낮추는 옵션 있음

`isaac-ros-accel.md §GPU 예산` 의 표와 일관.

---

## 4. 카메라 intrinsic 일관성

Isaac Sim 의 카메라 prim 이 가지는 focal_length, horizontal_aperture, resolution 으로부터 intrinsic K 가 결정된다. ROS 의 `camera_info` 와 **동일한 K** 를 publish 해야 server / sort_decision_logic 이 정확한 3D pose 를 산출.

```python
def camera_info_from_omni(cam: Camera):
    # cam.get_horizontal_fov() 또는 prim 속성에서 fx, fy 계산
    width, height = cam.get_resolution()
    focal = cam.get_focal_length()          # mm
    horiz_aperture = cam.get_horizontal_aperture()  # mm
    fx = (focal / horiz_aperture) * width
    fy = fx                                  # square pixel 가정
    cx, cy = width / 2.0, height / 2.0
    info = CameraInfo()
    info.width = width
    info.height = height
    info.k = [fx, 0.0, cx,  0.0, fy, cy,  0.0, 0.0, 1.0]
    info.distortion_model = "plumb_bob"
    info.d = [0.0, 0.0, 0.0, 0.0, 0.0]      # Isaac Sim 카메라는 distortion 없음
    return info
```

**중요**: Replicator 로 학습 데이터를 만들 때도 동일한 focal_length / horizontal_aperture 를 사용. 학습 데이터 ↔ 런타임 intrinsic 가 다르면 detection bbox 가 픽셀 단위로 어긋난다 (sim2real gap 의 한 축).

---

## 5. Detection2DArray publish 와 namespace

토픽 명명 (`warehouse-sorting-pipeline.md §3` 의 규약):

| 토픽 | 타입 | 의미 |
|---|---|---|
| `/{robot_id}/yolo/detections` | vision_msgs/Detection2DArray | bbox + class + conf |
| `/{robot_id}/yolo/detection_poses` | geometry_msgs/PoseArray | bbox → 3D pose (depth + intrinsic 활용) |
| `/{robot_id}/cam/conveyor/image_raw` | sensor_msgs/Image | 원본 RGB |
| `/{robot_id}/cam/conveyor/camera_info` | sensor_msgs/CameraInfo | §4 의 K |
| `/{robot_id}/cam/conveyor/depth` | sensor_msgs/Image (32FC1) | 선택, grasp z-offset |

QoS:
- detections: `SystemDefaultsQoS` (`reliability=RELIABLE`, `history=KEEP_LAST(10)`) — 손실 시 다음 프레임에 복구 가능, 단 reliable 권장
- image_raw / depth: `SensorDataQoS` (`reliability=BEST_EFFORT`, `history=KEEP_LAST(5)`) — 큰 페이로드, BE 가 정석

ros2-architect `communication.md §QoS` 와 일관.

---

## 6. bbox → 3D pose 추정

가장 단순한 방법 (대부분의 평면 분류 케이스에 충분):

```python
def bbox_to_world_pose(bbox_xywh, depth_map, K, T_cam_world):
    """
    bbox 중심 픽셀의 depth 를 읽고 카메라 좌표계 3D 점을 산출,
    그 후 카메라→월드 transform 으로 월드 좌표를 얻는다.
    """
    cx, cy, _, _ = bbox_xywh
    u, v = int(round(cx)), int(round(cy))
    z = float(depth_map[v, u])
    if z <= 0 or not np.isfinite(z):
        return None
    fx, fy = K[0, 0], K[1, 1]
    px, py = K[0, 2], K[1, 2]
    X_cam = np.array([(u - px) * z / fx, (v - py) * z / fy, z, 1.0])
    X_world = T_cam_world @ X_cam
    return X_world[:3]
```

**왜 bbox center 만 보는가** — 컨베이어 위 분류 대상은 보통 평면에 놓인 박스/캔. 평균 surface normal 이 +Z 로 가정 가능하고, bbox center 의 depth 가 grasp 면 중심에 가깝다.

복잡한 자세 추정이 필요해지는 시점:
- 객체가 자유 회전 (예: 누운 캔 vs 선 캔) → segmentation mask 활용 권장 (SAM2 + YOLO-seg)
- 객체가 겹쳐서 가려짐 → 6D pose estimator (FoundationPose) 별도 노드로 분리. 본 스킬 범위 밖.

---

## 7. 학습 데이터 생성 (Replicator + COCO writer)

`replicator-sdg.md §컨베이어+YOLO 학습 데이터` 와 짝. 핵심 요지:

```python
import omni.replicator.core as rep

with rep.new_layer():
    cam = rep.create.camera(position=(0, 1.0, 1.5), look_at=(0, 1.0, 0.0))
    with rep.trigger.on_frame(num_frames=1000):
        for cls in ["box_red", "box_blue", "can_a", "reject"]:
            with rep.create.from_usd_at(cls_usds[cls],
                                        position=rep.distribution.uniform((-0.4, 0.8, 0.05), (0.4, 1.2, 0.05)),
                                        rotation=rep.distribution.uniform((0,0,0), (0,360,360)),
                                        semantics=[("class", cls)]):
                pass
        rep.modify.attribute("xformOp:translate", rep.distribution.uniform((0,0.9,1.2),(0,1.1,1.6)),
                             prims=cam)
        rep.randomizer.color(rep.get.material(rep.get.prim_at_path("/World/Floor")))
        rep.randomizer.rotation(...)
    writer = rep.WriterRegistry.get("KittiWriter")
    writer.initialize(output_dir="/data/yolo_train/r0", rgb=True, bounding_box_2d_tight=True)
    writer.attach([cam])

rep.orchestrator.run()
```

- Output 은 KITTI 또는 COCO writer 로. ultralytics 학습 스크립트는 두 포맷 모두 받음.
- 1000 frame × 4 class × ~3 객체 ≈ 12,000 라벨. 일반 분류용 YOLOv8m fine-tune 에 충분.
- 도메인 랜덤화 (다음 절) 을 충분히 걸어야 학습된 모델이 추론 시 동일한 conveyor 에서도 다양한 조명/배경에 robust.

---

## 8. 도메인 랜덤화 — sim2real gap 줄이기

YOLO 가 시뮬에서 학습한 모델로 시뮬 자체를 인식한다면 gap 이 작지만, 도메인 랜덤화는 다음과 같은 효과:
1. 모델이 단일 시뮬 외관에 overfit 하지 않음 → 시뮬 안에서도 spawn position/회전이 달라질 때 robust
2. 추후 sim2real 로 옮길 때 동일 가중치를 재사용 가능 (real 환경 라이팅에도 일반화)

랜덤화 축:
- **Lighting**: `rep.randomizer.light(intensity=rep.distribution.uniform(500, 3000), color_temp=...)`
- **Floor/wall texture**: `rep.randomizer.color(...)` + 텍스처 swap (수십 종 PBR material)
- **Object material**: 같은 class 안에서도 색, roughness 변화 → 모델이 모양에 의존하도록
- **Camera jitter**: 위치 ± 5cm, look_at ± 2cm
- **Sensor noise** (선택): post-process `cv2.GaussianBlur` 또는 Replicator augmenter

`replicator-sdg.md §컨베이어+YOLO 학습 데이터` 에서 더 깊이 다룸.

---

## 9. 모델 로딩 / FP16 / TensorRT export

```python
from ultralytics import YOLO

m = YOLO("yolov8m.pt")               # FP32 PyTorch
m.export(format="engine", half=True, imgsz=720, dynamic=False)
# → yolov8m.engine 생성

# 런타임:
m = YOLO("yolov8m.engine")           # TensorRT FP16
res = m.predict(rgb, verbose=False)  # 동일 인터페이스
```

- TensorRT engine 은 cuDNN/CUDA/TensorRT 버전 / GPU SM 버전에 강결합 — Isaac Sim 컨테이너 안에서 export 한 engine 을 다른 머신/Docker 이미지로 옮기지 말 것
- `dynamic=False` 로 고정 입력 해상도 사용 시 빠름 — 시뮬은 카메라 해상도 고정이므로 ideal
- FP16 으로 약 2× 빠름, 정확도 손실은 분류 시나리오에서 무시 가능 수준

---

## 10. 안티패턴

- ❌ Action Graph 매 tick 마다 `YOLO("yolov8m.pt")` 호출 — GPU OOM 즉시
- ❌ CPU 로 inference (`device="cpu"`) — 4대 카메라 30FPS 면 100% CPU 점유, sim FPS 폭락
- ❌ Image topic 만 publish 하고 detection 은 외부 노드에서 처리 — 본 스킬의 1차 권장이 아님 (resource 격리가 필요해지면 그때 분리)
- ❌ camera_info 미publish 후 server bridge 가 K 를 추정 — 일관성 깨짐, bbox→pose 오차 누적
- ❌ YOLOv8x 같은 큰 모델로 4대 카메라 동시 — GPU 메모리 초과, FPS 폭락
- ❌ 학습 데이터의 camera intrinsic 과 런타임 camera intrinsic 가 다름 — bbox 가 픽셀 단위로 어긋남

---

## 11. 교차 참조

- `warehouse-sorting-pipeline.md §6` — Replicator 스폰 (학습 데이터의 입력원)
- `replicator-sdg.md §컨베이어+YOLO 학습 데이터` — 학습 데이터 파이프라인
- `sort-decision-logic.md` — detection 받아 motion 결정
- `omnigraph-ros-bridge.md §다중 로봇 OG 팩토리` — 카메라 prim 의 OG 노드
- `isaac-ros-accel.md §isaac_ros_yolov8 사용 결정` — 분리 시점
- `physx-tuning.md §GPU 예산` — §3 의 메모리 계산
- 외부: ultralytics docs (`/home/hoon/isaac-sim-skill-research/11-warehouse-sorting/ultralytics/repo/docs/`), NVIDIA-ISAAC-ROS/isaac_ros_object_detection (`11-warehouse-sorting/isaac_ros_yolov8/repo/`)
