# Design Principles for ROS 2 Systems

What separates a robotics codebase that scales to a fleet from one that breaks the moment a
new feature lands. These principles apply across languages and frameworks but are especially
sharp in ROS 2 because the consequences (silent QoS drops, runaway behaviors, stuck lifecycle
states) are physical.

## Contents

1. Why robotics software is harder than CRUD apps
2. Single Responsibility — one node, one job
3. Dependency Inversion — depend on abstractions
4. Open-Closed — extend without modifying
5. Interface Segregation — small focused interfaces
6. Liskov Substitution — replaceable implementations
7. Separation of Rates — don't block fast loops with slow work
8. Fail-Safe Defaults — safe until proven otherwise
9. Configuration Over Code — externalize what changes
10. Architecture decision checklist
11. Anti-patterns (cross-cutting)

## 1. Why robotics software is harder than CRUD apps

Three properties make robotics systems unforgiving:

- **The system has physical consequences.** A bug in a webapp shows a wrong number; a bug in a
  motion controller hits a person. Defaults must be safe; partial failures must stop motion.
- **The system runs at multiple timescales simultaneously.** A control loop runs at 1 kHz; a
  perception pipeline runs at 30 Hz; a high-level planner runs at 1 Hz. Coupling these via
  blocking calls is how you get jittery motors and missed deadlines.
- **The system spans many processes and machines.** A single bug at the DDS / QoS / namespace
  layer manifests as silence — a topic that "should be there" simply doesn't exist. Debugging
  needs introspection, not a debugger.

Every principle below exists because of one of these three facts.

## 2. Single Responsibility — one node, one job

A node should do one thing: drive a sensor, plan a path, run a state machine. When a node
accumulates responsibilities, every change risks every other capability.

**Bad:**

```python
class GodNode(Node):
    """Reads camera, runs perception, plans path, sends commands, logs."""
    def __init__(self):
        super().__init__('robot')
        # ... 600 lines of mixed concerns ...
```

**Good:**

```
camera_driver        → /image_raw
perception_node      → /detections   (subscribes /image_raw)
planner_node         → /path         (subscribes /detections, /goal)
controller_node      → /cmd_vel      (subscribes /path, /odom)
data_logger          → file          (subscribes everything)
```

Each node is replaceable. Want to swap perception models? Stop `perception_node`, start a new
one. The rest of the graph keeps running.

The exception: when intra-process communication latency dominates (e.g., 1080p image processing
at 30 Hz), the same logical chain *can* live as composable nodes in one container — but each
component still has one job.

## 3. Dependency Inversion — depend on abstractions

High-level modules should not depend on hardware. They should depend on **interfaces** that
hardware implements.

**Bad:** the planner imports `RealsenseDriver` directly. Now the planner doesn't run without a
RealSense camera plugged in.

**Good:** the planner subscribes to `sensor_msgs/PointCloud2` on a topic. *Anything* that
publishes that topic — RealSense, simulated camera, recorded bag — drives the planner.

In ROS 2, the *topic* is the abstraction. As soon as you find yourself importing a vendor SDK
into business logic, you've inverted the dependency. Push the vendor code into a driver node
that publishes to a standard topic.

```python
# ❌ business logic depends on hardware vendor
from realsense2_camera import RealsensePipeline
class Perception:
    def __init__(self):
        self.cam = RealsensePipeline(...)   # locked to RealSense

# ✅ business logic depends on a topic
class Perception(Node):
    def __init__(self):
        super().__init__('perception')
        self.create_subscription(PointCloud2, 'points', self.cb, qos)
```

## 4. Open-Closed — extend without modifying

Add new capabilities by adding nodes, not by editing existing ones. The plugin pattern makes
this explicit: `pluginlib`-loaded controllers and sensors mean the controller_manager doesn't
need to know what's plugged in.

For application code, this often looks like:

```python
# Sensor selection via parameter; controller picks at startup.
self.declare_parameter('sensor_type', 'rgbd')
sensor_type = self.get_parameter('sensor_type').value
self.sensor = SensorFactory.create(sensor_type, self)
```

Now adding a new sensor is "register a new factory entry" — the controller, planner, etc. are
untouched.

## 5. Interface Segregation — small, focused interfaces

A camera that publishes RGB and depth and orientation should expose three topics, not one big
`SensorState` message. A node that wants only RGB doesn't pay the bandwidth or processing cost
of depth and IMU.

ROS 2's topic-per-data-type style enforces this naturally — resist the temptation to bundle
everything into one custom message "for convenience". The convenience always evaporates the
moment you want to record only one stream, throttle one stream, or replace one source.

## 6. Liskov Substitution — replaceable implementations

If two drivers both publish `sensor_msgs/PointCloud2` on `/points` with the same QoS and frame
convention, the rest of the graph can't tell them apart. That's substitutability — the test of
a good interface contract.

Common violations:

- One driver publishes in `base_link`, another in `camera_optical_frame` without a static
  transform. Downstream visually breaks.
- One driver publishes `intensity` field, another doesn't. RViz Display configured for intensity
  shows nothing.
- One driver runs at 30 Hz, another at 5 Hz. The downstream's Deadline QoS rejects the slow one.

Fix: define and document the contract for each "kind" of topic in your project (frame, fields,
rate, QoS), and require every implementation to honor it.

## 7. Separation of Rates — don't block fast loops with slow work

A control loop at 1 kHz cannot wait for a perception pipeline at 30 Hz. Putting them in the
same callback group means the slow callback freezes the fast one.

**Bad:**

```python
class Controller(Node):
    def __init__(self):
        # Both subscribers in the default mutually-exclusive group.
        self.create_subscription(Image, 'image', self.heavy_perception, ...)
        self.create_subscription(JointState, 'joints', self.fast_control, ...)
```

If `heavy_perception` takes 50 ms, `fast_control` is blocked the whole time. Loop deadline
missed.

**Good:**

```python
self.fast_cb_group = MutuallyExclusiveCallbackGroup()
self.slow_cb_group = ReentrantCallbackGroup()

self.create_subscription(JointState, 'joints', self.fast_control,
                          callback_group=self.fast_cb_group, qos=1)
self.create_subscription(Image, 'image', self.heavy_perception,
                          callback_group=self.slow_cb_group, qos=1)
```

Run with `MultiThreadedExecutor`. Fast and slow callbacks now run on different threads.

The deeper pattern: separate the rates into separate **nodes** entirely. A controller and a
perception node communicating via topics is more robust than a single node with two callback
groups, because the OS scheduler — not your callback group config — handles the priority.

## 8. Fail-Safe Defaults — safe until proven otherwise

The robot's default behavior on any uncertainty must be the safe one.

**Bad:**

```python
self.declare_parameter('max_velocity', 5.0)        # m/s — way too fast
self.declare_parameter('emergency_stop_enabled', False)
```

**Good:**

```python
self.declare_parameter('max_velocity', 0.2)        # safe walking pace
self.declare_parameter('emergency_stop_enabled', True)
self.declare_parameter('require_explicit_arm', True)  # robot won't move without a command
```

When a sensor fails, **stop**, don't extrapolate from the last reading.

```python
def perception_callback(self, msg):
    if (self.get_clock().now() - msg.header.stamp).nanoseconds > 5e8:
        self.stop_motion()
        self.get_logger().error('stale perception data — emergency stop')
        return
    # otherwise, normal processing
```

When a controller is uncertain, **stop**, don't guess.

This is the principle that keeps people unhurt. Apply it ruthlessly.

## 9. Configuration Over Code — externalize what changes

Things that change between robots, deployments, or experiments belong in YAML — not in code.

**Bad:** hardcoded list of joint names in three places, each consumed by a different node. To
swap robots, edit three files.

**Good:** one `robot_config.yaml` declaring joint names. All nodes load it via launch
parameters.

```yaml
# config/m0609.yaml
/**:
  ros__parameters:
    joint_names: [joint1, joint2, joint3, joint4, joint5, joint6]
    home_pose: [0.0, 0.0, 1.5708, 0.0, 1.5708, 0.0]
    max_velocity: 0.5
    workspace_radius: 0.9
```

```python
self.declare_parameter('joint_names', ['joint1','joint2','joint3','joint4','joint5','joint6'])
self.joint_names = self.get_parameter('joint_names').value
```

This pattern carries through the whole stack: URDFs are parameterized via xacro, controllers
configured via YAML, MoveIt poses kept in YAML, RViz views saved as `.rviz` files. The
codebase never knows which robot it's running on.

## 10. Architecture decision checklist

Before committing to a design, walk through these:

- **Is each node's job describable in one sentence?** If you need "and" or commas, it's doing
  too much.
- **Does any node import a vendor SDK?** Push that import to a thin driver node; everything else
  uses topics.
- **Are there hardcoded topic names, frame names, joint names anywhere?** They belong in YAML.
- **Does the slow loop block the fast loop?** Use callback groups or separate nodes.
- **What happens when topic X disappears?** The downstream should detect staleness and enter a
  safe state, not freeze or extrapolate.
- **Can the system recover from a node crash without restarting the bringup?** Two-process
  architecture — see SKILL.md §Two-Process Architecture.
- **Is the configuration reproducible?** Can a colleague run `ros2 launch ... use_sim_time:=true`
  on a fresh machine and see the same behavior?
- **Is every QoS profile chosen consciously?** Default QoS for a sensor topic is a bug.
- **Are launch arguments declared with `description=` and types?** Anonymous arguments are
  invisible to users.
- **Does CI exercise integration, not just unit tests?** A unit test catches algorithm bugs;
  integration tests catch QoS / namespace / lifecycle bugs.

## 11. Anti-patterns (cross-cutting)

- **One giant launch file with no namespacing.** Two robots' nodes collide; one silently fails.
  Use `GroupAction` + `PushRosNamespace`.
- **Logging everything at INFO.** Your logs are unreadable; the actually-important warnings get
  drowned. Use INFO for lifecycle events, WARN for recoverable anomalies, ERROR for failures.
- **Synchronous service calls from inside callbacks.** Deadlock on the executor. See
  `node-design.md` §Executors.
- **Using time.sleep() instead of timers.** Freezes the executor. Use `create_timer`.
- **Storing state in module-level globals.** Breaks `MultiThreadedExecutor`, breaks composable
  nodes, breaks tests. Put state on `self`.
- **Coupling business logic to a specific simulation.** Today's Gazebo, tomorrow's Isaac Sim,
  next year's Mujoco. Keep the boundary at standard topics; sim-specific code lives in driver
  nodes.
- **No mock for hardware.** CI can't run; tests slow down to a crawl when bottlenecked on real
  hardware. Use `mock_components/GenericSystem` and bag replay (see `testing.md`).
- **Hand-rolling state machines from scratch in one node.** Behavior trees (BehaviorTree.CPP) and
  dedicated FSMs (smach, yasmin) are battle-tested; rolling your own is rarely worth the
  effort. The exception: very simple sequences where a few `if/else` branches are clearer than
  a tree.
- **Mixing Python and C++ in the same package.** Use separate packages with a shared
  `_interfaces` package for messages. Mixing breeds CMake pain.
- **Skipping rosdep**, then surprised the robot doesn't boot in CI. Always declare deps in
  `package.xml` and run `rosdep install` in CI.
