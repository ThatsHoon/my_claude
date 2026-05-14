# Node Design

How to write ROS 2 nodes that survive integration. The patterns here apply to both rclpy and
rclcpp; pick the language section after deciding the architecture.

## Contents

1. The node lifecycle question — pick before you start
2. The canonical Python node template
3. The canonical C++ node template
4. Executors and callback groups
5. Lifecycle (managed) nodes
6. Composable nodes and component containers
7. Parameters — declare, read, react
8. Logging — what to log and at what severity
9. Shutdown and cleanup
10. Anti-patterns

## 1. The node lifecycle question — pick before you start

Before writing a single line, decide which of these four shapes the node is:

| Shape | Use when | Example |
|---|---|---|
| **Plain Node** | The node has one job, runs from launch to shutdown, and never needs a "start/stop" external command. | A camera driver, a TF broadcaster, a logger. |
| **Lifecycle (Managed) Node** | The node has clearly distinct *unconfigured / inactive / active* states, and an external orchestrator should be able to bring it up and down without restarting the process. | Sensor drivers in Nav2, controllers in ros2_control. |
| **Composable Node** | Multiple nodes that publish to each other inside the same process to avoid serialization cost. Best for high-rate sensor → processing → output pipelines. | Image processing pipeline (rectify → debayer → detect). |
| **Action Server / Client** | The work is long-running, cancellable, and reports progress. | Move to pose, plan trajectory, execute behavior. |

These are not exclusive: a lifecycle node can also be composable; an action server is just a
node that registers an `ActionServer`. Pick the *primary* shape and add capabilities as needed.

## 2. The canonical Python node template

```python
#!/usr/bin/env python3
"""perception_node.py — annotated reference template.

Demonstrates: parameter declaration with descriptors, QoS selection per topic,
parameter change callback, timer-based work, graceful shutdown.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from rcl_interfaces.msg import ParameterDescriptor, FloatingPointRange, SetParametersResult
from sensor_msgs.msg import Image
from std_msgs.msg import Header


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')

        # 1) Declare parameters with full descriptors.
        # The descriptor is what shows up in `ros2 param describe` and gates dynamic updates.
        self.declare_parameter(
            'rate_hz', 30.0,
            descriptor=ParameterDescriptor(
                description='Processing rate in Hz',
                floating_point_range=[FloatingPointRange(
                    from_value=1.0, to_value=120.0, step=0.0
                )],
            ),
        )
        self.declare_parameter('confidence_threshold', 0.7)
        self.declare_parameter('frame_id', 'camera_link')
        self.declare_parameter('use_sim_time', False)  # Always declare; launch wants to set this.

        # 2) Read parameters into self.* once. Re-read in the parameter callback if they change.
        rate_hz = self.get_parameter('rate_hz').value
        self.threshold = self.get_parameter('confidence_threshold').value
        self.frame_id = self.get_parameter('frame_id').value

        # 3) QoS profiles — pick the right one per topic.
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        reliable_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # 4) Publishers first, then subscribers. This avoids a race where the subscriber's
        #    first message arrives before the publisher exists, costing a frame.
        self.det_pub = self.create_publisher(Image, 'detections', reliable_qos)

        # 5) Subscribers carry the QoS that matches the *upstream* publisher.
        #    Sensor topics are almost always BEST_EFFORT — match that.
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, sensor_qos
        )

        # 6) Timer for periodic work. Period is in seconds.
        self.timer = self.create_timer(1.0 / rate_hz, self.timer_callback)

        # 7) Parameter callback for runtime changes (replaces ROS 1 dynamic_reconfigure).
        self.add_on_set_parameters_callback(self.param_callback)

        self.get_logger().info(
            f'perception_node up: rate={rate_hz}Hz threshold={self.threshold} frame={self.frame_id}'
        )

    # Parameter validation: return successful=False to *reject* the change.
    def param_callback(self, params):
        for p in params:
            if p.name == 'confidence_threshold':
                if not 0.0 <= p.value <= 1.0:
                    return SetParametersResult(successful=False, reason='must be in [0,1]')
                self.threshold = p.value
                self.get_logger().info(f'threshold -> {p.value}')
        return SetParametersResult(successful=True)

    def image_callback(self, msg: Image):
        # Process incoming images. Keep this fast; if you need heavy work, hand it to a
        # ReentrantCallbackGroup or a worker thread (see §Executors).
        pass

    def timer_callback(self):
        # Periodic work — emit detections, heartbeat, etc.
        pass


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

Why every line is there:

- **Descriptor on the rate parameter**: enforces the range at runtime via the parameter callback,
  and `ros2 param describe` displays it. Saves "what's the valid range?" debugging.
- **Sensor QoS = BEST_EFFORT depth 1**: a stale frame is worse than a dropped frame for vision.
  Matching upstream publisher prevents silent drops.
- **Publishers before subscribers**: if a subscriber receives data and tries to republish before
  its publisher exists, the message is dropped. Order matters.
- **Timer instead of `while True: sleep`**: a timer hands control back to the executor between
  ticks so other callbacks (parameter, lifecycle, log) can run.

## 3. The canonical C++ node template

```cpp
// perception_node.cpp
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <rcl_interfaces/msg/set_parameters_result.hpp>

class PerceptionNode : public rclcpp::Node {
public:
  PerceptionNode() : Node("perception_node") {
    // Declare parameters
    this->declare_parameter<double>("rate_hz", 30.0);
    this->declare_parameter<double>("confidence_threshold", 0.7);
    this->declare_parameter<std::string>("frame_id", "camera_link");

    rate_hz_ = this->get_parameter("rate_hz").as_double();
    threshold_ = this->get_parameter("confidence_threshold").as_double();
    frame_id_ = this->get_parameter("frame_id").as_string();

    // QoS
    auto sensor_qos = rclcpp::QoS(rclcpp::SensorDataQoS());
    auto reliable_qos = rclcpp::QoS(10);  // depth=10, RELIABLE+VOLATILE default.

    // Publishers / subscribers
    det_pub_ = this->create_publisher<sensor_msgs::msg::Image>("detections", reliable_qos);
    image_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
        "camera/image_raw", sensor_qos,
        std::bind(&PerceptionNode::image_callback, this, std::placeholders::_1));

    // Timer
    auto period = std::chrono::duration<double>(1.0 / rate_hz_);
    timer_ = this->create_wall_timer(
        std::chrono::duration_cast<std::chrono::nanoseconds>(period),
        std::bind(&PerceptionNode::timer_callback, this));

    // Parameter callback
    param_cb_ = this->add_on_set_parameters_callback(
        [this](const std::vector<rclcpp::Parameter> & params) {
          rcl_interfaces::msg::SetParametersResult result;
          result.successful = true;
          for (const auto & p : params) {
            if (p.get_name() == "confidence_threshold") {
              double v = p.as_double();
              if (v < 0.0 || v > 1.0) {
                result.successful = false;
                result.reason = "must be in [0,1]";
                return result;
              }
              threshold_ = v;
            }
          }
          return result;
        });

    RCLCPP_INFO(this->get_logger(), "perception_node up: rate=%.1f thr=%.2f frame=%s",
                rate_hz_, threshold_, frame_id_.c_str());
  }

private:
  void image_callback(const sensor_msgs::msg::Image::ConstSharedPtr msg) { (void)msg; }
  void timer_callback() {}

  double rate_hz_, threshold_;
  std::string frame_id_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr det_pub_;
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr param_cb_;
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PerceptionNode>());
  rclcpp::shutdown();
  return 0;
}
```

C++ specifics: prefer `SharedPtr` aliases, use `std::bind` or lambdas for callbacks, and use
`rclcpp::SensorDataQoS()` / `rclcpp::SystemDefaultsQoS()` profile shortcuts instead of building
QoS by hand for standard cases.

## 4. Executors and callback groups

The single most common ROS 2 deadlock looks like this:

```python
# inside callback A on a single-threaded executor
result = some_service_client.call(req)   # waits forever — service response callback can't run
```

Why: `rclpy.spin()` defaults to `SingleThreadedExecutor` with one mutually-exclusive callback
group. Callback A is holding the executor; the service response callback can't run; `call()` waits
for that response forever.

### Three fixes (pick the simplest that works)

**Fix 1 — `call_async` + done callback.**
```python
future = client.call_async(req)
future.add_done_callback(self.on_response)
```
The current callback returns immediately; the executor handles the response when it arrives.

**Fix 2 — `MultiThreadedExecutor` + `ReentrantCallbackGroup`.**
```python
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

self.cb_group = ReentrantCallbackGroup()
self.client = self.create_client(SomeSrv, 'some_srv', callback_group=self.cb_group)

# in main():
executor = MultiThreadedExecutor(num_threads=4)
executor.add_node(node)
executor.spin()
```
Now multiple callbacks run concurrently; service responses don't queue behind the caller.

**Fix 3 — `spin_until_future_complete`.**
```python
future = client.call_async(req)
rclpy.spin_until_future_complete(self.node, future)
result = future.result()
```
Uses a temporary inline executor that pumps callbacks until the future is done. This is what
many vendor libraries (DSR_ROBOT2, etc.) use internally — but it only works when the *caller* is
not already inside an executor's callback. Don't use it from inside a subscription callback.

### Callback group cheat sheet

| Group | Behavior |
|---|---|
| `MutuallyExclusiveCallbackGroup` (default) | At most one callback in this group runs at a time. Safe by default; can deadlock if you call into the same group. |
| `ReentrantCallbackGroup` | Any number of callbacks in this group can run concurrently on a `MultiThreadedExecutor`. Required for service-calling-service. |

Rule: every node has *one* default mutually-exclusive group. Add a `ReentrantCallbackGroup` for
service clients and timers that need to coexist with long-running subscription callbacks.

## 5. Lifecycle (managed) nodes

A lifecycle node has the state machine:

```
unconfigured → inactive → active → inactive → finalized
            (configure) (activate) (deactivate)
```

Use it when an external orchestrator (Nav2, ros2_control, your own bringup) needs to bring this
node up and down without killing the process — for example, hot-swapping a controller, or
restarting a sensor after a USB reset.

```python
import rclpy
from rclpy.lifecycle import LifecycleNode, TransitionCallbackReturn, State

class CameraDriver(LifecycleNode):
    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('configuring')
        # Allocate device handles, declare parameters, but do not publish yet.
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('activating')
        # Start streaming. Lifecycle publishers were created in on_configure but only
        # actually publish after on_activate.
        return super().on_activate(state)

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('deactivating')
        return super().on_deactivate(state)

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        # Release resources allocated in on_configure.
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        return TransitionCallbackReturn.SUCCESS
```

Drive transitions with `ros2 lifecycle set <node> configure|activate|deactivate|cleanup`.

Common mistake: starting hardware in `__init__` instead of `on_configure`. The whole point of
lifecycle nodes is that `__init__` should be cheap and side-effect-free; configuration cost goes
into `on_configure`.

## 6. Composable nodes and component containers

A "component" is a node compiled as a shared library that can be loaded into a `component_container`
process. Multiple components in the same container share an address space, so publish/subscribe
between them avoids inter-process serialization (zero-copy intra-process).

When to use: a high-rate pipeline of three or more nodes that all run on the same machine and
publish big messages (images, point clouds) to each other.

```cpp
// my_component.cpp
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_components/register_node_macro.hpp"

namespace mypkg {
class MyComponent : public rclcpp::Node {
 public:
  explicit MyComponent(const rclcpp::NodeOptions & opts) : Node("my_component", opts) {}
};
}  // namespace mypkg

RCLCPP_COMPONENTS_REGISTER_NODE(mypkg::MyComponent)
```

`CMakeLists.txt`:

```cmake
add_library(my_component SHARED src/my_component.cpp)
ament_target_dependencies(my_component rclcpp rclcpp_components)
rclcpp_components_register_nodes(my_component "mypkg::MyComponent")
install(TARGETS my_component LIBRARY DESTINATION lib)
```

Loading at runtime:

```bash
ros2 component load /ComponentManager mypkg mypkg::MyComponent
```

Or in a launch file via `ComposableNodeContainer` — see `launch-system.md` §Composition.

## 7. Parameters — declare, read, react

Three rules:

1. **Always declare before reading.** Reading an undeclared parameter raises in modern rclpy.
2. **Use a descriptor for ranges and dynamic typing.** It enables validation in the parameter
   callback and makes `ros2 param describe` informative.
3. **React via `add_on_set_parameters_callback`.** Don't poll. The callback is called *before*
   the parameter is committed; return `successful=False` to reject invalid changes.

```python
# Declare with a constraint.
self.declare_parameter(
    'max_velocity', 1.5,
    descriptor=ParameterDescriptor(
        description='Max linear velocity (m/s)',
        floating_point_range=[FloatingPointRange(from_value=0.0, to_value=2.0, step=0.0)],
    ),
)
```

Loading parameters from YAML in launch is the standard production pattern — see
`launch-system.md` §Parameter Loading.

## 8. Logging — what to log and at what severity

| Severity | Use for |
|---|---|
| `DEBUG` | Per-message diagnostics — not on by default. Don't log every callback. |
| `INFO` | Lifecycle events: node up, configuration loaded, target reached. |
| `WARN` | Recoverable anomalies: dropped frame, timeout retried, fallback to default. |
| `ERROR` | Operation failed but the node continues: service call rejected, transform unavailable. |
| `FATAL` | Cannot continue. Usually followed by `rclpy.shutdown()`. |

Throttled logging avoids flooding when a callback runs at 100 Hz:

```python
self.get_logger().warn('frame dropped', throttle_duration_sec=1.0)
```

Anti-pattern: rolling your own `if self._last_log + 1.0 < now`. The library handles it correctly
(monotonic clock, lock-free counter); reinventing it usually introduces a bug.

### Logger severity caveat (rclpy)

The Python logger keys on (file, line). If two calls share the same line and you change severity,
rclpy raises `Logger severity cannot be changed between calls`. Symptoms include:

```python
log = self.get_logger().info if ok else self.get_logger().warn  # SAME LINE — bad
log("status: %s" % msg)
```

Fix: separate the severities into different statements / lines:

```python
if ok:
    self.get_logger().info(f'status: {msg}')
else:
    self.get_logger().warn(f'status: {msg}')
```

## 9. Shutdown and cleanup

```python
def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
```

The `if rclpy.ok()` guard matters because the `KeyboardInterrupt` may have been raised inside
`rclpy.init()` itself, leaving the context invalid. Calling `shutdown()` on an invalid context
raises a confusing `Context must be initialized` error.

For C++, use `rclcpp::on_shutdown([] { ... })` to register cleanup that runs even on Ctrl-C, and
prefer `rclcpp::shutdown()` over manual flag-checking.

## 10. Anti-patterns

- **`time.sleep()` in a callback.** Freezes the callback group. Use a timer or
  `spin_until_future_complete`. If you really must sleep, do it in a worker thread, not a callback.
- **Synchronous service calls from inside callbacks.** Deadlocks the executor. Use `call_async` or
  a `ReentrantCallbackGroup`.
- **Reading a parameter without declaring it.** Silently empty in old rclpy, raises in new. Always
  `declare_parameter` first.
- **Using the default QoS for sensor topics.** Sensor data is BEST_EFFORT; default is RELIABLE.
  Mismatch = silent drop.
- **One giant node that does perception, planning, and control.** Split by responsibility. See
  `design-principles.md` §Single Responsibility.
- **`while True: ... sleep()` instead of a timer.** A `while` loop in `main()` is fine *if it
  also calls `rclpy.spin_once(node, timeout_sec=...)` on each iteration*; otherwise no callbacks
  run. Almost always cleaner to use a timer.
- **Putting hardware initialization in `__init__` of a lifecycle node.** Goes in `on_configure`.
- **Hardcoding topic / service / action names.** Always use `~` or remap-via-launch to keep names
  configurable.
