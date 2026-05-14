# RViz2

Configuration of RViz2 plus how to write your own Display, Panel, and Tool plugins. RViz is the
authoritative debugging surface for ROS 2; mastering it pays off across every project.

## Contents

1. RViz mental model — Displays, Panels, Tools, Views
2. Working with `.rviz` configuration files
3. Launch RViz from a launch file
4. Common Display types and their gotchas
5. Writing a custom Display plugin (C++)
6. Writing a custom Panel plugin (C++)
7. Writing a custom Tool plugin (C++)
8. RViz from Python — limited, but possible
9. Anti-patterns

## 1. RViz mental model — Displays, Panels, Tools, Views

RViz is built on Ogre (3D rendering) wrapped in Qt (UI). Four extension types:

| Type | What it does | Examples |
|---|---|---|
| **Display** | Subscribes to a topic and renders it in the 3D view. | RobotModel, PointCloud2, Image, MarkerArray. |
| **Panel** | A Qt widget docked into the main window. | Tool Properties, Views, your custom control panel. |
| **Tool** | Mouse interaction in the 3D view (click, drag). | "2D Pose Estimate", "Publish Point". |
| **View** | Camera control type. | Orbit, FPS, TopDownOrtho, ThirdPerson. |

A `.rviz` file is a YAML serialization of the user's chosen Displays + Panels + View
configuration. Save / reopen it to recover a session.

## 2. Working with `.rviz` configuration files

Generate a config interactively in RViz, then save it:

```
File → Save Config As → my_robot.rviz
```

Open it from the command line:

```bash
ros2 run rviz2 rviz2 -d /path/to/my_robot.rviz
```

The file is YAML and it's reasonable to edit by hand. Key sections:

```yaml
Panels:
  - Class: rviz_common/Displays
  - Class: rviz_common/Views
  - Class: rviz_common/Selection
Visualization Manager:
  Class: ""
  Displays:
    - Class: rviz_default_plugins/Grid
      Enabled: true
      Plane Cell Count: 10
    - Class: rviz_default_plugins/RobotModel
      Description Topic:
        Value: /robot_description
        Durability Policy: Transient Local
        Reliability Policy: Reliable
      Enabled: true
    - Class: rviz_default_plugins/PointCloud2
      Topic:
        Value: /lidar/points
        Durability Policy: Volatile
        Reliability Policy: Best Effort
      Style: Points
      Size (m): 0.02
      Color Transformer: Intensity
  Global Options:
    Fixed Frame: base_link
    Frame Rate: 30
  Tools:
    - Class: rviz_default_plugins/Interact
    - Class: rviz_default_plugins/MoveCamera
    - Class: rviz_default_plugins/SetInitialPose
      Topic:
        Value: /initialpose
        Durability Policy: Volatile
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 3.0
```

Pin this file in your bringup package's `rviz/` directory and ship it via `install(DIRECTORY rviz
...)`.

## 3. Launch RViz from a launch file

```python
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

rviz_config = PathJoinSubstitution([
    FindPackageShare('my_bringup'), 'rviz', 'my_robot.rviz'
])

Node(
    package='rviz2', executable='rviz2', name='rviz2',
    arguments=['-d', rviz_config, '--ros-args', '--log-level', 'warn'],
    parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    condition=IfCondition(LaunchConfiguration('rviz')),
    output='screen',
)
```

`use_sim_time` matters even for RViz — without it, time-stamped data from sim looks like it's
from years in the future and is silently rejected by RobotModel and TF displays.

`--log-level warn` suppresses noisy info logs ("Subscribed to topic ...") that pollute the
terminal.

## 4. Common Display types and their gotchas

### RobotModel

Visualizes a URDF. Two ways to provide it:

```yaml
- Class: rviz_default_plugins/RobotModel
  Description Topic:
    Value: /robot_description     # subscribe to a topic — usual choice
    Durability Policy: Transient Local
```

The `Transient Local` durability is essential — `/robot_description` is published once at
bringup with TRANSIENT_LOCAL QoS. A VOLATILE subscriber misses it and shows nothing.

### TF

Renders the TF tree. The single most useful debug display.

```yaml
- Class: rviz_default_plugins/TF
  Frame Timeout: 15
  Show Names: true
  Show Axes: true
  Tree:
    base_link:
      lidar_link: {}
      camera_link: {}
```

If a frame doesn't appear, check `ros2 run tf2_tools view_frames` to confirm the publisher.

### PointCloud2

```yaml
- Class: rviz_default_plugins/PointCloud2
  Topic:
    Value: /points
    Durability Policy: Volatile
    Reliability Policy: Best Effort       # match the LiDAR driver's QoS
  Style: Points
  Size (m): 0.02
  Color Transformer: Intensity            # FlatColor / Intensity / RGB8 / AxisColor
  Decay Time: 0.0
```

QoS mismatch is the most common reason "no points show up". LiDAR drivers typically publish
BEST_EFFORT; the default subscriber QoS is RELIABLE.

### Image

```yaml
- Class: rviz_default_plugins/Image
  Topic:
    Value: /camera/image_raw
    Durability Policy: Volatile
    Reliability Policy: Best Effort
  Transport Hint: raw                      # or 'compressed', 'theora'
```

For compressed transports you also need `image_transport_plugins` installed
(`apt install ros-${ROS_DISTRO}-image-transport-plugins`).

### Marker / MarkerArray

The catch-all for custom debug visualization.

```python
from visualization_msgs.msg import Marker, MarkerArray

m = Marker()
m.header.frame_id = 'base_link'
m.header.stamp = self.get_clock().now().to_msg()
m.ns = 'targets'
m.id = 0
m.type = Marker.SPHERE
m.action = Marker.ADD
m.pose.position.x = 0.5
m.pose.orientation.w = 1.0
m.scale.x = m.scale.y = m.scale.z = 0.1
m.color.r = 1.0
m.color.a = 1.0
m.lifetime.sec = 0  # forever

self.marker_pub.publish(m)
```

The `ns + id` pair is the marker's identity; publish a new marker with the same `(ns, id)` to
update, with `action=DELETE` to remove. Use `MarkerArray` to publish many at once.

### Path

For trajectory visualization. Subscribe to `nav_msgs/Path`. Useful for showing planned vs
executed trajectories side-by-side (different colors, different topics).

## 5. Writing a custom Display plugin (C++)

Use case: you want to render something specific to your robot — e.g., the workspace bounds, a
heatmap of force, a custom annotation. Default Markers handle 90% of cases; write a custom
Display only when:

- Performance matters (rendering 1M+ points; Markers can't keep up)
- You need custom interaction (hover tooltips, click-to-select)
- You want a property panel with custom widgets

### Skeleton

```cpp
// my_workspace_display.hpp
#pragma once
#include <rviz_common/display.hpp>
#include <rviz_rendering/objects/shape.hpp>
#include <rviz_common/properties/float_property.hpp>
#include <rviz_common/properties/color_property.hpp>
#include <my_msgs/msg/workspace_bounds.hpp>

namespace my_workspace_display {

class WorkspaceDisplay
  : public rviz_common::MessageFilterDisplay<my_msgs::msg::WorkspaceBounds> {
  Q_OBJECT
 public:
  WorkspaceDisplay();
  ~WorkspaceDisplay() override;

  void onInitialize() override;
  void reset() override;

 private Q_SLOTS:
  void updateColor();

 protected:
  void processMessage(my_msgs::msg::WorkspaceBounds::ConstSharedPtr msg) override;

 private:
  std::shared_ptr<rviz_rendering::Shape> shape_;
  rviz_common::properties::ColorProperty * color_prop_;
  rviz_common::properties::FloatProperty * alpha_prop_;
};

}  // namespace my_workspace_display
```

```cpp
// my_workspace_display.cpp
#include "my_workspace_display.hpp"
#include <pluginlib/class_list_macros.hpp>

namespace my_workspace_display {

WorkspaceDisplay::WorkspaceDisplay() {
  color_prop_ = new rviz_common::properties::ColorProperty(
      "Color", QColor(0, 255, 0), "Workspace box color",
      this, SLOT(updateColor()));
  alpha_prop_ = new rviz_common::properties::FloatProperty(
      "Alpha", 0.3, "Transparency", this);
}

WorkspaceDisplay::~WorkspaceDisplay() = default;

void WorkspaceDisplay::onInitialize() {
  MFDClass::onInitialize();
  shape_ = std::make_shared<rviz_rendering::Shape>(
      rviz_rendering::Shape::Cube, scene_manager_, scene_node_);
}

void WorkspaceDisplay::reset() { MFDClass::reset(); }

void WorkspaceDisplay::processMessage(
    my_msgs::msg::WorkspaceBounds::ConstSharedPtr msg) {
  Ogre::Vector3 pos(msg->center.x, msg->center.y, msg->center.z);
  Ogre::Vector3 scale(msg->size.x, msg->size.y, msg->size.z);
  shape_->setPosition(pos);
  shape_->setScale(scale);
  updateColor();
}

void WorkspaceDisplay::updateColor() {
  QColor c = color_prop_->getColor();
  shape_->setColor(c.redF(), c.greenF(), c.blueF(), alpha_prop_->getFloat());
}

}  // namespace my_workspace_display

PLUGINLIB_EXPORT_CLASS(
    my_workspace_display::WorkspaceDisplay, rviz_common::Display)
```

### CMakeLists.txt

```cmake
find_package(rviz_common REQUIRED)
find_package(rviz_rendering REQUIRED)
find_package(pluginlib REQUIRED)

set(CMAKE_AUTOMOC ON)
qt5_wrap_cpp(MOC_FILES include/my_workspace_display/my_workspace_display.hpp)

add_library(${PROJECT_NAME} SHARED
  src/my_workspace_display.cpp
  ${MOC_FILES})

target_link_libraries(${PROJECT_NAME}
  rviz_common::rviz_common
  rviz_rendering::rviz_rendering
  Qt5::Widgets)

ament_target_dependencies(${PROJECT_NAME} pluginlib my_msgs)

# Plugin description file (see below)
pluginlib_export_plugin_description_file(rviz_common plugins.xml)

install(TARGETS ${PROJECT_NAME} LIBRARY DESTINATION lib)
install(FILES plugins.xml DESTINATION share/${PROJECT_NAME})
```

### plugins.xml

```xml
<library path="my_workspace_display">
  <class name="my_workspace_display/WorkspaceDisplay"
         type="my_workspace_display::WorkspaceDisplay"
         base_class_type="rviz_common::Display">
    <description>Visualize workspace bounds.</description>
    <message_type>my_msgs/msg/WorkspaceBounds</message_type>
  </class>
</library>
```

After `colcon build` and re-sourcing, your display appears in the "Add" dialog under
`my_workspace_display`.

## 6. Writing a custom Panel plugin (C++)

A Panel is a Qt widget docked into the main RViz window. Use it for control UIs that subscribe
to status and publish commands.

```cpp
// control_panel.hpp
#pragma once
#include <rviz_common/panel.hpp>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <QPushButton>

namespace my_panels {

class ControlPanel : public rviz_common::Panel {
  Q_OBJECT
 public:
  explicit ControlPanel(QWidget * parent = nullptr);

  void onInitialize() override;

 private Q_SLOTS:
  void onStartClicked();

 private:
  std::shared_ptr<rclcpp::Node> node_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr cmd_pub_;
  QPushButton * start_button_;
};

}  // namespace my_panels
```

```cpp
// control_panel.cpp
#include "control_panel.hpp"
#include <QVBoxLayout>
#include <pluginlib/class_list_macros.hpp>

namespace my_panels {

ControlPanel::ControlPanel(QWidget * parent) : rviz_common::Panel(parent) {
  start_button_ = new QPushButton("Start", this);
  auto * layout = new QVBoxLayout;
  layout->addWidget(start_button_);
  setLayout(layout);
  connect(start_button_, &QPushButton::clicked, this, &ControlPanel::onStartClicked);
}

void ControlPanel::onInitialize() {
  // getDisplayContext()->getRosNodeAbstraction() gives access to a node.
  auto raw_node = getDisplayContext()
      ->getRosNodeAbstraction().lock()->get_raw_node();
  cmd_pub_ = raw_node->create_publisher<std_msgs::msg::String>("ui/cmd", 10);
}

void ControlPanel::onStartClicked() {
  std_msgs::msg::String msg;
  msg.data = "start";
  cmd_pub_->publish(msg);
}

}  // namespace my_panels

PLUGINLIB_EXPORT_CLASS(my_panels::ControlPanel, rviz_common::Panel)
```

`plugins.xml` adds:

```xml
<class name="my_panels/ControlPanel"
       type="my_panels::ControlPanel"
       base_class_type="rviz_common::Panel">
  <description>Panel with a start button.</description>
</class>
```

After build, "Panels → Add New Panel" lists `my_panels/ControlPanel`.

## 7. Writing a custom Tool plugin (C++)

A Tool handles mouse events in the 3D viewport. Use it for click-to-pose, click-to-pick, etc.
The most common pattern is a click that publishes a `geometry_msgs/PoseStamped`.

```cpp
// click_pick_tool.hpp
#pragma once
#include <rviz_common/tool.hpp>
#include <rviz_common/properties/string_property.hpp>
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>

namespace my_tools {

class ClickPickTool : public rviz_common::Tool {
  Q_OBJECT
 public:
  ClickPickTool();
  void onInitialize() override;
  void activate() override {}
  void deactivate() override {}
  int processMouseEvent(rviz_common::ViewportMouseEvent & event) override;

 private:
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr pub_;
  rviz_common::properties::StringProperty * topic_prop_;
};

}  // namespace my_tools
```

The `processMouseEvent` returns `Render` to keep redrawing while dragging, `Finished` when done.
See `rviz_default_plugins/tools/pose/SetInitialPoseTool` for a reference.

## 8. RViz from Python — limited, but possible

There is no official Python plugin API for Displays/Panels/Tools — they must be C++. However,
you can:

- **Drive RViz from Python** by publishing Markers, MarkerArrays, Images, and Paths.
- **Save and load `.rviz` configs from Python** (they're just YAML; use `pyyaml`).
- **Programmatically launch RViz** with different configs from a Python launch file.

For "Python plugin" in spirit, write a Python node that publishes Markers — it's almost as
flexible and 10× easier to maintain.

## 9. Anti-patterns

- **Using QoS Reliable for sensor topic displays.** LiDAR / camera publishers are BEST_EFFORT.
  The display silently shows nothing. Set Reliability Policy = Best Effort.
- **Forgetting Durability Transient Local for `/robot_description` and `/tf_static`.** They're
  latched; VOLATILE subscribers miss them on connect.
- **Hardcoding paths in `.rviz` configs.** RViz writes absolute paths to mesh files. When
  shipping the config to other machines, replace them with `package://<pkg>/...` URIs.
- **Loading a huge URDF with thousands of meshes.** RViz becomes unresponsive. Use simplified
  meshes for `<visual>` (decimate to 10k triangles) and full meshes only for `<collision>`.
- **Custom Display rendering 1 frame per ROS message.** If messages arrive at 100 Hz, you'll
  burn frames waiting for vsync. Throttle the renderer to 30 Hz inside `processMessage`.
- **Forgetting to install `plugins.xml` in CMakeLists.txt.** Plugin doesn't appear in the Add
  dialog. Always `install(FILES plugins.xml DESTINATION share/${PROJECT_NAME})` and
  `pluginlib_export_plugin_description_file(rviz_common plugins.xml)`.
