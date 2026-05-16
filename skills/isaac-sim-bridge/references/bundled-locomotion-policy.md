# bundled-locomotion-policy.md — Isaac Sim 번들 사전학습 보행 정책

Isaac Sim 5.1 은 4족/휴머노이드 **사전학습 RL 보행 정책**을 번들로 제공한다
(`isaacsim.robot.policy.examples`). Isaac Lab 학습 없이 실제 물리 보행을 즉시
구동 가능 — 범용 메커니즘 문서. 프로젝트별 조합(예: GP waypoint)은 해당
프로젝트 스킬에서.

## 목차
1. 무엇이 번들되어 있나
2. PolicyController 베이스 API
3. AnymalFlatTerrainPolicy (effort + SEA actuator)
4. SpotFlatTerrainPolicy (position)
5. 표준 구동 시퀀스
6. flat 정책의 한계 (중요)
7. 함정

---

## 1. 무엇이 번들되어 있나

소스: `~/dev_ws/isaac_sim/isaacsim/source/extensions/isaacsim.robot.policy.examples/isaacsim/robot/policy/examples/`
- `robots/anymal.py` `AnymalFlatTerrainPolicy`, `robots/spot.py`
  `SpotFlatTerrainPolicy`, `robots/h1.py` `H1FlatTerrainPolicy`
- `controllers/policy_controller.py` `PolicyController` (베이스)
- `utils/actuator_network.py` `LstmSeaNetwork`
- 표준 루프: `source/standalone_examples/api/isaacsim.robot.policy.examples/{anymal,spot}_standalone.py`

에셋(런타임 다운로드, `assets_root = get_assets_root_path()`):
- `anymal_c.usd` + `/Isaac/Samples/Policies/Anymal_Policies/{anymal_policy.pt,anymal_env.yaml,sea_net_jit2.pt}`
- `spot.usd` + `/Isaac/Samples/Policies/Spot_Policies/{spot_policy.pt,spot_env.yaml}`

> 클라우드 USD Search(`NVIDIA_API_KEY`)와 무관 — 이 에셋은 표준 Isaac
> asset 서버에서 받는다. 정책은 학습된 로봇과 **정확히 일치**해야 한다
> (anymal_c 정책 → anymal_c USD. anymal_d 금지).

## 2. PolicyController 베이스 API

`controllers/policy_controller.py`:

```
__init__(name, prim_path, root_path=None, usd_path=None, position=None, orientation=None)
  prim 없으면 define_prim + AddReference(usd_path); SingleArticulation 생성
load_policy(policy_file_path, policy_env_path)
  omni.client.read_file → torch.jit.load ; parse_env_config(yaml)
  → self._decimation, self._dt, self.render_interval
initialize(physics_sim_view=None, effort_modes="force", control_mode="position",
           set_gains=True, set_limits=True, set_articulation_props=True)
  robot.initialize → set_effort_modes → switch_control_mode(control_mode)
  → gains/max_effort/max_vel from env yaml → _set_articulation_props
_compute_action(obs)  : torch.no_grad, policy(obs).view(-1).numpy()
post_reset()          : robot.post_reset()
```

`_compute_observation()` / `forward()` 는 베이스에서 NotImplemented —
서브클래스가 구현. 즉 obs 레이아웃·제어는 robot 별.

## 3. AnymalFlatTerrainPolicy (effort + SEA)

`robots/anymal.py`:
- `__init__` usd 기본 `anymal_c.usd`; `load_policy(anymal_policy.pt, anymal_env.yaml)`;
  `_action_scale=0.5`, `_previous_action=zeros(12)`, `_policy_counter=0`
- **obs 48** (`_compute_observation(command)`):
  `[0:3]` base lin vel(body), `[3:6]` ang vel(body), `[6:9]` gravity(body),
  `[9:12]` command `[v_x,v_y,w_z]`, `[12:24]` jpos-default, `[24:36]` jvel,
  `[36:48]` prev action
- `forward(dt, command)`: decimation 마다 obs→정책→action;
  `_actuator_network.compute_torques(jpos,jvel, action*0.5)` →
  `robot.set_joint_efforts(tau)`; counter++
- `initialize()` → `super().initialize(control_mode="effort")` 후
  `LstmSeaNetwork().setup(sea_net_jit2.pt, default_pos)` + `reset()`
  (ANYmal Series-Elastic Actuator 모델, torque clip[-80,80])

## 4. SpotFlatTerrainPolicy (position)

`robots/spot.py`: obs 48 동일 구조. **차이**: actuator net 없음,
`control_mode="position"`(기본), `_action_scale=0.2`, action →
target joint position(`default_pos + action*scale`) → `set_joint_positions`.

## 5. 표준 구동 시퀀스 (키프레임/sleep 금지)

```python
from isaacsim.core.api import World
from isaacsim.robot.policy.examples.robots import AnymalFlatTerrainPolicy
import numpy as np
world = World(stage_units_in_meters=1.0, physics_dt=1/200, rendering_dt=1/60)
world.reset()
robot = AnymalFlatTerrainPolicy(prim_path="/World/Anymal", name="anymal",
                                position=np.array([0,0,0.7]))
first=True
def on_phys(step):
    global first
    if first: robot.initialize(); first=False
    else:     robot.forward(step, base_command)   # [vx,vy,wz]
world.add_physics_callback("anymal", on_phys)
# world.step(render=True) 루프 또는 타임라인 play
```

규칙:
- `initialize()` 는 **첫 physics step**, `world.reset()` 이후.
- command 매 step 갱신(body-frame, |v|≲1, |w|≲1). decimation 은 내부 처리.
- `time.sleep`/장기 for 루프를 callback/execute_script 에 넣지 말 것
  (Kit thread block). 멈춤은 command=0.
- 정지/리셋 시 `post_reset()` + actuator net `reset()`(anymal).

## 6. flat 정책의 한계 (중요)

번들 정책은 **평지 학습본**. 험지에서 보행 보장 안 됨. 대응 원칙:
- 지형을 정책 안정 범위로 만든다(국소 경사/진폭 제한) — *우회가 아니라
  운용 조건 명시*.
- 진짜 험지 = Isaac Lab rough-terrain 재학습(별도, 명시적 단계).
- 페이로드(팔 등) 결합은 CoM 이동 → 불안정 가능. 질량 경감 + stow 자세 +
  필요 시 재학습으로 *근본 대응*. 땜질(키프레임 보정 등) 금지.

## 7. 함정

- 정책↔USD 불일치(anymal_d 에 c 정책) → 즉시 불안정.
- `initialize()` 누락/순서 오류 → effort/gain 미설정으로 붕괴.
- obs command 슬롯(9:12) 미갱신 → 제자리.
- Spot 은 position, Anymal 은 effort+SEA — 혼동 시 토크/포즈 오작동.
- MCP 라이브 구동 시 결과 검증은 [[isaac-sim-mcp]] `/tmp` 패턴.
