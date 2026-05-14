# TF2 and URDF

Coordinate frames and robot kinematics. Get this right and visualization, planning, and motion
all work; get it wrong and you spend a week chasing transform errors.

## Contents

1. The TF2 mental model — a tree of timestamped frames
2. Static vs dynamic transforms
3. URDF anatomy
4. xacro — the URDF preprocessor you actually use
5. `robot_state_publisher` and `joint_state_publisher`
6. Looking up transforms in code (Python and C++)
7. The four common TF errors and how to read them
8. Visualizing the tree
9. Anti-patterns

## 1. The TF2 mental model — a tree of timestamped frames

TF2 is a directed tree of named coordinate frames. Each edge is a transform from parent to
child, timestamped. There is exactly one root (usually `world` or `map` or `odom`).

The graph holds **a buffer of recent transforms** — typically 10 seconds. To use a transform,
you query the buffer: "give me the transform from `base_link` to `tool0` at time `t`". The
buffer interpolates between adjacent timestamps.

Two consequences:

- **Late lookups fail.** If you ask for a transform at time `t` and the buffer's newest entry
  for that edge is from time `t - 11s`, the lookup raises `ExtrapolationException`. Either ask
  for a more recent time, or ensure the publisher is running.
- **Future lookups fail.** Asking for time `t + 1s` (future) raises `ExtrapolationException`
  unless the publisher has explicitly published a future-timestamped transform (rare).

The convention: every transform's `header.stamp` is set to *the time the data was sensed*, not
the time it was published. A camera publishing detections at 30 Hz attaches the camera's frame
acquisition time to each detection.

## 2. Static vs dynamic transforms

| Transform type | Topic | Publisher | Lifetime |
|---|---|---|---|
| **Static** | `/tf_static` | `StaticTransformBroadcaster` | Latched (TRANSIENT_LOCAL QoS). Published once, replayed to late joiners. |
| **Dynamic** | `/tf` | `TransformBroadcaster` | Streaming. Published every cycle. |

Examples of each:

- **Static**: `base_link` → `lidar_link`, `base_link` → `camera_link`. The relative pose of
  sensors to the robot body never changes.
- **Dynamic**: `odom` → `base_link` (from wheel odometry), `base_link` → `tool0` (from joint
  states + URDF kinematics, published by `robot_state_publisher`), `map` → `odom` (from SLAM /
  localization).

A common bug: publishing a fixed sensor mount on `/tf` instead of `/tf_static`. The transform
streams at 100 Hz forever, eats CPU and bandwidth, and breaks RViz when streamed past the
buffer horizon. Fix: use `StaticTransformBroadcaster`, publish once.

## 3. URDF anatomy

URDF (Unified Robot Description Format) is XML that describes a robot's links (rigid bodies)
and joints (connections). A minimal arm:

```xml
<?xml version="1.0"?>
<robot name="my_arm">
  <link name="base_link">
    <visual>
      <geometry><cylinder length="0.1" radius="0.05"/></geometry>
      <material name="grey"><color rgba="0.5 0.5 0.5 1"/></material>
    </visual>
    <collision>
      <geometry><cylinder length="0.1" radius="0.05"/></geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
    </inertial>
  </link>

  <link name="link1">
    <visual><geometry><box size="0.05 0.05 0.3"/></geometry></visual>
  </link>

  <joint name="joint1" type="revolute">
    <parent link="base_link"/>
    <child link="link1"/>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="100" velocity="2.0"/>
  </joint>
</robot>
```

Joint types:

| Type | DOF | Use for |
|---|---|---|
| `fixed` | 0 | Welded mount (sensor on a bracket). Becomes a static transform. |
| `revolute` | 1 | Hinge with limits (most arm joints). |
| `continuous` | 1 | Hinge without limits (wheels). |
| `prismatic` | 1 | Slider with limits (linear actuator). |
| `floating` | 6 | Free in 3D (mobile base in `map`). |
| `planar` | 3 | XY + yaw (some mobile bases). |

Each link should have visual, collision, and inertial — but you can omit them at the cost of
visualization, planning, or simulation respectively.

## 4. xacro — the URDF preprocessor you actually use

Real URDFs are written in xacro and converted to URDF on the fly. xacro adds macros, includes,
math, and parameter expansion.

```xml
<?xml version="1.0"?>
<robot name="my_arm" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <xacro:property name="link_length" value="0.3"/>
  <xacro:property name="pi" value="3.14159265359"/>

  <xacro:macro name="cylinder_link" params="name length radius color">
    <link name="${name}">
      <visual>
        <geometry><cylinder length="${length}" radius="${radius}"/></geometry>
        <material name="${color}"/>
      </visual>
    </link>
  </xacro:macro>

  <xacro:cylinder_link name="link1" length="${link_length}" radius="0.025" color="grey"/>
  <xacro:cylinder_link name="link2" length="${link_length * 0.8}" radius="0.020" color="grey"/>

  <xacro:include filename="$(find my_arm_description)/urdf/inertia_macros.xacro"/>
</robot>
```

In a launch file, expand xacro at runtime:

```python
import xacro
from launch_ros.actions import Node

robot_description = xacro.process_file(
    os.path.join(get_package_share_directory('my_arm_description'), 'urdf', 'arm.urdf.xacro'),
    mappings={'arm_id': 'left'},   # xacro:arg passed in
).toxml()

return LaunchDescription([
    Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
    ),
])
```

You can also use `xacro` from the command line:

```bash
xacro arm.urdf.xacro arm_id:=left > arm.urdf
```

## 5. `robot_state_publisher` and `joint_state_publisher`

These two nodes turn a URDF + joint angles into a TF tree.

| Node | Subscribes | Publishes |
|---|---|---|
| `robot_state_publisher` | `/joint_states` (sensor_msgs/JointState) | `/tf` (for each non-fixed joint) and `/tf_static` (for fixed joints) |
| `joint_state_publisher` | (none) — provides a default | `/joint_states` |
| `joint_state_publisher_gui` | (none) — provides sliders | `/joint_states` |

In a real robot, the **driver** publishes `/joint_states` from encoders. `robot_state_publisher`
turns those into transforms. You don't need `joint_state_publisher` in production — only in sim
or when previewing a URDF without hardware.

```python
# Typical bringup sequence
Node(
    package='robot_state_publisher', executable='robot_state_publisher',
    parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}],
),
# Hardware driver publishes /joint_states. If running URDF-only preview:
Node(
    package='joint_state_publisher_gui', executable='joint_state_publisher_gui',
    condition=IfCondition(LaunchConfiguration('preview_only')),
),
```

## 6. Looking up transforms in code

### Python (rclpy + tf2_ros)

```python
import rclpy
from rclpy.node import Node
import tf2_ros
from rclpy.duration import Duration

class TfConsumer(Node):
    def __init__(self):
        super().__init__('tf_consumer')
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.create_timer(0.1, self.tick)

    def tick(self):
        try:
            t = self.tf_buffer.lookup_transform(
                'base_link',          # target frame (where you want the value expressed)
                'tool0',              # source frame (the thing whose pose you want)
                rclpy.time.Time(),    # latest available
                timeout=Duration(seconds=0.1),
            )
            self.get_logger().info(
                f'tool0 in base_link: x={t.transform.translation.x:.3f}'
            )
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException,
                tf2_ros.ExtrapolationException) as e:
            self.get_logger().warn(f'TF lookup failed: {e}', throttle_duration_sec=1.0)
```

Frame argument order trips everyone up: `lookup_transform(target, source, time)` returns the
pose of `source` expressed in `target`. Read it as "I have a point in `source` frame, multiply
by this transform to get it in `target` frame".

### C++ (rclcpp + tf2_ros)

```cpp
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>

class TfConsumer : public rclcpp::Node {
public:
  TfConsumer() : Node("tf_consumer") {
    tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);
    timer_ = this->create_wall_timer(std::chrono::milliseconds(100),
                                     [this] { this->tick(); });
  }
private:
  void tick() {
    try {
      auto t = tf_buffer_->lookupTransform("base_link", "tool0", tf2::TimePointZero);
      RCLCPP_INFO(this->get_logger(), "x=%.3f", t.transform.translation.x);
    } catch (const tf2::TransformException & e) {
      RCLCPP_WARN(this->get_logger(), "TF lookup failed: %s", e.what());
    }
  }
  std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
  rclcpp::TimerBase::SharedPtr timer_;
};
```

### Static transform broadcaster (publish once at startup)

```python
from geometry_msgs.msg import TransformStamped
import tf2_ros

class StaticPub(Node):
    def __init__(self):
        super().__init__('static_pub')
        self.broadcaster = tf2_ros.StaticTransformBroadcaster(self)
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'lidar_link'
        t.transform.translation.x = 0.2
        t.transform.translation.z = 0.5
        t.transform.rotation.w = 1.0
        self.broadcaster.sendTransform(t)
```

The static broadcaster keeps the latest transform alive in `/tf_static` even after the publisher
exits — that's TRANSIENT_LOCAL durability at work.

## 7. The four common TF errors and how to read them

### "Lookup would require extrapolation into the future"

You asked for a transform at time `t`, but the publisher's most recent transform is older. Three
causes:

1. **Wrong clock**: `use_sim_time` is true on your subscriber but false on the publisher (or
   vice versa). They live in different time domains. Fix: propagate `use_sim_time` to *every*
   node consistently.
2. **Publisher stalled**: the URDF expander or hardware driver crashed. Check `ros2 topic hz
   /joint_states`.
3. **Latency**: subscriber's clock ran ahead. Use `rclpy.time.Time()` (latest available) instead
   of `now()` to avoid the issue.

### "Lookup would require extrapolation into the past"

You asked for a transform at time `t`, older than the buffer's oldest entry. Either widen the
buffer (`tf2_ros.Buffer(cache_time=Duration(seconds=30))`) or use a more recent `t`.

### "Could not find a connection between 'A' and 'B' because they are not part of the same tree"

The frames exist but no path between them. Run `ros2 run tf2_tools view_frames` to dump the
current tree to PDF. Usually a missing publisher (e.g., `map` → `odom` not yet published by
SLAM, or static transform from `base_link` to `lidar_link` was never sent).

### "Frame 'X' does not exist"

Self-explanatory. The frame name has never appeared in `/tf` or `/tf_static`. Check spelling
(`base_link` vs `baselink` vs `base`), and that the publisher has actually started.

## 8. Visualizing the tree

```bash
# Dump the current tree to a PDF.
ros2 run tf2_tools view_frames
# Generates frames.pdf in the current directory.

# Live monitor a single transform.
ros2 run tf2_ros tf2_echo base_link tool0

# Open RViz with TF display enabled — best for interactive debugging.
ros2 run rviz2 rviz2
# Add → TF, set Fixed Frame to your root.
```

`view_frames` saves a snapshot every 5 seconds. If frames disappear from the snapshot when you
expect them, the publisher is intermittent.

## 9. Anti-patterns

- **Publishing static-mount transforms on `/tf` at high rate.** They never change. Publish on
  `/tf_static` once. Saves CPU, bandwidth, and reduces the buffer turnover.
- **Mismatched `use_sim_time`.** One node uses sim time, another uses wall time. TF lookups fail
  with future/past extrapolation. Always set `use_sim_time` via a top-level launch arg and
  propagate to all nodes.
- **Hardcoded frame names in code.** Make them parameters. URDF link names change between robot
  variants; hardcoded string `"tool0"` breaks silently.
- **Looking up a transform inside a tight loop without a timeout.** Without a timeout, the lookup
  blocks forever if the publisher is down. Always pass `timeout=Duration(seconds=N)` or use
  `tf_buffer.can_transform()` first.
- **Putting non-fixed joints with type `fixed` to "make them simpler".** `robot_state_publisher`
  treats `fixed` joints as static; if you ever drive them via `/joint_states`, they're ignored.
  Use `revolute` with `lower==upper==0` if you really mean "currently locked".
- **URDF without inertial blocks for Gazebo.** Sim won't load. Add at minimum `<inertial><mass
  value="0.001"/><inertia ixx="..."/></inertial>`.
- **Two publishers writing to the same TF edge.** Multiple writers cause inconsistent
  interpolation. Each edge has exactly one publisher.
- **`tf2_ros.Buffer(node)` without keeping a reference to the listener.** The listener gets
  garbage-collected. Always store `self.tf_listener` on the node.
