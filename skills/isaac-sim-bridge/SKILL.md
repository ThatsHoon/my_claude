---
name: isaac-sim-bridge
description: >
  Use this skill whenever the user works on NVIDIA Isaac Sim, Isaac Lab, Isaac ROS, or
  Omniverse — importing URDF/MJCF/xacro into a USD/PhysX simulator, authoring USD scenes,
  building OmniGraph/Action Graph for ROS 2 sensor publishing (camera, lidar, IMU, TF,
  JointState) or debugging missing ROS 2 topics from Isaac Sim, training reinforcement
  learning policies in Isaac Lab (Manager-based vs Direct env, PPO/SAC, thousands of
  GPU-parallel environments, asymmetric actor-critic), generating synthetic data with
  Replicator (domain randomization of textures, lighting, materials, friction, mass per
  reset), tuning PhysX 5 (articulation drives, solver iterations, contact/friction,
  TGS vs PGS), accelerating perception/planning with Isaac ROS (NITROS zero-copy,
  cuMotion, cuRobo, isaac_ros_visual_slam, Isaac Manipulator), closing a sim-to-real
  gap on a manipulator (policy works in sim but fails on real robot), or planning an
  end-to-end pipeline that trains a policy in simulation and deploys it on a physical
  robot (URDF→USD conversion → Isaac Lab RL training → real-robot deployment via vendor
  controllers like dsr_controller2, ros2_control, franka_ros2). Also trigger when the
  user describes any workflow that combines a simulator + real robot for the same arm
  (UR, Franka, Doosan m0609, etc.) regardless of whether they name "Isaac" explicitly.
  Trigger on terms:
  isaac sim, isaacsim, isaac lab, isaaclab, isaac ros, omniverse, omnigraph, action
  graph, usd, openusd, urdf importer, mjcf importer, replicator, sdg, sim2real,
  sim-to-real, domain randomization, physx, articulation, joint drive, cumotion, curobo,
  nitros, isaac manipulator, kit app, kit extension. Also Korean: 아이작 심, 아이작 랩,
  옴니버스, 옴니그래프, 도메인 랜덤화, 합성 데이터, 정책 학습, GPU 모션 플래너, Jetson
  배포. Trigger even when the user does not say "Isaac" if the scenario fits — e.g. a
  USD/PhysX simulator with thousands of GPU-parallel envs, or a policy that succeeds in
  sim but fails on the real arm. Covers Isaac Sim 5.x/6.x, Isaac Lab main, Isaac ROS DP
  and GA. Defer ROS 2 middleware (QoS, executors, rclpy, lifecycle, launch) to
  `ros2-architect`, and Doosan m0609 vendor APIs (DRL, DRFL, dsr_controller2,
  servoj_rt_stream) to `doosan-robotics`.
license: Apache-2.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, WebFetch]
---

# Isaac Sim Bridge Skill

A deep, opinionated guide to building, debugging, and shipping robotics systems on
NVIDIA Isaac Sim — covering the simulator itself, the satellite stack (OmniGraph, USD,
Isaac Lab, Replicator, PhysX, Isaac ROS), and the sim-to-real handoff. The body of this
file is the **decision router and core mental model**. Detailed patterns, code, and
anti-patterns live in `references/<topic>.md`. Read the relevant reference file before
writing non-trivial code — the body alone is intentionally too thin to copy-paste from.

## How to use this skill

1. **Identify the task category** in the Decision Router below. Most Isaac Sim tasks
   fall into one of seven buckets — installation, ROS 2 bridge / OmniGraph, URDF→USD
   import, Isaac Lab RL, Replicator SDG, PhysX tuning, Isaac ROS acceleration.
2. **Read the matching reference file**. Each reference is self-contained: TOC, working
   code, anti-patterns, and links to the relevant Isaac Sim docs page (mirrored locally
   under `/home/hoon/isaac-sim-skill-research/`).
3. **Apply the core mental model** (next section) regardless of category. These are the
   invariants that make the difference between "the demo runs" and "the policy
   transfers to the real robot."
4. **For ROS 2 plumbing or vendor-specific motion APIs**, defer to `ros2-architect` and
   `doosan-robotics` respectively. This skill stays inside the simulator and the
   Omniverse-side acceleration stack.

## Core mental model — the things that matter on every Isaac Sim task

These six ideas come up in nearly every reference. Internalize them first.

### 1. Isaac Sim is four engines stitched together — know which one is failing

Isaac Sim = **Kit application shell** + **Omniverse runtime** (USD composition,
hydra rendering pipeline) + **RTX renderer** + **PhysX 5 simulator**. When something
breaks, the first diagnostic is *which layer*:

- **Black viewport / no render**: RTX or GPU driver. Check `nvidia-smi`, the Kit log
  for `[carb.graphics-vulkan]` errors, and whether `--/renderer/enabled=rtx` is set.
- **Robot loaded but no motion**: PhysX. Check the `Physics Inspector` tab, look for
  `articulation root` warnings, verify joint drives are enabled.
- **OmniGraph node fires but no ROS topic**: Omniverse runtime did not propagate the
  attribute change. Check `Action Graph` window for a red node and the Console
  (Window → Console) for `[omni.graph]` errors.
- **Kit crashes on startup**: extension loading order. Read `~/.local/share/ov/data/Kit/.../kit_*.log`.

This four-layer split also explains why **`ros2 topic list` showing no topics is not
the same as "the bridge is broken"** — the ROS bridge extension may be loaded but no
Action Graph yet wired. See `omnigraph-ros-bridge.md` §"Did the bridge actually
publish?".

### 2. USD is the source of truth — URDF/MJCF are throwaway intermediates

The instant you finish importing a URDF, **the URDF is dead to you**. Every
modification — joint limits, drive gains, masses, collision meshes, sensor
attachments — happens on the USD stage, persists as `.usd`/`.usda` files, and is
composed via Layer/Reference/Variant.

Consequences:
- **Re-importing a URDF after edits to the USD obliterates the USD.** The importer
  has no merge mode. Either edit the URDF and re-import (then redo every USD edit), or
  edit only the USD. Pick one.
- **Articulation root must be on the *base* of a kinematic chain**, not on a child
  link. The URDF importer guesses; for non-trivial robots (mobile manipulators,
  dual-arm) you must verify in the Property panel. Wrong root = no motion at all.
- **Visual mesh ≠ collision mesh.** The importer will reuse the URDF's `<visual>` for
  collision unless you provide `<collision>`. Convex decomposition (CoACD, V-HACD) is
  almost always required for a usable collision mesh. See `usd-from-urdf.md`.
- **`.usda` is human-readable and diffable; `.usd` is binary.** For source-controlled
  robot definitions, prefer `.usda`. For payload assets (meshes, textures), `.usd`.

### 3. The ROS 2 bridge is OmniGraph, not code

The Isaac Sim ROS 2 bridge does not work the way Gazebo's does. You **do not write a
Python rclpy node inside Isaac Sim** to publish camera frames. Instead:

- You build an **Action Graph** (`Window → Visual Scripting → Action Graph`) that
  contains a chain of OG nodes: `OnPlaybackTick → IsaacReadCamera → ROS2PublishCamera`.
- Each OG node has typed attributes (input ports, output ports, state). When the graph
  ticks, the runtime evaluates each node and the `ROS2Publish*` node calls into the
  internal rclcpp publisher.
- The QoS profile is set on the OG node (a dropdown), not in code. Mismatch with
  external subscribers behaves exactly as in `ros2-architect` §QoS.
- **You can author OG graphs in Python** via `omni.graph.core` for reproducibility, but
  the runtime is identical.

This is the single largest source of confusion for engineers coming from Gazebo. See
`omnigraph-ros-bridge.md` §"OG vs rclpy: what to write where".

### 4. Sim ↔ real gap has four named axes — fix them one at a time

When a policy that works in Isaac Sim fails on the real robot, the cause is almost
always one (or more) of these, in this order of frequency:

1. **PhysX solver mismatch** — substep count, position/velocity iterations, contact
   offset. Default Isaac Sim settings are tuned for visual fidelity, not physical
   accuracy. See `physx-tuning.md` §Solver.
2. **Friction & contact** — the URDF importer drops `<contact>` tags; restitution and
   dynamic friction must be set per-material on the USD. Real-robot friction is rarely
   the default 0.5/0.5.
3. **Sensor noise** — the simulator delivers perfect joint encoders and noise-free
   cameras. Real sensors do not. Add Replicator-style domain randomization to the
   training pipeline. See `replicator-sdg.md` §Online randomization for RL.
4. **Control rate & latency** — Isaac Sim runs PhysX at 60 Hz by default; many real
   controllers run at 250 Hz–1 kHz with sub-ms latency. If the policy outputs torque,
   you must match the rate; if it outputs joint positions for a downstream PID, you
   must match the PID gains. See `physx-tuning.md` §Control rate.

If sim2real fails, walk these four in order. **Do not retrain until you have ruled out
1–3.**

### 5. Isaac Lab has two paradigms — Manager-based and Direct — never mix them

Isaac Lab (the RL framework on top of Isaac Sim) supports two ways to define an
environment:

- **Manager-based (`ManagerBasedEnv`/`ManagerBasedRLEnv`)**: declarative. You define
  config dataclasses (ObservationCfg, ActionCfg, RewardCfg, EventCfg, …) and the
  framework wires the loop. Best for tasks that fit standard patterns (locomotion,
  manipulation reward shaping). Most official examples are this style.
- **Direct (`DirectRLEnv`)**: imperative. You override `_setup_scene`, `_pre_physics_step`,
  `_apply_action`, `_get_observations`, `_get_rewards`. Best for tasks with unusual
  control loops (variable-step, asymmetric actor-critic observations, custom physics
  hooks).

**Symptoms of mixing them**: trying to use `EventManagerCfg` from a `DirectRLEnv`,
or trying to override `_get_observations` on a `ManagerBasedRLEnv`. Pick one *before*
writing the env class. See `isaaclab-rl.md` §Choosing a paradigm.

### 6. GPU memory is shared between rendering, PhysX, and DNN inference

A common late-stage failure: training works, but as soon as you turn on cameras for
visual-policy learning or run Replicator alongside, you get `CUDA OOM`. Why:

- **PhysX GPU pipeline** holds tensors for every rigid body, articulation joint, contact
  pair across all parallel envs (`num_envs × bodies × 13` floats for state alone).
- **RTX rendering** allocates per-camera framebuffers, denoising history, accumulation
  buffers — easily 1–2 GB per RTX-Real-Time camera at 1080p.
- **DNN inference** (e.g., Isaac ROS DNN nodes, Isaac Manipulator perception) reserves
  TensorRT engine memory.

Mitigations: lower `num_envs`, render at lower res, disable RTX-Real-Time and use
PathTracing only on demand, use `ROS2Camera` with `_PT` (pathtraced) only for SDG runs,
not for RL. See `isaac-ros-accel.md` §GPU budget.

## Decision router

Pick the row that matches the user's task and read the listed reference file(s). Most
tasks involve two or three references in combination.

| Task | Primary reference | Also relevant |
|---|---|---|
| Installing Isaac Sim (workstation, container, cloud, Jetson), choosing ROS 2 distro, IsaacAutomator setup | `installation.md` | `omnigraph-ros-bridge.md` for ROS distro matrix |
| Publishing camera/lidar/IMU/JointState/TF to ROS 2, building Action Graph for ROS, QoS issues, "no topics published" | `omnigraph-ros-bridge.md` | `installation.md` for ROS distro, `usd-from-urdf.md` for sensor frame attachment |
| Importing URDF/MJCF/OnShape, fixing articulation root, joint drive gains, collision meshes, per-vendor (UR/Franka/Doosan) caveats | `usd-from-urdf.md` | `physx-tuning.md` for drive gain math |
| Building an Isaac Lab env (Manager vs Direct), domain randomization, PPO/SAC training, policy export, sim-to-real deployment | `isaaclab-rl.md` | `replicator-sdg.md` for randomization, `physx-tuning.md` for sim accuracy |
| Generating synthetic datasets (COCO/KITTI), Annotators/Writers/Distributions, Replicator-Agent (humans, behaviors), online randomization for RL | `replicator-sdg.md` | `isaaclab-rl.md` for RL integration |
| Tuning PhysX 5 (TGS vs PGS solver, substeps, iteration counts), articulation drive (P/D), contact/friction, fixing sim-to-real physical gap | `physx-tuning.md` | `usd-from-urdf.md` for where parameters live in USD, `isaaclab-rl.md` for batch impact |
| Using Isaac ROS GPU-accelerated nodes (NITROS zero-copy), cuMotion vs MoveIt2, cuRobo direct API, Visual SLAM, Isaac Manipulator, Jetson tuning | `isaac-ros-accel.md` | `omnigraph-ros-bridge.md` for the bridge side |

If the task touches **Kit extension authoring**, **OpenUSD low-level APIs**, **Omniverse
Connect SDK**, or **Nucleus content management**, those are not yet first-class in this
skill — consult `https://docs.omniverse.nvidia.com/kit/` directly or the
`/home/hoon/isaac-sim-skill-research/10-gap-fills/omniverse-kit-api/` mirror.

## Universal workflow — apply this to every non-trivial Isaac Sim task

1. **Confirm versions.** `cat ~/.local/share/ov/pkg/isaac-sim-*/VERSION` and the ROS 2
   distro (`echo $ROS_DISTRO`). The Isaac Sim 5.1↔6.0 boundary moved several APIs;
   the 5.0↔5.1 boundary added simulation_interfaces v1.1.0. Pin the answer at the top
   of any code you write.
2. **Identify the entry mode.** Headless Python (`./python.sh script.py`)? Standalone
   GUI (`./isaac-sim.sh`)? Embedded Kit extension? The choice affects extension load
   order, asset path resolution, and whether `omni.kit.app.get_app().run_loop()` is
   available. Each requires different boilerplate.
3. **Verify USD before logic.** Open the stage in the GUI at least once and check:
   articulation root visible in the Property panel, joints have drive enabled, masses
   are non-zero. 80% of "robot doesn't move" is here. If you must do this in code,
   `omni.physics.tensors.SimulationView.get_articulation_view()` exposes the same
   information programmatically.
4. **Verify the OG graph.** If ROS or sensors are involved, open `Action Graph` window
   and confirm there are no red nodes. A red `ROS2PublishCamera` node usually means the
   camera prim path is wrong or the stage timecode is not advancing.
5. **Watch the console, not the terminal.** Most Isaac Sim errors are in the in-app
   `Window → Console` and the Kit log file (`~/.local/share/ov/data/Kit/.../kit_*.log`),
   not on stdout. Tail the Kit log in a second terminal: `tail -F
   ~/.local/share/ov/data/Kit/Apps/Isaac-Sim/*/kit_*.log`.

## When this skill should defer

- **ROS 2 middleware specifics** — `rclpy`/`rclcpp` patterns, QoS profiles, lifecycle,
  executors, launch files, tf2 broadcasters, ros2_control, MoveIt2 plugins, rqt
  plugins, `colcon` builds: defer to `ros2-architect`. This skill deals with the
  simulator-side OG nodes that publish *into* ROS; everything ROS-internal lives in
  the architect skill.
- **Doosan m0609 vendor SDK** — `DSR_ROBOT2`, `dsr_controller2`, mode transitions,
  DRL scripts, the 161 Doosan services/topics: defer to `doosan-robotics`. Use the USD
  model for the m0609 (Phase A5 of `usd-from-urdf.md`), but for behavior code, the
  vendor skill is authoritative. Cross-reference the Doosan dev-docs at
  `/home/hoon/Documents/services/` and `/home/hoon/Documents/topics/`.
- **Project-local conventions** — anything in a workspace `CLAUDE.md` overrides this
  skill. The user is in control.

## Skill output expectations

When this skill is active, code written should:

- **Always** record the Isaac Sim version and ROS 2 distro at the top of any new
  Python script. Mismatches are the most common silent failure mode.
- **Always** prefer `omni.isaac.core` (and in Isaac Sim 6.x, `isaacsim.core.api`) over
  raw `omni.usd` for robot manipulation. The Core API enforces articulation contracts
  the raw USD API does not.
- **Always** use `SimulationContext` (not `World`) when running headless, and
  `World.reset()` before any read of articulation state. Reading state before reset
  returns stale or NaN values.
- **Prefer** authoring Action Graphs in Python via `omni.graph.core.Controller.edit`
  over hand-clicking in the GUI for anything that needs to be reproducible or version
  controlled. GUI-only graphs lose to source control.
- **Never** call `simulation_app.update()` in a loop without checking the timestep.
  At the wrong timestep this silently changes simulation behavior. Use
  `world.step(render=True)` (Isaac Sim Core API) which encapsulates the right pattern.
- **Never** put `time.sleep()` in an Isaac Sim main loop — it freezes the Kit event
  loop and can corrupt the OG graph state. Use `await
  omni.kit.app.get_app().next_update_async()` in async contexts.
- **Never** ship a policy trained without domain randomization to a real robot. Even
  if "it transferred fine in Pybullet" — Isaac Sim's higher fidelity tightens the
  overfit.
- **Never** mix Isaac Lab Manager-based and Direct env idioms in the same file.

## Related references in this skill

```
isaac-sim-bridge/
├── SKILL.md                          ← you are here (router + core mental model)
├── references/
│   ├── installation.md               ← Workstation/Container/Cloud/Jetson setup,
│   │                                   ROS 2 distro matrix, IsaacAutomator
│   ├── omnigraph-ros-bridge.md       ← OG node model, Action Graph for ROS,
│   │                                   sensor publishing, QoS, debugging
│   ├── usd-from-urdf.md              ← URDF/MJCF Importer, articulation, joint drive,
│   │                                   collision meshes, per-vendor (UR/Franka/Doosan)
│   ├── isaaclab-rl.md                ← Manager vs Direct env, domain randomization,
│   │                                   PPO/SAC, policy export, sim-to-real
│   ├── replicator-sdg.md             ← Annotators/Writers/Distributions,
│   │                                   COCO/KITTI, Replicator-Agent, online DR
│   ├── physx-tuning.md               ← TGS vs PGS, substeps, iterations,
│   │                                   articulation drive math, sim-to-real gap
│   └── isaac-ros-accel.md            ← NITROS, cuMotion vs MoveIt2, cuRobo,
│                                       Visual SLAM, Isaac Manipulator, Jetson
└── scripts/
    └── urdf_to_usd_check.py          ← post-import sanity check: articulation root,
                                        joint drive enabled, mass nonzero, mesh ratio
```

Each reference is written to be readable on its own. Cross-references between files
are explicit ("see `physx-tuning.md` §Solver"). When the task crosses categories, read
the primary reference first, then skim the secondary ones for the pieces you need.

## Local research mirror

A 514+ MB curated mirror of Isaac Sim, Isaac Lab, Isaac ROS, OmniGraph, Replicator,
PhysX SDK, cuRobo, MoveIt2 (Isaac pages), and per-vendor manipulator repos lives at
`/home/hoon/isaac-sim-skill-research/`. The references in this skill cite that mirror
by relative path so they remain useful offline. The mirror's index lives at
`_meta/INDEX.md` and source URLs at `_meta/SOURCES.md`. Re-run `wget` per the
INDEX.md commands to refresh.
