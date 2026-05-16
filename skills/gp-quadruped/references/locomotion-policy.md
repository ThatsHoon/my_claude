# locomotion-policy.md — ANYmal-C 보행 + waypoint + m0609 stow 조합

GP 프로젝트의 보행 오케스트레이션. 번들 정책 *내부 메커니즘*은
[[isaac-sim-bridge]] `bundled-locomotion-policy.md` 참조 — 여기서는 **이 프로젝트
조합**(ANYmal-C + route 추종 + m0609 결합)만 다룬다.

## 목차
1. 자산·클래스 (검증 경로)
2. 구동 시퀀스 (sleep/키프레임 없음)
3. waypoint follower (classical P 제어)
4. m0609 결합 + stow (D3a 완화)
5. D2 — flat 정책 운용 조건
6. 함정 체크리스트

---

## 1. 자산·클래스 (검증 경로)

| 항목 | 경로 |
|---|---|
| 클래스 | `isaacsim.robot.policy.examples.robots.AnymalFlatTerrainPolicy` |
| 로봇 USD | `<assets_root>/Isaac/Robots/ANYbotics/anymal_c/anymal_c.usd` |
| 정책 | `<assets_root>/Isaac/Samples/Policies/Anymal_Policies/anymal_policy.pt` |
| env yaml | `<assets_root>/Isaac/Samples/Policies/Anymal_Policies/anymal_env.yaml` |
| actuator net | `<assets_root>/Isaac/Samples/Policies/Anymal_Policies/sea_net_jit2.pt` |

`<assets_root>` = `get_assets_root_path()` (isaacsim.storage.native). 정책은
**anymal_c** 학습본 — anymal_d 사용 금지(불안정). command = `[v_x, v_y, w_z]`
body-frame 속도, 권장 |v_x|≤1 m/s, |w_z|≤1 rad/s.

## 2. 구동 시퀀스 (불변식 1)

`anymal_standalone.py` 패턴. **execute_script 안에 sleep/장기 루프 금지**
(Kit thread block) — physics callback 으로만.

```python
from isaacsim.core.api import World
from isaacsim.robot.policy.examples.robots import AnymalFlatTerrainPolicy
import numpy as np

world = World(stage_units_in_meters=1.0, physics_dt=1/200, rendering_dt=1/60)
world.reset()
robot = AnymalFlatTerrainPolicy(prim_path="/World/Robot/anymal",
                                name="anymal", position=ROUTE[0])
first = True
def on_phys(step):
    global first
    if first:
        robot.initialize()          # control_mode="effort" + SEA actuator net
        first = False
    else:
        robot.forward(step, base_command)   # base_command = [vx,vy,wz]
world.add_physics_callback("anymal", on_phys)
# 이후 world.step(render=True) 루프 또는 Kit 타임라인 play
```

핵심 내부 동작(상세는 [[isaac-sim-bridge]] `bundled-locomotion-policy.md`):
- `initialize()` → `super().initialize(control_mode="effort")` + `LstmSeaNetwork`
  setup/reset (ANYmal SEA 액추에이터)
- `forward(dt,cmd)` → decimation 마다 48-obs 계산 → 정책 → action(scale 0.5)
  → `_actuator_network.compute_torques()` → `set_joint_efforts()`
- obs[9:12] = command. 매 step command 갱신해도 decimation 내부 처리됨.

## 3. waypoint follower (net-new, classical P 제어)

번들 정책은 **속도 명령만** 받는다 → 경로 추종 상위 제어가 필요(정책 재학습
아님). `/World/Path/route`(BasisCurves/Points polyline)를 순차 추종.

```python
pos, quat = robot.robot.get_world_pose()
yaw   = quat_to_yaw(quat)
tx,ty = ROUTE[idx]
d     = hypot(tx-pos[0], ty-pos[1])
brg   = atan2(ty-pos[1], tx-pos[0])
herr  = wrap_pi(brg - yaw)
# heading 오차 크면 전진 억제(제자리 회전 우선) — cos gate
gate  = max(0.0, cos(herr))
vx    = clip(KP_V*d, 0, V_MAX) * gate
wz    = clip(KP_W*herr, -W_MAX, W_MAX)
if d < ARRIVE_R:
    idx += 1
    if idx >= len(ROUTE): vx, wz = 0.0, 0.0   # 정지(마지막=Fence 앞)
base_command = np.array([vx, 0.0, wz])
```

- 권장 시작값: `KP_V=0.6, KP_W=1.2, V_MAX=0.8, W_MAX=0.8, ARRIVE_R=0.4 m`.
  넘어지면 V_MAX/KP_V 부터 낮춘다.
- "정해진 길" = route prim 사전 정의. C2 goto(`/robot/nav/goal`) 수신 시
  route 를 (현위치→goal) 갱신(사전 경로그래프 우선, 없으면 직선).
- 상태(`PATROL/ARRIVE/IDLE`, 현 idx)를 `/robot/state` 로 발행 → C2.

## 4. m0609 결합 + stow (불변식 3 / D3a)

m0609 를 ANYmal `base` 에 **fixed joint** 로 결합(USD `PhysicsFixedJoint`).
결합은 base CoM 을 이동 → flat 정책 불안정 가능. **항상 3종 완화 동반**:

1. **링크 질량 경감**: m0609 각 링크 mass 를 페이로드 수준으로 스케일
   (관성텐서 동반 조정). CoM 이동 최소화.
2. **보행 중 stow hold**: m0609 6축을 접힌 정자세로 position drive hold
   (예 posj 류 — 정확 값은 [[doosan-robotics]] `sim-integration.md`).
   동적 토크 외란 제거.
3. **조준은 정지 시에만**: 보행(`PATROL`) 중 팔 조작 금지. `ARRIVE/IDLE`
   에서만 link_6 를 타깃 지향(간이 IK / joint 목표).

URDF→USD 임포트·fixed joint 문법은 [[isaac-sim-bridge]] `usd-from-urdf.md`
§m0609 / [[doosan-robotics]] `sim-integration.md`. prim: `/World/Robot/m0609`,
`base_link` ↔ anymal `base`.

## 5. D2 — flat 정책 운용 조건 (불변식 2)

지형은 `references/terrain-build.md` 에서 **국소 경사 ≲15°, 진폭은 ANYmal
foot clearance 이내**로 클램프해 생성한다. 이는 정책 한계의 *우회*가 아니라
flat 정책의 *유효 운용 조건* 명시. 진짜 험지는 P4 Isaac Lab rough-terrain
재학습(범위 밖 — 문서에 명시만, 임시 땜질로 대체 금지).

## 6. 함정 체크리스트

- [ ] anymal_**c** 사용(d 아님). 정책/usd 모두 c.
- [ ] `initialize()` 는 첫 physics step 에서 1회. world.reset() 이후.
- [ ] command 는 매 step 갱신, body-frame, 크기 제한 준수.
- [ ] sleep/키프레임/루트 텔레포트 0건 (불변식 1).
- [ ] m0609 결합 시 질량경감+stow 동반(불변식 3) — 누락 시 보행 붕괴.
- [ ] 지형 D2 클램프 적용(불변식 2).
- [ ] 변경 후 영향 점검: route·`/robot/state`·C2 goto 경로 연동 확인.
