# physx-tuning.md — PhysX 5 솔버·드라이브·sim2real 튜닝

이 reference 는 **시뮬과 실제 로봇의 물리 거동을 일치시키는 모든 노브**를 다룬다. PhysX 5 솔버 선택, 서브스텝, 이터레이션, 마찰/접촉, articulation drive 의 수식과 안정성, 그리고 sim2real gap 의 4개 축 처방.

## Contents
1. PhysX 5 의 전체 시뮬 루프
2. Solver 선택 — TGS vs PGS
3. Substep & timestep
4. Position / velocity iterations
5. Articulation drive 수식과 안정성
6. 마찰 / 접촉 / restitution
7. Self-collision 와 contact offset
8. CPU vs GPU pipeline
9. Sim2real 4개 축 처방
10. 학습 안정성 영향 (Isaac Lab 관점)
11. 자주 발생하는 물리 함정

---

## 1. PhysX 5 의 전체 시뮬 루프

매 시뮬 step 마다 다음 순서:

```
1. Apply external forces / drive targets
2. Detect contacts (broad phase → narrow phase)
3. Build articulation Jacobian
4. Solve constraints (positions, velocities)   ← Solver 단계
5. Integrate positions
6. Update transforms / publish to USD
```

4번이 가장 비싸고 가장 많이 튜닝하는 곳. 1, 2, 5 는 거의 손 안 댄다.

원본: `07-physx/physics/`, `10-gap-fills/physx-sdk/PhysX/physx/source/`

## 2. Solver 선택 — TGS vs PGS

| Solver | 정식 명 | 특징 | 권장 용도 |
|---|---|---|---|
| **TGS** | Temporal Gauss-Seidel | substep 마다 constraint 재선형화 → contact-rich, articulation 안정 | **매니퓰레이터, 휴머노이드, 다관절** |
| **PGS** | Projected Gauss-Seidel | 빠르지만 articulation 정확도 낮음 | rigid body 다수, particle, contact-poor |

설정:
```python
from pxr import PhysxSchema

physics_scene = stage.GetPrimAtPath("/physicsScene")
physxAPI = PhysxSchema.PhysxSceneAPI.Apply(physics_scene)
physxAPI.CreateSolverTypeAttr().Set("TGS")   # 또는 "PGS"
```

**기본값은 PGS** (5.x), **6.0 부터 TGS 가 articulation 환경의 권장 기본**. URDF Importer 가 자동으로 TGS 로 설정하지만, 일부 샘플 씬은 PGS 그대로 → 직접 확인.

증상으로 보는 잘못된 선택:
- TGS 인데도 매니퓰레이터가 진동 → iteration / damping 부족 (§4)
- PGS 에서 articulation 이 폭주 → TGS 로 전환

## 3. Substep & timestep

```python
physxAPI.CreateTimeStepsPerSecondAttr().Set(60)   # PhysX 가 초당 몇 step
# 또는
physics_scene.GetAttribute("physxScene:timeStepsPerSecond").Set(60)

# Substep: 한 render frame 당 PhysX 내부 step 수
# Default: 1. 다관절 + 빠른 충돌 → 2~4 권장
```

**물리적 의미**: 작은 step 일수록 contact 안정. **단점**: 선형으로 느려진다.

| 시나리오 | 권장 rate |
|---|---|
| RL 학습 (수천 envs) | 60 Hz, substep=1 |
| 정밀 매니퓰레이션 시뮬 | 120 Hz, substep=2 |
| 실 로봇 컨트롤러 (1 kHz) 매칭 | 1000 Hz (실용적으론 240 Hz + 외부 PID) |
| 휴머노이드 보행 | 200 Hz, substep=2 |

**실 로봇 매칭이 핵심**: 시뮬 rate ≠ 컨트롤러 rate 면 학습한 정책이 실 로봇에서 이상하게 동작. Isaac Lab 에서는 `sim.dt` 와 `decimation` 두 개로 분리:
```python
sim_dt = 1 / 120          # 시뮬 1 step = 8.33 ms
decimation = 4            # policy step 마다 4 sim step → policy = 30 Hz
```

## 4. Position / velocity iterations

PhysX 가 한 step 내에서 constraint solver 를 몇 번 반복하느냐. Articulation 마다 따로 설정:

```python
from pxr import PhysxSchema
articulation_prim = stage.GetPrimAtPath("/World/Robot")
phys = PhysxSchema.PhysxArticulationAPI.Apply(articulation_prim)
phys.CreateSolverPositionIterationCountAttr().Set(32)   # default 4
phys.CreateSolverVelocityIterationCountAttr().Set(1)    # default 1
```

| 항목 | Default | RL 학습 | 정밀 매니퓰 | 휴머노이드 |
|---|---:|---:|---:|---:|
| Position iter | 4 | 16 | 64 | 32 |
| Velocity iter | 1 | 1 | 8 | 4 |

**증상으로 보는 부족**:
- 그리퍼가 물체를 꽉 잡으면 손가락 떨림 → Position iter ↑
- 빠른 충돌에서 물체가 관통 → Substep ↑ 또는 Position iter ↑
- Joint limit 에서 진동 → Position iter ↑

**비용**: position iter 가 비싸다. RL 학습에서 32 이상 쓰면 throughput 이 3-4배 떨어진다. 16 이 좋은 타협점.

원본: `07-physx/physics/physics_introduction.html` 부근.

## 5. Articulation drive 수식과 안정성

`usd-from-urdf.md` §4 의 수식 다시:
```
τ = stiffness * (targetPos - currentPos)
  + damping * (targetVel - currentVel)
clamped to [-maxForce, +maxForce]
```

**안정성의 핵심**: critical damping. 1자유도 가정에서
```
damping ≈ 2 * sqrt(stiffness * inertia)
```

inertia 는 link 의 회전 관성. URDF `<inertial>` 에서 가져옴. **stiffness 만 올리고 damping 안 올리면 진동**. damping 만 올리면 응답이 느림.

### 튜닝 절차

1. 모든 joint 의 drive target 을 0 (또는 home pose) 으로.
2. stiffness 와 damping 을 작게 시작 (예: 1e3, 1e2).
3. Play. 중력으로 처지면 stiffness ↑ (5배씩).
4. 처짐이 멈추면 small step perturbation (target 0.1 rad jump) → 진동 보면 damping ↑.
5. 정착 시간 100 ms 이하면 합격.

### maxForce — 실 로봇 spec

datasheet 의 max torque (또는 max effort) 를 그대로. m0609 의 joint 별:
- J1 (base): 200 N·m
- J2 (shoulder): 200
- J3 (elbow): 100
- J4-6 (wrist): 50

너무 크면 시뮬 안에서 비현실적으로 강한 동작 (예: 1 kg 페이로드를 1 m/s² 으로 흔들기) → real 에선 토크 saturation 으로 못 함 → sim-to-real 갭.

## 6. 마찰 / 접촉 / restitution

PhysicsMaterial 로 정의:
```python
from pxr import UsdPhysics, UsdShade

mat_path = "/World/Materials/HighFriction"
mat = UsdShade.Material.Define(stage, mat_path)
phys_mat = UsdPhysics.MaterialAPI.Apply(mat.GetPrim())
phys_mat.CreateStaticFrictionAttr().Set(0.8)
phys_mat.CreateDynamicFrictionAttr().Set(0.6)
phys_mat.CreateRestitutionAttr().Set(0.1)
phys_mat.CreateDensityAttr().Set(1000.0)
```

이걸 collision prim 의 material binding 으로:
```python
UsdShade.MaterialBindingAPI.Apply(collision_prim).Bind(mat)
```

**핵심**:
- URDF 의 `<contact>` 태그는 임포터가 무시. 모든 마찰을 USD 측에서 다시.
- 두 표면이 접촉할 때 최종 마찰은 각각의 `combineMode` 에 따라 (`average`, `min`, `max`, `multiply`).
- 실 로봇의 finger ↔ 물체 마찰을 측정한 적 있다면 그 값 사용. 없으면 0.5/0.4 시작 후 grasping 성공률 보고 조정.

## 7. Self-collision 와 contact offset

기본은 self-collision OFF (`usd-from-urdf.md` §2). ON 하면:
- 손가락이 손바닥 위에 닿는 게 막힘 → grasping 학습 시 OFF 가 안전
- 다리가 몸통과 충돌 → 휴머노이드 학습 시 ON 필수
- 비용: contact pair 폭증 → 시뮬 느려짐

`contactOffset`, `restOffset` (collision shape attribute):
- `contactOffset` = PhysX 가 contact 으로 판단하기 시작하는 거리 (큐션 두께). Default 0.02. 작으면 jitter, 크면 visual gap.
- `restOffset` = 두 표면이 닿았을 때의 거리. 0 이면 정확히 닿음.

**튜닝 규칙**: `contactOffset > restOffset` 항상. 두 값 합이 객체 크기의 1% 미만이어야 visual gap 안 보임.

## 8. CPU vs GPU pipeline

```python
physxAPI.CreateGpuMaxRigidContactCountAttr().Set(524288)
physxAPI.CreateEnableGPUDynamicsAttr().Set(True)
physxAPI.CreateBroadphaseTypeAttr().Set("MBP")   # 또는 "SAP", "GPU"
```

**GPU pipeline** 은:
- Isaac Lab RL (수천 envs) → 필수
- 단일 매니퓰레이터 정밀 시뮬 → CPU 가 더 정확할 수 있음 (TGS CPU 의 collision detection 이 다름)

`EnableGPUDynamics=True` 시 일부 기능 미지원:
- Soft body, particle, fluid 의 일부
- 특정 joint type
- 일부 contact callback

증상: GPU pipeline 켰는데 simulation 이 정지 → log 에 `[physx] gpu_unsupported_feature` 확인.

원본: `10-gap-fills/physx-sdk/PhysX/physx/include/PxSceneDesc.h`.

## 9. Sim2real 4개 축 처방

SKILL.md Core mental model #4 의 자세한 처방.

### 축 1: Solver 정확도

| 증상 | 처방 |
|---|---|
| 실 로봇이 목표 위치보다 짧게 멈춤 | Position iter ↑ (16→32) |
| 그리퍼가 시뮬에선 잡았는데 실기는 미끄러짐 | TGS + Position iter 32 + 마찰 측정값 사용 |
| 빠른 동작에서 시뮬↔실기 trajectory 다름 | substep ↑ + 시뮬 rate 를 실 rate 에 맞춤 |

### 축 2: 마찰

| 증상 | 처방 |
|---|---|
| 시뮬 grasping 100% → 실기 30% | finger material 마찰 0.8/0.7 로 (보수적으로 높게) + Replicator 로 ±0.3 도메인 랜덤화 |
| 슬라이딩 거리가 다름 | floor / table material 마찰 측정 후 사용. 측정 안 되면 0.5/0.4 보수적 |
| 회전 마찰이 다름 (예: 컵 회전) | `dynamicFrictionDamping` 추가 (PhysX 5.3+) |

### 축 3: 센서 노이즈

학습용은 시뮬에서 **노이즈 합성**해야 함. 두 방법:

**OG 측 노이즈 (간단, 가볍)**:
- 카메라: `Camera Distortion Node` (배럴/핀쿠션) + 노이즈 텍스처 overlay
- IMU: 자체 노이즈 추가 노드 없음 → 외부 노드에서 `cv2.randn` 류

**Replicator 측 (포괄적)**:
- `replicator-sdg.md` §"센서 노이즈 랜덤화" 참조

**원칙**: real 의 노이즈 분포(std, distribution shape)를 측정해 시뮬에서 같은 분포 합성.

### 축 4: 제어 rate & latency

| 항목 | 시뮬 기본 | 실기 |
|---|---|---|
| PhysX rate | 60 Hz | — |
| 정책 출력 rate | 30 Hz | 30~100 Hz |
| Actuator latency | 0 | 5~50 ms |
| 토크/위치 변환 latency | 0 | PID 1~5 ms |

처방:
- 시뮬 rate 를 실기 컨트롤러에 맞추거나, 시뮬에 인공 latency 노드 추가:
  ```python
  # Isaac Lab event manager 에서
  event_cfg.actuator_latency = mdp.UniformRandomLatency(low=0.005, high=0.05)
  ```
- 정책이 위치 target 만 출력하면 실기 PID gain 과 같은 stiffness/damping 사용
- 토크 출력 정책이면 actuator 모델 (DC motor torque-speed curve) 시뮬에 반영

원본: 일반 sim2real 자료는 `06-replicator/synthetic_data_generation/` 및 NVIDIA blog `10-gap-fills/nvidia-blog/` 의 sim2real 글들.

## 10. 학습 안정성 영향 (Isaac Lab 관점)

| 파라미터 | RL 학습에 미치는 영향 |
|---|---|
| Solver position iter | ↑ → throughput ↓, 정확도 ↑. 16 이 sweet spot |
| Substep | ↑ → throughput 선형 ↓. 1 권장 |
| Self-collision | ON → 학습 reward 분산 ↑ (정책이 self-contact 회피 학습 필요) |
| Drive stiffness | 너무 낮음 → 정책이 학습한 motion 이 실기서 안 됨. 너무 높음 → reward 시그널이 noisy |
| Friction randomization | ↑ → robustness ↑, 학습 시간 ↑ |

PPO 같은 on-policy 학습에서 reward 가 noisy 하면 더 오래 학습해야 함. 시뮬 정확도와 학습 속도는 trade-off — RL 단계에선 적당히, 평가/배포 단계에선 정밀하게.

## 11. 자주 발생하는 물리 함정

| 증상 | 원인 | 해결 |
|---|---|---|
| 매니퓰레이터가 중력으로 처짐 | `fix_base=False` 또는 drive stiffness 0 | `usd-from-urdf.md` §2, §4 |
| 그리퍼가 떨림 | damping 부족 또는 stiffness 과다 | critical damping 공식 (§5) |
| 빠른 모션에서 link 가 link 통과 (tunneling) | substep=1 + 빠른 속도 | substep ↑ 또는 contactOffset ↑ |
| 두 손가락이 물체에서 미끄러짐 | 마찰 0.5 미만 | finger material 마찰 0.8 + 0.7 |
| Sim 에선 reward 잘 나오는데 real 에선 fail | sim2real gap 4개 축 (§9) | 축 1→2→3→4 순서로 검증 |
| Headless 학습 시 GPU 메모리 폭발 | num_envs 너무 큼 + camera 켜짐 | num_envs ↓ 또는 visual policy 만 별도 |
| Articulation 이 갑자기 NaN | drive maxForce 미설정 + 큰 target jump | maxForce 명시 + target rate limit |
| 두 환경의 동일 시드인데 다른 결과 | GPU pipeline 의 비결정성 | `EnableEnhancedDeterminismAttr=True` (성능 ↓) |
| Joint limit 근처에서 폭주 | hard limit 진입 시 큰 contact force | Soft joint limit (`<limit><safety_controller>`) 활용 또는 PID 미리 멈춤 |
| Restitution 이 1.0 인데 안 튐 | Material 이 collision prim 에 안 bind | `UsdShade.MaterialBindingAPI` 확인 |

## See also

- `usd-from-urdf.md` §4 — drive 파라미터를 처음에 어디에 넣나
- `isaaclab-rl.md` §"환경 안정성" — RL 학습 측의 물리 설정
- `replicator-sdg.md` §"센서 노이즈 랜덤화" — sim2real 축 3
- 원문: `07-physx/physics/`, `10-gap-fills/physx-sdk/PhysX/physx/`
- NVlabs/curobo (`10-gap-fills/curobo/repo/`) 의 motion gen 정밀도 비교
