# Server Bridge — REST + WebSocket on top of ROS 2

**1문장 요지** — Isaac Sim warehouse 시뮬레이션의 ROS 2 토픽/서비스/액션을 외부 dashboard·operator 콘솔·외부 마이크로서비스에서 사용할 수 있도록 FastAPI 프로세스 + rosbridge_suite 를 결합해 노출하는 패턴을 정의한다. 32개 통신 기능 (`warehouse-sorting-pipeline.md` §3) 중 E1~E9 가 이 reference 의 범위.

> **본 스킬은 아키텍처와 ROS↔HTTP 매핑 패턴만 다룬다.** 보안 정석 (OAuth2/SSO) 은 supabase Auth 의 활용 방법으로 위임. ROS 2 미들웨어 정석 (QoS, executors, lifecycle) 은 `ros2-architect` 위임.

---

## Contents

1. 아키텍처 (FastAPI + rosbridge_suite 의 분담)
2. 엔드포인트 매핑 표 (E1~E9 ↔ ROS 2)
3. FastAPI + rclpy 동시 실행 패턴
4. WebSocket 이벤트 스트림
5. 인증 (간이 API key + CORS)
6. 에러 매핑 (ROS error → HTTP)
7. Prometheus exposition (`/metrics`)
8. Launch 통합
9. 보안 주의사항
10. 안티패턴
11. 교차 참조

---

## 1. 아키텍처 — FastAPI + rosbridge_suite 의 분담

| 컴포넌트 | 역할 | 왜 분리 |
|---|---|---|
| **rosbridge_suite (rosbridge_server)** | 표준 ROS 2 ↔ JSON/WebSocket 게이트웨이. 토픽 subscribe/publish, 서비스 호출을 JSON 메시지로 변환 | "투명한 ROS API" — 모든 토픽이 디폴트로 노출됨. 디버깅 도구, dashboard 의 raw 데이터 스트림에 적합 |
| **FastAPI 게이트웨이** | 비즈니스 의미 부여 — 라우팅, 권한 검사, 에러 매핑, Prometheus 집계, OpenAPI 문서화 | rosbridge 가 노출 못 하는 보안/도메인 로직을 캡슐화. 외부 클라이언트가 보는 API 표면 |

두 컴포넌트의 트래픽:

```
   external client
        │
        ▼ HTTP / WS
   ┌─────────────────────────────┐
   │  FastAPI  (REST + WS)       │  ← 비즈니스 API
   └─────┬──────────────┬────────┘
         │ rclpy        │ ws:9090
         ▼              ▼
   ┌─────────────────┐  ┌─────────────────┐
   │  rclpy executor │  │ rosbridge_server│  ← 표준 ROS bridge (raw)
   │  (custom node)  │  └─────────────────┘
   └─────────────────┘            │
         │                        │ ROS 2 (DDS)
         ▼                        ▼
   ┌─────────────────────────────────────┐
   │  Isaac Sim (OG ROS 2 publishers /   │
   │  Sort decision nodes / Loggers)     │
   └─────────────────────────────────────┘
```

**권장**: 본 시나리오는 *비즈니스 의미가 있는 API* 가 핵심 → FastAPI 가 1차. rosbridge 는 옵션 (dashboard 가 ROS 표준 클라이언트 라이브러리를 쓰면 추가).

자료실 `/home/hoon/isaac-sim-skill-research/11-warehouse-sorting/rosbridge-fastapi/rosbridge_suite/` 와 `m2-farzan/ros2-asyncio` 참조.

---

## 2. 엔드포인트 매핑 표

| # | 외부 API | 메소드 + path | 내부 ROS 2 매핑 | 비고 |
|---|---|---|---|---|
| E1 | 로봇 목록 | `GET /robots` | (서비스) `/sim/list_robots` 또는 supabase `robots` 테이블 조회 | active/heartbeat 정보는 캐시된 latest joint_state 의 ts 로 추정 |
| E2 | 로봇 스냅샷 | `GET /robots/{id}/state` | (subscribe) `/{id}/joint_states` 의 latest + `/{id}/robot_state` + 최근 detection (supabase) | 캐시 1초 TTL |
| E3 | 최근 detection | `GET /robots/{id}/recent-detections?since=ISO` | supabase `detections` 테이블 SELECT | `since` 기본값 5초 |
| E4 | 모드 변경 | `POST /robots/{id}/mode` body `{mode}` | (서비스 호출) `/{id}/mode/set` | mode ∈ {manual, auto, maintenance} |
| E5 | 모션 abort | `POST /robots/{id}/preempt` | (서비스 호출) `/{id}/motion/abort` | 즉시, 응답 std_srvs/Trigger |
| E6 | 이벤트 스트림 | `WS /events` | subscribe `/{*}/yolo/detections`, `/cycle_events`, `/contact_events`, `/diagnostics` | 클라이언트가 `robot_id` filter 가능 |
| E7 | 사이클 쿼리 | `GET /telemetry/cycles?robot_id=&since=&until=` | supabase view `v_cycle_summary` SELECT | 페이지네이션 |
| E8 | 메트릭 (Prom) | `GET /metrics` | prometheus_client registry (cycle_time, throughput, gpu_mem 등) | scrape 호환 |
| E9 | Scene preview | `GET /scene/snapshot.jpg` | subscribe `/conveyor/cam/image_raw` 의 latest, JPEG 인코딩 | 1FPS rate limit |

추가:
| - | 헬스체크 | `GET /healthz` | ROS 노드 alive + supabase ping | k8s 호환 |
| - | OpenAPI docs | `GET /docs` (FastAPI 자동) | — | dev 환경 only |

---

## 3. FastAPI + rclpy 동시 실행 패턴

FastAPI 는 asyncio 이벤트 루프, rclpy 는 자체 executor. 두 루프를 한 프로세스에서 안전히 돌리는 방법.

### 방법 A — MultiThreadedExecutor 전용 스레드 (권장)

```python
import threading, rclpy
from rclpy.executors import MultiThreadedExecutor
from fastapi import FastAPI

app = FastAPI()
rclpy.init()
node = ServerBridgeNode()                     # rclpy 노드 (subscribers, service clients)
executor = MultiThreadedExecutor(num_threads=4)
executor.add_node(node)

def spin_ros():
    executor.spin()

ros_thread = threading.Thread(target=spin_ros, daemon=True)

@app.on_event("startup")
async def startup():
    ros_thread.start()

@app.on_event("shutdown")
async def shutdown():
    executor.shutdown()
    rclpy.shutdown()
```

쓰레드 안전성: rclpy 의 publisher/subscriber callback 은 ROS executor 스레드에서 실행. FastAPI 핸들러는 asyncio 스레드. 둘이 공유하는 자료구조 (예: latest joint state cache) 는 `threading.Lock` 또는 `asyncio.Queue` 로 보호.

### 방법 B — asyncio.run_in_executor (단순)

```python
@app.get("/robots/{rid}/state")
async def state(rid: str):
    loop = asyncio.get_running_loop()
    snap = await loop.run_in_executor(None, lambda: node.get_state_blocking(rid, timeout=0.5))
    return snap
```

단점: rclpy 서비스 호출이 동기 wait — FastAPI 의 동시성 슬롯 점유.

### 방법 C — rclpy AsyncIO bridge (m2-farzan/ros2-asyncio)

`11-warehouse-sorting/rosbridge-fastapi/ros2_asyncio` 의 패턴. rclpy futures 를 asyncio.Future 로 wrap. FastAPI 핸들러 안에서 `await client.call_async(req)` 가 자연스럽게 동작.

```python
from ros2_asyncio import RosAsyncIO

ros = RosAsyncIO(node)

@app.post("/robots/{rid}/preempt")
async def preempt(rid: str):
    req = std_srvs.srv.Trigger.Request()
    res = await ros.call_service(f"/{rid}/motion/abort", req, timeout=1.0)
    if not res.success:
        raise HTTPException(409, res.message)
    return {"ok": True}
```

권장: **방법 A + 방법 C 조합**. 캐시는 ROS thread 가 채워두고, 비동기 호출은 ros2_asyncio 로.

---

## 4. WebSocket 이벤트 스트림

`WS /events` 가 push 하는 이벤트 유형:

| 이벤트 | 트리거 | 페이로드 |
|---|---|---|
| `detection` | `/{*}/yolo/detections` | `{robot_id, ts, class_name, confidence, bbox, pose}` |
| `cycle_event` | `/cycle_events` 토픽 또는 supabase trigger | `{robot_id, cycle_id, event_type, ts}` |
| `failure` | `/failures` | `{robot_id, category, message, ts}` |
| `collision` | `/{*}/contact_events` (severity ≥ medium) | `{robot_id, body_a, body_b, impulse}` |
| `mode_change` | `/{*}/mode/set` ack | `{robot_id, from, to}` |

구현:

```python
from fastapi import WebSocket
import asyncio

active_ws: set[WebSocket] = set()

@app.websocket("/events")
async def events_ws(ws: WebSocket, robot_id: str | None = None):
    await ws.accept()
    active_ws.add(ws)
    try:
        while True:
            ev = await event_queue.get()                   # asyncio.Queue
            if robot_id and ev.get("robot_id") != robot_id:
                continue
            await ws.send_json(ev)
    except WebSocketDisconnect:
        active_ws.discard(ws)

# ROS subscriber callback (executor thread)
def on_detection(msg):
    for det in msg.detections:
        ev = {"type": "detection", "robot_id": ..., "ts": ..., ...}
        # ROS thread → asyncio: loop.call_soon_threadsafe(queue.put_nowait, ev)
        asyncio.run_coroutine_threadsafe(event_queue.put(ev), main_loop)
```

**backpressure**: `event_queue` 가 가득 차면 oldest drop. `asyncio.Queue(maxsize=10_000)`. 1만 이상 쌓이면 dashboard 가 느리거나 비정상 — failure 로 간주.

---

## 5. 인증 (간이 API key + CORS)

본 스킬은 **내부 도구** 가정. 정식 OAuth/SSO 는 supabase Auth 로 별도 통합 (`telemetry-supabase.md §RLS 정책`).

```python
from fastapi import Depends, Header, HTTPException

API_KEY = os.environ["ISAAC_SIM_API_KEY"]   # launch 에서 주입

def verify_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(403, "invalid api key")

@app.post("/robots/{rid}/mode", dependencies=[Depends(verify_key)])
async def set_mode(rid: str, body: dict):
    ...
```

읽기 전용 GET 은 key 없이 허용 (내부 dashboard 단순화), **상태 변경 POST 는 반드시 key 요구** — 비대칭 정책.

CORS:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ALLOWED", "*").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)
```

운영 시 `*` 금지 — 명시적 origin 리스트.

---

## 6. 에러 매핑 (ROS error → HTTP)

| ROS 결과 | HTTP 상태 | 의미 |
|---|---|---|
| Service `success=true` | 200 | 정상 |
| Service `success=false`, message includes "already" | 409 Conflict | 이미 같은 상태 |
| Service `success=false`, message includes "not_found" | 404 | 잘못된 robot_id 등 |
| Service `success=false`, other | 422 Unprocessable | 일반 실패 |
| Service timeout (rclpy `call_async` 미응답) | 504 Gateway Timeout | 노드 응답 없음 |
| Action 의 ABORTED | 409 | 충돌, 강제 abort 등 |
| Action 의 REJECTED | 422 | goal 검증 실패 |

이 매핑은 `references` 코드 작성 시 상수로 표현하고 `dependencies=[Depends(handle_ros_errors)]` 같은 데코레이터로 일관 처리.

---

## 7. Prometheus exposition (`/metrics`)

```python
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app

CYCLE_DURATION = Histogram("isaac_sim_cycle_ms", "cycle duration",
                           labelnames=["robot_id", "outcome"],
                           buckets=(100, 200, 400, 800, 1600, 3200, 6400))
DETECTIONS = Counter("isaac_sim_detections_total", "yolo detections",
                     labelnames=["robot_id", "class_name"])
GPU_USED_MB = Gauge("isaac_sim_gpu_used_mb", "gpu memory used")

# /metrics 라우트 부착
app.mount("/metrics", make_asgi_app())
```

ROS subscriber 콜백에서 metric 갱신 (다른 스레드, prometheus_client 는 스레드 안전). Grafana 대시보드가 표준 PromQL 로 scrape.

---

## 8. Launch 통합

ros2-architect `references/launch-system.md` 패턴.

```python
# server_bridge/launch/bridge.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        # 1. rosbridge_server (선택)
        Node(package="rosbridge_server", executable="rosbridge_websocket",
             parameters=[{"port": 9090}]),

        # 2. FastAPI 게이트웨이
        ExecuteProcess(
            cmd=["uvicorn", "server_bridge.app:app", "--host", "0.0.0.0", "--port", "8000"],
            env={"ISAAC_SIM_API_KEY": "...", "SUPABASE_DB_URL": "..."},
        ),
    ])
```

운영 시 systemd unit 또는 docker compose 가 더 자연스러움 — 본 스킬은 launch 통합 예시까지만.

---

## 9. 보안 주의사항

- **모드 전환은 항상 API key 보호** — 외부에서 `maintenance` 로 잠그면 자동 운영 중단됨. 의도된 운영자만 호출 가능해야 함
- **mod=manual 로 전환된 상태에서 motion command 는 reject** — server bridge 가 굳이 막을 필요 없이 ROS 측 controller 가 reject 하면 됨 (doosan-robotics `launch-and-modes.md §mode` 와 일관)
- **camera image 노출은 의도된 dashboard 만** — `/scene/snapshot.jpg` 는 1FPS rate limit + API key 보호
- **WS `/events` 는 read-only** — write 요청을 받지 않음. abort/mode 는 별도 POST 라우트로만
- **Supabase 직접 노출 금지** — RLS 정책이 있어도 server bridge 가 게이트웨이로 항상 중간에 둠 (필터/감사 로깅)

---

## 10. 안티패턴

- ❌ ROS topic 을 rosbridge_server 만으로 전부 노출 + dashboard 가 직접 service call — 권한 일관 적용 불가, 감사 불가
- ❌ FastAPI 핸들러 안에서 rclpy node 를 매번 새로 생성 — DDS discovery 부담 폭발
- ❌ ROS callback 안에서 직접 `requests.post(...)` 호출 — executor 스레드 blocking, 다른 callback 까지 멈춤
- ❌ WS broadcast 큐 unbounded — 클라이언트가 느리면 메모리 풀까지 폭증
- ❌ CORS `allow_origins=["*"]` 운영 환경에서 사용
- ❌ API key 가 코드/launch 파일에 평문 — env 또는 secret store

---

## 11. 교차 참조

- `warehouse-sorting-pipeline.md §3` — namespacing (URL path 의 `{robot_id}` 대응)
- `sort-decision-logic.md §9` — abort/preempt 의 내부 동작
- `telemetry-supabase.md §쿼리 예시` — E3, E7 의 supabase view 활용
- `yolo-perception.md §5` — E6 WS event 의 detection 페이로드
- 외부: ros2-architect `references/communication.md §QoS` (subscribe 시 QoS 매칭), ros2-architect `references/launch-system.md`, supabase 스킬 (Auth/RLS)
- 자료: `11-warehouse-sorting/rosbridge-fastapi/rosbridge_suite/`, `11-warehouse-sorting/rosbridge-fastapi/ros2_asyncio/`
