# Launch System

ROS 2 launch files are Python programs that describe a *system topology* — which nodes run with
which parameters, in what order, and on what conditions. They run once at startup and exit.
Don't confuse a launch file with a node; it has no spin loop.

## Contents

1. The launch file mental model
2. The minimum useful launch file
3. Node, IncludeLaunchDescription, GroupAction, OpaqueFunction
4. LaunchConfigurations, LaunchArguments, and substitutions
5. Conditions — IfCondition, UnlessCondition
6. Parameter loading — YAML, dict, mixed
7. Composition — ComposableNodeContainer
8. Lifecycle handler events
9. Logging, output redirection, prefix (gdb, valgrind)
10. Anti-patterns

## 1. The launch file mental model

A launch file's `generate_launch_description()` returns a `LaunchDescription` — a *static
description* of actions. The launch system then resolves substitutions, evaluates conditions,
and executes actions. Most actions spawn processes (`Node`, `ExecuteProcess`); some configure
the system (`SetEnvironmentVariable`, `LogInfo`).

Crucial: **the file runs at launch time, not at node runtime**. Code in `generate_launch_description`
runs once, in the launch process, before any node starts. Don't put `rclpy.init()` or sleep
loops there.

When the file needs runtime resolution of a `LaunchConfiguration` (because the value was passed
on the command line), wrap that logic in `OpaqueFunction` — see §4.

## 2. The minimum useful launch file

```python
# launch/bringup.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_perception',
            executable='perception_node',
            name='perception',
            namespace='vision',
            parameters=[{'rate_hz': 30.0, 'frame_id': 'camera_link'}],
            remappings=[('image_in', 'camera/image_raw')],
            output='screen',
        ),
    ])
```

Run with `ros2 launch my_perception bringup.launch.py`. To pass arguments:
`ros2 launch my_perception bringup.launch.py log_level:=debug`.

`output='screen'` sends stdout/stderr to the terminal. Default is `log` (file only); switching
to `screen` while developing saves debugging time.

## 3. Node, IncludeLaunchDescription, GroupAction, OpaqueFunction

### Node

```python
Node(
    package='my_pkg',
    executable='my_node',
    name='my_node',                      # node name (overrides default)
    namespace='robot_a',                 # all topics prefixed with /robot_a
    parameters=[                          # list of dicts and/or YAML files
        os.path.join(get_package_share_directory('my_pkg'), 'config', 'params.yaml'),
        {'use_sim_time': use_sim_time},   # override one param
    ],
    remappings=[('cmd_vel', 'robot_a/cmd_vel')],
    arguments=['--ros-args', '--log-level', 'debug'],
    output='screen',
    emulate_tty=True,                    # preserves color in logs
    prefix=['xterm -e gdb -ex run --args'],   # debugger wrapping (rare)
    respawn=True,                        # restart if it dies (only for daemons)
    respawn_delay=2.0,
)
```

### IncludeLaunchDescription — composing launches

Real systems compose multiple launches: `bringup.launch.py` includes `hardware.launch.py`,
`sensors.launch.py`, `rviz.launch.py`, etc.

```python
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

hardware_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('my_bringup'), 'launch', 'hardware.launch.py')
    ),
    launch_arguments={'robot_id': 'robot_a', 'use_sim_time': 'false'}.items(),
)
```

### GroupAction — apply to a group

```python
from launch_ros.actions import PushRosNamespace
from launch.actions import GroupAction

robot_a = GroupAction([
    PushRosNamespace('robot_a'),
    Node(package='my_pkg', executable='driver', name='driver'),
    Node(package='my_pkg', executable='controller', name='controller'),
])
```

Everything inside the group inherits the namespace. Use this for fleet bringup where each robot
gets its own namespace.

### OpaqueFunction — for runtime decisions

Sometimes the launch file's structure depends on a value that is only known after substitutions
are resolved. `OpaqueFunction` defers the decision:

```python
from launch.actions import OpaqueFunction

def launch_setup(context, *args, **kwargs):
    robot_model = LaunchConfiguration('robot_model').perform(context)
    if robot_model == 'm0609':
        urdf = '/share/m0609/urdf/m0609.urdf.xacro'
    else:
        urdf = '/share/m1013/urdf/m1013.urdf.xacro'
    return [
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': urdf}]),
    ]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('robot_model', default_value='m0609'),
        OpaqueFunction(function=launch_setup),
    ])
```

Without `OpaqueFunction`, you cannot do `if x == 'foo'` on a `LaunchConfiguration` — it's still
a Substitution object, not a string.

## 4. LaunchConfigurations, LaunchArguments, and substitutions

```python
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

# Declare a launchable argument with default and description.
use_sim_time_arg = DeclareLaunchArgument(
    'use_sim_time', default_value='false',
    description='Use Gazebo clock instead of wall clock')

# Read it later (lazy).
use_sim_time = LaunchConfiguration('use_sim_time')

# Use it in Node parameters — works because Node evaluates Substitutions itself.
Node(parameters=[{'use_sim_time': use_sim_time}, ...])

# Compose paths.
config_file = PathJoinSubstitution([
    FindPackageShare('my_pkg'),
    'config',
    'params.yaml',
])
```

Pass values from the command line:

```bash
ros2 launch my_pkg bringup.launch.py use_sim_time:=true robot_model:=m0609
```

The standard arguments to declare on every bringup launch:

| Arg | Default | Purpose |
|---|---|---|
| `use_sim_time` | `false` | Whether to use the simulation clock. Propagate to *every* node. |
| `namespace` | `''` | Top-level namespace for the whole stack. |
| `log_level` | `info` | Default log level for all nodes. |
| `rviz` | `true` | Whether to launch RViz — useful to disable on headless robots. |
| `<robot_model>` | varies | Which robot variant. Drives URDF/MoveIt config selection. |

## 5. Conditions — IfCondition, UnlessCondition

```python
from launch.conditions import IfCondition, UnlessCondition

Node(
    package='rviz2', executable='rviz2',
    arguments=['-d', rviz_config_file],
    condition=IfCondition(LaunchConfiguration('rviz')),
)

Node(
    package='joy', executable='joy_node',
    condition=UnlessCondition(LaunchConfiguration('headless')),
)
```

Conditions evaluate at launch time. The action either runs in full or doesn't run at all —
there's no "run X with different parameters depending on Y" via condition; for that, use
`OpaqueFunction`.

## 6. Parameter loading — YAML, dict, mixed

A single Node can take multiple parameter sources, merged in order:

```python
Node(
    parameters=[
        '/path/to/defaults.yaml',          # base defaults
        '/path/to/robot_specific.yaml',    # override per robot
        {'use_sim_time': use_sim_time},    # final override from launch arg
    ],
)
```

The YAML must be in `<node_name>: ros__parameters:` form:

```yaml
# config/params.yaml
perception:
  ros__parameters:
    rate_hz: 30.0
    confidence_threshold: 0.7
    frame_id: camera_link
```

If the node is launched with a different `name=` than its default, the YAML key must match the
launched name. A common bug: YAML says `perception_node:` but launch uses `name='perception'` →
parameters silently not applied.

Wildcard `'/**'` can apply parameters to any node in a namespace:

```yaml
/**:
  ros__parameters:
    use_sim_time: true
```

This is the cleanest way to set `use_sim_time` for every node in a launch.

## 7. Composition — ComposableNodeContainer

For high-rate intra-process pipelines (see `node-design.md` §Composable Nodes):

```python
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

vision_container = ComposableNodeContainer(
    name='vision_container',
    namespace='',
    package='rclcpp_components',
    executable='component_container_mt',     # 'component_container' for single-threaded
    composable_node_descriptions=[
        ComposableNode(
            package='image_proc',
            plugin='image_proc::DebayerNode',
            name='debayer',
            parameters=[{'use_intra_process_comms': True}],
        ),
        ComposableNode(
            package='my_perception',
            plugin='my_perception::DetectorNode',
            name='detector',
            remappings=[('image', 'image_color')],
            parameters=[{'use_intra_process_comms': True}],
        ),
    ],
    output='screen',
)
```

Pick `component_container_mt` (multithreaded) unless you have a strong reason for the single-
threaded variant — it's almost always what you want.

## 8. Lifecycle handler events

For lifecycle nodes, drive transitions automatically from the launch file:

```python
from launch_ros.actions import LifecycleNode
from launch.actions import RegisterEventHandler, EmitEvent
from launch.events.process import ProcessStarted
from lifecycle_msgs.msg import Transition

camera = LifecycleNode(
    package='camera_driver', executable='camera_driver',
    name='camera', namespace='',
)

# When the camera process is up, configure it.
configure_camera = RegisterEventHandler(
    OnProcessStart(
        target_action=camera,
        on_start=[EmitEvent(event=ChangeState(
            lifecycle_node_matcher=matches_action(camera),
            transition_id=Transition.TRANSITION_CONFIGURE,
        ))],
    ),
)
```

This pattern is repeated in Nav2 and ros2_control launch files. For a hand-rolled lifecycle
service node, use `ros2 lifecycle set` from the shell instead.

## 9. Logging, output redirection, prefix

```python
Node(
    output='screen',                              # or 'log' (default), 'both'
    emulate_tty=True,                             # preserve color codes
    arguments=['--ros-args', '--log-level',       # set this node's log level
               LaunchConfiguration('log_level')],
    prefix=['xterm -e gdb -ex run --args'],       # debugger wrapping
)
```

Useful prefix patterns:

- `['stdbuf -oL']` — line-buffer stdout so logs flush immediately.
- `['valgrind --leak-check=full']` — memory check (slow).
- `['gdb -batch -ex run -ex bt --args']` — auto-print backtrace on crash.

## 10. Anti-patterns

- **Putting `time.sleep(N)` in `generate_launch_description`.** The launch system has its own
  delay mechanism — `TimerAction(period=N, actions=[...])`. Sleep blocks the launch process and
  prevents Ctrl-C from working cleanly.
- **Doing logic on `LaunchConfiguration` outside `OpaqueFunction`.** The value is a Substitution,
  not a string. `if my_config == 'foo'` is always False. Wrap the logic in OpaqueFunction.
- **Hardcoding absolute paths to URDF/RViz/YAML files.** Use `FindPackageShare` and
  `PathJoinSubstitution`. Hardcoded paths break on any other machine.
- **Forgetting to install the launch file in `setup.py` data_files / `CMakeLists.txt` install.**
  The launch builds, but `ros2 launch my_pkg bringup.launch.py` fails with "file not found".
- **Mixing Python and XML launch files in the same package.** XML launch (legacy ROS 1 style) is
  supported but limited. Prefer Python; it's strictly more powerful.
- **Including the same launch twice with no namespace.** Two robot drivers with the same name
  collide on the DDS graph and one silently fails. Use `GroupAction` + `PushRosNamespace`.
- **Putting non-trivial logic at module top-level instead of inside `generate_launch_description`.**
  Top-level runs at import time, before `ros2 launch` finishes parsing arguments. Anything that
  needs the resolved arguments belongs in the function.
- **Using `Node(name=...)` to remap topics.** That sets the *node name*, not the topic name. Use
  `remappings=[(old, new)]`.
