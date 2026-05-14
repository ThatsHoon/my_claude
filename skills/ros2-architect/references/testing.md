# Testing

How to test ROS 2 code with confidence. Two main techniques: `pytest` for unit tests (no ROS
runtime needed), and `launch_testing` for integration tests with multiple nodes.

## Contents

1. The two-tier test strategy
2. pytest for pure-logic unit tests
3. ROS-aware unit tests (rclpy node fixtures)
4. launch_testing — integration tests
5. Testing services and actions
6. Mock hardware interfaces
7. Assertion helpers — when to write a custom matcher
8. CI integration
9. Anti-patterns

## 1. The two-tier test strategy

| Tier | Tool | Tests |
|---|---|---|
| **Unit** | `pytest` (no ROS) | Algorithms, message converters, math, parameter validation. Fast (milliseconds), runs anywhere. |
| **Integration** | `launch_testing` + `pytest` | Multiple nodes communicating, end-to-end behavior. Slow (seconds to minutes), needs ROS env. |

A healthy package has 80% unit tests, 20% integration tests, and as few hardware-in-the-loop
tests as you can get away with.

## 2. pytest for pure-logic unit tests

If a function is "given a list of waypoints, return the next one to visit", that's pure logic —
test it without ROS:

```python
# my_planner/planner.py
def next_waypoint(current, waypoints, threshold=0.05):
    if not waypoints:
        return None
    nearest = min(waypoints, key=lambda w: dist(current, w))
    return nearest if dist(current, nearest) > threshold else None
```

```python
# test/test_planner.py
import pytest
from my_planner.planner import next_waypoint

def test_returns_none_when_empty():
    assert next_waypoint((0, 0), []) is None

def test_returns_nearest():
    wps = [(1, 0), (0, 1), (5, 5)]
    assert next_waypoint((0, 0), wps) == (1, 0)

def test_skips_when_close_enough():
    assert next_waypoint((0, 0), [(0.01, 0)]) is None

@pytest.mark.parametrize('threshold,expected', [
    (0.0, (0.01, 0)),
    (0.05, None),
    (0.005, (0.01, 0)),
])
def test_threshold(threshold, expected):
    assert next_waypoint((0, 0), [(0.01, 0)], threshold=threshold) == expected
```

Run it:

```bash
colcon test --packages-select my_planner
colcon test-result --verbose --test-result-base build/my_planner/
```

Or directly with pytest:

```bash
cd ~/my_ws/src/my_planner
python3 -m pytest test/
```

## 3. ROS-aware unit tests (rclpy node fixtures)

When the unit under test is a node, you still don't need a full launch — instantiate it in a
test process:

```python
# test/test_perception_node.py
import pytest
import rclpy
from my_perception.perception_node import PerceptionNode

@pytest.fixture
def rclpy_init():
    rclpy.init()
    yield
    rclpy.shutdown()

@pytest.fixture
def node(rclpy_init):
    n = PerceptionNode()
    yield n
    n.destroy_node()

def test_default_threshold(node):
    assert node.threshold == 0.7

def test_param_callback_rejects_bad_value(node):
    from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
    p = rclpy.parameter.Parameter('confidence_threshold',
                                  rclpy.Parameter.Type.DOUBLE, 1.5)
    result = node.param_callback([p])
    assert result.successful is False
```

Spin briefly to allow callbacks to run:

```python
def test_publishes_on_image(node):
    received = []
    sub = node.create_subscription(
        Image, 'detections', lambda msg: received.append(msg), 10)
    # Inject an input
    node.image_callback(make_test_image())
    rclpy.spin_once(node, timeout_sec=0.5)
    assert len(received) == 1
```

## 4. launch_testing — integration tests

For testing two or more nodes that talk to each other, use `launch_testing`. The test file is
a launch file with extra annotations.

```python
# test/test_pipeline_integration.py
import os
import unittest
import pytest
import launch
import launch.actions
import launch_ros.actions
import launch_testing
import launch_testing.actions
import rclpy
from std_msgs.msg import String

@pytest.mark.launch_test
def generate_test_description():
    perception_node = launch_ros.actions.Node(
        package='my_perception',
        executable='perception_node',
        name='perception',
        parameters=[{'confidence_threshold': 0.5}],
    )
    decision_node = launch_ros.actions.Node(
        package='my_decision',
        executable='decision_node',
        name='decision',
    )
    return (
        launch.LaunchDescription([
            perception_node,
            decision_node,
            launch_testing.actions.ReadyToTest(),    # signals tests can start
        ]),
        # Locals that test methods can grab
        {'perception_node': perception_node, 'decision_node': decision_node},
    )


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_node')

    def tearDown(self):
        self.node.destroy_node()

    def test_decision_publishes_after_detection(self):
        received = []
        sub = self.node.create_subscription(
            String, '/decision/action',
            lambda msg: received.append(msg.data), 10)

        # Trigger by injecting a detection.
        pub = self.node.create_publisher(String, '/perception/detection', 10)
        msg = String()
        msg.data = 'cup'
        pub.publish(msg)

        # Wait for downstream effect.
        end = time.time() + 5.0
        while time.time() < end and not received:
            rclpy.spin_once(self.node, timeout_sec=0.1)

        self.assertEqual(received, ['pick'])


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):
    def test_clean_exit(self, perception_node, decision_node):
        launch_testing.asserts.assertExitCodes([perception_node, decision_node])
```

Key elements:

- **`@pytest.mark.launch_test`** on `generate_test_description` — pytest-launch finds it.
- **`launch_testing.actions.ReadyToTest()`** — without it, tests start before nodes are up.
- **Two test phases**: regular tests run while nodes are alive; `@post_shutdown_test()` runs
  after everything's down (good for checking exit codes / log assertions).

Run integration tests:

```bash
colcon test --packages-select my_perception --event-handlers console_cohesion+
colcon test-result --all --verbose
```

Or directly:

```bash
launch_test test/test_pipeline_integration.py
```

## 5. Testing services and actions

Service test, in a launch_testing harness:

```python
def test_set_pose_succeeds(self):
    cli = self.node.create_client(SetPose, '/set_pose')
    self.assertTrue(cli.wait_for_service(timeout_sec=5.0))

    req = SetPose.Request()
    req.pose.position.x = 1.0
    future = cli.call_async(req)
    rclpy.spin_until_future_complete(self.node, future, timeout_sec=5.0)
    response = future.result()
    self.assertTrue(response.success)
    self.assertEqual(response.message, 'OK')
```

Action test (with feedback collection):

```python
def test_pick_place_completes(self):
    client = ActionClient(self.node, PickPlace, '/pick_place')
    self.assertTrue(client.wait_for_server(timeout_sec=5.0))

    feedbacks = []
    goal = PickPlace.Goal()
    goal.target.position.x = 0.5

    send_goal_future = client.send_goal_async(
        goal, feedback_callback=lambda f: feedbacks.append(f.feedback))
    rclpy.spin_until_future_complete(self.node, send_goal_future, timeout_sec=5.0)
    goal_handle = send_goal_future.result()
    self.assertTrue(goal_handle.accepted)

    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(self.node, result_future, timeout_sec=30.0)
    result = result_future.result().result

    self.assertTrue(result.success)
    self.assertGreater(len(feedbacks), 0)        # progress was reported
```

## 6. Mock hardware interfaces

To test a node that depends on hardware, replace the hardware with a fake. Two approaches:

### Approach 1 — `mock_components` ros2_control plugin

ros2_control ships a `mock_components/GenericSystem` that pretends to be hardware:

```xml
<ros2_control name="my_arm" type="system">
  <hardware>
    <plugin>mock_components/GenericSystem</plugin>
  </hardware>
  <joint name="joint1">
    <command_interface name="position"/>
    <state_interface name="position"/>
  </joint>
</ros2_control>
```

The mock loops command back as state, so trajectories "execute" instantly. Useful for testing
controllers and trajectory generation without real hardware.

### Approach 2 — bag-replayed sensor inputs

For perception tests, record a representative scenario and replay it:

```python
# test_perception_with_real_data.py
@pytest.mark.launch_test
def generate_test_description():
    perception = launch_ros.actions.Node(...)
    bag_play = launch.actions.ExecuteProcess(
        cmd=['ros2', 'bag', 'play', os.path.join(
            get_package_share_directory('my_perception_test'), 'data', 'kitchen.bag')],
        output='screen')
    return launch.LaunchDescription([
        perception, bag_play,
        launch_testing.actions.ReadyToTest(),
    ])
```

The test then asserts on what the perception node outputs given the recorded inputs.

### Approach 3 — Python mock node

For service/action dependencies, write a small mock in the test file:

```python
class MockArmServer(Node):
    def __init__(self):
        super().__init__('mock_arm')
        self._action_server = ActionServer(
            self, FollowJointTrajectory, '/arm/follow_joint_trajectory',
            self.execute_cb)

    def execute_cb(self, goal_handle):
        # pretend to execute, then return success
        result = FollowJointTrajectory.Result()
        result.error_code = result.SUCCESSFUL
        goal_handle.succeed()
        return result
```

## 7. Assertion helpers — when to write a custom matcher

If you find yourself writing the same wait-for-message + parse + compare logic across many
tests, factor it out:

```python
def wait_for_message(node, topic, msg_type, timeout=5.0):
    """Block until a message arrives on `topic`, or raise."""
    received = []
    sub = node.create_subscription(msg_type, topic,
                                    lambda m: received.append(m), 10)
    end = time.time() + timeout
    while time.time() < end and not received:
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_subscription(sub)
    if not received:
        raise TimeoutError(f'No message on {topic} within {timeout}s')
    return received[0]
```

For TF assertions:

```python
def assert_transform_close(buffer, target, source, expected_xyz, tol=0.01):
    t = buffer.lookup_transform(target, source, rclpy.time.Time())
    actual = (t.transform.translation.x, ..., t.transform.translation.z)
    for a, e in zip(actual, expected_xyz):
        assert abs(a - e) < tol, f'{actual} != {expected_xyz} (tol {tol})'
```

## 8. CI integration

GitHub Actions example:

```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-22.04
    container: ros:humble
    steps:
      - uses: actions/checkout@v4
        with: { path: src/${{ github.event.repository.name }} }

      - run: |
          apt update && apt install -y python3-colcon-common-extensions
          rosdep update
          rosdep install --from-paths src --ignore-src -r -y

      - run: |
          . /opt/ros/humble/setup.sh
          colcon build --event-handlers console_cohesion+

      - run: |
          . /opt/ros/humble/setup.sh
          . install/setup.sh
          colcon test --event-handlers console_cohesion+
          colcon test-result --verbose
```

`colcon test-result --verbose` is what fails the job — `colcon test` always returns 0.

For headless integration tests with RViz disabled, set the `rviz:=false` launch arg or wrap
RViz in `IfCondition(LaunchConfiguration('rviz'))` (see `launch-system.md`).

## 9. Anti-patterns

- **No tests at all because "robotics is too dynamic".** The pure-logic parts (path planners,
  state machines, message converters) are the easiest to test and the most valuable to verify.
  At least 60% of robotics code is pure logic.
- **Putting hardware connections in unit tests.** Tests must run in CI without the robot.
  Mock the hardware interface.
- **Tests that depend on wall-clock time** (`assert time.time() - start < 5.0`). Flaky in CI
  on shared runners. Use `use_sim_time` or asynchronous waits with bounded retries.
- **Forgetting `ReadyToTest()` in launch_testing.** Tests run before nodes start; everything
  fails with timeouts. Always include it as the last action.
- **Testing only the happy path.** The interesting bugs are at the seams: QoS mismatch,
  parameter validation rejection, action goal preemption, lifecycle transition failure.
- **`time.sleep(N)` instead of `wait_for_message`.** Slow and brittle. Use bounded spin loops.
- **Asserting on internal node state from outside.** Tests should drive nodes via their
  public ROS interfaces (topics, services, actions) — not poke at private attributes.
