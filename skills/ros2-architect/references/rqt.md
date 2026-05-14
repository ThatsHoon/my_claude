# rqt — Plugin Development

rqt is a Qt-based plugin host. It loads "perspective" files that compose multiple plugins into
a debugging dashboard — `rqt_graph` (DDS topology), `rqt_plot` (live data plots), `rqt_console`
(log viewer), `rqt_topic` (topic introspection), and many others. It's also an ideal place to
ship custom operator UIs that don't deserve to live in RViz.

## Contents

1. rqt mental model — plugins, perspectives, dashboards
2. Built-in plugins worth knowing
3. Writing a Python rqt plugin (the common case)
4. Writing a C++ rqt plugin
5. python_qt_binding — the Qt abstraction layer
6. Wiring rqt plugin into a node — the right pattern
7. Distributing your plugin
8. Anti-patterns

## 1. rqt mental model — plugins, perspectives, dashboards

| Concept | What it is |
|---|---|
| **Plugin** | A self-contained Qt widget that does one job (plot a topic, send a service call, etc.). Discovered via pluginlib. |
| **Perspective** | A saved layout of one or more plugins. Stored as `.perspective` JSON. |
| **Standalone** | Run a plugin without the rqt shell: `rqt --standalone rqt_plot`. |

Run rqt:

```bash
rqt              # launches the empty shell; add plugins via Plugins menu
rqt --standalone rqt_graph
rqt -p ~/my.perspective    # load a saved perspective
```

## 2. Built-in plugins worth knowing

| Plugin | What it shows |
|---|---|
| `rqt_graph` | The DDS topology — which nodes publish/subscribe to which topics. The first thing to launch when "wires aren't connecting." |
| `rqt_console` | Live `/rosout` viewer with severity filters. Far better than `tail -f` log files. |
| `rqt_plot` | Live scalar plots from any topic field. Type `topic_name/field` in the textbox. |
| `rqt_topic` | Topic list + introspection (rate, type, subscribers). |
| `rqt_service_caller` | Send a service request without writing code. |
| `rqt_publisher` | Publish a message without writing code. |
| `rqt_param` | Live parameter viewer/editor. |
| `rqt_image_view` | Image topic viewer. |
| `rqt_bag` | Visualize and replay rosbag2 contents. |
| `rqt_tf_tree` | Visualize the live TF tree (alternative to `view_frames`). |
| `rqt_robot_steering` | Joystick-like cmd_vel publisher. |
| `rqt_logger_level` | Per-node log level changer. |

## 3. Writing a Python rqt plugin (the common case)

A Python plugin is the right choice when:

- You need it fast — plumbing is much shorter than C++.
- Your plugin uses widely available Qt widgets (no custom OpenGL).
- You're publishing/subscribing standard messages.

### Skeleton

`my_rqt_plugin/my_plugin.py`:

```python
import os
from ament_index_python.packages import get_package_share_directory
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String


class MyPlugin(Plugin):
    """Sends 'start'/'stop' commands to /ui/cmd and shows last received status."""

    def __init__(self, context):
        super().__init__(context)
        self.setObjectName('MyPlugin')

        # Qt widget + UI from .ui file (designed in Qt Designer).
        self._widget = QWidget()
        ui_file = os.path.join(
            get_package_share_directory('my_rqt_plugin'), 'resource', 'my_plugin.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('MyPluginUi')

        # If multiple instances open, distinguish them.
        if context.serial_number() > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle() + f' ({context.serial_number()})')

        context.add_widget(self._widget)

        # rqt provides a node via context.node — use it. Don't create a new node.
        self._node = context.node
        self._pub = self._node.create_publisher(String, 'ui/cmd', 10)
        self._sub = self._node.create_subscription(
            String, 'ui/status',
            lambda msg: self._widget.statusLabel.setText(msg.data),
            QoSProfile(reliability=ReliabilityPolicy.RELIABLE, depth=10))

        self._widget.startButton.clicked.connect(lambda: self._send('start'))
        self._widget.stopButton.clicked.connect(lambda: self._send('stop'))

    def _send(self, cmd):
        msg = String()
        msg.data = cmd
        self._pub.publish(msg)

    def shutdown_plugin(self):
        # Tear down subscriptions/publishers.
        self._node.destroy_publisher(self._pub)
        self._node.destroy_subscription(self._sub)

    def save_settings(self, plugin_settings, instance_settings):
        instance_settings.set_value('last_status', self._widget.statusLabel.text())

    def restore_settings(self, plugin_settings, instance_settings):
        last = instance_settings.value('last_status', '')
        if last:
            self._widget.statusLabel.setText(last)
```

### `.ui` file (Qt Designer)

```bash
designer  # opens Qt Designer GUI; build the form, save as my_plugin.ui
```

The `.ui` is XML; `loadUi` parses it at runtime so you can edit visually without rebuilding.

### plugin.xml (rqt-style, not RViz-style)

```xml
<library path="my_rqt_plugin">
  <class name="My Plugin"
         type="my_rqt_plugin.my_plugin.MyPlugin"
         base_class_type="qt_gui_py_common.plugin.Plugin">
    <description>Send start/stop commands.</description>
    <qtgui>
      <group>
        <label>Custom</label>
      </group>
      <label>My Plugin</label>
    </qtgui>
  </class>
</library>
```

### setup.py

```python
from setuptools import setup
from glob import glob

package_name = 'my_rqt_plugin'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'plugin.xml']),
        ('share/' + package_name + '/resource', glob('resource/*.ui')),
    ],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'my_rqt_plugin = my_rqt_plugin.my_plugin:main',
        ],
    },
)
```

### package.xml

```xml
<package format="3">
  <name>my_rqt_plugin</name>
  <version>0.1.0</version>
  <description>Custom rqt plugin.</description>
  <maintainer email="me@example.com">Me</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_python</buildtool_depend>
  <depend>rclpy</depend>
  <depend>rqt_gui</depend>
  <depend>rqt_gui_py</depend>
  <depend>python_qt_binding</depend>
  <depend>std_msgs</depend>
  <export>
    <build_type>ament_python</build_type>
    <rqt_gui plugin="${prefix}/plugin.xml"/>
  </export>
</package>
```

The `<rqt_gui plugin="..."/>` line is what lets rqt's plugin loader find the plugin.xml.

After build:

```bash
colcon build --symlink-install --packages-select my_rqt_plugin
source install/setup.bash
rqt --standalone my_rqt_plugin       # standalone test
rqt                                  # then Plugins → Custom → My Plugin
```

## 4. Writing a C++ rqt plugin

Use C++ only when you need:

- Custom rendering (OpenGL, OpenSceneGraph)
- Significant CPU work that would block Python's GIL
- Compile-time integration with another C++ library

The structure mirrors the Python version but the plugin class extends
`rqt_gui_cpp::Plugin`. See `rqt_image_view` source for a reference.

```cpp
// my_plugin.hpp
#include <rqt_gui_cpp/plugin.h>
#include <QWidget>

class MyPlugin : public rqt_gui_cpp::Plugin {
  Q_OBJECT
 public:
  MyPlugin();
  void initPlugin(qt_gui_cpp::PluginContext & context) override;
  void shutdownPlugin() override;
  void saveSettings(qt_gui_cpp::Settings & plugin_settings,
                    qt_gui_cpp::Settings & instance_settings) const override;
  void restoreSettings(const qt_gui_cpp::Settings & plugin_settings,
                       const qt_gui_cpp::Settings & instance_settings) override;
 private:
  QWidget * widget_;
};
```

```cpp
// in my_plugin.cpp
#include <pluginlib/class_list_macros.hpp>
PLUGINLIB_EXPORT_CLASS(MyPlugin, rqt_gui_cpp::Plugin)
```

The plugin.xml uses `base_class_type="rqt_gui_cpp::Plugin"`.

## 5. `python_qt_binding` — the Qt abstraction layer

ROS 2's rqt uses `python_qt_binding` to abstract over PyQt5 and PySide. Always import through
it instead of directly:

```python
# Good
from python_qt_binding.QtWidgets import QWidget, QVBoxLayout
from python_qt_binding.QtCore import Qt, QTimer
from python_qt_binding import loadUi

# Bad (works on your machine, breaks on others)
from PyQt5.QtWidgets import QWidget
```

The binding picks PyQt5 or PySide at import time based on what's installed. Hardcoding one
backend means your plugin only works on machines with that exact backend.

## 6. Wiring rqt plugin into a node — the right pattern

rqt provides a single rclpy node shared by all loaded plugins (`context.node`). Use it. **Do
not** call `rclpy.init()` or create a separate node — that competes with rqt's executor and
silently breaks discovery for everyone.

If you need long-running work that shouldn't block the Qt event loop:

```python
from python_qt_binding.QtCore import QThread, pyqtSignal as Signal

class WorkerThread(QThread):
    result_ready = Signal(str)

    def __init__(self, node):
        super().__init__()
        self._node = node

    def run(self):
        # Heavy ROS work here. Use call_async on services, etc.
        # Don't touch widgets directly — emit a signal and let the GUI thread handle it.
        self.result_ready.emit('done')
```

Connect `result_ready` to a slot that updates the widget. This keeps the GUI responsive.

For periodic widget updates from ROS callbacks, the cleanest pattern is a `QTimer` in the GUI
thread that polls a thread-safe value updated by the ROS callback:

```python
from queue import Queue
from python_qt_binding.QtCore import QTimer

class MyPlugin(Plugin):
    def __init__(self, context):
        super().__init__(context)
        self._queue = Queue()
        self._sub = context.node.create_subscription(
            String, 'status', lambda msg: self._queue.put(msg.data), 10)
        self._timer = QTimer()
        self._timer.timeout.connect(self._drain_queue)
        self._timer.start(50)  # 20 Hz UI update

    def _drain_queue(self):
        while not self._queue.empty():
            data = self._queue.get_nowait()
            self._widget.statusLabel.setText(data)
```

This pattern (queue + timer) avoids cross-thread Qt widget access — touching widgets from a
non-GUI thread is undefined behavior in Qt and crashes intermittently.

## 7. Distributing your plugin

The plugin appears in rqt's Plugins menu after:

1. `colcon build --packages-select my_rqt_plugin`
2. `source install/setup.bash`
3. `rqt` (or restart it if already running)

For team distribution: include `my_rqt_plugin` in the team's workspace `src/` directory.
For wider distribution: publish to a Bloom-managed apt repo or just GitHub.

Save a perspective for the team:

```
rqt → Perspectives → Export
```

Save the JSON. Anyone can `rqt -p team.perspective` and get the same dashboard.

## 8. Anti-patterns

- **`rclpy.init()` inside the plugin.** rqt already initialized rclpy. Reinitializing breaks the
  shared executor. Use `context.node` instead.
- **Long-running ROS calls on the GUI thread.** Freezes the UI. Use a `QThread` worker or
  `call_async` + signal.
- **Widget updates from ROS callbacks.** Qt widgets are not thread-safe. Use a queue + timer.
- **Hardcoding `PyQt5` or `PySide` imports.** Use `python_qt_binding`. Otherwise you ship a
  plugin that crashes on half the machines.
- **Forgetting `<rqt_gui plugin="..."/>` export in package.xml.** The plugin builds but never
  appears in the rqt menu.
- **Using a separate `<plugin path="..."/>` for `package.xml` (the RViz pattern).** rqt uses a
  different export tag (`<rqt_gui plugin="..."/>`). Mixing them silently fails.
- **Loading a `.ui` file with hardcoded path.** Always go through
  `get_package_share_directory(...)`. Hardcoded paths break the moment you `colcon build`
  install-packages elsewhere.
- **Reinventing built-in plugins.** Before writing a plot or graph viewer, check whether
  `rqt_plot` / `rqt_graph` already does what you want with a saved perspective.
