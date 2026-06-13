-- isaac-sim-bridge / warehouse conveyor sorting telemetry
-- Target: Supabase Postgres (works on plain Postgres 14+)
--
-- Apply via:
--   supabase db push                                   (Supabase CLI)
-- or:
--   psql "$SUPABASE_DB_URL" -f 0001_telemetry_schema.sql
--
-- This migration creates a 9-table event-sourcing schema for telemetry from
-- the Isaac Sim warehouse sorting scenario (multi m0609+RG2 robot arms,
-- conveyor, in-process YOLO, hand-coded sort decisions). Every event the
-- simulation emits — detections, sort decisions, cycle phases, joint
-- snapshots, collisions, failures, GPU metrics — lands in its own table,
-- keyed by robot_id + ts so per-robot debugging stays cheap.
--
-- The schema is OFF by default for RLS; activate the policies at the bottom
-- if this database is exposed beyond the internal tooling.

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────
-- 1. robots — registry of every simulated arm
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS robots (
    robot_id     TEXT PRIMARY KEY,                     -- e.g. 'r0', 'r1'
    model        TEXT NOT NULL,                        -- 'm0609'
    namespace    TEXT NOT NULL,                        -- ROS namespace, e.g. '/r0'
    location     TEXT,                                 -- 'conveyor_left_zone1' etc
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata     JSONB NOT NULL DEFAULT '{}'::JSONB
);

COMMENT ON TABLE robots IS
    'One row per simulated robot arm. Every event table FKs robot_id here.';

-- ─────────────────────────────────────────────────────────────────────────
-- 2. detections — every YOLO detection result (one row per object per frame)
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS detections (
    id              BIGSERIAL PRIMARY KEY,
    robot_id        TEXT NOT NULL REFERENCES robots(robot_id) ON DELETE CASCADE,
    ts              TIMESTAMPTZ NOT NULL,
    frame_seq       BIGINT NOT NULL,                   -- camera frame sequence id
    class_id        INT NOT NULL,                      -- YOLO class index
    class_name      TEXT NOT NULL,
    confidence      REAL NOT NULL,
    bbox_x          REAL NOT NULL,                     -- pixel coords, top-left
    bbox_y          REAL NOT NULL,
    bbox_w          REAL NOT NULL,
    bbox_h          REAL NOT NULL,
    depth_m         REAL,                              -- median depth inside bbox, nullable
    pose_x          REAL,                              -- estimated 3D pose in robot base frame
    pose_y          REAL,
    pose_z          REAL,
    pose_qx         REAL,
    pose_qy         REAL,
    pose_qz         REAL,
    pose_qw         REAL
);

CREATE INDEX IF NOT EXISTS idx_detections_robot_ts
    ON detections (robot_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_detections_class
    ON detections (class_id, ts DESC);

-- ─────────────────────────────────────────────────────────────────────────
-- 3. decisions — sort decision (which detection → which bin)
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS decisions (
    id              BIGSERIAL PRIMARY KEY,
    detection_id    BIGINT NOT NULL REFERENCES detections(id) ON DELETE CASCADE,
    robot_id        TEXT NOT NULL REFERENCES robots(robot_id) ON DELETE CASCADE,
    ts              TIMESTAMPTZ NOT NULL,
    target_bin      TEXT NOT NULL,                     -- 'bin_red', 'bin_reject', etc
    plan_id         UUID,                              -- cuMotion / MoveIt plan id
    rejected_reason TEXT,                              -- non-null if decision = skip
    notes           JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_decisions_robot_ts
    ON decisions (robot_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_detection
    ON decisions (detection_id);

-- ─────────────────────────────────────────────────────────────────────────
-- 4. cycles — pick&place cycle (one row per attempted pick)
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cycles (
    id              BIGSERIAL PRIMARY KEY,
    robot_id        TEXT NOT NULL REFERENCES robots(robot_id) ON DELETE CASCADE,
    detection_id    BIGINT REFERENCES detections(id) ON DELETE SET NULL,
    decision_id     BIGINT REFERENCES decisions(id) ON DELETE SET NULL,
    start_ts        TIMESTAMPTZ NOT NULL,
    pick_ts         TIMESTAMPTZ,                       -- gripper closed
    place_ts        TIMESTAMPTZ,                       -- gripper opened at bin
    end_ts          TIMESTAMPTZ,                       -- returned to home / next-ready
    success         BOOLEAN,                           -- NULL while in flight
    fail_reason     TEXT
);

CREATE INDEX IF NOT EXISTS idx_cycles_robot_start
    ON cycles (robot_id, start_ts DESC);
CREATE INDEX IF NOT EXISTS idx_cycles_outcome
    ON cycles (success, fail_reason);

-- ─────────────────────────────────────────────────────────────────────────
-- 5. cycle_events — fine-grained phase transitions inside a cycle
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cycle_events (
    id              BIGSERIAL PRIMARY KEY,
    cycle_id        BIGINT NOT NULL REFERENCES cycles(id) ON DELETE CASCADE,
    ts              TIMESTAMPTZ NOT NULL,
    event_type      TEXT NOT NULL,                     -- 'reached_pre_grasp', 'gripper_closed', 'lift_complete', 'place_reached', 'gripper_opened', 'retracted'
    payload         JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_cycle_events_cycle_ts
    ON cycle_events (cycle_id, ts);

-- ─────────────────────────────────────────────────────────────────────────
-- 6. joint_snapshots — periodic or phase-triggered joint state samples
-- ─────────────────────────────────────────────────────────────────────────
-- Stored as float8 arrays; m0609 has 6 joints + we record gripper width.
CREATE TABLE IF NOT EXISTS joint_snapshots (
    id              BIGSERIAL PRIMARY KEY,
    robot_id        TEXT NOT NULL REFERENCES robots(robot_id) ON DELETE CASCADE,
    cycle_id        BIGINT REFERENCES cycles(id) ON DELETE SET NULL,
    ts              TIMESTAMPTZ NOT NULL,
    q               DOUBLE PRECISION[] NOT NULL,       -- joint positions [rad]
    qd              DOUBLE PRECISION[],                -- joint velocities (nullable)
    tau             DOUBLE PRECISION[],                -- effort/torque (nullable; sim stub)
    gripper_width   REAL                               -- meters
);

CREATE INDEX IF NOT EXISTS idx_joint_snapshots_robot_ts
    ON joint_snapshots (robot_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_joint_snapshots_cycle
    ON joint_snapshots (cycle_id, ts);

-- ─────────────────────────────────────────────────────────────────────────
-- 7. collisions — PhysX contact events worth flagging (filtered)
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS collisions (
    id              BIGSERIAL PRIMARY KEY,
    robot_id        TEXT NOT NULL REFERENCES robots(robot_id) ON DELETE CASCADE,
    cycle_id        BIGINT REFERENCES cycles(id) ON DELETE SET NULL,
    ts              TIMESTAMPTZ NOT NULL,
    body_a          TEXT NOT NULL,                     -- USD prim path
    body_b          TEXT NOT NULL,
    impulse_n       REAL NOT NULL,                     -- magnitude in newton·sec
    contact_point   DOUBLE PRECISION[]                 -- [x,y,z] in world frame
);

CREATE INDEX IF NOT EXISTS idx_collisions_robot_ts
    ON collisions (robot_id, ts DESC);

-- ─────────────────────────────────────────────────────────────────────────
-- 8. failures — IK fail, grasp slip, timeout, OOM, etc.
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS failures (
    id              BIGSERIAL PRIMARY KEY,
    robot_id        TEXT REFERENCES robots(robot_id) ON DELETE CASCADE,  -- NULLable for sim-wide failures (GPU OOM)
    cycle_id        BIGINT REFERENCES cycles(id) ON DELETE SET NULL,
    ts              TIMESTAMPTZ NOT NULL,
    category        TEXT NOT NULL,                     -- 'ik_fail', 'plan_fail', 'grasp_slip', 'timeout', 'gpu_oom', 'controller_disconnect', etc
    message         TEXT NOT NULL,
    payload         JSONB NOT NULL DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_failures_robot_ts
    ON failures (robot_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_failures_category
    ON failures (category, ts DESC);

-- ─────────────────────────────────────────────────────────────────────────
-- 9. gpu_metrics — periodic GPU health (5s polling typical)
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gpu_metrics (
    id              BIGSERIAL PRIMARY KEY,
    ts              TIMESTAMPTZ NOT NULL,
    gpu_index       INT NOT NULL DEFAULT 0,
    used_mb         INT NOT NULL,
    total_mb        INT NOT NULL,
    util_pct        REAL,                              -- 0..100
    isaac_pid       INT
);

CREATE INDEX IF NOT EXISTS idx_gpu_metrics_ts
    ON gpu_metrics (ts DESC);

-- ─────────────────────────────────────────────────────────────────────────
-- Convenience views
-- ─────────────────────────────────────────────────────────────────────────

-- Per-robot per-day cycle summary (success rate, mean cycle time)
CREATE OR REPLACE VIEW v_cycle_summary AS
SELECT
    robot_id,
    date_trunc('day', start_ts) AS day,
    count(*)                                          AS attempts,
    count(*) FILTER (WHERE success IS TRUE)           AS successes,
    count(*) FILTER (WHERE success IS FALSE)          AS failures,
    avg(EXTRACT(EPOCH FROM (end_ts - start_ts)) * 1000) FILTER (WHERE end_ts IS NOT NULL)
                                                      AS mean_cycle_ms,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (end_ts - start_ts)) * 1000)
        FILTER (WHERE end_ts IS NOT NULL)             AS p95_cycle_ms,
    CASE WHEN count(*) > 0
         THEN count(*) FILTER (WHERE success IS TRUE)::REAL / count(*)::REAL
         ELSE NULL END                                AS success_rate
FROM cycles
GROUP BY robot_id, date_trunc('day', start_ts);

COMMENT ON VIEW v_cycle_summary IS
    'Per-robot per-day aggregate for dashboard / SLA tracking.';

-- Recent failures across all robots (last 24h)
CREATE OR REPLACE VIEW v_recent_failures AS
SELECT
    f.id,
    f.ts,
    f.robot_id,
    f.cycle_id,
    f.category,
    f.message
FROM failures f
WHERE f.ts > now() - INTERVAL '24 hours'
ORDER BY f.ts DESC;

-- ─────────────────────────────────────────────────────────────────────────
-- Realtime publication (Supabase-only; safe to skip on plain Postgres)
-- ─────────────────────────────────────────────────────────────────────────
-- Uncomment to push cycle/failure events to subscribed dashboards.
--
-- DO $$
-- BEGIN
--   IF EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'supabase_realtime') THEN
--     ALTER PUBLICATION supabase_realtime ADD TABLE cycles, failures, cycle_events;
--   END IF;
-- END$$;

-- ─────────────────────────────────────────────────────────────────────────
-- RLS — OFF by default (this is internal tooling)
-- ─────────────────────────────────────────────────────────────────────────
-- If exposing to authenticated users, copy and adapt the template below.
-- Assumption: each robot belongs to a tenant, and the auth claim
-- 'robot_ids' contains the list the user may read.
--
-- ALTER TABLE robots          ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE detections      ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE decisions       ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cycles          ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE cycle_events    ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE joint_snapshots ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE collisions      ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE failures        ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY robot_read_own ON robots FOR SELECT USING (
--   robot_id = ANY (string_to_array(auth.jwt() -> 'app_metadata' ->> 'robot_ids', ','))
-- );
-- (repeat similar policies for child tables, joining on robot_id)

COMMIT;
