# isaac-ros-accel.md — Isaac ROS GPU 가속 통합

이 reference 는 **GPU 가속 perception / motion planning 노드를 ROS 2 그래프에 끼워 넣는 방법**을 다룬다. NITROS (zero-copy GPU 메시지), cuMotion vs MoveIt2, cuRobo 직접 API, Visual SLAM, Isaac Manipulator, Jetson 성능 튜닝.

## Contents
1. Isaac ROS 가 뭔지 — DP/GA, NGC, apt
2. NITROS — zero-copy 메시지 모델
3. cuMotion vs MoveIt2 — 언제 어떤 걸
4. cuRobo 직접 사용 (ROS 없이)
5. Visual SLAM (cuVSLAM) — 카메라/스테레오 SLAM
6. Isaac Manipulator — perception + motion + grasp 통합
7. DNN inference 노드 (object detect, pose estimation)
8. Apriltag / fiducials
9. Jetson 측 셋업 & 성능 튜닝
10. Isaac Sim ↔ Isaac ROS 동시 실행 (디지털 트윈)
11. GPU 예산 관리
12. 자주 발생하는 통합 함정

---

## 1. Isaac ROS 가 뭔지

NVIDIA 가 만든 **ROS 2 패키지 컬렉션**. Isaac Sim 과 별개 — host 의 ROS 2 워크스페이스에 설치.

- **30+ 패키지**: isaac_ros_apriltag, isaac_ros_visual_slam, isaac_ros_cumotion, isaac_ros_dnn_inference, isaac_ros_object_detection, isaac_ros_pose_estimation, ...
- **공통점**: GPU 가속 + NITROS (§2) + ROS 2 표준 인터페이스
- **호환 distro**: Humble, Jazzy. JetPack 6.0+ 의 ROS 2 Humble 도 동일.

릴리스 채널:
- **GA** (General Availability): 안정. apt install 가능.
- **DP** (Developer Preview): 새 기능, 베타.

설치:
```bash
# Ubuntu 22.04 + Humble
sudo apt update
sudo apt install -y ros-humble-isaac-ros-common
sudo apt install -y ros-humble-isaac-ros-cumotion  # 예
# 또는 source build
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone --depth=1 https://github.com/nvidia-isaac-ros/isaac_ros_common.git
git clone --depth=1 https://github.com/nvidia-isaac-ros/isaac_ros_cumotion.git
cd ~/ros2_ws && colcon build
```

Jetson 은 §9.

원본: `08-isaac-ros/isaac_ros_standalone/getting_started/`, `09-github-repos/isaac_ros_common/`

## 2. NITROS — zero-copy 메시지 모델

문제: 일반 ROS 2 토픽은 메시지를 직렬화→DDS→역직렬화. GPU tensor 같은 큰 데이터는 매번 host↔device 복사. 카메라 4K @ 30fps 만 해도 GB/s 대역.

NITROS 해결법:
1. 메시지를 GPU 메모리에 두고 **포인터(handle)만 전달**.
2. 같은 노드 컨테이너 안의 NITROS-aware 노드끼리는 zero-copy.
3. 외부 (non-NITROS) 노드와는 자동으로 일반 메시지로 변환 (overhead 있음).

코드 차이는 거의 없다 — 같은 노드 컨테이너에 NITROS 노드들을 묶어 `composable_node` 로 실행:

```python
# launch file
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

container = ComposableNodeContainer(
    name="nitros_container",
    namespace="",
    package="rclcpp_components",
    executable="component_container_mt",
    composable_node_descriptions=[
        ComposableNode(
            package="isaac_ros_image_proc",
            plugin="nvidia::isaac_ros::image_proc::ImageFormatConverterNode",
            name="image_format_converter",
            parameters=[{"encoding_desired": "rgb8"}],
        ),
        ComposableNode(
            package="isaac_ros_dnn_image_encoder",
            plugin="nvidia::isaac_ros::dnn_inference::DnnImageEncoderNode",
            name="dnn_image_encoder",
            ...
        ),
    ],
)
```

같은 container 안의 두 노드는 GPU 메모리 직접 공유.

원본: `08-isaac-ros/isaac_ros_standalone/nitros/` 디렉토리, `09-github-repos/isaac_ros_nitros/`

## 3. cuMotion vs MoveIt2 — 언제 어떤 걸

| 항목 | MoveIt2 | cuMotion (Isaac ROS) |
|---|---|---|
| 플래너 | OMPL (RRT, RRT*, PRM), Pilz, STOMP | cuRobo (GPU parallel optimization) |
| 속도 (단일 plan) | 50~500 ms | 10~50 ms |
| 속도 (배치 plan, 100개) | 5~50 s (sequential) | 100~500 ms (parallel) |
| 메모리 (GPU) | 0 | 2~4 GB |
| 학습 곡선 | 가파름 (config + tutorial) | 완만 |
| Custom constraints | OMPL 콜백, plugin | Python 직접 추가 |
| collision objects | URDF + SRDF + scene msg | URDF + obstacle list |
| 산업 표준 | ✓ | 새 도구 |
| ROS 2 인터페이스 | `/move_group` action | `cuMotion` action (action_msgs) |

**결정**:
- 기존 MoveIt2 셋업 있고 plan 1개씩 → MoveIt2
- 새 프로젝트, 빠른 plan 필요, 배치 plan 필요 → cuMotion
- 둘 다 시도해보고 latency 측정해서 결정 가능 (어차피 같은 robot URDF)

원본: `08-isaac-ros/cumotion/`, `09-github-repos/isaac_ros_cumotion/`

## 4. cuRobo 직접 사용 (ROS 없이)

`isaac_ros_cumotion` 은 cuRobo 의 ROS 래퍼. cuRobo 자체를 Python 에서 직접 호출하면 더 유연.

```python
from curobo.types.math import Pose
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig

cfg = MotionGenConfig.load_from_robot_config(
    "/home/me/curobo_configs/franka.yml",   # robot kinematics + collision spheres
    "/home/me/curobo_configs/world.yml",    # obstacles
    interpolation_dt=0.01,
)
motion_gen = MotionGen(cfg)
motion_gen.warmup()    # JIT 컴파일 (~5s 한 번만)

start_state = JointState.from_position(torch.tensor([0.0]*7).cuda())
goal_pose = Pose(position=torch.tensor([0.5, 0.0, 0.3]).cuda(),
                 quaternion=torch.tensor([1.0, 0.0, 0.0, 0.0]).cuda())

result = motion_gen.plan_single(start_state, goal_pose)
trajectory = result.get_interpolated_plan()
print(f"Success: {result.success}, plan time: {result.solve_time*1000:.1f} ms")
```

**Robot config YAML** 작성이 가장 큰 부담. cuRobo 의 `10-gap-fills/curobo/repo/curobo/content/configs/robot/` 에 Franka, UR, KUKA 등 사전 정의 있음. 새 로봇은 collision sphere approximation 을 직접 정의.

cuRobo 의 다른 기능:
- `IKSolver`: inverse kinematics 만 (수십 μs)
- `MotionGen`: 풀 모션 플래닝
- `ParallelMotionGen`: 배치
- `RolloutBase` 클래스로 직접 cost function 정의

원본: `10-gap-fills/curobo/repo/`, `10-gap-fills/curobo/docs/`

## 5. Visual SLAM (cuVSLAM) — 카메라/스테레오 SLAM

`isaac_ros_visual_slam` — stereo RGB 카메라 (또는 RGB-D) 로 odometry + SLAM.

```yaml
# launch param
left_camera_topic: /stereo/left/image
right_camera_topic: /stereo/right/image
left_camera_info_topic: /stereo/left/camera_info
right_camera_info_topic: /stereo/right/camera_info
enable_imu_fusion: True
imu_topic: /imu/data
```

출력 토픽:
- `/visual_slam/tracking/odometry` — `nav_msgs/Odometry`
- `/visual_slam/tracking/pose` — `geometry_msgs/PoseStamped`
- `/visual_slam/vis/observations_cloud` — 디버그 시각화

Isaac Sim 에서 stereo 카메라 두 개 (`omnigraph-ros-bridge.md` §6) 발행 → cuVSLAM 노드 → 추정 odometry. **테스트용으로 매우 유용** — 진짜 SLAM 알고리즘이 시뮬 카메라에서 잘 도나 검증.

원본: `09-github-repos/isaac_ros_visual_slam/`

## 6. Isaac Manipulator — perception + motion + grasp 통합

여러 Isaac ROS 패키지를 묶은 high-level 패키지. 입력: RGB-D 카메라 + URDF + 목표 객체 → 출력: pick-and-place 동작.

내부 구성:
- `isaac_ros_foundationpose` — 6D pose estimation (DNN)
- `isaac_ros_centerpose` 또는 `isaac_ros_dope` — 객체 검출
- `isaac_ros_cumotion` — 모션 계획
- `isaac_manipulator_bringup` — 통합 launch

```bash
# 예제 launch (Franka + Realsense)
ros2 launch isaac_manipulator_bringup foundationpose.launch.py \
  robot_type:=franka \
  camera_type:=realsense
```

데모는 Franka 위주. UR / Doosan 으로 옮기려면 cumotion config + URDF + frame mapping 작업.

원본: `09-github-repos/isaac_manipulator/`

## 7. DNN inference 노드

`isaac_ros_dnn_inference` 는 TensorRT 백엔드 + 표준 입력/출력 ROS 인터페이스. 학습된 모델 (ONNX/PT) 을 ROS 노드로 감싸기:

```yaml
model_file_path: /home/me/models/yolo_v8.onnx
engine_file_path: /home/me/models/yolo_v8.plan   # TRT 컴파일 결과 (없으면 자동 생성)
input_tensor_names: ["images"]
input_binding_names: ["images"]
output_tensor_names: ["output0"]
output_binding_names: ["output0"]
verbose: false
```

같은 그래프에 `isaac_ros_dnn_image_encoder` (이미지 → tensor 인코딩) + `dnn_inference` + 후처리 노드를 합쳐 zero-copy pipeline.

`isaaclab-rl.md` §10 의 ONNX 출력을 이 노드로 추론하면 학습한 정책을 Jetson 에서 실행 가능.

## 8. Apriltag / fiducials

`isaac_ros_apriltag` — Apriltag 검출, GPU 가속.

```bash
ros2 launch isaac_ros_apriltag isaac_ros_apriltag_pipeline.launch.py \
  family:=tag36h11 size:=0.06
```

Pose calibration, SLAM ground truth, 또는 hand-eye calibration 에 유용.

## 9. Jetson 측 셋업 & 성능 튜닝

`installation.md` §6 의 자세한 버전.

### 성능 모드

```bash
sudo nvpmodel -m 0       # MAXN (full power)
sudo jetson_clocks       # CPU/GPU 클럭 고정 max
sudo nvpmodel -q         # 현재 모드 확인
```

### GPU 사용량 모니터

```bash
sudo tegrastats           # 실시간 CPU/GPU/EMC/mem
jtop                      # TUI (sudo pip install jetson-stats)
```

### TensorRT 엔진 사전 컴파일

DNN 노드는 첫 실행 시 ONNX → TRT 변환에 10초~수 분. 미리 컴파일:
```bash
/usr/src/tensorrt/bin/trtexec \
  --onnx=yolo_v8.onnx \
  --saveEngine=yolo_v8.plan \
  --fp16 \
  --workspace=4096
```

`fp16` 가 Jetson 에서 2-3배 빠름. INT8 quantization 은 calibration 데이터 필요.

### Disk I/O

Jetson 의 eMMC 는 느림. 가능하면 NVMe SSD 추가 (Orin AGX/NX 는 지원) → ROS 2 워크스페이스 / SDG output / 로그 모두 NVMe 로.

원본: `08-isaac-ros/isaac_ros_standalone/concepts/`, `09-github-repos/isaac_ros_common/scripts/`

## 10. Isaac Sim ↔ Isaac ROS 동시 실행 (디지털 트윈)

같은 호스트에서:
- Isaac Sim 이 시뮬 카메라/로봇 발행 (OG 그래프)
- Host 의 Isaac ROS 노드가 그 토픽을 받아 SLAM / perception / motion 수행
- 결과를 다시 Isaac Sim 으로 보내거나, 실 로봇에도 동시 적용

```
[Isaac Sim]                              [host]
  ROS2PublishCamera ──── /camera/rgb ──→ isaac_ros_visual_slam
  ROS2PublishImu ──────── /imu/data ──→
                                          ↓
                            /visual_slam/tracking/pose
                                          ↓
  ROS2SubscribeOdometry ←─── (시각화 또는 학습 입력)
```

GPU 자원 공유 — Isaac Sim 의 RTX 와 Isaac ROS 의 TensorRT 가 같은 GPU 메모리. §11 의 예산.

원본: `08-isaac-ros/digital_twin/`

## 11. GPU 예산 관리

(SKILL.md Core mental model #6 의 자세한 처방)

| 컴포넌트 | 메모리 (예: RTX 4090 24GB) |
|---|---:|
| Isaac Sim Kit | 1.5~2 GB |
| RTX rendering (camera 1080p, RTX-RT) | 1~2 GB / camera |
| PhysX GPU (4096 envs, 7-dof robot) | 2~3 GB |
| TensorRT engine (yolo v8 fp16) | 200~500 MB |
| TensorRT engine (foundationpose) | 1.5 GB |
| Isaac ROS NITROS buffers | 500 MB |
| Replicator (texture cache) | 1~3 GB |
| 여유 (헤드룸) | 2 GB+ |

**합산이 GPU 메모리를 넘으면 CUDA OOM** — 학습/추론 둘 다 죽음.

대응:
- num_envs 줄이기 (4096 → 1024 → 512)
- RTX-RT 카메라 끄기 (학습용으로 안 쓰는 시점)
- TensorRT INT8 quantization
- 학습 / 평가 / 배포 단계로 분리 — 동시에 다 켜지 말기

## 12. 자주 발생하는 통합 함정

| 증상 | 원인 | 해결 |
|---|---|---|
| cuMotion 첫 plan 이 5초 걸림 | warmup 미호출 | `motion_gen.warmup()` 1회 |
| cuRobo 의 robot config YAML 작성 어려움 | collision sphere 수동 | `09-github-repos/IsaacLab/source/isaaclab_assets/isaaclab_assets/` 의 ManagerBasedCfg 또는 `10-gap-fills/curobo/repo/curobo/content/configs/robot/` 의 기존 YAML 참고 |
| DNN inference 가 CPU 만 사용 | onnx 인데 TRT 엔진 미생성 | trtexec 로 사전 컴파일 |
| NITROS 인데 메시지 복사 발생 | composable node 가 아닌 separate process | 같은 container 안에 묶기 |
| cuVSLAM 의 odometry 가 drift | stereo intrinsics 잘못 | `omnigraph-ros-bridge.md` §6 카메라 calib 재확인 |
| Jetson 에서 노드가 sigkill | OOM | swap 추가 또는 모델 크기 ↓ |
| TensorRT FP16 정확도가 FP32 보다 크게 떨어짐 | 모델이 numerically sensitive | 일부 layer 만 FP32 (mixed precision) |
| Isaac ROS 빌드가 매번 30분 | ccache 미사용 | `export CC=ccache CXX=ccache++` |
| Apriltag 검출이 시뮬에선 됐는데 real 안 됨 | 시뮬 카메라 K 가 real 과 다름 | calib 일치, distortion 모델 일치 |
| `--network=host` 안 쓰면 Docker→Host ROS 안 보임 | DDS multicast 차단 | `--network=host` 또는 Fast-DDS discovery server |

## See also

- `omnigraph-ros-bridge.md` — Isaac Sim → ROS 데이터 발행
- `isaaclab-rl.md` §10 — ONNX export 후 DNN inference 로
- `physx-tuning.md` §11 — Jetson 에서 시뮬 안 돌리는 이유 (못 함)
- `installation.md` §6 — Jetson 셋업
- `ros2-architect` 스킬: `references/launch-system.md` (composable_node), `references/communication.md` (composable 컨테이너 패턴)
- 원문: `08-isaac-ros/`, `09-github-repos/isaac_ros_*/`, `10-gap-fills/curobo/`, `10-gap-fills/moveit2-isaac/`
