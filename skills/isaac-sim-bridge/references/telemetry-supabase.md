# Telemetry to Supabase Postgres

**1문장 요지** — Isaac Sim warehouse 시뮬의 모든 detection/decision/cycle/joint snapshot/collision/failure/GPU 이벤트를 `db/migrations/0001_telemetry_schema.sql` 의 9-테이블 event-sourcing 스키마에 ROS 2 logger 노드가 batch insert 로 적재. 추후 디버깅·성능 점검·SLA 추적을 SQL 로 수행.

> 본 reference 는 **무엇을 어디에 적재하는지**와 logger 노드 패턴만 다룬다. Supabase 의 운영 정석 (RLS 정책 디자인, Auth 통합, Realtime 활성화 절차, CLI 사용) 은 `supabase` 스킬로 위임. 마이그레이션 적용은 §6 참조.

---

## Contents

1. 스키마 설계 원칙
2. 9개 테이블 요약 (D1~D9)
3. ROS 2 → Postgres logger 노드 패턴 (rclpy + asyncpg)
4. Batch insert vs Realtime 트레이드오프
5. 데이터 보존 정책
6. 마이그레이션 적용 (Supabase CLI / SQL editor)
7. 운영 쿼리 예시
8. RLS — 내부 도구 vs 외부 노출
9. 안티패턴
10. 교차 참조

---

## 1. 스키마 설계 원칙

본 스키마는 다음 원칙으로 설계됨:

| 원칙 | 적용 |
|---|---|
| **Event sourcing** | 모든 이벤트는 immutable row. UPDATE 없음, 새 row 만 INSERT. 시간 순서가 진실 |
| **robot_id + ts 인덱스 우선** | 가장 빈번한 쿼리 — "이 로봇이 X 시간 동안 뭐했나" — 가 0.5ms 안에 끝나야 함 |
| **외래키 cascade** | robot 삭제 시 child 모두 삭제. 단 cycle 삭제 시 joint_snapshots 는 SET NULL (분석 자료는 보존) |
| **JSON 페이로드 최소화** | 자주 필터/조회되는 필드는 컬럼으로, 가변 metadata 만 jsonb |
| **Append-only 가정** | 마지막에 도착한 detection 이 가장 최근. 시간 역행 거부 (logger 가 timestamp 정렬 가정) |

`db/migrations/0001_telemetry_schema.sql` 본문이 1차 자료. 표는 그 SQL 의 요약.

---

## 2. 9개 테이블 요약

| 테이블 | 키 컬럼 | 기록 시점 | 빈도 (4 로봇) |
|---|---|---|---|
| `robots` | robot_id (PK) | bringup 1회 | 4 rows total |
| `detections` | id, robot_id, ts | 매 YOLO 결과 (객체당 1 row) | ~30Hz × 평균 2 객체 = 60 rows/s |
| `decisions` | id, detection_id, robot_id, ts | FSM `PLAN` 진입 | ~로봇당 1Hz, 합 4 rows/s |
| `cycles` | id, robot_id, start_ts | FSM `IDLE → PLAN` (1 row 이후 UPDATE 로 닫음) | 4Hz, but UPDATE 패턴 — §3 주의 |
| `cycle_events` | id, cycle_id, ts | 모든 FSM 상태 전환 | 사이클당 ~7건, 합 28 rows/s |
| `joint_snapshots` | id, robot_id, ts | 100ms 주기 또는 phase 전환 | 4 × 10Hz = 40 rows/s |
| `collisions` | id, robot_id, ts | contact threshold 초과 시 | sparse (~1/min 정상) |
| `failures` | id, robot_id, ts | 예외 발생 시 | sparse (~1/min 정상) |
| `gpu_metrics` | id, ts | 5초 주기 polling | 0.2 rows/s |

**총량 추정** (4 로봇, 정상 운영): ~135 rows/s ≈ 12M rows/day. 인덱스 포함 1일 약 1~2GB. 보존 90일 가정 시 90~180GB. supabase 의 적정 plan 또는 자체 호스팅 Postgres + S3 cold storage 필요.

---

## 3. ROS 2 → Postgres logger 노드 패턴

핵심 디자인: **rclpy node 가 ROS 토픽 subscribe → asyncio.Queue → asyncpg batch INSERT**. rclpy executor 스레드와 asyncpg 의 asyncio loop 를 분리.

```python
import asyncio, threading, rclpy, asyncpg, os
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
from sensor_msgs.msg import JointState

DB_URL = os.environ["SUPABASE_DB_URL"]            # postgres://...
BATCH_SIZE = 100
FLUSH_INTERVAL_SEC = 1.0

class TelemetryLogger(Node):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__("telemetry_logger")
        self.loop = loop
        self.queues = {
            "detections": asyncio.Queue(maxsize=10_000),
            "joint_snapshots": asyncio.Queue(maxsize=10_000),
            ...
        }
        # 모든 robot 의 namespace 를 wildcard 로 subscribe (rclpy 1.x 는 직접 지원 안 함)
        # → robot_id 리스트를 파라미터로 받아 명시적으로 subscribe
        for rid in self.declare_parameter("robot_ids", ["r0","r1","r2","r3"]).value:
            self.create_subscription(Detection2DArray,
                f"/{rid}/yolo/detections",
                lambda m, rid=rid: self._enqueue_detection(rid, m), 10)
            self.create_subscription(JointState,
                f"/{rid}/joint_states",
                lambda m, rid=rid: self._enqueue_joint(rid, m), 10)
        # 100ms 주기 joint_snapshot 은 별도 timer 로 (latest joint_state cache 활용)

    def _enqueue_detection(self, rid, msg):
        for det in msg.detections:
            row = (rid, msg.header.stamp, det.results[0].hypothesis.class_id,
                   ..., det.bbox.center.position.x, det.bbox.center.position.y,
                   det.bbox.size_x, det.bbox.size_y)
            # rclpy callback (executor thread) → asyncio loop 로 안전 푸시
            asyncio.run_coroutine_threadsafe(
                self.queues["detections"].put(row), self.loop)


async def flush_loop(pool, queue, table, columns):
    while True:
        batch = []
        try:
            row = await asyncio.wait_for(queue.get(), timeout=FLUSH_INTERVAL_SEC)
            batch.append(row)
            while len(batch) < BATCH_SIZE and not queue.empty():
                batch.append(queue.get_nowait())
        except asyncio.TimeoutError:
            continue
        if not batch:
            continue
        async with pool.acquire() as conn:
            await conn.copy_records_to_table(table, records=batch, columns=columns)


async def main_async():
    pool = await asyncpg.create_pool(DB_URL, min_size=2, max_size=10)
    rclpy.init()
    loop = asyncio.get_running_loop()
    node = TelemetryLogger(loop)

    # ROS executor 를 별도 스레드에서
    def spin():
        rclpy.spin(node)
    threading.Thread(target=spin, daemon=True).start()

    await asyncio.gather(
        flush_loop(pool, node.queues["detections"],     "detections",     [...]),
        flush_loop(pool, node.queues["joint_snapshots"], "joint_snapshots", [...]),
        # 각 테이블 1개씩
    )

if __name__ == "__main__":
    asyncio.run(main_async())
```

**왜 copy_records_to_table** — asyncpg 의 `executemany` 보다 `COPY` 가 batch insert 시 ~10× 빠름. 100건 묶음으로 1초마다 plush 하면 60+ rows/s 의 detection 도 여유 있게 처리.

**cycles 의 UPDATE 처리** — cycle 은 시작 시 INSERT 후, place_ts/end_ts/success 갱신은 UPDATE. event sourcing 원칙에 맞춰 가려면 별도 `cycle_outcomes` 테이블로 분리 가능하지만, 본 스킬은 단순화를 위해 UPDATE 허용. logger 노드가 cycle_id 를 메모리에 유지해 한 cycle 동안 같은 row 를 갱신.

자료실 `11-warehouse-sorting/rosbridge-fastapi/ros2_asyncio/` 의 패턴이 rclpy ↔ asyncio bridge 의 참고.

---

## 4. Batch insert vs Realtime 트레이드오프

| 옵션 | 지연 (detect → DB) | 비용 | 권장 |
|---|---|---|---|
| Per-row INSERT | <50ms | Postgres connection 부하 큼, ~200 rows/s 한계 | 디버그 시만 |
| Batch INSERT (본 권장) | 0~1초 (FLUSH_INTERVAL) | 가장 효율적 | 정상 운영 |
| Supabase Realtime broadcast (subscribed clients) | ~100ms | logical replication 사용, 부하 ↑ | 외부 dashboard 가 실시간 보아야 할 때만 |

본 시나리오: **batch insert** 가 기본, Realtime 은 옵션. `cycles`, `failures`, `cycle_events` 만 Realtime publication 에 추가 (SQL 의 주석 처리된 ALTER PUBLICATION 부분).

```sql
alter publication supabase_realtime add table cycles, failures, cycle_events;
```

이렇게 두면 server-bridge 의 WS `/events` 가 supabase 클라이언트 SDK 로 직접 구독 가능 (rosbridge subscribe 대신).

---

## 5. 데이터 보존 정책

| 테이블 | 보존 기간 (권장) | 이유 |
|---|---|---|
| `robots` | 영구 | 메타데이터 |
| `detections` | 30일 | 분량 큼, 30일 이상 retro 분석은 sampled snapshot 으로 충분 |
| `decisions` | 90일 | 분류 정책 점검 |
| `cycles`, `cycle_events` | 1년 | SLA / 성능 회귀 분석 핵심 |
| `joint_snapshots` | 14일 | 가장 분량 큼, 장기 분석 시 down-sampling |
| `collisions`, `failures` | 1년 | 사후 분석 |
| `gpu_metrics` | 30일 | 추이 충분 |

cron / pg_partman / supabase scheduled function 으로 retention 자동화:

```sql
-- 예: 30일 지난 detections 삭제 (cascade 로 decisions 와 cycles 의 detection_id 는 SET NULL)
DELETE FROM detections WHERE ts < now() - INTERVAL '30 days';
```

대안: 월별 파티셔닝 (`pg_partman`) + 오래된 파티션 detach + parquet export. 본 스킬 범위 밖 — `supabase` 스킬과 통합 시 가이드.

---

## 6. 마이그레이션 적용

세 가지 방법:

### 6.1 Supabase CLI (권장)

```bash
# 프로젝트 디렉토리에서
supabase migration new telemetry_schema    # 파일 생성 prompt
# 본 스킬의 0001_telemetry_schema.sql 내용을 그 파일로 복사
supabase db push                            # 적용
```

### 6.2 SQL editor (Supabase Dashboard)

Dashboard → SQL Editor → 본 SQL 붙여넣기 → Run.
주의: Dashboard 는 SQL 을 단일 트랜잭션으로 감싸므로 `CREATE INDEX CONCURRENTLY` 불가 — 본 스킬의 0001 은 일반 CREATE INDEX 만 사용해 호환됨.

### 6.3 직접 psql

```bash
psql "$SUPABASE_DB_URL" -f db/migrations/0001_telemetry_schema.sql
```

검증 dry-run (실제 DB 변경 없이 syntax 만):

```bash
psql "$SUPABASE_DB_URL" -c "BEGIN; \i db/migrations/0001_telemetry_schema.sql; ROLLBACK;"
```

`supabase` 스킬의 가이드를 따라 CLI 셋업.

---

## 7. 운영 쿼리 예시

### 특정 로봇의 사이클 시간 분포 (지난 24h)

```sql
SELECT
    percentile_cont(0.5)  WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (end_ts - start_ts))*1000) AS p50_ms,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (end_ts - start_ts))*1000) AS p95_ms,
    avg(EXTRACT(EPOCH FROM (end_ts - start_ts))*1000) AS mean_ms,
    count(*) FILTER (WHERE success) AS successes,
    count(*) FILTER (WHERE NOT success) AS failures
FROM cycles
WHERE robot_id = 'r0' AND start_ts > now() - INTERVAL '24 hours' AND end_ts IS NOT NULL;
```

### 실패 원인별 분포

```sql
SELECT category, count(*) AS occurrences
FROM failures
WHERE ts > now() - INTERVAL '24 hours'
GROUP BY category
ORDER BY occurrences DESC;
```

### GPU 메모리 추세

```sql
SELECT date_trunc('minute', ts) AS minute,
       max(used_mb) AS peak_mb,
       avg(used_mb) AS mean_mb
FROM gpu_metrics
WHERE ts > now() - INTERVAL '1 hour'
GROUP BY minute
ORDER BY minute;
```

### 특정 cycle 의 joint trajectory (offline replay 입력)

```sql
SELECT ts, q, qd
FROM joint_snapshots
WHERE cycle_id = 12345
ORDER BY ts;
```

`scripts/replay_telemetry.py` 가 이 쿼리를 사용.

### 컨베이어 zone 별 detection 분포

```sql
SELECT robot_id, class_name, count(*)
FROM detections
WHERE ts > now() - INTERVAL '1 hour'
GROUP BY robot_id, class_name
ORDER BY robot_id, count(*) DESC;
```

---

## 8. RLS — 내부 도구 vs 외부 노출

기본은 **OFF** — 본 스킬은 내부 도구 가정. server-bridge 가 API key 로 인증, supabase 직접 노출 안 함.

외부에 노출할 경우 (예: 고객용 dashboard):

```sql
-- 1) 테이블별 RLS 활성화
ALTER TABLE robots ENABLE ROW LEVEL SECURITY;
ALTER TABLE detections ENABLE ROW LEVEL SECURITY;
-- ... (event 테이블 전체)

-- 2) auth.users 에 robot_ids 클레임 (예: ['r0','r1'])
-- 3) 각 테이블에 정책
CREATE POLICY robot_read_own ON robots FOR SELECT
USING (robot_id = ANY (
    string_to_array(auth.jwt() -> 'app_metadata' ->> 'robot_ids', ',')
));
-- detections, decisions, cycles 등은 robot_id 컬럼 기반 동일 패턴
```

정식 운영 디자인은 `supabase` 스킬로 위임. 본 스킬 SQL 의 RLS 섹션은 주석으로 템플릿만 둠.

---

## 9. 안티패턴

- ❌ Logger 노드가 ROS callback 안에서 직접 INSERT — executor 스레드 blocking, ROS callback 지연 ↑
- ❌ Per-row INSERT — Postgres 연결 부하, 운영 중 OOM 가능
- ❌ joint_snapshots 를 모든 frame 마다 적재 (60Hz × 4 = 240 rows/s) — 디스크 폭증. 100ms 또는 phase 전환 시만
- ❌ jsonb 안에 자주 조회되는 필드를 넣음 — 인덱싱 비효율, 정렬 어려움
- ❌ retention policy 없이 운영 — 1년 후 DB 비대로 마이그레이션 비싸짐
- ❌ RLS 활성화하면서 server-bridge 의 service_role key 사용 — RLS 우회됨, 의도와 반대
- ❌ Realtime publication 에 detections (60 rows/s) 추가 — broadcast 부하 폭증

---

## 10. 교차 참조

- `db/migrations/0001_telemetry_schema.sql` — 본 reference 의 1차 자료
- `warehouse-sorting-pipeline.md §7` — 충돌 이벤트 정의
- `sort-decision-logic.md §2` — cycle / cycle_events 발생 위치
- `yolo-perception.md §5` — detection 발생 위치
- `server-bridge.md §7` — Prometheus 메트릭 vs supabase 쿼리 선택
- `replay_telemetry.py` (scripts/) — 본 reference 의 쿼리를 사용하는 도구
- 외부: `supabase` 스킬 전반, `supabase:supabase-postgres-best-practices` (인덱스/쿼리 최적화)
