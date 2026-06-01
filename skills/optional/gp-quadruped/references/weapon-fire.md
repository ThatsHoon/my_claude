# weapon-fire.md — raycast 사격 시뮬 + 트레이서 + FireEvent

GP 무기 시뮬레이션. **시뮬 전용**(D5): 실무기·탄도 없음. 조준 + raycast
히트판정 + 시각 트레이서 + 이벤트 로깅만. 자동 발사 없음 — 항상 C2 운용자
버튼 명시 트리거.

## 목차
1. 원칙 (시뮬 한정 / 운용자 트리거)
2. 조준 (정지 상태에서만)
3. raycast 히트판정
4. 트레이서 시각화
5. FireEvent + 명령불이행 타이머
6. 함정 체크리스트

---

## 1. 원칙

- **시뮬 전용**. 발사체 rigid body·탄도 없음(P 옵션). 기본은 raycast 1발
  히트 bool + 거리 + 시각 트레이서 + `FireEvent` 기록.
- **운용자 트리거만**: `POST /robots/{id}/fire`(X-API-Key) →
  service `/robot/weapon/fire`. 자동/자율 발사 절대 금지.
- 명령불이행 타이머는 *사격 허가 UI 활성*까지만 — 실제 발사는 항상 사람.

## 2. 조준 (불변식 3 — 정지 시에만)

- 보행(`PATROL`) 중 팔 조작 금지. `ARRIVE/IDLE` 에서만.
- 타깃 = C2 가 준 detection id 의 world pose(또는 직접 pose).
- m0609 link_6(또는 tool0) 를 타깃 방향으로 지향: 간이 IK 또는 joint 목표
  (m0609 IK/joint 한계는 [[doosan-robotics]] `sim-integration.md`).
- 총구 origin = link_6 자식 muzzle prim 의 world transform.

## 3. raycast 히트판정

PhysX scene query. MCP execute_script 안에서 실행 시 결과는 `/tmp` 로
([[isaac-sim-mcp]]).

```python
from omni.physx import get_physx_scene_query_interface
import carb

origin = muzzle_world_pos          # Gf.Vec3 → carb.Float3
direction = normalize(target_pos - origin)
hit = get_physx_scene_query_interface().raycast_closest(
        carb.Float3(*origin), carb.Float3(*direction), 200.0)  # max 200 m
if hit["hit"]:
    hit_prim = hit["rigidBody"]      # 또는 collision prim path
    dist     = hit["distance"]
    hit_pos  = hit["position"]
```

생체 타깃 prim 에 semantic/이름 규약을 두어 `hit_prim` 으로 명중 대상 식별.

## 4. 트레이서 시각화

origin→hit_pos(또는 max range) 선분을 1회성 prim 으로:
- `UsdGeom.BasisCurves` 또는 가는 `Cylinder` 1개, emissive 머티리얼,
  ~0.1 s 후 제거(또는 visibility 토글). prim 경로 `/World/FX/tracer`.
- MCP 라이브면 prim 생성 후 `/tmp` 검증, sleep 금지(타이머는 physics
  callback step 누적으로).

## 5. FireEvent + 명령불이행 타이머

```
FireEvent { ts, operator, target_ref, hit:bool, hit_prim, distance_m }
```
- ROS 발행 + `fire_events` 테이블 적재(영상 외 전 데이터 psql, 불변식 4).
- 명령불이행 흐름: 확성기 명령 송출 → `c2_command_node` FSM 타이머 N 초 →
  미반응 시 C2 UI "사격 허가" 활성(발사 자체는 운용자 버튼). 타이머는
  physics/노드 step 누적, `time.sleep` 금지.

## 6. 함정 체크리스트

- [ ] 발사는 service 트리거 + X-API-Key. 자동 발사 코드 0건.
- [ ] 조준은 정지 상태에서만(보행 중 팔 금지, 불변식 3).
- [ ] raycast 결과/트레이서 생성은 MCP 시 `/tmp` 검증.
- [ ] FireEvent 는 psql `fire_events` 적재(영상은 절대 미적재).
- [ ] 타이머에 sleep 금지 — step 누적.
- [ ] 변경 후 영향: c2_command FSM·UI 사격버튼·telemetry 스키마 점검.
