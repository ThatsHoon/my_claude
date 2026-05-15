---
name: ros2-architect
description: >
  Comprehensive ROS 2 architecture, design, and engineering skill for production-grade robotics systems.
  Use this skill whenever the user works on ROS 2 — building nodes (rclpy/rclcpp), workspaces (colcon/ament),
  launch files, custom messages/services/actions, QoS profiles, DDS configuration, lifecycle (managed) nodes,
  composable nodes, ros2_control hardware interfaces, MoveIt 2, Nav2, tf2, URDF/xacro, robot_state_publisher,
  rviz2 configuration and Display/Panel plugin development, rqt plugin development, rosbag2 recording/playback,
  launch_testing, pytest+ROS, micro-ROS, multi-robot DDS isolation, real-time control, or production deployment.
  Trigger on keywords: ros2, ros 2, rclpy, rclcpp, colcon, ament_cmake, ament_python, package.xml, rosdep,
  setup.py, CMakeLists.txt for ROS, msg, srv, action, QoS, DDS, RMW, Fast-DDS, CycloneDDS, lifecycle,
  managed node, composable node, component_container, executor, MultiThreadedExecutor, callback group,
  launch.py, IncludeLaunchDescription, LaunchDescription, Node action, OpaqueFunction, tf2, tf2_ros,
  StaticTransformBroadcaster, TransformListener, robot_state_publisher, joint_state_publisher, urdf, xacro,
  rviz, rviz2, RViz Display plugin, rqt, rqt_plugin, python_qt_binding, ros2_control, controller_manager,
  hardware_interface, moveit, moveit2, nav2, behavior tree, rosbag2, ros2 bag, launch_testing, pytest_ros,
  ros2 topic/service/action/node/param/lifecycle/component/doctor/daemon, ros2 launch, RMW_IMPLEMENTATION,
  ROS_DOMAIN_ID. Also trigger when the user mentions: 로봇, 로보틱스, ROS2, 노드 설계, launch 파일, 커스텀 메시지,
  QoS 설정, lifecycle 노드, MoveIt, Nav2, tf2, URDF, RViz 설정/플러그인, rqt 플러그인, ros2_control, 하드웨어
  인터페이스, rosbag, real-time 제어, ros 디버깅, colcon 빌드, ament. Trigger even if the user does not
  explicitly say "ROS2" — if they describe a multi-process publish/subscribe robotics system with topics,
  services, actions, transforms, URDF, or robot visualization, this skill is the right tool. Covers Humble,
  Iron, Jazzy, Kilted, and Rolling. Two-process architecture (bringup + behavior) is assumed by default.
license: Apache-2.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# ROS 2 Architect Skill

A deep, opinionated guide to designing, building, debugging, and shipping ROS 2 systems. The body
of this file is the **decision router and core mental model**. Detailed patterns, code templates,
and anti-patterns live in `references/<topic>.md`. Read the relevant reference file before writing
non-trivial code — the body alone is intentionally too thin to copy-paste from.

## How to use this skill

1. **Identify the task category** in the Decision Router below. Most ROS 2 tasks fall into one of
   ten buckets — workspace/build, node design, communication, launch, tf/URDF, RViz, rqt,
   ros2_control, debugging, or testing.
2. **Read the matching reference file**. Each reference is self-contained: TOC, working code,
   anti-patterns, and links to the relevant `ros2 <verb>` CLI commands and rosdoc pages.
3. **Apply the core mental model** (next section) regardless of category. These are the invariants
   that make the difference between a node that works in a demo and one that survives integration.
4. **For domain-specific robots** (e.g., the user's m0609 / Doosan stack), defer to that domain's
   skill or `CLAUDE.md` for vendor specifics. This skill stays vendor-neutral.

## Core mental model — the things that matter on every ROS 2 task

These four ideas come up in nearly every reference. Internalize them first.

### 1. ROS 2 is a peer-to-peer DDS graph, not a star network

There is no roscore. Every node discovers peers via DDS multicast (or a discovery server). A topic
is just a named QoS-tagged stream that any number of publishers and subscribers can join. This has
huge consequences:

- **A subscriber that receives nothing is usually a QoS mismatch, not a missing publisher.** The
  publisher and subscriber must agree on reliability (RELIABLE vs BEST_EFFORT) and durability
  (VOLATILE vs TRANSIENT_LOCAL). Mismatch = silent drop. Use `ros2 topic info -v` to see both
  sides' QoS and look for `Incompatible QoS events` in `ros2 doctor`.
- **`ROS_DOMAIN_ID` partitions the graph.** Two robots on the same LAN with different domain IDs
  cannot see each other's topics. Use this to isolate fleets, CI environments, and dev machines.
- **Discovery is not free.** On a busy LAN, multicast discovery generates significant traffic.
  Set `ROS_LOCALHOST_ONLY=1` for single-machine work, or run a Fast-DDS Discovery Server for
  large fleets. See `references/communication.md`.

### 2. Two-process architecture is the default

Robotics systems split cleanly into two long-lived processes:

- **Bringup process** — `dsr_bringup2`-style launch that brings up the controller manager,
  hardware interfaces, robot_state_publisher, and (optionally) RViz. Long-running, restarted only
  on hardware reset.
- **Behavior process** — your application code (motion sequences, perception loops, state machines).
  Restarted frequently as you iterate.

These talk only via the DDS graph. **Never put your behavior code inside the bringup launch.**
You will lose the ability to restart it without re-initializing hardware. This pattern is so
universal that several vendor SDKs (e.g., Doosan DSR) hard-code it.

### 3. Spin loops, executors, and callback groups are the source of every deadlock you will hit

The ROS 2 client library is callback-driven. A callback runs only when an executor spins it. The
default `rclpy.spin(node)` uses a **single-threaded executor with a single mutually-exclusive
callback group**, which means:

- Two callbacks on the same node never run concurrently.
- A callback that blocks (e.g., `client.call(req)` instead of `call_async`) waiting for *another
  callback* on the same node deadlocks forever.
- Service-calling-service patterns require a `MultiThreadedExecutor` + `ReentrantCallbackGroup`,
  or `call_async` + `spin_until_future_complete`.

When in doubt, draw the callback graph first. See `references/node-design.md` for the patterns.

### 4. Time, frames, and QoS are the silent killers

Most "weird" bugs in ROS 2 are one of three things:

- **Time mismatch** — `use_sim_time` not propagated to every node, leading to TF lookups that fail
  with "extrapolation into the future". Set it via launch parameter to *every* node, or none.
- **Frame mismatch** — publishing in `base_link` when downstream expects `base_footprint`, or
  forgetting to publish a static transform. Always run `ros2 run tf2_tools view_frames` before
  declaring TF working.
- **QoS mismatch** — see point 1. The most common case is a sensor publishing `BEST_EFFORT` and a
  recorder subscribing `RELIABLE`. Recorder gets nothing.

## Decision router

Pick the row that matches the user's task and read the listed reference file(s). Most tasks
involve two or three references in combination.

| Task | Primary reference | Also relevant |
|---|---|---|
| Setting up a workspace, writing `package.xml` / `CMakeLists.txt` / `setup.py`, running `rosdep` / `colcon build`, fixing build errors | `workspace-and-build.md` | `node-design.md` for entry points |
| Writing a publisher/subscriber/timer node, choosing executor, lifecycle node, composable node | `node-design.md` | `communication.md` for QoS |
| Choosing between topic / service / action, designing custom `.msg`/`.srv`/`.action`, picking a QoS profile, debugging "no messages received" | `communication.md` | `node-design.md` for callback groups |
| Writing a launch file, conditional launching, parameter substitution, including other launches, namespace remapping | `launch-system.md` | `node-design.md`, `tf2-urdf.md` |
| Designing TF tree, URDF/xacro authoring, `robot_state_publisher`, `joint_state_publisher`, static transforms, troubleshooting frame errors | `tf2-urdf.md` | `launch-system.md` |
| Configuring RViz2, writing `.rviz` configs, building a custom RViz Display / Panel / Tool plugin | `rviz.md` | `tf2-urdf.md` for what to visualize |
| Writing or extending an rqt plugin, embedding Qt widgets, using `python_qt_binding` | `rqt.md` | `node-design.md` |
| Writing a `hardware_interface` plugin, configuring `controller_manager`, switching controllers, joint trajectory controllers | `ros2-control.md` | `launch-system.md`, `tf2-urdf.md` |
| Debugging — `ros2 topic hz`, `ros2 doctor`, `ros2 lifecycle`, log inspection, daemon issues, DDS introspection | `debugging.md` | every other reference |
| Writing tests — `launch_testing`, `pytest`, mock hardware, golden-file checks, CI for ROS 2 | `testing.md` | `workspace-and-build.md` |
| Architecture review, anti-patterns, SOLID for robotics, rate separation, fail-safe defaults, sim-to-real | `design-principles.md` | every other reference |

If the task touches **MoveIt 2**, **Nav2**, **rosbag2**, **micro-ROS**, **SROS2 security**, or
**multi-robot fleets**, the references currently treat them inline within the relevant topic file
(e.g., MoveIt servo configuration is mentioned in `ros2-control.md`; rosbag2 QoS preservation is
in `debugging.md`). For these specialized stacks, also consult the upstream documentation —
`docs.ros.org/en/<distro>` and the project-specific tutorial sites — because they evolve faster
than this skill.

## Universal workflow — apply this to every non-trivial ROS 2 task

1. **Identify the distro and source it.** Run `echo $ROS_DISTRO`. If empty, source
   `/opt/ros/<distro>/setup.bash`. Skill-Claude should not assume a sourced environment; verify.
2. **Identify the workspace.** Look for `colcon.meta`, `src/`, `install/setup.bash` siblings.
   Source the overlay (`source install/setup.bash`) before any `ros2 run` / `ros2 launch`.
3. **Identify the two-process boundary.** Is the user's task in the bringup or the behavior
   process? Behavior code does not go in bringup launches. Bringup launches do not embed
   long-running custom logic.
4. **Read the matching reference file in full** before writing code. ROS 2 is full of footguns
   that are obvious in hindsight; the references exist to surface them up front.
5. **Write code that is restartable, observable, and parameterized.** Hardcoded topic names,
   blocking sleeps in callbacks, missing QoS specs, and missing parameter declarations are the
   four most common smells. See `design-principles.md`.
6. **Verify with introspection commands.** Before declaring done: `ros2 node list`, `ros2 topic
   list -t`, `ros2 topic hz <topic>`, `ros2 doctor --report`. If any are wrong, fix before
   moving on.

## Skill output expectations

When this skill is active, code written should:

- **Always** declare ROS 2 parameters with `declare_parameter(name, default, descriptor=...)`.
  Reading an undeclared parameter is silently empty in older code, raises in newer rclpy. See
  `node-design.md` for the canonical pattern.
- **Always** specify a QoS profile explicitly when creating a publisher or subscriber. Default
  QoS is RELIABLE+VOLATILE+depth=10, which is wrong for sensor streams (use SENSOR_DATA / BEST_EFFORT)
  and wrong for latched data (use TRANSIENT_LOCAL). See `communication.md`.
- **Always** clean up in `destroy_node()` and guard `rclpy.shutdown()` with `if rclpy.ok()`.
  ROS 2 shutdown ordering bugs cause hard-to-debug "context already invalid" errors.
- **Prefer launch.py composition over shell scripts.** A launch file is reproducible; a bash
  script that runs three `ros2 run` commands in tmux panes is not.
- **Never** put `time.sleep(...)` in a callback to "wait for something". Use a timer, an action
  goal callback, or `spin_until_future_complete`. Sleeping in a callback freezes that callback
  group and can deadlock the executor.
- **Never** call `client.call(req)` (synchronous) from inside a callback. Use `call_async` and
  attach a done-callback, or hand the work to a separate `ReentrantCallbackGroup`.
- **Never** use `setup.bash` from `build/`. The build tree is incomplete; only `install/` is.

## When this skill should defer

- **Vendor-specific motion APIs** (Doosan DSR_ROBOT2, Universal Robots URScript, Franka FCI):
  vendor skills / vendor docs are authoritative. This skill covers the ROS 2 plumbing around
  them, not the vendor SDK.
- **Specific Nav2 plugin parameters**, **specific MoveIt 2 OMPL planner tuning**: these change
  per distro and per robot. Reference upstream docs.
- **Project-local conventions** (CLAUDE.md instructions, internal style guides): user instructions
  always win over this skill.

## Live MCP tools — when they apply

ROS 2 is host-side middleware, so most MCP servers don't have a direct role. Three narrow cases
where MCPs do help:

- **Isaac Sim side of a ROS 2 topic** (OmniGraph publishers/subscribers inside Kit): use the
  `isaac-sim-mcp` skill. The OG nodes that bridge Kit ↔ ROS 2 live in Isaac Sim's process; this
  skill's `references/communication.md` covers the host side they talk to.
- **Foxglove Studio / rosbridge_suite web UI debugging**: when a ROS 2 system exposes a browser
  UI (Foxglove, custom dashboards over rosbridge), `chrome-devtools` MCP is the right tool —
  navigate the page, inspect console errors, capture screenshots. The web-slide skill's
  `references/live-preview-mcp.md` documents the chrome-devtools patterns.
- **Headless launch + CLI inspection**: stays in plain `Bash` (run `ros2` CLI, `colcon test`,
  etc.). No MCP needed and none would help.

Everything else (writing nodes, designing launch files, debugging QoS) is plain code work —
use this skill's references directly, no MCP layer.

## Related references in this skill

```
ros2-architect/
├── SKILL.md                            ← you are here (router + core)
├── references/
│   ├── workspace-and-build.md          ← colcon, ament_cmake, ament_python, package.xml, rosdep
│   ├── node-design.md                  ← rclpy/rclcpp patterns, lifecycle, components, executors
│   ├── communication.md                ← topics/services/actions, QoS profiles, DDS, ROS_DOMAIN_ID
│   ├── launch-system.md                ← launch.py, conditions, OpaqueFunction, namespace
│   ├── tf2-urdf.md                     ← tf2, robot_state_publisher, URDF/xacro
│   ├── rviz.md                         ← .rviz configs, Display/Panel/Tool plugin development
│   ├── rqt.md                          ← rqt plugin development, python_qt_binding
│   ├── ros2-control.md                 ← hardware_interface, controller_manager, JTC
│   ├── debugging.md                    ← ros2 CLI, daemon, DDS introspection, common errors
│   ├── testing.md                      ← launch_testing, pytest+ROS, mock hardware, CI
│   └── design-principles.md            ← SOLID for robotics, fail-safe, rate separation, anti-patterns
└── scripts/
    ├── create_ros2_package.sh          ← scaffold ament_cmake or ament_python package
    └── qos_check.py                    ← introspect QoS of a topic and flag mismatches
```

Each reference is written to be readable on its own. Cross-references between files are explicit
("see `node-design.md` §Lifecycle"). When the user's task crosses categories, read the primary
reference first, then skim the secondary ones for the pieces you need.
