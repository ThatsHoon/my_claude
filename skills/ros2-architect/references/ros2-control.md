# ros2_control

ros2_control is the standard hardware-abstraction layer for actuators and controllers. It
defines a `controller_manager` process that loads `hardware_interface` plugins (talk to motors)
and `controller` plugins (compute commands). This file covers writing, configuring, and
debugging the stack.

## Contents

1. The architecture in one diagram
2. URDF additions for ros2_control
3. Writing a `hardware_interface` plugin
4. Configuring controllers via YAML
5. Loading and switching controllers
6. Joint Trajectory Controller — the workhorse
7. Other built-in controllers
8. MoveIt 2 integration
9. Real-time considerations
10. Anti-patterns

## 1. The architecture in one diagram

```
                  ┌──────────────────────────┐
                  │   Application / MoveIt   │
                  │   (sends trajectories)   │
                  └─────────┬────────────────┘
                            │ FollowJointTrajectory action
                  ┌─────────▼────────────────┐
                  │   controller_manager      │
                  │   (process, periodic)     │
                  ├──────────────────────────┤
                  │  Controllers (plugins):   │
                  │   - JointTrajectoryCtrl   │
                  │   - JointStateBroadcaster │
                  │   - VelocityController    │
                  └─────────┬────────────────┘
                            │ command_interfaces / state_interfaces
                  ┌─────────▼────────────────┐
                  │   hardware_interface      │
                  │   (plugin: your code)     │
                  └─────────┬────────────────┘
                            │ vendor SDK / EtherCAT / serial
                  ┌─────────▼────────────────┐
                  │       Motors              │
                  └──────────────────────────┘
```

The `controller_manager` runs a periodic loop:

1. Read state from `hardware_interface` (joint positions, velocities, efforts).
2. Update each loaded controller (compute commands).
3. Write commands to `hardware_interface`.

This loop runs at a fixed rate (typically 100–1000 Hz).

## 2. URDF additions for ros2_control

A normal URDF describes geometry. ros2_control adds a `<ros2_control>` block describing what
each joint exposes:

```xml
<robot ...>
  <!-- existing <link>/<joint> definitions -->

  <ros2_control name="my_arm_system" type="system">
    <hardware>
      <plugin>my_robot_hw/MyRobotHardware</plugin>
      <param name="device">/dev/ttyUSB0</param>
      <param name="baudrate">115200</param>
    </hardware>

    <joint name="joint1">
      <command_interface name="position">
        <param name="min">-3.14</param>
        <param name="max">3.14</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>

    <joint name="joint2">
      <command_interface name="position"/>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
    </joint>
  </ros2_control>
</robot>
```

Key points:

- **`type="system"`** — the whole robot is one hardware interface. Other types: `actuator`
  (single joint) and `sensor` (read-only).
- **`<plugin>`** — the pluginlib-registered class name of your hardware interface.
- **`<param>`** entries become parameters available to your hardware in `on_init`.
- **`<command_interface>`** — what the controller can write. Common: `position`, `velocity`,
  `effort`.
- **`<state_interface>`** — what the controller can read.

A joint with both `position` command and state interfaces is fully servoed; one with only
`position` state is a passive joint (free spinning, you only observe).

## 3. Writing a `hardware_interface` plugin

A hardware interface is a C++ plugin that bridges ros2_control's interfaces to your motor SDK.

```cpp
// my_robot_hw.hpp
#pragma once
#include <hardware_interface/system_interface.hpp>
#include <hardware_interface/types/hardware_interface_return_values.hpp>
#include <rclcpp_lifecycle/state.hpp>

namespace my_robot_hw {

class MyRobotHardware : public hardware_interface::SystemInterface {
 public:
  hardware_interface::CallbackReturn on_init(
      const hardware_interface::HardwareInfo & info) override;

  hardware_interface::CallbackReturn on_configure(
      const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_activate(
      const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_deactivate(
      const rclcpp_lifecycle::State & previous_state) override;

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  hardware_interface::return_type read(
      const rclcpp::Time & time, const rclcpp::Duration & period) override;
  hardware_interface::return_type write(
      const rclcpp::Time & time, const rclcpp::Duration & period) override;

 private:
  std::vector<double> hw_position_states_;
  std::vector<double> hw_velocity_states_;
  std::vector<double> hw_effort_states_;
  std::vector<double> hw_position_commands_;
  std::string device_;
  int baudrate_;
};

}  // namespace my_robot_hw
```

```cpp
// my_robot_hw.cpp (essentials)
#include "my_robot_hw.hpp"
#include <pluginlib/class_list_macros.hpp>

namespace my_robot_hw {

CallbackReturn MyRobotHardware::on_init(const HardwareInfo & info) {
  if (SystemInterface::on_init(info) != CallbackReturn::SUCCESS) {
    return CallbackReturn::ERROR;
  }
  hw_position_states_.resize(info_.joints.size(), 0.0);
  hw_velocity_states_.resize(info_.joints.size(), 0.0);
  hw_effort_states_.resize(info_.joints.size(), 0.0);
  hw_position_commands_.resize(info_.joints.size(), 0.0);

  device_ = info_.hardware_parameters["device"];
  baudrate_ = std::stoi(info_.hardware_parameters["baudrate"]);
  return CallbackReturn::SUCCESS;
}

CallbackReturn MyRobotHardware::on_configure(const State &) {
  // Open the serial port / EtherCAT bus / vendor SDK connection here.
  return CallbackReturn::SUCCESS;
}

CallbackReturn MyRobotHardware::on_activate(const State &) {
  // Enable motor torque, reset commands to current state.
  for (size_t i = 0; i < hw_position_commands_.size(); ++i) {
    hw_position_commands_[i] = hw_position_states_[i];
  }
  return CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface>
MyRobotHardware::export_state_interfaces() {
  std::vector<hardware_interface::StateInterface> ifaces;
  for (size_t i = 0; i < info_.joints.size(); ++i) {
    ifaces.emplace_back(info_.joints[i].name, "position", &hw_position_states_[i]);
    ifaces.emplace_back(info_.joints[i].name, "velocity", &hw_velocity_states_[i]);
    ifaces.emplace_back(info_.joints[i].name, "effort", &hw_effort_states_[i]);
  }
  return ifaces;
}

std::vector<hardware_interface::CommandInterface>
MyRobotHardware::export_command_interfaces() {
  std::vector<hardware_interface::CommandInterface> ifaces;
  for (size_t i = 0; i < info_.joints.size(); ++i) {
    ifaces.emplace_back(info_.joints[i].name, "position", &hw_position_commands_[i]);
  }
  return ifaces;
}

return_type MyRobotHardware::read(const rclcpp::Time &, const rclcpp::Duration &) {
  // Talk to the motors: poll positions/velocities/efforts.
  // for (size_t i = 0; i < info_.joints.size(); ++i) {
  //   hw_position_states_[i] = vendor_sdk_.get_position(i);
  //   ...
  // }
  return return_type::OK;
}

return_type MyRobotHardware::write(const rclcpp::Time &, const rclcpp::Duration &) {
  // Send hw_position_commands_ to the motors.
  // vendor_sdk_.send_positions(hw_position_commands_);
  return return_type::OK;
}

}  // namespace my_robot_hw

PLUGINLIB_EXPORT_CLASS(my_robot_hw::MyRobotHardware,
                       hardware_interface::SystemInterface)
```

`read()` and `write()` are called every controller_manager cycle. Their performance directly
determines achievable rate. **Do not allocate, log, or sleep in these functions** — they're on
the real-time path.

`plugins.xml`:

```xml
<library path="my_robot_hw">
  <class name="my_robot_hw/MyRobotHardware"
         type="my_robot_hw::MyRobotHardware"
         base_class_type="hardware_interface::SystemInterface">
    <description>Hardware interface for MyRobot.</description>
  </class>
</library>
```

## 4. Configuring controllers via YAML

`config/controllers.yaml`:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz
    use_sim_time: false

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController

    velocity_controller:
      type: forward_command_controller/ForwardCommandController

# Configure each controller's params:
arm_controller:
  ros__parameters:
    joints:
      - joint1
      - joint2
      - joint3
      - joint4
      - joint5
      - joint6
    command_interfaces:
      - position
    state_interfaces:
      - position
      - velocity
    state_publish_rate: 50.0
    action_monitor_rate: 20.0
    allow_partial_joints_goal: false
    constraints:
      stopped_velocity_tolerance: 0.01
      goal_time: 0.5
      joint1: { trajectory: 0.05, goal: 0.01 }

velocity_controller:
  ros__parameters:
    joints: [joint1, joint2, joint3, joint4, joint5, joint6]
    interface_name: velocity
```

## 5. Loading and switching controllers

```bash
# List available and active controllers.
ros2 control list_controllers

# Load and configure (but don't activate).
ros2 control load_controller arm_controller

# Activate.
ros2 control set_controller_state arm_controller active
# Or in one shot:
ros2 control load_controller --set-state active arm_controller

# Deactivate.
ros2 control set_controller_state arm_controller inactive

# Switch atomically (deactivate one, activate another).
ros2 control switch_controllers \
    --activate velocity_controller \
    --deactivate arm_controller
```

The standard launch sequence:

```python
# launch.py — bring up controller_manager and load JSB + arm_controller
control_node = Node(
    package='controller_manager', executable='ros2_control_node',
    parameters=[robot_description, controllers_yaml],
    output='screen',
)

joint_state_broadcaster_spawner = Node(
    package='controller_manager', executable='spawner',
    arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
)

arm_controller_spawner = Node(
    package='controller_manager', executable='spawner',
    arguments=['arm_controller', '--controller-manager', '/controller_manager'],
)

# Order: control_node first, then JSB, then the arm controller.
return LaunchDescription([
    control_node,
    RegisterEventHandler(
        OnProcessStart(
            target_action=control_node,
            on_start=[joint_state_broadcaster_spawner],
        ),
    ),
    RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[arm_controller_spawner],
        ),
    ),
])
```

The chained event handlers ensure JSB is up before the arm controller tries to claim the same
joints.

## 6. Joint Trajectory Controller — the workhorse

`JointTrajectoryController` (JTC) is what MoveIt and most application code actually uses. It
takes a `trajectory_msgs/JointTrajectory` and interpolates between waypoints in real time.

Action interface:

```bash
# Goal: a JointTrajectory.
# Topic: /arm_controller/follow_joint_trajectory
# Type: control_msgs/action/FollowJointTrajectory
```

Sending a trajectory programmatically:

```python
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

client = ActionClient(node, FollowJointTrajectory, '/arm_controller/follow_joint_trajectory')
client.wait_for_server()

goal = FollowJointTrajectory.Goal()
goal.trajectory.joint_names = ['joint1', 'joint2', 'joint3']

p1 = JointTrajectoryPoint()
p1.positions = [0.0, 0.0, 0.0]
p1.time_from_start = Duration(sec=0, nanosec=0)
p2 = JointTrajectoryPoint()
p2.positions = [0.5, 0.3, -0.2]
p2.time_from_start = Duration(sec=2, nanosec=0)
goal.trajectory.points = [p1, p2]

future = client.send_goal_async(goal)
```

Common errors:

- **"INVALID_JOINTS"**: the goal's `joint_names` doesn't match the controller's configured
  joints, or order differs. Match exactly.
- **"OLD_HEADER_TIMESTAMP"**: the trajectory starts in the past. Set `header.stamp = 0` to mean
  "execute now" — the controller treats epoch as relative.

## 7. Other built-in controllers

| Controller | Purpose |
|---|---|
| `joint_state_broadcaster` | Publishes `/joint_states` from state interfaces. Always load this first. |
| `joint_trajectory_controller` | Position trajectory with cubic interpolation. The standard arm controller. |
| `forward_command_controller` | Pass-through for velocity/effort commands on a topic. |
| `velocity_controllers/JointGroupVelocityController` | Same as above but pre-configured for velocity. |
| `effort_controllers/JointGroupEffortController` | Effort version. |
| `diff_drive_controller` | Differential-drive base from cmd_vel. |
| `tricycle_controller`, `ackermann_steering_controller` | Mobile base variants. |
| `gripper_action_controller` | Gripper action server. |
| `imu_sensor_broadcaster` | Publishes IMU sensor state. |
| `force_torque_sensor_broadcaster` | Publishes wrench from FT sensor state. |

## 8. MoveIt 2 integration

MoveIt sends trajectories to JTC (or compatible). Configuration in
`moveit_config/<robot>/config/moveit_controllers.yaml`:

```yaml
moveit_simple_controller_manager:
  controller_names:
    - arm_controller

  arm_controller:
    type: FollowJointTrajectory
    action_ns: follow_joint_trajectory
    default: true
    joints:
      - joint1
      - joint2
      ...
```

Most arms work with the default servo + JTC pipeline. For force-controlled / compliant motion,
look at MoveIt Servo + a compliance controller.

## 9. Real-time considerations

For 1 kHz control loops the controller_manager process must:

- Run with real-time priority (SCHED_FIFO).
- Pin to dedicated cores (`taskset` or `cpuset`).
- Use `mlockall` to prevent paging.
- Avoid memory allocation, logging, and locking in `read`/`write`.

A typical setup:

```bash
# /etc/security/limits.d/realtime.conf
@realtime - rtprio 99
@realtime - memlock unlimited
```

```python
# In the launch file, pre-configure ulimits via prefix:
Node(
    package='controller_manager', executable='ros2_control_node',
    prefix=['chrt -f 80'],  # SCHED_FIFO priority 80
    ...
)
```

For micro-second jitter requirements, consider PREEMPT_RT kernel and Cyclonedds with shared
memory (Iceoryx).

## 10. Anti-patterns

- **Allocating in `read`/`write`.** Causes page faults, breaks RT determinism. Pre-allocate
  everything in `on_configure`.
- **Logging at high rate from `read`/`write`.** Even `RCLCPP_DEBUG_THROTTLE` does string
  formatting. Move logging to a separate non-RT thread that polls a lock-free queue.
- **Loading two controllers that claim the same joints simultaneously.** controller_manager
  rejects the second. Use `switch_controllers` for hot-swap.
- **Mismatch between `joint_names` in trajectory goal and controller config.** INVALID_JOINTS
  rejection. Always read the config to construct the goal.
- **Forgetting to load `joint_state_broadcaster`.** Then `/joint_states` never publishes,
  TF chain breaks, RViz shows nothing.
- **Putting hardware-specific code in the controller (instead of `hardware_interface`).**
  Defeats the purpose of the abstraction. Controllers stay vendor-neutral; hardware interfaces
  encapsulate vendor SDK calls.
- **Running controller_manager at 1 kHz on a non-RT kernel without isolation.** Jitter spikes
  cause the loop to miss deadlines, motors twitch. Either reduce the rate or fix the kernel.
