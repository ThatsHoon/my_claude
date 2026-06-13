# installation.md — Isaac Sim 설치 & 환경 셋업

이 reference는 **"Isaac Sim 이 안 켜진다 / ROS distro 가 맞지 않다 / Jetson 에서 어떻게 돌리지"** 류의 모든 질문을 해결한다. 진입 모드(Workstation / Container / Cloud / Jetson)별 설치 경로, ROS 2 distro 매트릭스, GPU 요구사항, 그리고 자주 마주치는 함정만 다룬다.

## Contents
1. 진입 모드 선택 (4가지)
2. 시스템 요구사항 (GPU / 드라이버 / OS)
3. Workstation 설치 (Linux native)
4. Container 설치 (Docker)
5. Cloud / IsaacAutomator
6. Jetson (Orin) 배포
7. ROS 2 distro 매트릭스
8. 첫 실행 검증 5단계
9. 자주 발생하는 설치 실패 패턴
10. 업그레이드 / 다운그레이드 / 멀티버전

---

## 1. 진입 모드 선택

| 모드 | 언제 쓰나 | 권장 호스트 | 단점 |
|---|---|---|---|
| Workstation (native) | 개발·디버깅·GUI 인터랙션이 잦은 단계 | Ubuntu 22.04/24.04 + RTX 4070 이상 | 의존성 충돌 잘 남, 다중 사용자 X |
| Container (Docker) | CI, 다중 사용자, "내 PC에선 됐는데" 회피 | 동일 + nvidia-container-toolkit | 첫 빌드 30+분, GUI는 별도 셋업 (xpra/VNC) |
| Cloud (IsaacAutomator) | 대규모 RL 학습, GPU 풀 임차 | AWS g5.xlarge / Azure NC-A100 / GCP A100 | 분당 과금, 데이터 전송비, 네트워크 지연 |
| Jetson (Orin) | 실 로봇 onboard 추론·인식 | Jetson AGX Orin 32GB+ 권장 | 풀 Isaac Sim X (Isaac ROS 만), CUDA arch 호환성 |

**원칙**: Workstation 으로 시작 → CI 안정화 단계에서 Container → 학습 스케일링 시 Cloud → 배포는 Jetson. 한 번에 4개 다 셋업하려고 하지 말 것.

## 2. 시스템 요구사항

| 항목 | 최소 | 권장 | 비고 |
|---|---|---|---|
| GPU | RTX 3070 (8GB) | RTX 4080+ (16GB+) | 학습 시 16GB 미만은 OOM 빈발 |
| GPU 드라이버 | 535.x | 555.x 이상 | Vulkan 1.3 필수 |
| OS | Ubuntu 22.04 | Ubuntu 22.04 | 24.04 는 6.0 부터 공식 지원 |
| RAM | 32 GB | 64 GB+ | USD 큰 씬 + RL 동시 실행 시 |
| Storage | 100 GB SSD | 500 GB NVMe | 에셋 캐시 + 학습 로그 |

**확인 명령** (실 셋업 전 반드시):
```bash
nvidia-smi              # 드라이버 버전, GPU 메모리
glxinfo | grep "OpenGL renderer"   # NVIDIA GPU 인식 확인
vulkaninfo --summary    # Vulkan 1.3 지원
df -h ~/.local/share    # ov 캐시 위치 여유 공간
```

## 3. Workstation 설치 (Ubuntu 22.04 기준)

```bash
# 1. Omniverse Launcher 설치 (deb)
wget https://install.launcher.omniverse.nvidia.com/installers/omniverse-launcher-linux.AppImage
chmod +x omniverse-launcher-linux.AppImage
./omniverse-launcher-linux.AppImage  # GUI 로그인 후 Isaac Sim 항목 설치

# 2. 또는 standalone (Launcher 없이, 6.0부터 지원)
wget <release_url>/isaac-sim-standalone-6.0.0-linux-x86_64.zip
unzip isaac-sim-standalone-6.0.0-linux-x86_64.zip -d ~/isaacsim
cd ~/isaacsim
./isaac-sim.sh           # GUI
./python.sh -h           # 헤드리스 Python
```

**경로 컨벤션**:
- 설치: `~/.local/share/ov/pkg/isaac-sim-<ver>/`
- 캐시: `~/.cache/ov/`, `~/.local/share/ov/data/`
- 로그: `~/.local/share/ov/data/Kit/Apps/Isaac-Sim/<ver>/kit_*.log`

세 곳 모두 SSD 권장. 캐시가 HDD 면 첫 실행이 30분 이상 걸린다.

원본 설치 가이드: `/home/hoon/isaac-sim-skill-research/01-isaac-sim-core/installation/install_workstation.html`

## 4. Container 설치

```bash
# nvidia-container-toolkit 사전 설치 (host)
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# 공식 이미지 (NGC)
docker pull nvcr.io/nvidia/isaac-sim:6.0.0
docker run --name isaac-sim --entrypoint bash -it --runtime=nvidia --gpus all \
  -e "ACCEPT_EULA=Y" \
  -e "PRIVACY_CONSENT=Y" \
  -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
  -v ~/docker/isaac-sim/cache/ov:/root/.cache/ov:rw \
  -v ~/docker/isaac-sim/cache/pip:/root/.cache/pip:rw \
  -v ~/docker/isaac-sim/cache/glcache:/root/.cache/nvidia/GLCache:rw \
  -v ~/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache:rw \
  -v ~/docker/isaac-sim/logs:/root/.nvidia-omniverse/logs:rw \
  -v ~/docker/isaac-sim/data:/root/.local/share/ov/data:rw \
  -v ~/docker/isaac-sim/documents:/root/Documents:rw \
  --network=host \
  nvcr.io/nvidia/isaac-sim:6.0.0
```

**캐시 볼륨 마운트가 핵심**. 안 마운트하면 컨테이너 재시작마다 30분씩 USD 셰이더 컴파일 다시 한다.

GUI 가 필요하면 `xpra` 또는 `webrtc-streaming` 모드:
```bash
docker run ... -p 8211:8211 -p 49100:49100 nvcr.io/nvidia/isaac-sim:6.0.0 \
  ./runheadless.webrtc.sh  # 브라우저에서 http://localhost:8211 접속
```

원본: `01-isaac-sim-core/installation/install_container.html`

## 5. Cloud / IsaacAutomator

대규모 RL 학습이나 다수 SDG 워커가 필요할 때. AWS / Azure / GCP / Alibaba 4종 지원.

```bash
git clone --depth=1 https://github.com/isaac-sim/IsaacAutomator.git
cd IsaacAutomator
./run.sh deploy-aws     # 또는 deploy-azure, deploy-gcp
# 인터랙티브 프롬프트: 인스턴스 타입, 리전, AMI, SSH 키 등
```

생성되는 자원: VPC, Security Group, EC2/VM (g5.xlarge 이상), EBS, key pair. 종료는 반드시 `./run.sh destroy-aws` — 안 하면 시간당 $1+ 과금.

소스: `09-github-repos/IsaacAutomator/`

## 6. Jetson 배포

**중요**: Jetson 에는 **Isaac Sim 자체는 안 돌아간다**. Isaac Sim 으로 학습한 모델/USD 를 export 해서, Jetson 에서는 **Isaac ROS** 패키지로 추론·인식만 한다.

Jetson 셋업:
```bash
# JetPack 6.0+ (Ubuntu 22.04 기반) 권장
sudo apt install -y nvidia-jetpack
sudo apt install -y ros-humble-isaac-ros-common  # apt 또는 source build

# 또는 Docker 로 통째로
docker run -it --runtime=nvidia --network=host \
  -v /dev:/dev -v /tmp/argus_socket:/tmp/argus_socket \
  nvcr.io/nvidia/isaac/ros:x86_64-aarch64-humble-2026.0
```

성능 모드:
```bash
sudo nvpmodel -m 0       # MAXN
sudo jetson_clocks       # 클럭 최대
```

자세한 패키지별 셋업: `08-isaac-ros/isaac_ros_standalone/getting_started/` 와 `09-github-repos/isaac_ros_common/` 의 README.

## 7. ROS 2 distro 매트릭스

| Isaac Sim | 권장 ROS 2 | 호환 (실험적) | 비고 |
|---|---|---|---|
| 4.5.x | Humble | Iron | simulation_interfaces v0.0.x |
| 5.0.x | Humble | Iron | sim_interfaces v1.0 |
| 5.1.x | **Humble**, Jazzy | Iron, Rolling | sim_interfaces v1.1.0 |
| 6.0.x | **Humble**, Jazzy | 모든 native distro (실험적) | sim_interfaces v1.1.0+ |

**핵심 규칙**: Isaac Sim 의 ROS 2 브리지는 자체 내장 라이브러리(`humble`/`jazzy`)를 쓰지만, **호스트의 `/opt/ros/<distro>/setup.bash` 가 source 되어 있어야** 외부 노드와 통신이 된다. 매번 두 줄을 같은 셸에서:

```bash
source /opt/ros/humble/setup.bash
~/.local/share/ov/pkg/isaac-sim-6.0.0/isaac-sim.sh
```

distro 가 안 맞으면 발생하는 증상:
- `ros2 topic list` 에 Isaac Sim 토픽이 안 보인다
- 보이는데 `ros2 topic echo` 가 무한 대기
- `ros2 doctor --report` 에 `RMW_IMPLEMENTATION` 불일치

해결: 둘 다 같은 distro 로 통일. distro 변경은 host 단의 `/opt/ros/...` 재설치가 가장 깔끔.

원본: `01-isaac-sim-core/installation/install_ros.html`

## 8. 첫 실행 검증 5단계

설치 직후 반드시 이 순서로:

1. **GUI 부팅**: `./isaac-sim.sh` → Welcome 창에서 "Open Sample" → `Welcome.usd`. 부팅에 1~2분, 첫 USD 로드에 또 1분 정도 정상.
2. **Robot 샘플**: `Isaac → Robots → Franka` 메뉴에서 Franka 로드. 빨간 articulation 경고 없으면 OK.
3. **Physics 재생**: Play 버튼. Franka 가 중력으로 미세하게 처지면 PhysX 정상.
4. **ROS 브리지**: `Window → Extensions` → 검색 `isaac.ros2_bridge` enabled 확인. Console 에 `[isaacsim.ros2.bridge] Initialized` 보이면 OK.
5. **Headless Python**: 별도 터미널에서 `./python.sh -c "from isaacsim import SimulationApp; app = SimulationApp({'headless': True}); app.close()"` — 5초 안에 깔끔히 종료되면 OK.

5단계 모두 통과해야 다음 reference 로 진입 가능.

## 9. 자주 발생하는 설치 실패 패턴

| 증상 | 원인 | 해결 |
|---|---|---|
| `vulkaninfo` segfault, GUI 검은 화면 | Mesa 가 NVIDIA Vulkan 위에 우선됨 | `sudo apt remove mesa-vulkan-drivers` 또는 `__GLX_VENDOR_LIBRARY_NAME=nvidia` env |
| `[carb.graphics-vulkan.plugin] Cannot find Vulkan` | nvidia driver < 535 | 드라이버 업그레이드 |
| Container 안에서 GUI 안 뜸 | xhost 미설정 | host: `xhost +local:docker` |
| 첫 부팅 후 30분째 멈춤 | 셰이더 캐시 빌드 중 (HDD 라면 더 김) | 기다리거나 SSD 로 캐시 옮기기 |
| `ros2 topic list` 비어있음 | distro 불일치 또는 RMW 미일치 | §7 매트릭스 확인, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` 통일 |
| `OSError: [Errno 24] Too many open files` | RL 학습 시 num_envs 큰 경우 | `ulimit -n 65535` |
| Jetson 에서 Isaac ROS 노드 즉사 | CUDA arch 미스매치 | JetPack 버전 확인, `sudo apt update && sudo apt full-upgrade` |
| `ImportError: cannot import name '...' from 'omni.isaac.core'` | 6.0 에서 모듈 경로 변경 | `from isaacsim.core.api import ...` 로 마이그레이션 |

가장 흔한 두 가지: **드라이버 버전 / distro 불일치**. 90% 의 셋업 문제는 이 두 라인으로 해결.

## 10. 업그레이드 / 다운그레이드 / 멀티버전

여러 버전 공존이 흔하다 (예: 5.1 + 6.0 동시 보유).

```bash
# Launcher 사용 시: Library 탭에서 버전별 설치/삭제
# Standalone 사용 시: 디렉토리만 분리해서 둘 수 있음
~/isaacsim-5.1/
~/isaacsim-6.0/
```

다른 버전 호출:
```bash
~/isaacsim-5.1/isaac-sim.sh   # 5.1 GUI
~/isaacsim-6.0/python.sh script.py  # 6.0 헤드리스
```

`ov-data` 캐시는 버전별로 서브폴더가 갈리므로 충돌 안 한다. 단 Nucleus / Asset Library 의 USD 경로는 버전별 호환성 확인 필요. 5.1 USD 를 6.0 으로 열면 대개 자동 마이그레이션되지만 articulation 설정이 깨질 수 있어 §3 §4 검증 다시 통과시킬 것.

## See also

- `omnigraph-ros-bridge.md` §"Bridge extension 활성화" — ROS 브리지 첫 셋업
- `usd-from-urdf.md` §"Importer 확장 활성화" — URDF/MJCF 임포터
- `isaac-ros-accel.md` §"Jetson 성능 튜닝" — Jetson 측 최적화
- `ros2-architect` 스킬: `references/workspace-and-build.md` — host ROS 2 워크스페이스 셋업 정석

---

## Isaac 내부 ROS2 ↔ 호스트 ROS2 — 같은-PC DDS 한계 (중요)

Isaac Sim 5.x 는 **자체 번들 ROS2**(빌드의 Python, 예: 5.1=Python 3.11)를
쓴다. 호스트 ROS 2 Humble 은 Python 3.10. **같은 호스트에서 Isaac 내부 DDS
↔ 시스템 DDS 가 디스커버리되지 않는** 사례가 있다(Isaac 측 발행 정상이나
외부 `ros2 topic info` Publisher 0).

검증된 사실(같은-호스트는 다 실패): cyclone 통일+`CYCLONEDDS_URI` localhost
peer / `LD_LIBRARY_PATH`=`exts/isaacsim.ros2.bridge/<distro>/lib` / 시스템
ROS env scrub(→내부 rclpy 는 로드되나 여전히 미발견) / FastDDS UDP-only
프로파일(= NVIDIA 공식 `IsaacSim-ros_workspaces/<distro>_ws/fastdds.xml`).
→ **같은-호스트 한정 병리**.

판단:
- **2-PC LAN(머신 분리)** = 지원 경로. DDS 와이어는 ABI/Python버전 무관 →
  같은 `ROS_DOMAIN_ID` + `fastdds.xml`(UDP-only) 로 동작.
- **같은-PC 개발/검증** = ROS2 디스커버리에 매달리지 말고 **HTTP 직결 우회**
  (`omnigraph-ros-bridge.md` §"ROS2 우회: HTTP POST"). 또는 NVIDIA 공식
  `build_ros.sh`(Docker, Isaac-ABI Python)로 워크스페이스 빌드 후 C2 를
  Isaac-호환 ROS2 컨테이너화(무겁다).

## standalone 의 ROS 환경 격리 (scrub 레시피)

Isaac `python.sh` standalone 이 **시스템 ROS 2 가 소싱된 셸**에서 실행되면
Isaac(py3.11)이 시스템 rclpy(py3.10)를 만나 `Could not import rclpy` →
번들 ROS2 모드가 깨진다. 런처에서 exec 전에 시스템 ROS 흔적 제거:
```bash
unset AMENT_PREFIX_PATH AMENT_CURRENT_PREFIX COLCON_PREFIX_PATH \
      ROS_VERSION ROS_PYTHON_VERSION PYTHONPATH
# LD_LIBRARY_PATH 에서 /opt/ros/* 및 IsaacSim-ros_workspaces 토큰 제거
# 그 후 RMW_IMPLEMENTATION + (필요시) Isaac 번들 <distro>/lib 만 추가
```
이러면 Isaac 가 **자체 번들 내부 rclpy** 를 깨끗이 로드한다(로그
`Attempting to load internal rclpy ... rclpy loaded`).
