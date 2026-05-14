# Workspace and Build

How ROS 2 workspaces, packages, and the build system fit together. Read this before creating
a new package, debugging a build error, or onboarding a new repo.

## Contents

1. The colcon workspace mental model
2. Creating a workspace from scratch
3. Anatomy of a `package.xml`
4. Anatomy of `CMakeLists.txt` (ament_cmake)
5. Anatomy of `setup.py` / `setup.cfg` (ament_python)
6. The four package types
7. `colcon build` — common flags and what they mean
8. `rosdep` — what it is, when to run it
9. Overlays, underlays, and sourcing order
10. Common build errors, decoded
11. CI strategy

## 1. The colcon workspace mental model

A colcon workspace is a directory with three siblings that you mostly never touch by hand:

```
my_ws/
├── src/         ← your packages (and cloned dependencies) live here
├── build/       ← intermediate build artifacts (per-package). Disposable.
├── install/     ← the merged final artifacts. This is what you source.
└── log/         ← build and test logs. Inspect when things break.
```

`colcon build` reads `src/`, runs each package's build system (CMake or Python setup.py), and
populates `build/` and `install/`. `source install/setup.bash` then puts the workspace's
binaries, Python modules, and resource paths on your shell's environment.

Two iron rules:

1. **Source `install/setup.bash`, never `build/setup.bash`.** The build tree is incomplete; many
   files are missing or stale. Sourcing it leads to mysterious "package not found" errors.
2. **Never edit anything in `build/` or `install/` by hand.** Anything you change is overwritten
   on next build. Edits go in `src/`.

## 2. Creating a workspace from scratch

```bash
mkdir -p ~/my_ws/src
cd ~/my_ws

# Source the ROS distro first (e.g., humble, jazzy).
source /opt/ros/$ROS_DISTRO/setup.bash

# Clone packages or create new ones into src/, then:
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

`--symlink-install` links Python files and shared resources from `src/` instead of copying. You
can edit Python in `src/`, restart the node, and the change is live with no rebuild. (For C++
nodes you still need to rebuild — `--symlink-install` doesn't change C++ semantics.)

Add `source ~/my_ws/install/setup.bash` to `~/.bashrc` so every new terminal has the workspace
on its environment automatically.

## 3. Anatomy of a `package.xml`

`package.xml` is the **rosdep-readable** manifest. Format 3 is current.

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
            schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>my_perception</name>
  <version>0.1.0</version>
  <description>Object detection node for the lab arm.</description>
  <maintainer email="me@example.com">Hoon</maintainer>
  <license>Apache-2.0</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <!-- runtime dependencies — must be both build and exec -->
  <depend>rclcpp</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>my_robot_interfaces</depend>

  <!-- build-time only (e.g., test frameworks, code generators) -->
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Key elements:

- **`<depend>` vs separate `<build_depend>`/`<exec_depend>`.** Use `<depend>` when both apply (the
  common case). Separate them only when they truly differ — e.g., `rosidl_default_generators`
  is build-only, `rosidl_default_runtime` is exec-only.
- **`<member_of_group>rosidl_interface_packages</member_of_group>`** is required for any package
  that defines `.msg`/`.srv`/`.action` files. Without it, `rosdep install --reinstall` won't pick
  up the message generation toolchain.
- **`<build_type>`** in `<export>` selects the build system: `ament_cmake` (C++ or mixed),
  `ament_python` (pure Python), `cmake` (plain CMake without ament).

## 4. Anatomy of `CMakeLists.txt` (ament_cmake)

Minimum viable `CMakeLists.txt` for a C++ node with a custom message dependency:

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_perception)

# Default to C++17 — required by rclcpp.
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies — match every <depend> in package.xml.
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(my_robot_interfaces REQUIRED)

# An executable node.
add_executable(perception_node src/perception_node.cpp)
ament_target_dependencies(perception_node
  rclcpp std_msgs sensor_msgs my_robot_interfaces)

# Install the executable to lib/<package> so `ros2 run` finds it.
install(TARGETS perception_node DESTINATION lib/${PROJECT_NAME})

# Install resource directories.
install(DIRECTORY launch config rviz urdf
  DESTINATION share/${PROJECT_NAME}
  OPTIONAL                       # tolerate missing dirs during incremental dev
)

# Tests
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

Composable node (component) variant:

```cmake
add_library(perception_component SHARED src/perception_component.cpp)
ament_target_dependencies(perception_component rclcpp rclcpp_components ...)
rclcpp_components_register_nodes(perception_component "mypkg::PerceptionComponent")
install(TARGETS perception_component
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)
```

## 5. Anatomy of `setup.py` / `setup.cfg` (ament_python)

For pure-Python packages, use `ament_python`:

```python
# setup.py
from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'my_behavior'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        (os.path.join('share', package_name), ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Hoon',
    maintainer_email='me@example.com',
    description='Behavior nodes for the lab arm.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pick_place = my_behavior.pick_place_node:main',
            'state_machine = my_behavior.state_machine:main',
        ],
    },
)
```

`setup.cfg`:

```ini
[develop]
script_dir=$base/lib/my_behavior

[install]
install_scripts=$base/lib/my_behavior
```

The `console_scripts` entries are what `ros2 run my_behavior pick_place` invokes. Each entry is
`<command> = <module>:<function>`. The function (usually `main`) gets called with `args=None`.

Common mistake: forgetting the `data_files` entry for `package.xml` and `resource/<pkg>` — the
package builds but `ros2 pkg list` doesn't show it, and `ros2 launch my_behavior foo.py` fails
with "package not found".

## 6. The four package types

| Type | `<build_type>` | Use for |
|---|---|---|
| **ament_cmake** | `ament_cmake` | C++ nodes, mixed C++/Python, anything with native code. The default for performance-critical work. |
| **ament_python** | `ament_python` | Pure Python nodes. Faster iteration with `--symlink-install`. |
| **ament_cmake_python** | `ament_cmake` (with `ament_python_install_package`) | Mostly C++ but ships some Python helpers. Less common. |
| **rosidl_interface_packages** | `ament_cmake` (with `rosidl_generate_interfaces`) | Custom messages/services/actions only. Must include `<member_of_group>rosidl_interface_packages</member_of_group>`. |

Don't mix: a single package should have C++ source *or* Python source, not both. If you have
both, split into two packages with the same prefix (`my_pkg_cpp`, `my_pkg_py`) or use
`ament_cmake_python`.

## 7. `colcon build` — common flags and what they mean

```bash
# Build all packages, fully parallel.
colcon build

# Edit Python without rebuilding (only useful for ament_python / launch / config).
colcon build --symlink-install

# Build only one package and its dependencies (huge time saver).
colcon build --packages-up-to my_perception
colcon build --packages-select my_perception   # just this package, no deps

# Pass CMake args to all packages.
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# Show all output (default suppresses unless build fails).
colcon build --event-handlers console_direct+

# Limit parallelism (large C++ packages OOM with full -j).
MAKEFLAGS="-j2" colcon build --executor sequential

# Treat warnings as errors (CI gate).
colcon build --cmake-args -DCMAKE_CXX_FLAGS=-Werror

# Clean rebuild.
rm -rf build install log && colcon build --symlink-install
```

`--executor sequential` builds packages one at a time but can still parallelize *within* a
package (Make/Ninja). Use this when memory is tight.

For incremental development: `colcon build --packages-up-to <changed_pkg> --symlink-install` is
the daily driver.

## 8. `rosdep` — what it is, when to run it

`rosdep` reads `package.xml` files in your workspace, looks up each `<depend>` against a YAML
database, and apt-installs (or pip-installs) the corresponding system package.

```bash
# First-time setup on a machine. Idempotent — re-running is fine.
sudo rosdep init
rosdep update

# In the workspace root, after cloning new packages or seeing a "Could not find" CMake error.
rosdep install --from-paths src --ignore-src -r -y
```

Flags:

- `--from-paths src` — search workspace `src/` for `package.xml`.
- `--ignore-src` — don't try to apt-install packages you have in source.
- `-r` — keep going if some deps fail (continue on errors).
- `-y` — assume yes.

If `rosdep` complains about an unknown key, add it to `/etc/ros/rosdep/sources.list.d/` or
`~/.config/rosdistro/` — but 99% of the time it just works.

When `rosdep install` runs `sudo -H apt-get install` and that prompts for a password it doesn't
have, the installs silently fail. Either run with `sudo -v` first to cache credentials, or add
the user to a passwordless-sudo group for apt.

## 9. Overlays, underlays, and sourcing order

A workspace is an *overlay* on top of an *underlay*. The overlay's packages take precedence
when names collide. Multiple workspaces compose:

```bash
source /opt/ros/jazzy/setup.bash         # underlay (system ROS)
source ~/cobot_ws/install/setup.bash      # overlay 1 (Doosan workspace)
source ~/my_ws/install/setup.bash         # overlay 2 (your project)
```

Iron rules:

1. **Source the underlay before building the overlay.** Otherwise the overlay's `find_package`
   calls fail.
2. **Don't source the overlay you're about to rebuild.** Re-sourcing after build is fine, but
   sourcing before rebuilding can confuse CMake about installed paths.
3. **Source order matters.** `my_ws` overrides `cobot_ws` overrides `/opt/ros`. Put your
   workspace last in `.bashrc`.

If you see `Could not find a package configuration file provided by "X"`:

- Did you source the underlay containing X?
- If X is in your workspace, did you build it first (`colcon build --packages-select X`)?
- Did you re-source the overlay after building?

## 10. Common build errors, decoded

| Error message | Real meaning | Fix |
|---|---|---|
| `Could not find a package configuration file provided by "X"` | CMake can't locate package X. | `rosdep install --from-paths src --ignore-src -r -y`, or `source` the underlay containing X. |
| `Package 'X' not found` (at runtime, not build) | The package built but you haven't sourced the overlay. | `source install/setup.bash`. |
| `ModuleNotFoundError: No module named 'X.msg'` (Python) | Custom message package missing `<exec_depend>rosidl_default_runtime</exec_depend>`. | Add it to package.xml, rebuild. |
| `Multiple packages with the same name` | Duplicate `package.xml` somewhere. Often a leftover from a moved/renamed dir. | `colcon list --packages-select X` to find both, delete the wrong one. |
| `c++: fatal error: Killed signal terminated program cc1plus` | OOM during compile (heavy C++ template / debug build). | `MAKEFLAGS="-j2" colcon build` or add swap. |
| `error: 'ament_cmake_python' was not declared` | Missing `find_package(ament_cmake_python REQUIRED)` in CMakeLists. | Add it. |
| Python entry-point not found at `ros2 run` | Forgot to install `resource/<pkg>` or `package.xml` in `data_files`, or `entry_points` typo. | Check setup.py `data_files` and `entry_points`. |
| Build succeeds, node runs, but `ros2 pkg list` doesn't show it | Same as above — `data_files` for `resource/<pkg>` is missing. | Add it. |
| `Symlink install` flag has no effect on C++ changes | Expected — `--symlink-install` only affects Python and shared resources, not compiled artifacts. | Rebuild for C++ changes. |
| `ImportError: dynamic module does not define module export function` (custom msg in Python) | Built against a different Python ABI than runtime. Common when switching between `python3.10` and `python3.12` distros. | Clean rebuild after sourcing the right ROS distro. |

## 11. CI strategy

Minimal GitHub Actions for a ROS 2 workspace:

```yaml
name: ROS 2 CI
on: [push, pull_request]
jobs:
  build_and_test:
    runs-on: ubuntu-22.04
    container: ros:humble
    steps:
      - uses: actions/checkout@v4
        with:
          path: src/${{ github.event.repository.name }}

      - name: Install deps
        run: |
          apt update && apt install -y python3-pip python3-colcon-common-extensions
          rosdep update
          rosdep install --from-paths src --ignore-src -r -y

      - name: Build
        run: |
          . /opt/ros/humble/setup.sh
          colcon build --event-handlers console_cohesion+

      - name: Test
        run: |
          . /opt/ros/humble/setup.sh
          . install/setup.sh
          colcon test --event-handlers console_cohesion+
          colcon test-result --verbose
```

Key tips:

- Use the official `ros:<distro>` Docker image — it has the right Python, the right Fast-DDS,
  and rosdep prepopulated.
- `colcon test-result --verbose` is the line that actually fails the job. `colcon test` returns
  0 even if tests fail; `test-result` is what reads the XUnit XML and exits nonzero.
- Cache `~/.ros/rosdep` and the `build/` directory between runs to speed up rebuilds.
