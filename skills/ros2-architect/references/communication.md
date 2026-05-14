# Communication — Topics, Services, Actions, QoS, DDS

The single hardest-to-debug class of ROS 2 bugs lives here. Read this file before adding any new
publisher, subscriber, service client, or action client.

## Contents

1. Choosing topic vs service vs action
2. QoS profiles — what each policy does
3. The five canonical QoS profiles
4. QoS compatibility rules (and how to read mismatch errors)
5. Custom messages, services, and actions — defining and using
6. DDS implementations and `RMW_IMPLEMENTATION`
7. `ROS_DOMAIN_ID` and `ROS_LOCALHOST_ONLY`
8. Discovery server pattern for fleets
9. Intra-process communication
10. Anti-patterns and common pitfalls

## 1. Choosing topic vs service vs action

| Mechanism | Semantics | Use when | Don't use when |
|---|---|---|---|
| **Topic** | Many-to-many anonymous pub/sub. Best-effort or reliable, but always asynchronous; no ack to publisher. | Streaming sensor data, state broadcasts, commands without ack. | You need to know the request was *handled* (use a service). |
| **Service** | Strict request/response. One server, many clients. Synchronous from the client's perspective. | Configuration changes, atomic operations that complete in <1 second. | The work takes >1 second (use an action). The work has multiple clients that can each request it (services queue; action goal handles preemption). |
| **Action** | Long-running goal with progress feedback and cancellation. | Move to pose, plan trajectory, run mission. Anything where the user might want to cancel mid-flight. | The work is fast and atomic (use a service). The work has no meaningful "progress" or "result" (use a topic). |

A useful test: if the operation has a notion of *cancellation*, it's an action. If it has a
notion of *response*, it's a service. Otherwise it's a topic.

## 2. QoS profiles — what each policy does

A QoS profile is a tuple of these policies. The ones that bite are starred.

| Policy | Values | What it controls |
|---|---|---|
| **Reliability** ★ | `RELIABLE`, `BEST_EFFORT` | Whether the middleware retransmits lost messages. RELIABLE = TCP-like, BEST_EFFORT = UDP-like. Sensor streams use BEST_EFFORT; commands use RELIABLE. |
| **Durability** ★ | `VOLATILE`, `TRANSIENT_LOCAL` | Whether late-joining subscribers get the last value. TRANSIENT_LOCAL = "latched" (e.g., `/tf_static`, `/robot_description`). |
| **History** | `KEEP_LAST` (depth=N), `KEEP_ALL` | Buffer size on publisher side. Almost always KEEP_LAST. |
| **Depth** | integer | The buffer size for KEEP_LAST. 1 for sensors (only latest matters), 10 for commands. |
| **Deadline** | duration | Subscriber expects a message every X seconds; publishes are tagged. |
| **Lifespan** | duration | Messages older than X are dropped at the publisher. |
| **Liveliness** | `AUTOMATIC`, `MANUAL_BY_TOPIC` | How the middleware detects a dead publisher. |
| **Liveliness lease** | duration | Threshold for "dead". |

Reliability and Durability are the only two that commonly cause silent communication failures.
Memorize them.

## 3. The five canonical QoS profiles

Almost every topic in a real robot fits into one of these five buckets. Use these as your
starting point and only deviate when you have a specific reason.

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

# 1) Sensor data — cameras, LiDARs, IMU. Tolerate drops, want latest.
SENSOR_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
)

# 2) Commands — velocity setpoints, joint targets. Never miss, small queue.
COMMAND_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
)

# 3) Latched / static — /tf_static, /robot_description, map. Late joiners must get it.
LATCHED_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
)

# 4) State — joint_states, robot_state. Reliable, some history for late joiners.
STATE_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
)

# 5) Default for everything else — same as DDS default.
DEFAULT_QOS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=10,
)
```

`rclcpp` ships these as built-in profiles: `SensorDataQoS()`, `ServicesQoS()`, `ParametersQoS()`,
`SystemDefaultsQoS()`. In Python, define them once in a shared module and import everywhere.

### Topic-by-topic reference table

| Topic | Profile | Why |
|---|---|---|
| `/camera/image_raw`, `/scan`, `/imu` | SENSOR | Drops are fine; staleness is not. |
| `/cmd_vel`, joint command topics | COMMAND | Cannot drop a stop command. |
| `/tf_static`, `/robot_description`, `/map` | LATCHED | Late joiners (RViz on a different machine) must get it on connect. |
| `/joint_states`, robot state topics | STATE | Reliable so subscribers don't miss state changes. |
| `/diagnostics`, `/rosout` | DEFAULT | Already standardized. |
| `/tf` (the dynamic one) | DEFAULT | Reliable but volatile; late joiners get a fresh stream. |

## 4. QoS compatibility rules

Compatibility is one-directional: think of it as **subscriber requirements**. The subscriber's
profile is the *minimum* it accepts; the publisher must offer at least that.

| Subscriber requests | Publisher offers | Compatible? |
|---|---|---|
| BEST_EFFORT | BEST_EFFORT | ✓ |
| BEST_EFFORT | RELIABLE | ✓ (publisher exceeds; OK) |
| RELIABLE | BEST_EFFORT | ✗ Mismatch — silent drop |
| RELIABLE | RELIABLE | ✓ |
| VOLATILE | VOLATILE | ✓ |
| VOLATILE | TRANSIENT_LOCAL | ✓ |
| TRANSIENT_LOCAL | VOLATILE | ✗ Mismatch — late joiner gets nothing |
| TRANSIENT_LOCAL | TRANSIENT_LOCAL | ✓ |

### Diagnosing a "0 messages received" bug

```bash
# Step 1 — confirm the publisher exists and is publishing.
ros2 topic info /my_topic --verbose
ros2 topic hz /my_topic         # if hz prints, publisher is up

# Step 2 — confirm the subscriber sees it.
ros2 node info /my_subscriber_node    # check it lists /my_topic

# Step 3 — read both QoS profiles from `topic info -v`. Look for:
#   "Reliability:" — both must match (or sub BEST_EFFORT)
#   "Durability:"  — sub VOLATILE accepts both; sub TRANSIENT_LOCAL needs pub TRANSIENT_LOCAL

# Step 4 — incompatible QoS events surface in ros2 doctor.
ros2 doctor --report
```

If the publisher and subscriber are in the same node, also check that the publisher was created
*before* the subscriber's first message arrived (publisher-before-subscriber rule).

## 5. Custom messages, services, and actions

Always create custom interfaces in their own package — by convention `<robotname>_msgs` or
`<project>_interfaces`. Don't put `.msg` definitions next to your runtime nodes; the build
graph hates it.

```
my_robot_interfaces/
├── package.xml          (build_depend rosidl_default_generators, exec_depend rosidl_default_runtime)
├── CMakeLists.txt       (find_package rosidl_default_generators, rosidl_generate_interfaces)
├── msg/
│   └── Detection.msg
├── srv/
│   └── GetPose.srv
└── action/
    └── PickPlace.action
```

`Detection.msg`:

```
std_msgs/Header header
string label
float32 confidence
geometry_msgs/Point center
```

`GetPose.srv`:

```
string frame_id
---
geometry_msgs/PoseStamped pose
bool success
string message
```

`PickPlace.action`:

```
# Goal
geometry_msgs/PoseStamped target
float32 approach_height
---
# Result
bool success
geometry_msgs/PoseStamped achieved_pose
---
# Feedback
float32 progress       # 0.0 to 1.0
string status
```

`CMakeLists.txt` essentials:

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_robot_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Detection.msg"
  "srv/GetPose.srv"
  "action/PickPlace.action"
  DEPENDENCIES std_msgs geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

`package.xml`:

```xml
<buildtool_depend>ament_cmake</buildtool_depend>
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<depend>std_msgs</depend>
<depend>geometry_msgs</depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

A common mistake: forgetting `<exec_depend>rosidl_default_runtime</exec_depend>` — the package
builds, but Python nodes that import the generated message fail at runtime with `ModuleNotFoundError`.

## 6. DDS implementations and `RMW_IMPLEMENTATION`

ROS 2 swaps DDS via the RMW (ROS Middleware) abstraction. The two production-grade options:

| Implementation | Strengths | Weaknesses |
|---|---|---|
| **rmw_fastrtps_cpp** (default) | Mature, widely tested, good multi-machine. | Discovery can be chatty on busy LANs. |
| **rmw_cyclonedds_cpp** | Lower latency, smaller, used by Nav2 historically. | Slightly different QoS edge-case behavior. |

Switching is one env var:

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

All nodes on the wire must use the *same* RMW for full interop. They can theoretically interop
but you'll hit edge cases.

### Tuning Fast-DDS

For multi-machine setups, write a `fastdds.xml` and point the daemon at it:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <participant profile_name="default_participant" is_default_profile="true">
    <rtps>
      <builtin>
        <discovery_config>
          <leaseDuration>
            <sec>30</sec>
          </leaseDuration>
        </discovery_config>
      </builtin>
    </rtps>
  </participant>
</profiles>
```

```bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/path/to/fastdds.xml
```

For Cyclone DDS, use `CYCLONEDDS_URI` pointing at an XML config.

## 7. `ROS_DOMAIN_ID` and `ROS_LOCALHOST_ONLY`

`ROS_DOMAIN_ID` (0–101 typically) partitions the DDS network. Two robots on the same LAN with
different domain IDs cannot see each other. Use this:

- **Per-robot domain ID** in fleets. Robot 1 = 25, Robot 2 = 26. Prevents cross-talk and cuts
  discovery noise.
- **Per-developer domain ID** on shared dev networks. Gives each dev their own private graph.
- **Per-CI-job domain ID** to isolate parallel test runs.

```bash
export ROS_DOMAIN_ID=25
```

`ROS_LOCALHOST_ONLY=1` restricts discovery to the loopback interface. For single-machine work
this both eliminates noise and avoids accidentally interfering with the lab network.

```bash
export ROS_LOCALHOST_ONLY=1
```

When using either, **set them before launching anything** — they are read at process startup.
Changing them mid-session has no effect on already-running nodes.

## 8. Discovery server pattern for fleets

Default DDS discovery uses multicast, which scales poorly past ~10 nodes per LAN. The fix is the
**discovery server** — a centralized broker that nodes register with.

Fast-DDS:

```bash
# Start the discovery server
fastdds discovery -i 0 -l 192.168.1.10 -p 11811

# Each node points at it
export ROS_DISCOVERY_SERVER=192.168.1.10:11811
ros2 run my_pkg my_node
```

Cyclone DDS uses a different mechanism (`CycloneDDS Discovery`) — see project docs.

This pattern is essential for: 30+ node graphs, robots on Wi-Fi (where multicast is unreliable),
and cross-VLAN setups.

## 9. Intra-process communication

When two nodes are in the same `component_container` (see `node-design.md` §Composable Nodes),
they can publish/subscribe with **zero copy** — the message pointer is passed directly without
serialization.

To enable:

```python
# In the launch file:
ComposableNodeContainer(
    name='vision_container',
    namespace='',
    package='rclcpp_components',
    executable='component_container_mt',  # mt = multithreaded
    composable_node_descriptions=[
        ComposableNode(
            package='image_proc',
            plugin='image_proc::DebayerNode',
            extra_arguments=[{'use_intra_process_comms': True}],
        ),
        ComposableNode(
            package='my_pkg',
            plugin='my_pkg::DetectionNode',
            extra_arguments=[{'use_intra_process_comms': True}],
        ),
    ],
)
```

Caveats:

- Only `unique_ptr` ownership transfer enables true zero-copy in C++. Subscribers that hold a
  shared reference to the message force a copy.
- BEST_EFFORT topics support intra-process comms; mixing reliability levels degrades performance.
- For Python nodes, intra-process is mostly irrelevant — you pay the GIL cost anyway.

## 10. Anti-patterns and common pitfalls

- **Default QoS on a sensor topic**: Default is RELIABLE; sensor publishers are typically
  BEST_EFFORT. Subscriber receives nothing.
- **TRANSIENT_LOCAL subscriber on a VOLATILE publisher**: Late joiner expects to be caught up;
  publisher won't replay. Fix: match durability.
- **Publishing transforms on `/tf_static` from a non-static publisher**: `tf_static` is latched
  with infinite lifetime. Use `StaticTransformBroadcaster` exactly once at startup; for moving
  frames, use `TransformBroadcaster` on `/tf`.
- **Calling a service synchronously from a callback**: Deadlock. See `node-design.md` §Executors.
- **Using a topic for a single-shot configuration**: Configuration is a service or a parameter,
  not a topic. Topics have no acknowledgement; the receiver may be down at the moment you publish.
- **Custom message in the runtime package**: Build dependency cycles. Custom interfaces always
  go in a separate `<project>_interfaces` package.
- **Hardcoding `frame_id` strings**: Make them parameters. URDF link names change across
  variants of the same robot; hardcoded values break silently.
- **Using ROS 1 `<remap from="x" to="y"/>` syntax in launch.py**: ROS 2 uses `remappings=[('x', 'y')]`
  in the `Node()` constructor. Wrong syntax fails silently.
- **Mixing `rclpy` and `rclcpp` clients in the same process**: Possible but rarely works
  cleanly because they have separate executors and parameter stores. Pick one per process.
