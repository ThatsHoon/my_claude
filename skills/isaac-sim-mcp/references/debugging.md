# debugging.md — When MCP tool calls fail

The failure modes for MCP calls cluster into a small set. This reference is a flat
diagnostic table → root cause → fix. Read the row matching your symptom first.

## Contents
1. Recovering connection
2. Reading Kit's log
3. Common error signatures
4. Stuck/frozen simulation
5. Stale state (yesterday's prims still there)
6. Wrong values silently accepted (USD/PhysX)
7. Multiple Isaac Sim instances
8. Permission denied / sandboxed errors

---

## 1. Recovering connection

**Symptom**: Every MCP tool returns `Connection refused: [Errno 111]` or similar.

**Diagnose in this order** (run via `Bash`, not MCP — MCP is the thing that's broken):

```bash
# 1. Is Isaac Sim running at all?
pgrep -af isaac-sim
# Expected: a process matching isaac-sim.sh + python.sh

# 2. Is the extension listening on 8766?
ss -tlnp 2>/dev/null | grep 8766
# Expected: LISTEN ... 127.0.0.1:8766

# 3. Did the MCP server (Python subprocess) start?
pgrep -af "isaac_mcp/server.py"
# Expected: one process running .venv/bin/python server.py
```

**Causes by what's missing**:

| Missing | Cause | Fix |
|---|---|---|
| Isaac Sim process | Not launched | Tell user: open terminal, run `isaac-mcp`, wait 1-2 min for boot |
| Isaac Sim running but no 8766 listener | Extension not loaded | `isaac-mcp` was launched without `--enable isaac.sim.mcp_extension`, or the extension itself failed to load. Tell user to check Isaac Sim's `Window → Console` for red errors mentioning `isaac.sim.mcp` |
| Both running but MCP server dead | Server crashed | Restart Claude Code session (the server is spawned by Claude on session start) |
| Everything running but still refused | Kit's main thread is blocked | Wait 10s and retry. If still failing, see §4 |

**The `isaac-mcp` alias** (set in `~/.bashrc`):
```bash
alias isaac-mcp='~/dev_ws/isaac_sim/isaacsim/_build/linux-x86_64/release/isaac-sim.sh \
  --ext-folder /home/rokey/dev_ws/isaac-sim-mcp/ \
  --enable isaac.sim.mcp_extension'
```

If the alias is missing or broken, the manual command above launches with extension.

---

## 2. Reading Kit's log

Kit writes a verbose log to `~/.nvidia-omniverse/logs/` and (for source builds) also
to `~/.local/share/ov/data/Kit/Apps/Isaac-Sim/<version>/kit_*.log`. The MCP server can
read these too.

**Tail the latest log via Bash**:
```bash
# Find the newest kit log
KIT_LOG=$(ls -t ~/.nvidia-omniverse/logs/Kit/*/kit_*.log 2>/dev/null | head -1)
[ -z "$KIT_LOG" ] && KIT_LOG=$(ls -t ~/.local/share/ov/data/Kit/Apps/Isaac-Sim/*/kit_*.log 2>/dev/null | head -1)
echo "Latest log: $KIT_LOG"

# Tail last 50 lines for errors
tail -50 "$KIT_LOG" | grep -iE "error|warning|exception|traceback" | tail -30
```

**Tail live during a test**:
```bash
tail -F "$KIT_LOG"
```

**What to look for**:
- `[Error] [omni.physx.plugin]` → PhysX setup issue (collider, articulation)
- `[Error] [asyncio] Task exception was never retrieved` → an `async def` raised but
  wasn't awaited. Often from BaseSample `setup_post_load` failures
- `[Error] [omni.usd] Stage opening or closing already in progress` → race condition
  on LOAD button (§5)
- `[Error] [omni.graph]` → OmniGraph node validation failure (red node)
- `[carb.graphics-vulkan]` → GPU/driver issue (rare on this user's RTX 5080)

After the first MCP `execute_script` call that crashes, **always** read the kit log
before retrying. The error printed to the MCP response is often a generic wrapper; the
real cause is in kit.log.

---

## 3. Common error signatures

### `NameError: name 'np' is not defined`
The `execute_script` snippet uses `np.` but didn't import numpy. Add
`import numpy as np` at the top.

### `AttributeError: 'NoneType' object has no attribute 'get_articulation_controller'`
`world.scene.get_object("name")` returned `None` because the prim doesn't exist OR the
robot wasn't added to the scene OR it wasn't reset yet. Fix:
```python
robot = world.scene.get_object("m0609")
if robot is None:
    print("ERROR: robot not in scene. Did you forget world.scene.add(Robot(...))?")
else:
    ctrl = robot.get_articulation_controller()
```

### `Exception: There is no stage currently opened`
Stage was closed (File → New, or unloaded). Open one first:
```python
import omni.usd
omni.usd.get_context().new_stage()
```
Or wait for the user to load a scene manually.

### `PhysX error: Supplied PxGeometry is not valid. Shape creation method returns NULL`
Mesh is degenerate (scale=0, empty, or perfectly flat for convex hull). See
[[isaac-sim-bridge]] `references/usd-from-urdf.md` §collision-fixes, then fix via
`execute_script`:
```python
from pxr import UsdGeom, Gf
prim = stage.GetPrimAtPath("/World/Cube_01")
# Diagnose: read scale and size
# Fix: set non-degenerate values
xf = UsdGeom.Xformable(prim)
for op in xf.GetOrderedXformOps():
    if op.GetOpName() == "xformOp:scale":
        op.Set(Gf.Vec3f(1, 1, 1))
```

### `setCollider: /...belt... is a part of a rigid body. Resetting approximation shape from none (trimesh) to convexHull`
**Warning, not error** — PhysX auto-fixed. Underlying issue: trimesh collider on a
dynamic body (PhysX forbids). Either remove RigidBodyAPI (conveyor should be static)
or accept the convex hull approximation. See `cobot3-recipes.md` §conveyor.

### `Task exception was never retrieved: ... NameError ...`
An `async def` in a BaseSample handler raised. The PDF's broken `hello_world.py`
exhibits this. See `cobot3-recipes.md` §"Fixing broken samples" or just rewrite the
handler.

---

## 4. Stuck/frozen simulation

**Symptom**: Viewport frozen, `get_scene_info` times out.

**Causes (most likely first)**:
1. **`time.sleep()` inside a physics callback or `execute_script`** — blocks Kit
   thread. Identify and remove.
2. **Tight loop in `execute_script`** — e.g., `for _ in range(1000): world.step()`.
   Same issue. Use `add_physics_callback` instead.
3. **Modal dialog stuck open in GUI** — user must dismiss it. Ask them to look at the
   GUI window.
4. **GPU hang** — rare, requires Isaac Sim restart.

**Recovery from MCP side**:
```python
# execute_script (may itself time out — try anyway)
import omni.timeline
omni.timeline.get_timeline_interface().stop()
```

If that fails, ask user to click `Stop` in viewport. If GUI also unresponsive →
restart Isaac Sim.

---

## 5. Stale state — yesterday's prims still there

**Symptom**: New session, you expect an empty stage, but `get_scene_info` shows prims
from a previous session.

**Cause**: Isaac Sim doesn't auto-clean stage between sessions. If a previous test
created `/World/Cube_01`, it's still there.

**Fix (always at the start of a fresh task)**:
```python
# execute_script
import omni.usd
omni.usd.get_context().new_stage()
```

Verify with `get_scene_info` — should be down to `/World` and `/Render`.

---

## 6. Wrong values silently accepted

USD and PhysX often accept invalid attribute values without raising. Examples:

- Setting `xformOp:scale` to `Gf.Vec3f(0, 1, 1)` — accepted, but the prim becomes
  degenerate. PhysX then fails downstream.
- Calling `prim.GetAttribute("nonExistent").Set(5)` — silently does nothing. No
  exception.
- Setting a typed attribute to wrong type — usually silent on USD side, blows up
  later.

**Defense**: After any `execute_script` that sets attributes, **read them back**:
```python
val = prim.GetAttribute("xformOp:scale").Get()
print(f"scale after set: {val}")
assert val[0] != 0, "scale.x is zero — refused or set wrong"
```

For typed APIs, use the typed wrappers when available:
```python
# Don't: prim.GetAttribute("...").Set(...)
# Do:    UsdGeom.Cube(prim).GetSizeAttr().Set(...)
```

---

## 7. Multiple Isaac Sim instances

If two Isaac Sim instances are running, only one has the extension listening on 8766
(the one started with `isaac-mcp`). MCP talks to that one.

**Confirm via Bash**:
```bash
pgrep -af isaac-sim
ss -tlnp | grep 8766
```

**If the user wants MCP to target a different instance**: the alternate instance must
have been launched with `--enable isaac.sim.mcp_extension`, and the port is allocated
sequentially (8766, 8767, ...). The MCP server connects to 8766 by default — to point
elsewhere, modify the server config (see `~/dev_ws/isaac-sim-mcp/isaac_mcp/server.py`
for the port).

---

## 8. Permission denied / sandboxed errors

Rare. If `execute_script` fails with file-system permission errors (e.g., writing to
`/etc/`), Kit runs with the user's permissions — if the user can't write there, Kit
can't either.

Common cases:
- Writing to `/etc/`, `/var/`, `/usr/` — needs sudo, which Kit doesn't have. Use
  `~/dev_ws/...` paths.
- Writing to a mounted read-only filesystem (e.g., NVIDIA's S3-mounted asset library)
  — use `omniverse://localhost/` (own Nucleus) or local paths.

---

## When in doubt — the universal diagnostic chain

1. `get_scene_info` via MCP — does it return? If no, §1.
2. If yes but result is unexpected: `execute_script` to dump prim list:
   ```python
   import omni.usd
   stage = omni.usd.get_context().get_stage()
   for p in stage.Traverse():
       print(p.GetPath(), p.GetTypeName())
   ```
3. Read latest kit.log (via Bash) for errors.
4. If error is PhysX-related, defer to [[isaac-sim-bridge]] `physx-tuning.md` and
   `usd-from-urdf.md`.
5. If error is OG-related, [[isaac-sim-bridge]] `omnigraph-ros-bridge.md`.
6. If nothing matches → ask the user to send screenshot of `Window → Console` red
   lines, plus the last 30 lines of `tail -F` on the kit log.

---

## 9. execute_script dict 반환 → validation 에러 — **2026-05 코드에서 수정됨**

**증상(과거)**: `execute_script` 가 항상
`Error executing tool execute_script: 1 validation error ... result Input should be
a valid string [type=string_type, input_value={'status': '...', ...}]` 로 끝남.

**근본 원인**: `server.py` 의 `execute_script` 가 `-> str` 로 선언됐는데 Kit 측
dict 를 그대로 반환 → FastMCP/pydantic 이 string 검증 실패. 코드는 실행됐지만
반환값을 못 받아 매 호출 `/tmp` 파일 우회를 강제했음.

**수정 (적용됨)**: `isaac_mcp/server.py` 의 `execute_script` 가
`json.dumps(result, indent=2)` 문자열을 반환하도록 변경.
→ **이제 결과·status·traceback 이 반환값으로 직접 온다. `/tmp` 우회 불필요.**

**현재 규칙**:
- 수정된 빌드에서는 반환 JSON 의 `status`/`message`/`traceback` 을 그대로 신뢰.
- 여전히 `'status':'error'` 면 `traceback` 필드가 실제 원인 — 그걸 보고 고친다.
- 깔끔한 connection 에러면 Kit 미연결(§1) 또는 포트 다운(§10).

**레거시 폴백** (수정 안 된 구 빌드에서만): 결과를 `/tmp` 에 write 후 Bash `cat`.
수정된 빌드에선 이 우회를 **쓰지 말 것** — 왕복만 2배가 된다.

---

## 10. KIT_UP / PORT_DOWN — 서버 스레드 사망 (워치독이 자동복구)

**증상**: Kit 프로세스는 살아있는데 (`pgrep kit` 잡힘) 8766 포트가 닫힘
(`ss -ltn | grep 8766` 없음), 모든 MCP 호출이 connection refused / `'status':'error'`.
특히 **무거운 `omni.usd.get_context().open_stage()` 직후** 자주 발생.

**근본 원인**: 익스텐션 소켓 서버 스레드가 죽으면 과거엔 **자동 복구 로직이
전혀 없었다**. (추가로 `_start` 실패 시 `self.stop()` 오타 → AttributeError 가
진짜 에러를 가렸음.)

**수정 (적용됨, `extension.py`)**:
- Kit update 이벤트 구독 **워치독**: 3초마다 `socket`/`server_thread` 헬스 체크,
  죽었으면 `_restart_server()` 로 소켓 재바인드+스레드 재기동 (SO_REUSEADDR).
- `self.stop()` → `self._stop()` 오타 수정, `listen(1)`→`listen(5)`.
→ **이제 스레드가 어떤 이유로 죽어도 ~3초 내 자가 복구. PORT_DOWN 영구화 없음.**

**그래도 호출이 실패하면**:
1. 3~5초 기다린 뒤 1회 재시도 (워치독이 복구 중).
2. 그래도면 `tail kit 로그`에서 `MCP watchdog: ... restarting` 출현 확인.
3. 복구가 안 되면 Kit 자체 문제 → §1 진단 후 재기동.

**예방책 — `open_stage` 트리거 회피**:
- MCP `execute_script` 안에서 `open_stage()` 를 호출하지 말 것. 대신 **Isaac Sim
  을 씬 파일과 함께 기동**:
  ```bash
  setsid bash -c '<isaac-sim.sh> --ext-folder <mcp> \
    --enable isaac.sim.mcp_extension /path/to/scene.usd' </dev/null >log 2>&1 &
  ```
  기동 시 Kit 이 스테이지를 로드하므로 MCP open_stage 가 불필요 → 스레드 사망
  트리거 자체를 제거. (워치독이 있어도 이 패턴이 가장 안정적.)

---

## 11. execute_script 결과 처리 (성공인데 validation 에러)

소스빌드/특정 래퍼에서 `execute_script` 가 **코드는 정상 실행됐는데**
`pydantic ... Input should be a valid string ... {'status':'success',
'message':'Script executed successfully', 'result': None}` 로 반환되는
경우가 있다. inner `status` 로 판별:
- `status:'success'` → **코드 실행됨**(반환만 깨짐). 결과는 스크립트가
  `/tmp/xxx.txt` 에 write 하게 하고 **Bash 로 read** 해 확인.
- `status:'error'` → 실제 코드 예외(traceback 포함) → 그걸 디버그.
패턴: 모든 진단/검증 스크립트는 끝에 `open('/tmp/...','w').write(요약)` →
다음 턴에 `cat /tmp/...`. (verify 없이 write→write→write 금지.)

## 12. JSON parse 노이즈 — 무시

`Parsing error: [json.exception.parse_error.101] ... last read: 's'` 가
Isaac stdout/Console 에 무한 반복되면, 이는 `isaac.sim.mcp_extension`
소켓(8766)에 **Claude 가 띄운 MCP relay(또는 stale 연결)** 가 비-JSON 을
보내며 나는 노이즈. **시뮬/ROS/렌더와 무관, 무해.** 신경 쓰지 말 것
(정 거슬리면 relay 프로세스 정리 또는 mcp 확장 비활성).

종종 `[Error] [omni.usd-abi.plugin] IRenderSettings::getRenderSettings
failed getting a stage-id` 가 **1:1 로 끼어** 같이 폭주한다 — 같은
실패 왕복의 짝일 뿐 동일하게 무해.

**cobot3-isaacSim-gui / run_camera_pub*.sh 와 비양립**: 이들은
standalone `python.sh`(mcp 확장 미적재)다. isaac-sim MCP 서버가 동시에
떠 있으면 빈 8766 소켓을 계속 두드려 위 두 줄이 매 틱 폭주(무해하나
시끄러움). **근본조치(둘 중 하나)**: ① MCP 워크플로가 아니면 서버 비활성
`claude mcp remove "isaac-sim" -s user`(되돌리기 `claude mcp add isaac-sim
-s user -- <venv python> <isaac_mcp/server.py>`), ② MCP 가 필요하면
standalone 대신 `--enable isaac.sim.mcp_extension` 로 띄워 소켓에 정상
JSON 피어를 둔다. 증상 가림(로그 필터)은 지양 — 위 ①/②가 근본.

## 13. 기동 라이프사이클 (Bash 툴 환경 특성)

- `setsid bash -c '...isaac-sim.sh...' & disown` — Bash 툴 호출이 끝나면
  프로세스 그룹이 정리돼 **Isaac 이 동반 종료**될 수 있음(로그 미생성 = 신호).
- **GUI `isaac-sim.sh`** 를 harness `run_in_background` 로 띄우면 **DISPLAY
  부재로 즉시 exit 144**(출력 0B). GUI 는 **사용자가 직접** 프롬프트에서
  `! <런처>` 로 띄워야 함(사용자 X 세션 DISPLAY 사용).
- **headless `python.sh <script>`** 는 harness `run_in_background` 로 안정
  구동(렌더 필요 시 `SimulationApp({"headless":True,"renderer":...})` —
  headless 라도 render product 는 생성됨).
- MCP 준비 판정은 포트(8766)만으로 부족(릴레이가 항상 listen) — 로그에
  "MCP server started on localhost:8766" 또는 실제 `execute_script` 성공으로.

## 14. Isaac↔호스트 ROS2 가 안 보일 때

같은-PC 에서 Isaac 발행 토픽이 호스트 `ros2` 에 안 보이면 MCP/OG 문제가
아니라 **Isaac 번들 ROS2(빌드 Python) ↔ 시스템 ROS2 같은-호스트 DDS 불통**
(상세 [[isaac-sim-bridge]] `installation.md`). MCP 로 풀 수 없음 — **2-PC
LAN 또는 HTTP 직결 우회**로 전환(gp-quadruped `ros2-interop-and-bypass.md`).
