#!/usr/bin/env bash
# create_ros2_package.sh — scaffold a ROS 2 package with sensible defaults.
#
# Usage:
#   create_ros2_package.sh <name> <type> [deps...]
#
# Where:
#   <name>  package name (snake_case)
#   <type>  one of: ament_cmake | ament_python | rosidl
#   [deps]  additional <depend> entries beyond the defaults
#
# Examples:
#   create_ros2_package.sh my_perception ament_cmake rclcpp sensor_msgs
#   create_ros2_package.sh my_behavior ament_python rclpy std_msgs
#   create_ros2_package.sh my_robot_interfaces rosidl

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <name> <ament_cmake|ament_python|rosidl> [deps...]" >&2
  exit 1
fi

NAME="$1"
TYPE="$2"
shift 2
EXTRA_DEPS=("$@")

if [[ ! "$NAME" =~ ^[a-z][a-z0-9_]*$ ]]; then
  echo "Package name must be snake_case (lowercase, digits, underscores)." >&2
  exit 1
fi

if [[ -d "$NAME" ]]; then
  echo "Directory '$NAME' already exists." >&2
  exit 1
fi

mkdir -p "$NAME"
cd "$NAME"

# package.xml — common header
cat > package.xml <<EOF
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd"
            schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>${NAME}</name>
  <version>0.1.0</version>
  <description>TODO: package description.</description>
  <maintainer email="me@example.com">Me</maintainer>
  <license>Apache-2.0</license>

EOF

case "$TYPE" in
  ament_cmake)
    cat >> package.xml <<EOF
  <buildtool_depend>ament_cmake</buildtool_depend>

  <depend>rclcpp</depend>
EOF
    ;;
  ament_python)
    cat >> package.xml <<EOF
  <buildtool_depend>ament_python</buildtool_depend>

  <depend>rclpy</depend>
EOF
    ;;
  rosidl)
    cat >> package.xml <<EOF
  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>rosidl_default_generators</buildtool_depend>

  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>
  <exec_depend>rosidl_default_runtime</exec_depend>
  <member_of_group>rosidl_interface_packages</member_of_group>
EOF
    ;;
  *)
    echo "Unknown type: $TYPE" >&2
    exit 1
    ;;
esac

for d in "${EXTRA_DEPS[@]}"; do
  echo "  <depend>${d}</depend>" >> package.xml
done

cat >> package.xml <<EOF

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
EOF

case "$TYPE" in
  ament_cmake|rosidl)
    echo "    <build_type>ament_cmake</build_type>" >> package.xml ;;
  ament_python)
    echo "    <build_type>ament_python</build_type>" >> package.xml ;;
esac

cat >> package.xml <<EOF
  </export>
</package>
EOF

# Per-type scaffolding.
case "$TYPE" in
  ament_cmake)
    mkdir -p src include/"$NAME" launch config
    cat > CMakeLists.txt <<EOF
cmake_minimum_required(VERSION 3.8)
project(${NAME})

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
EOF
    for d in "${EXTRA_DEPS[@]}"; do
      echo "find_package(${d} REQUIRED)" >> CMakeLists.txt
    done
    cat >> CMakeLists.txt <<EOF

# add_executable(${NAME}_node src/${NAME}_node.cpp)
# ament_target_dependencies(${NAME}_node rclcpp ${EXTRA_DEPS[*]})
# install(TARGETS ${NAME}_node DESTINATION lib/\${PROJECT_NAME})

install(DIRECTORY launch config
  DESTINATION share/\${PROJECT_NAME}
  OPTIONAL)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
EOF
    ;;

  ament_python)
    mkdir -p "$NAME" launch config resource test
    touch "${NAME}/__init__.py"
    touch "resource/${NAME}"

    cat > setup.py <<EOF
from setuptools import setup
from glob import glob
import os

package_name = '${NAME}'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Me',
    maintainer_email='me@example.com',
    description='TODO: package description.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # 'my_node = ${NAME}.my_node:main',
        ],
    },
)
EOF

    cat > setup.cfg <<EOF
[develop]
script_dir=\$base/lib/${NAME}

[install]
install_scripts=\$base/lib/${NAME}
EOF
    ;;

  rosidl)
    mkdir -p msg srv action
    cat > CMakeLists.txt <<EOF
cmake_minimum_required(VERSION 3.8)
project(${NAME})

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# Add your interface files here, then re-build.
rosidl_generate_interfaces(\${PROJECT_NAME}
  # "msg/MyMessage.msg"
  # "srv/MyService.srv"
  # "action/MyAction.action"
  DEPENDENCIES std_msgs geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
EOF
    ;;
esac

echo "Created package: $NAME (type: $TYPE)"
echo
echo "Next steps:"
echo "  cd $(pwd)"
echo "  # add source files / msg defs"
echo "  cd ../.."
echo "  rosdep install --from-paths src --ignore-src -r -y"
echo "  colcon build --packages-select $NAME --symlink-install"
