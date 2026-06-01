# replicator-sdg.md — Replicator 기반 합성 데이터 & 도메인 랜덤화

이 reference 는 **vision/perception 학습용 라벨링된 데이터를 시뮬에서 자동 생성하거나, RL 학습 중 온라인으로 도메인 랜덤화**하는 방법을 다룬다. Annotator, Writer, Distribution API, COCO/KITTI 라이터, Replicator-Agent, 그리고 Isaac Lab 과의 결합.

## Contents
1. Replicator 의 위치 — offline SDG vs online DR
2. 첫 데이터셋 생성 (rep.* API)
3. Distribution — 랜덤화의 단위
4. Annotator — 라벨 종류
5. Writer — 디스크 저장 포맷
6. 카메라/라이트/머티리얼 랜덤화 패턴
7. 객체 배치 랜덤화 (cuboid scatter, ...)
8. Replicator-Agent — 사람·로봇 행동 시뮬
9. 센서 노이즈 랜덤화 (sim2real 축 3)
10. Isaac Lab 과 결합 — 온라인 DR
11. 학습 데이터 품질 체크리스트
12. 자주 발생하는 SDG 함정

---

## 1. Replicator 의 위치 — offline SDG vs online DR

Replicator 는 두 모드로 쓰임:

| 모드 | 산출물 | 트리거 | 용도 |
|---|---|---|---|
| **Offline SDG** | 이미지 + 라벨 (COCO/KITTI/npy) 디스크에 저장 | `rep.orchestrator.run()` | Detection/Segmentation 학습 데이터셋 |
| **Online DR** | 매 RL step 마다 씬 변형 | Isaac Lab EventTerm 또는 OG 노드 | sim2real 시각 갭 줄이기 |

두 모드의 코드는 비슷하지만 **Writer 가 붙느냐**가 결정 차. Offline 은 Writer 가 디스크에 저장하고, Online 은 Writer 없이 변경만 적용.

원본: `06-replicator/replicator_tutorials/`, `06-replicator/synthetic_data_generation/`

## 2. 첫 데이터셋 생성

```python
import omni.replicator.core as rep

with rep.new_layer():
    # 1) 씬 셋업
    camera = rep.create.camera(position=(2, 2, 2), look_at=(0, 0, 0))
    render_product = rep.create.render_product(camera, (1024, 768))

    cube = rep.create.cube(position=(0, 0, 0), semantics=[("class", "cube")])
    sphere = rep.create.sphere(position=(0.5, 0, 0), semantics=[("class", "sphere")])

    # 2) 랜덤화 그래프
    with rep.trigger.on_frame(num_frames=100):
        with cube:
            rep.modify.pose(position=rep.distribution.uniform((-1, -1, 0), (1, 1, 0)))
        with sphere:
            rep.modify.pose(position=rep.distribution.uniform((-1, -1, 0), (1, 1, 0)))

    # 3) Annotator + Writer
    writer = rep.WriterRegistry.get("BasicWriter")
    writer.initialize(
        output_dir="/home/me/dataset",
        rgb=True,
        bounding_box_2d_tight=True,
        semantic_segmentation=True,
    )
    writer.attach([render_product])

    # 4) 실행
    rep.orchestrator.run()
```

실행 후 `/home/me/dataset/rgb_xxxx.png`, `bounding_box_2d_tight_xxxx.npy`, `semantic_segmentation_xxxx.png` 가 100장씩 생성됨.

### 헤드리스로 자동 실행

```bash
~/.local/share/ov/pkg/isaac-sim-6.0.0/python.sh sdg_script.py
```

스크립트 끝에 `simulation_app.close()` 호출. 안 호출하면 프로세스가 안 끝남.

## 3. Distribution — 랜덤화의 단위

| API | 의미 | 예 |
|---|---|---|
| `rep.distribution.uniform(low, high)` | 균등 분포 | `(-1, -1, 0), (1, 1, 0)` 3D 박스 안 |
| `rep.distribution.normal(mean, std)` | 정규 | `(0, 0, 0), (0.1, 0.1, 0.1)` |
| `rep.distribution.choice([...])` | 이산 선택 | `["red.usd", "blue.usd", "green.usd"]` |
| `rep.distribution.sequence([...])` | 순환 | 첫 frame=v1, 둘=v2, ... |
| `rep.distribution.log_uniform(low, high)` | 로그 균등 | scale 류 randomize |

분포는 함수 호출이 아니라 **그래프 노드** — 매 trigger 마다 evaluate 됨. trigger 가 100 frame 이면 100번 샘플.

## 4. Annotator — 라벨 종류

라벨 종류별 attach 옵션 (BasicWriter 의 kwargs):

| Annotator | 출력 형식 | 용도 |
|---|---|---|
| `rgb=True` | PNG | 일반 학습 입력 |
| `depth=True` | float32 npy | depth estimation |
| `instance_segmentation=True` | PNG (palette) | instance seg 학습 |
| `semantic_segmentation=True` | PNG (palette) + JSON (mapping) | semantic seg |
| `bounding_box_2d_tight=True` | npy + JSON | object detection (COCO 호환) |
| `bounding_box_2d_loose=True` | npy + JSON | (occlusion 포함된 큰 박스) |
| `bounding_box_3d=True` | npy | 3D detection (KITTI 호환) |
| `normals=True` | float32 npy | surface normals |
| `motion_vectors=True` | float32 npy | optical flow |
| `pointcloud=True` | ply | 3D vision |

semantic 라벨은 USD 의 prim 에 부착해야 함:
```python
import omni.usd
from pxr import Semantics
prim = stage.GetPrimAtPath("/World/Cube")
sem = Semantics.SemanticsAPI.Apply(prim, "cube_semantics")
sem.CreateSemanticTypeAttr().Set("class")
sem.CreateSemanticDataAttr().Set("cube")
```

또는 `rep.create.cube(..., semantics=[("class", "cube")])` 처럼 생성 시 부여.

원본: `06-replicator/synthetic_data_generation/`

## 5. Writer — 디스크 저장 포맷

```python
writer = rep.WriterRegistry.get("BasicWriter")          # PNG + npy
writer = rep.WriterRegistry.get("KittiWriter")          # KITTI 포맷 (3D box, calib)
writer = rep.WriterRegistry.get("YoloWriter")           # YOLO txt 라벨 (커뮤니티)
writer = rep.WriterRegistry.get("CocoWriter")           # COCO json
```

커스텀 Writer:
```python
@rep.WriterRegistry.register
class MyWriter(rep.Writer):
    def write(self, data):
        rgb = data["rgb"]
        bbox = data["bounding_box_2d_tight"]
        # ... 자체 포맷으로 저장
```

## 6. 카메라/라이트/머티리얼 랜덤화 패턴

### 카메라 위치/자세

```python
with rep.trigger.on_frame(num_frames=500):
    with camera:
        rep.modify.pose(
            position=rep.distribution.uniform((1, 1, 1), (3, 3, 3)),
            look_at=(0, 0, 0),
            up=(0, 0, 1),
        )
```

look_at 까지 같이 랜덤화하면 카메라가 항상 객체를 향함 → bbox 가 항상 in-frame.

### 라이트

```python
with rep.create.light(light_type="dome", intensity=1000) as light:
    with rep.trigger.on_frame():
        rep.modify.attribute("intensity", rep.distribution.uniform(500, 5000))
        rep.modify.attribute("color", rep.distribution.uniform((0.5, 0.5, 0.5), (1.0, 1.0, 1.0)))
```

dome light + HDRI: HDR map 도 랜덤하게 교체:
```python
with rep.create.light(light_type="dome",
                      texture=rep.distribution.choice([
                          "/World/hdri/studio.hdr",
                          "/World/hdri/outdoor.hdr",
                          "/World/hdri/factory.hdr",
                      ])):
    pass
```

### 머티리얼

```python
mats = rep.create.from_usd("/World/Materials")
with cube:
    rep.randomizer.materials(mats)
```

100개의 머티리얼 라이브러리에서 매 frame 마다 cube 의 머티리얼 교체. **vision policy 의 색깔 over-fit 방지에 효과적**.

## 7. 객체 배치 랜덤화

### Uniform scatter in volume

```python
trays = rep.create.from_usd("/Iso/Office/desk.usd", count=50)
with trays:
    rep.modify.pose(
        position=rep.distribution.uniform((-1, -1, 0), (1, 1, 0)),
        rotation=rep.distribution.uniform((0, 0, 0), (0, 0, 360)),
    )
```

### Scatter on surface (PhysX 충돌 회피)

```python
plane = rep.create.plane(size=(2, 2))
with cubes:
    rep.randomizer.scatter_2d(plane, check_for_collisions=True)
```

빈 surface 위에 cube 50개 무작위 배치, 충돌 안 나도록 자동 spread.

### Sequence (체계적 sweep)

```python
with rep.trigger.on_frame(num_frames=10):
    with cube:
        rep.modify.pose(
            position=rep.distribution.sequence([
                (i*0.1, 0, 0) for i in range(10)
            ])
        )
```

## 8. Replicator-Agent — 사람·로봇 행동 시뮬

`06-replicator/action_and_event_data_generation/` 의 새 영역. 사람 모델이 시뮬 안에서 보행/제스처/상호작용 → 카메라가 캡처 → social robot / surveillance / HRI 학습.

```python
import omni.replicator.agent as ra

human = ra.create.character(name="Person_01", position=(0, 0, 0))
human.set_behavior_tree("/World/behaviors/walk_to_target.xml")

# 카메라가 따라가며 캡처
camera = ra.create.tracking_camera(target=human)
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(output_dir="/data/social", rgb=True, bounding_box_2d_tight=True)
writer.attach([camera])

ra.orchestrator.run(duration=60.0)
```

행동 트리 (behavior tree) 는 `Behave!` 의 XML 포맷. 기본 제공 액션: walk, sit, pick_up, gesture.

## 9. 센서 노이즈 랜덤화 (sim2real 축 3)

`physx-tuning.md` §9 축 3 의 자세한 처방.

### 카메라 노이즈 (Gaussian + 모션 블러 + barrel distortion)

```python
camera_distortion = rep.create.material(
    "OmniPBR",
    ...
)
# Camera attribute 랜덤화
with rep.trigger.on_frame():
    with camera:
        rep.modify.attribute("focusDistance",
                              rep.distribution.uniform(1.0, 3.0))
        rep.modify.attribute("fStop",
                              rep.distribution.uniform(2.0, 8.0))
```

또는 후처리:
```python
# 렌더 결과 위에 np.random.normal noise 추가하는 custom annotator
```

### Depth 노이즈 (Realsense / Kinect 모델)

Isaac Sim 5.1+ 에 Realsense 모델 내장:
```python
camera_prim = stage.GetPrimAtPath("/World/Camera")
camera_prim.GetAttribute("isaac:realsense").Set(True)
camera_prim.GetAttribute("isaac:realsense:depthNoise").Set(0.05)
```

### Lidar 노이즈

RTX Lidar prim 의 attribute:
```python
lidar.GetAttribute("rangeDistanceNoise").Set(0.02)   # m std
lidar.GetAttribute("intensityNoise").Set(0.1)
```

### IMU 노이즈

IMU 는 시뮬레이터가 노이즈를 안 넣음. OG 측 → 외부 노드에서 합성:
```python
# 외부 ROS 노드 (rclpy)
def imu_callback(msg):
    msg.linear_acceleration.x += np.random.normal(0, 0.05)
    ...
    self.publisher_.publish(msg)
```

## 10. Isaac Lab 과 결합 — 온라인 DR

RL 학습 중 매 reset 또는 매 step 마다 씬을 랜덤화.

### Visual policy 의 도메인 랜덤화

Isaac Lab 의 EventManager 에 Replicator-style randomization 추가:
```python
@configclass
class EventsCfg:
    randomize_lighting = EventTerm(
        func=mdp.randomize_visual_lighting,    # 커스텀 또는 isaaclab 내장
        mode="reset",
        params={"intensity_range": (500, 5000)},
    )
    randomize_textures = EventTerm(
        func=mdp.randomize_visual_textures,
        mode="reset",
        params={"texture_dir": "/home/me/textures"},
    )
```

`mdp.randomize_visual_*` 함수가 없으면 직접 작성하여 등록.

### Online randomization via OG

Replicator 그래프는 OG 위에서 동작 → Isaac Lab env 와 같은 stage 에서 공존 가능. 매 trigger 마다 OG 가 모양/색/조명 변경.

**비용**: shader recompile + texture upload → step latency 증가. 보통 매 N step 마다만 (N=10~50) 변경.

## 11. 학습 데이터 품질 체크리스트

생성한 데이터셋으로 학습 후 real 에서 안 되면:

1. **라벨이 정확한가**: bbox 가 객체에 딱 맞나? 무작위로 100장 시각화.
2. **클래스 분포 균형**: 각 클래스 인스턴스 개수가 비슷한가? log_uniform 대신 직접 균형 잡기.
3. **랜덤화 범위가 real 을 포함하나**: real 의 조명 intensity, 카메라 거리 범위를 측정 → SDG 범위가 그것을 cover.
4. **배경 다양성**: 흰 배경만 생성하면 흰 배경에 over-fit. dome light + HDRI 랜덤화 권장.
5. **객체 자세 분포**: real 에서 객체가 항상 똑바로 있는데 SDG 에선 360도 회전 → 학습 어려워짐. real 분포에 맞춰 좁히기.
6. **occlusion**: real 은 객체 위에 손이 자주 가는데 SDG 에 occluder 없음 → 다른 객체로 occluder 추가.

## 12. 자주 발생하는 SDG 함정

| 증상 | 원인 | 해결 |
|---|---|---|
| 생성된 이미지가 모두 동일 | trigger 안에서 modify 안 함, distribution 호출만 함 | `rep.trigger.on_frame` 안에 `rep.modify.pose` |
| Annotator 가 빈 결과 | semantics API 미적용 | `Semantics.SemanticsAPI.Apply(prim, "label")` |
| 헤드리스 실행이 안 끝남 | `simulation_app.close()` 누락 | 스크립트 끝에 명시 |
| RGB 만 잘 나오고 segmentation 이상 | renderer 가 PathTracing 인데 sem 은 RTX-RT 만 | renderer 모드 통일 |
| Bbox 가 객체보다 큼 | 부모 prim 의 transform 이 적용 안 됨 | `bounding_box_2d_tight` 사용 |
| 100장 만들기로 했는데 1만장 | 중복 trigger | 그래프 점검, on_frame 의 num_frames 명시 |
| Material randomization 후 GPU OOM | shader recompile cache 폭주 | texture 개수 ↓, `materials` 의 cache 관리 |
| Lidar SDG 안 됨 | RTX Lidar 의 ROS publish 와 별개 | `rep.create.from_usd(lidar.usd)` 가 아닌 직접 prim 참조 |
| KittiWriter 의 calib 이 비어있음 | camera prim 의 focal length 미설정 | `omnigraph-ros-bridge.md` §6 의 focalLength 설정 |
| Replicator-Agent 가 ground 아래로 떨어짐 | character 의 collision 비활성 | character prim 의 PhysicsRigidBodyAPI 확인 |

## 컨베이어 위 객체 스폰 + YOLO 학습 데이터 생성 (warehouse 시나리오)

`warehouse-sorting-pipeline.md §6` 의 spawn 메커니즘과 짝. 동일 Replicator 그래프가 **두 가지 모드** 로 운영됨:

1. **런타임 spawn** — sim 운영 중 객체를 컨베이어로 흘려보냄. detection 의 ground-truth 매칭과 cycle 트리거.
2. **오프라인 SDG** — 학습 데이터 생성. 같은 객체 카탈로그를 사용하되 더 많은 도메인 랜덤화 + writer 부착.

### 통합 그래프 (런타임 / SDG 공용)

```python
import omni.replicator.core as rep

CLASS_USDS = {
    "box_red":  "assets/box_red.usda",
    "box_blue": "assets/box_blue.usda",
    "can_a":    "assets/can_a.usda",
    "reject":   "assets/scrap.usda",
}
SPAWN_BBOX_MIN = (-0.40, 0.85, 0.05)
SPAWN_BBOX_MAX = ( 0.40, 1.15, 0.05)

def build_spawn_graph(mode: str = "runtime"):
    """mode: 'runtime' → 2초 간격 spawn, 'sdg' → 학습용 1000 frame burst."""
    if mode == "runtime":
        trigger = rep.trigger.on_time(interval=2.0)
        randomize_strong = False
        attach_writer = False
        num_frames = None
    else:   # sdg
        trigger = rep.trigger.on_frame(num_frames=1000)
        randomize_strong = True
        attach_writer = True

    with rep.new_layer():
        cam = rep.create.camera(position=(0, 1.0, 1.5), look_at=(0, 1.0, 0.0))
        with trigger:
            cls = rep.distribution.choice(list(CLASS_USDS.keys()))
            obj = rep.create.from_usd(
                CLASS_USDS[cls],
                position=rep.distribution.uniform(SPAWN_BBOX_MIN, SPAWN_BBOX_MAX),
                rotation=rep.distribution.uniform((0,0,0), (0,360,360)),
                semantics=[("class", cls)],
            )
            if randomize_strong:
                rep.modify.material(obj, rep.distribution.choice([
                    "/World/Looks/MetalBrushed", "/World/Looks/PlasticGloss", ...
                ]))
                rep.randomizer.rotation(prims=cam, min=(75,0,0), max=(105,0,360))
                rep.modify.attribute("xformOp:translate",
                                     rep.distribution.uniform((0,0.9,1.2),(0,1.1,1.6)),
                                     prims=cam)
                rep.randomizer.color(rep.get.material(rep.get.prim_at_path("/World/Floor")))
                rep.randomizer.light(intensity=rep.distribution.uniform(500, 3000),
                                     color_temp=rep.distribution.uniform(3500, 6500))
        if attach_writer:
            writer = rep.WriterRegistry.get("KittiWriter")
            writer.initialize(
                output_dir="/data/yolo_train",
                rgb=True, bounding_box_2d_tight=True, semantic_segmentation=False,
            )
            writer.attach([cam])

# 운영: build_spawn_graph("runtime")
# 학습 데이터 1회 생성: build_spawn_graph("sdg"); rep.orchestrator.run()
```

### 학습 ↔ 추론 일관성

학습 시 사용한 camera intrinsic (focal_length, aperture, resolution) 와 런타임 추론 시 카메라 intrinsic 이 **반드시 일치**. 그러지 않으면 bbox center 가 pixel 단위로 어긋난다.

`yolo-perception.md §4` 의 `camera_info_from_omni` 가 런타임 카메라의 K 를 publish — 학습 때도 동일 prim 속성으로 카메라를 만들면 자동 일치.

### Semantics → COCO/YOLO 라벨

KittiWriter 는 KITTI 포맷. ultralytics 학습 시 YOLO 포맷으로 변환:

```python
# 변환 스크립트 골격 (ultralytics docs 의 표준 변환 활용)
# /data/yolo_train/r0/{rgb_*.png, label_*.txt}  (KITTI)
# → /data/yolo_train/yolo/{images/*.png, labels/*.txt}  (YOLO normalized)
```

또는 COCO writer 사용 (`rep.WriterRegistry.get("CocoWriter")`) 후 ultralytics 가 COCO 직접 학습 지원.

### 도메인 랜덤화 축 (sim2real gap 줄이기)

| 축 | 변화 범위 | 학습 임팩트 |
|---|---|---|
| 객체 위치 | spawn bbox uniform | YOLO 의 spatial bias 제거 |
| 객체 회전 | yaw 0~360°, pitch ±15° | 자세 일반화 |
| 객체 재질/색 | 카탈로그 swap | 색에 의존 안 하게 (형태로 분류) |
| 카메라 위치 | ± 5cm | calibration 오차 robust |
| 카메라 yaw | ± 10° | mount 오차 robust |
| 라이팅 | 500~3000 lux, 3500~6500K | 실내 조명 다양성 |
| 배경 (floor/wall) | 텍스처 swap | 배경 invariance |

10000~50000 frame 정도면 YOLOv8m fine-tune 충분. ultralytics 학습:

```bash
yolo train data=warehouse.yaml model=yolov8m.pt epochs=50 imgsz=720 batch=16
```

`warehouse.yaml` 은 클래스 4개 + train/val 디렉토리 매핑.

### 런타임 spawn 의 ROS publish 통합

런타임 모드일 때 spawn 이벤트를 `/conveyor/spawn` 토픽으로 publish (ground-truth 매칭용):

```python
def on_spawn_callback(spawned_prim_path, class_name, world_pose):
    msg = SpawnEvent()
    msg.id = uuid.uuid4().hex
    msg.class_name = class_name
    msg.pose.position.x, msg.pose.position.y, msg.pose.position.z = world_pose
    msg.header.stamp = node.get_clock().now().to_msg()
    spawn_pub.publish(msg)
```

이 ground-truth 를 detection 과 매칭하면 detection accuracy / IoU 를 supabase `decisions` 또는 별도 `detection_gt_match` 테이블에 적재 가능.

### 안티패턴

- ❌ 런타임 spawn 그래프와 SDG 그래프를 완전히 분리 작성 — 코드 중복, intrinsic 불일치 위험
- ❌ Replicator 의 randomization 없이 동일 텍스처/조명으로만 학습 — 시뮬 안에서도 conveyor 위 객체 위치만 살짝 변해도 detection 실패
- ❌ 학습 카메라 prim 과 추론 카메라 prim 이 다른 focal_length — intrinsic 불일치
- ❌ semantics 라벨을 객체 swap 시 갱신 안 함 — KittiWriter 가 잘못된 클래스로 라벨

## See also

- `omnigraph-ros-bridge.md` §6, §7 — 카메라/라이다 prim 설정
- `omnigraph-ros-bridge.md §다중 로봇 OG 팩토리` — 런타임 카메라 prim 의 OG 셋업
- `yolo-perception.md §4, §7` — 카메라 intrinsic 일관성 / 학습 데이터 사용
- `warehouse-sorting-pipeline.md §6` — 런타임 spawn 의 전체 맥락
- `isaaclab-rl.md` §8 — Event-based DR
- `physx-tuning.md` §9 축 3 — 센서 노이즈 처방
- 원문: `06-replicator/`, NVIDIA blog `10-gap-fills/nvidia-blog/`, `11-warehouse-sorting/ultralytics/repo/docs/`
