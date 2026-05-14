# isaaclab-rl.md — Isaac Lab 환경 설계와 강화학습

이 reference 는 **Isaac Lab 위에서 RL 환경을 만들고 학습·평가·배포하는 전 단계**를 다룬다. Manager-based vs Direct 패러다임 선택, env 구성, 도메인 랜덤화, PPO/SAC, 정책 export, sim-to-real 배포.

## Contents
1. Isaac Lab 이 뭐고 Isaac Gym 과의 차이
2. 설치 및 첫 실행
3. Manager-based vs Direct — 어느 걸 쓸까
4. Manager-based env 작성 5단계
5. Direct env 작성 5단계
6. Asset 등록과 robot config
7. Observation / Action / Reward 설계 원칙
8. Termination 과 Event (도메인 랜덤화 포함)
9. PPO / SAC 학습 워크플로
10. 정책 export — ONNX / TorchScript / JIT
11. Sim-to-real 배포
12. 학습 디버깅 체크리스트
13. 자주 발생하는 환경 함정

---

## 1. Isaac Lab 이 뭐고 Isaac Gym 과의 차이

| 프레임워크 | 상태 | 위에 올라간 시뮬레이터 | 비고 |
|---|---|---|---|
| **Isaac Gym** (Preview) | 종료 (2023) | 자체 PhysX 5 — 별도 앱 | API 인기 있었으나 deprecated |
| **Orbit** | 종료 (2024 통합) | Isaac Sim | Isaac Lab 의 전신 |
| **Isaac Lab** | **현행** | Isaac Sim | 공식 표준. 본 문서가 다루는 것 |
| **IsaacGymEnvs** | 종료 (참조용) | Isaac Gym | 환경 모음. 마이그레이션 참조용 |

**핵심**: 새 프로젝트는 Isaac Lab. 기존 Isaac Gym 코드는 Isaac Lab 으로 마이그레이션 가능 (`05-isaac-lab/isaac_lab_full/source/migration/` 참조).

소스: `09-github-repos/IsaacLab/`, 문서: `05-isaac-lab/isaac_lab_full/`

## 2. 설치 및 첫 실행

Isaac Sim 이 먼저 설치되어 있어야 (`installation.md`).

```bash
# Conda env 권장
conda create -n isaaclab python=3.10
conda activate isaaclab

# Isaac Sim 의 Python 으로 pip 설치 안 됨 → bundled python.sh 사용
git clone --depth=1 https://github.com/isaac-sim/IsaacLab.git
cd IsaacLab

# Isaac Sim 위치 자동 탐지
./isaaclab.sh --install   # 또는 --conda 모드

# 검증
./isaaclab.sh -p source/standalone/tutorials/00_sim/launch_app.py
```

원본: `05-isaac-lab/isaac_lab_full/source/setup/`

## 3. Manager-based vs Direct — 어느 걸 쓸까

(SKILL.md Core mental model #5 의 자세한 결정 가이드)

| 기준 | Manager-based | Direct |
|---|---|---|
| 학습 곡선 | 가파름 (config 학습 필요) | 완만 (RL 코드처럼 보임) |
| 표준 reward shaping | 빠름 | 수동 |
| 비표준 obs (예: 비대칭 actor-critic) | 가능하지만 어색 | 자연스러움 |
| 가변 step (early termination 후 reset) | 어색 | 자연 |
| Population-based training | 어색 | 자연 |
| 코드 양 | 적음 (config 60~150 lines) | 많음 (env class 200~400 lines) |
| 공식 예제 수 | 30+ | 10+ |

**결정 트리**:
- "기존 manipulation/locomotion 패턴과 유사" → Manager-based
- "actor 와 critic 이 다른 obs" → Direct
- "step 안에서 condition 별로 다른 physics 호출" → Direct
- "처음 시작" → Manager-based, Isaac Lab 예제 fork

## 4. Manager-based env 작성 5단계

예: Franka 가 cube 를 잡아 target zone 으로 옮기는 task.

### Step 1: Asset configs

```python
# franka_lift/franka_lift_env_cfg.py
from isaaclab.assets import ArticulationCfg, RigidObjectCfg
from isaaclab.sim import UsdFileCfg
from isaaclab_assets.robots.franka import FRANKA_PANDA_CFG

@configclass
class FrankaLiftEnvCfg(ManagerBasedRLEnvCfg):
    scene = SceneCfg(num_envs=4096, env_spacing=2.5)
    robot: ArticulationCfg = FRANKA_PANDA_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    object: RigidObjectCfg = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Object",
        spawn=UsdFileCfg(usd_path="/home/me/cube.usd"),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.5, 0.0, 0.0)),
    )
```

### Step 2: Observations

```python
@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg:
        joint_pos = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=mdp.joint_vel_rel)
        object_pos = ObsTerm(func=mdp.object_position_in_robot_root_frame)
        target_pos = ObsTerm(func=mdp.target_position)
        actions = ObsTerm(func=mdp.last_action)

    policy = PolicyCfg()
```

각 ObsTerm 의 `func` 는 `mdp.*` 모듈에서 가져온다 (Isaac Lab 이 표준 obs 함수 제공). 없으면 직접 함수 정의 후 등록.

### Step 3: Actions

```python
@configclass
class ActionsCfg:
    arm_action = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=["panda_joint.*"],
        scale=0.5,
        use_default_offset=True,
    )
    gripper_action = mdp.BinaryJointPositionActionCfg(
        asset_name="robot",
        joint_names=["panda_finger.*"],
        open_command_expr={"panda_finger.*": 0.04},
        close_command_expr={"panda_finger.*": 0.0},
    )
```

### Step 4: Rewards

```python
@configclass
class RewardsCfg:
    reaching = RewTerm(
        func=mdp.object_ee_distance,
        weight=-1.0,
        params={"std": 0.1},
    )
    lifting = RewTerm(
        func=mdp.object_is_lifted,
        weight=15.0,
        params={"minimal_height": 0.04},
    )
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-1e-4)
```

### Step 5: Terminations + Events

```python
@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    object_dropped = DoneTerm(
        func=mdp.root_height_below_minimum,
        params={"minimum_height": -0.05, "asset_cfg": SceneEntityCfg("object")},
    )

@configclass
class EventsCfg:
    reset_object_pos = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={"pose_range": {"x": (0.4, 0.6), "y": (-0.2, 0.2)}, ...},
    )
```

위 5개 dataclass 를 묶어 `FrankaLiftEnvCfg` 의 멤버로 → 자동으로 env 구성. 학습 실행:
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Lift-Cube-Franka-v0 --num_envs 4096 --headless
```

원본 예제: `09-github-repos/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/lift/`

## 5. Direct env 작성 5단계

복잡한 흐름이 필요하면 Direct. 예: 휴머노이드 보행에서 actor obs 는 proprioception 만, critic obs 는 추가로 ground truth state.

```python
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg

@configclass
class HumanoidEnvCfg(DirectRLEnvCfg):
    episode_length_s = 20.0
    decimation = 4
    action_scale = 1.0
    num_actions = 21
    num_observations = 78
    num_states = 124   # critic obs (asymmetric)

class HumanoidEnv(DirectRLEnv):
    cfg: HumanoidEnvCfg

    def _setup_scene(self):
        self.robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self.robot
        spawn_ground_plane(...)
        self.scene.clone_environments(copy_from_source=False)

    def _pre_physics_step(self, actions):
        self.actions = actions.clone()
        targets = self.action_scale * self.actions + self.robot.data.default_joint_pos
        self.robot.set_joint_position_target(targets)

    def _apply_action(self):
        pass

    def _get_observations(self):
        obs = torch.cat([
            self.robot.data.joint_pos_rel,
            self.robot.data.joint_vel,
            self.robot.data.root_lin_vel_b,
            self.robot.data.root_ang_vel_b,
            self.actions,
        ], dim=-1)
        state = torch.cat([
            obs,
            self.robot.data.root_pos_w,
            self._target_pos,
        ], dim=-1)
        return {"policy": obs, "critic": state}
```

`_get_observations` 가 dict 반환 → asymmetric actor-critic. RSL-RL 의 `PolicyValueNet` 자동 처리.

원본 예제: `09-github-repos/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/direct/`

## 6. Asset 등록과 robot config

`isaaclab_assets.robots.franka.FRANKA_PANDA_CFG` 같은 사전 정의 config 를 재사용. 새 로봇이면 직접 정의:

```python
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

DOOSAN_M0609_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path="/home/me/usd/m0609.usd",
        activate_contact_sensors=False,
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={"joint1": 0.0, "joint2": -0.5},
        joint_vel={"joint.*": 0.0},
    ),
    actuators={
        "shoulder": ImplicitActuatorCfg(
            joint_names_expr=["joint[1-3]"],
            stiffness=4e6, damping=2e5, effort_limit=200.0, velocity_limit=2.0,
        ),
        "wrist": ImplicitActuatorCfg(
            joint_names_expr=["joint[4-6]"],
            stiffness=1e6, damping=5e4, effort_limit=50.0, velocity_limit=3.0,
        ),
    },
)
```

`ImplicitActuatorCfg` = USD 의 PhysicsDriveAPI 사용. `IdealPDActuatorCfg` = 자체 PID 시뮬 (latency 추가 가능).

## 7. Observation / Action / Reward 설계 원칙

### Observation
- **정규화 필수**: `mdp.joint_pos_rel` (default 대비 상대값) 같이 0 중심.
- **속도는 클램프**: noise 폭주 방지. 보통 ±5x default velocity.
- **목표 정보는 항상 robot frame**: world frame 으로 주면 학습이 절대좌표 외움 → 일반화 실패.

### Action
- **scale 작게**: `JointPositionActionCfg.scale=0.5` 가 시작점. 너무 크면 진동, 작으면 학습 느림.
- **delta vs absolute**: delta (지난 step 의 명령 + scale * action) 가 보통 더 안정.
- **그리퍼는 BinaryJointPositionActionCfg**: continuous gripper 보다 학습 빠름.

### Reward
- **분산이 비슷한 항들로 weighted sum**: 한 항이 다른 항보다 100배 크면 그것만 학습.
- **negative dense + sparse bonus**: distance penalty (dense, ~-1) + success bonus (sparse, +15).
- **action regularization 작게**: -1e-4 정도. 너무 크면 안 움직임.
- **velocity regularization**: 휴머노이드 보행에서 critical. 매니퓰레이션은 없어도 됨.

## 8. Termination 과 Event (도메인 랜덤화 포함)

Event 는 reset / startup / interval 시점에 fire. **도메인 랜덤화의 1순위 도구**.

```python
@configclass
class EventsCfg:
    randomize_friction = EventTerm(
        func=mdp.randomize_rigid_body_material,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("object"),
            "static_friction_range": (0.4, 0.9),
            "dynamic_friction_range": (0.3, 0.8),
            "restitution_range": (0.0, 0.1),
            "num_buckets": 64,
        },
    )
    randomize_mass = EventTerm(
        func=mdp.randomize_rigid_body_mass,
        mode="reset",
        params={"asset_cfg": SceneEntityCfg("object"), "mass_range": (0.05, 0.3)},
    )
    push_robot = EventTerm(
        func=mdp.apply_external_force_torque,
        mode="interval",
        interval_range_s=(2.0, 5.0),
        params={"force_range": {}},
    )
    randomize_robot_joint_stiffness = EventTerm(
        func=mdp.randomize_actuator_gains,
        mode="startup",
        params={"stiffness_distribution_params": (0.8, 1.2), "operation": "scale"},
    )
```

원칙: **real 의 분포를 측정**하여 그것을 시뮬에서 랜덤화. real distribution 모르면 ±20% 시작.

`replicator-sdg.md` §"센서 노이즈" 와 함께 사용.

## 9. PPO / SAC 학습 워크플로

Isaac Lab 은 3개 RL 라이브러리 지원: RSL-RL, RL-Games, skrl. 권장: **RSL-RL** (작고 빠르고 Isaac Sim 친화).

```bash
# 학습
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Lift-Cube-Franka-v0 \
  --num_envs 4096 \
  --headless \
  --max_iterations 1000

# Tensorboard 모니터링
tensorboard --logdir logs/rsl_rl/franka_lift

# 학습된 정책 재생
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
  --task Isaac-Lift-Cube-Franka-Play-v0 \
  --num_envs 32 \
  --checkpoint logs/rsl_rl/franka_lift/<run>/model_*.pt
```

PPO 권장 하이퍼 (Isaac Lab 기본이 잘 튜닝되어 있음):
- `num_steps_per_env=24`
- `learning_rate=1e-3` adaptive
- `clip_param=0.2`
- `num_mini_batches=4`
- `entropy_coef=0.005`

SAC 는 sample-efficient 하지만 Isaac Lab 에서는 PPO 만큼 검증 안 됨 — manipulation 에선 PPO 우선.

원본: `09-github-repos/IsaacLab/scripts/reinforcement_learning/rsl_rl/` (CLI 스크립트), `09-github-repos/IsaacLab/source/isaaclab_rl/isaaclab_rl/rsl_rl/` (RSL-RL 통합 모듈)

## 10. 정책 export — ONNX / TorchScript / JIT

학습된 `.pt` 를 배포용으로:

```python
import torch
from rsl_rl.runners import OnPolicyRunner

runner = OnPolicyRunner(env, train_cfg, log_dir=None, device="cuda")
runner.load("logs/.../model_1000.pt")
policy = runner.get_inference_policy(device="cuda")

# TorchScript
example_obs = torch.randn(1, obs_dim).cuda()
traced = torch.jit.trace(policy, example_obs)
traced.save("policy.pt")

# ONNX
torch.onnx.export(
    policy, example_obs, "policy.onnx",
    input_names=["obs"], output_names=["action"],
    dynamic_axes={"obs": {0: "batch"}, "action": {0: "batch"}},
    opset_version=15,
)
```

ONNX → 실 로봇 측 추론은 `onnxruntime` 또는 TensorRT 로. Jetson 배포 시 TensorRT 가 2-3배 빠름.

## 11. Sim-to-real 배포

순서:
1. **시뮬에서 도메인 랜덤화 학습 완료** (§8)
2. **시뮬 평가**: 별도 평가 envs 에서 robustness 측정 (no DR, 다른 시드)
3. **정책 export** (§10)
4. **실기 측 셋업**: ROS 2 추론 노드 — `/joint_states` → obs 변환 → policy → `/joint_command` 출력
5. **단순한 task 먼저**: home pose 유지, 다음 점 도달, 그 다음 grasp
6. **fallback 안전망**: torque limit, joint limit, e-stop

자주 마주치는 갭은 `physx-tuning.md` §9 의 4축. 거의 항상 마찰 (축 2) + 센서 노이즈 (축 3) 부족.

자세한 배포 가이드: `05-isaac-lab/isaac_lab_full/source/policy_deployment/`

## 12. 학습 디버깅 체크리스트

reward 가 안 오르면 이 순서로:

1. **Random policy reward 측정**: random action 으로 100 ep → 평균 reward. 학습이 이보다 명백히 높지 않으면 보상 자체 문제.
2. **Reward 항 별로 weight 0 으로 두고 하나씩 켜기**: 어느 항이 학습을 끄나 식별.
3. **Action 의 분포 보기**: tensorboard 의 `Train/loss/learning_rate`, `Train/std`. std 가 너무 작으면 entropy_coef ↑.
4. **Obs 의 분포 보기**: `mdp.observation_clip` 으로 outlier 잡혔는지. NaN 검출.
5. **num_envs ↓ 로 디버깅**: 16 envs 로 줄여서 GUI 켜고 행동 관찰.
6. **PhysX 안정성**: `physx-tuning.md` 의 position iter, drive gain 확인.

## 13. 자주 발생하는 환경 함정

| 증상 | 원인 | 해결 |
|---|---|---|
| Reward 가 ep 1 부터 끝까지 동일 | termination 이 안 작동 | DoneTerm 의 func 가 True 를 반환하는지 단위테스트 |
| 학습 초기 NaN | obs 가 unbounded + 정규화 안 됨 | `mdp.observation_clip(min, max)` 또는 normalize term |
| Episode length 안 차고 끝남 | time_out 의 `time_out=True` 누락 | `DoneTerm(func=mdp.time_out, time_out=True)` |
| Sim 에서 잘 되는데 real 에서 매번 fail | DR 부족 | §8 의 friction/mass/latency 추가 |
| GPU OOM (4096 envs + camera) | RTX-RT 가 메모리 폭발 | num_envs ↓ 또는 카메라 끔, SKILL.md §6 |
| `_setup_scene` 후 articulation 이 안 보임 | clone_environments 호출 누락 | `self.scene.clone_environments(copy_from_source=False)` |
| Manager-based 의 obs/action 차원 mismatch | ObsCfg 추가 후 num_observations 안 갱신 | Manager-based 는 자동, Direct 는 수동 — Direct cfg 확인 |
| Reset 시 articulation 이 home pose 가 아님 | InitialStateCfg.joint_pos 미설정 | `joint_pos={"j.*": 0.0}` 등 명시 |
| 정책이 한 곳에서 떨림 | action_rate reward 부족, action_scale 큼 | `action_rate_l2 weight=-1e-3`, scale 0.3 |
| 학습된 정책이 export 후 다른 결과 | Train 모드 / eval 모드, normalization 누락 | `policy.eval()` + obs normalizer 도 export |

## See also

- `usd-from-urdf.md` — 로봇 USD 준비 (특히 §10 m0609)
- `physx-tuning.md` §10 — 학습 안정성 영향
- `replicator-sdg.md` §"온라인 도메인 랜덤화" — visual policy 학습 시
- `isaac-ros-accel.md` §"GPU 예산" — RL + perception 동시 실행
- 원문: `05-isaac-lab/isaac_lab_full/`, `09-github-repos/IsaacLab/`
- 마이그레이션: `05-isaac-lab/isaac_lab_full/source/migration/` (Isaac Gym → Isaac Lab)
