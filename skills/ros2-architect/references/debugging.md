# Debugging

How to figure out what's wrong with a running ROS 2 system. The CLI is the front door; learn it
cold and most problems become obvious in seconds.

## Contents

1. The first commands to run when something is wrong
2. Topic introspection
3. Node introspection
4. Service and action calls from the command line
5. Lifecycle inspection
6. Parameter management
7. DDS introspection
8. The ROS 2 daemon
9. rosbag2 — record, replay, inspect
10. Tracing and profiling
11. The decision tree for "no messages received"

## 1. The first commands to run when something is wrong

When something is wrong and you don't know where to start, run these in order:

```bash
ros2 doctor --report
```

This reports the ROS distro, RMW, environment variables, and any missing dependencies. Read
the output top to bottom; obvious issues (missing `ROS_DOMAIN_ID`, mismatched RMW) jump out.

```bash
ros2 node list
```

If a node you expect is missing, the launch file failed silently or the node crashed. Check
launch logs.

```bash
ros2 topic list -t
```

The `-t` adds the message type. Useful for spotting typos (e.g., your node publishes
`/cmd_vel` but downstream subscribes to `/cmd/vel`).

```bash
ros2 topic hz /problem_topic
```

If `hz` blocks for more than a few seconds, no messages are arriving. Move to §11.

## 2. Topic introspection

```bash
# List all topics with types.
ros2 topic list -t

# Detailed info about a topic — publishers, subscribers, QoS profiles.
ros2 topic info /scan --verbose

# Live messages.
ros2 topic echo /joint_states
ros2 topic echo /joint_states --once       # one message only
ros2 topic echo /joint_states --no-arr     # hide large arrays for readability

# Filter fields.
ros2 topic echo /joint_states --filter "all(p > 0 for p in m.position)"

# Rate.
ros2 topic hz /scan          # rate over the last second
ros2 topic hz /scan --window 5    # over 5 seconds

# Bandwidth.
ros2 topic bw /image_raw

# Find subscribers.
ros2 topic info /cmd_vel --verbose | grep -A2 "Subscription"

# Publish a one-shot message (great for testing).
ros2 topic pub /chatter std_msgs/msg/String "data: 'hello'" --once
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
    "{linear: {x: 0.1}, angular: {z: 0.0}}" --rate 10
```

## 3. Node introspection

```bash
# List nodes.
ros2 node list

# Detailed info: subscribers, publishers, services, actions, parameters.
ros2 node info /perception_node

# Find which nodes publish/subscribe to a topic.
ros2 node info /perception_node | grep -A 10 "Publishers"
```

## 4. Service and action calls from the command line

```bash
# List services.
ros2 service list -t

# Service interface.
ros2 service type /set_pose
ros2 interface show geometry_msgs/srv/Pose

# Call a service.
ros2 service call /set_pose geometry_msgs/srv/Pose \
    "{position: {x: 1.0, y: 0.0, z: 0.5}}"

# Actions.
ros2 action list -t
ros2 action info /follow_joint_trajectory
ros2 action send_goal /follow_joint_trajectory \
    control_msgs/action/FollowJointTrajectory \
    "{trajectory: {joint_names: [j1], points: [{positions: [0.5], time_from_start: {sec: 2}}]}}" \
    --feedback
```

## 5. Lifecycle inspection

```bash
# Which nodes are lifecycle?
ros2 lifecycle nodes

# Current state.
ros2 lifecycle get /camera

# Available transitions from current state.
ros2 lifecycle list /camera

# Drive a transition.
ros2 lifecycle set /camera configure
ros2 lifecycle set /camera activate
```

## 6. Parameter management

```bash
# List a node's parameters.
ros2 param list /perception_node

# Get one.
ros2 param get /perception_node confidence_threshold

# Set one.
ros2 param set /perception_node confidence_threshold 0.85

# Describe (shows constraints from the parameter descriptor).
ros2 param describe /perception_node confidence_threshold

# Dump all to YAML.
ros2 param dump /perception_node > params.yaml

# Load YAML.
ros2 param load /perception_node params.yaml
```

## 7. DDS introspection

When you suspect a DDS-level issue (e.g., nodes not seeing each other across machines), you need
to look below ros2 CLI:

```bash
# Fast-DDS only — list all participants on the LAN.
fastdds discovery -i 0 -l <ip> -p 11811   # if running discovery server

# Cyclone DDS — IDLELOG environment.
export CYCLONEDDS_URI='<CycloneDDS><Domain><Tracing><Verbosity>finer</Verbosity><OutputFile>cdds.log</OutputFile></Tracing></Domain></CycloneDDS>'

# Wireshark with the rtps dissector — visualizes raw DDS packets. Slow but ground truth.
sudo wireshark -i any -f "udp port 7400 or udp portrange 7401-7500"
```

If two machines aren't seeing each other:

1. **`ROS_DOMAIN_ID` matches?** `echo $ROS_DOMAIN_ID` on both.
2. **Same RMW?** `echo $RMW_IMPLEMENTATION` on both.
3. **Multicast working?** Try `ping 239.255.0.1` and `iperf -u -c 239.255.0.1`. Many cloud and
   Wi-Fi setups block multicast.
4. **Firewall?** UDP ports 7400+ for Fast-DDS, 7400-7500 for Cyclone DDS.
5. **VPN / Wi-Fi separation?** Subscribers and publishers on different L2 broadcast domains
   never discover via multicast. Use a discovery server.

## 8. The ROS 2 daemon

`ros2 cli` commands talk to a daemon on port 11811 to cache topic/node lists. Sometimes the
daemon's cache becomes stale (e.g., after a node crashes mid-discovery).

```bash
# Stop the daemon.
ros2 daemon stop

# Start fresh.
ros2 daemon start

# Or just one-shot via:
ros2 topic list --no-daemon
```

If `ros2 topic list` shows topics that don't exist anymore, restart the daemon.

## 9. rosbag2 — record, replay, inspect

```bash
# Record specific topics.
ros2 bag record /scan /joint_states /tf /tf_static

# Record all (large!).
ros2 bag record -a

# Record with QoS preservation — important for sensor topics.
ros2 bag record /scan --include-hidden-topics --qos-profile-overrides-path qos.yaml

# Inspect.
ros2 bag info my_bag/

# Replay.
ros2 bag play my_bag/
ros2 bag play my_bag/ --rate 0.5         # half speed
ros2 bag play my_bag/ --start-offset 10  # skip first 10 sec
ros2 bag play my_bag/ --topics /scan     # replay only one topic
ros2 bag play my_bag/ --loop             # loop forever
```

`qos.yaml` for QoS-correct recording:

```yaml
/scan:
  reliability: best_effort
  durability: volatile
  depth: 10
/tf_static:
  reliability: reliable
  durability: transient_local
```

Without QoS overrides, `ros2 bag record` defaults to RELIABLE for everything, which silently
drops BEST_EFFORT publishes. The recording looks empty when replayed.

## 10. Tracing and profiling

For microsecond-level analysis use `ros2_tracing`:

```bash
ros2 trace --session-name my_trace
# ... run your system ...
# Stop tracing → Ctrl+C
babeltrace2 ~/.ros/tracing/my_trace      # text dump
```

Visualize with `tracecompass` or analyze with `tracetools_analysis` Python scripts.

For node-level CPU profiling, use `perf`:

```bash
perf record -p $(pgrep my_node)
perf report
```

For Python nodes, `py-spy` gives a flame graph without modifying code:

```bash
py-spy record -o flame.svg --pid $(pgrep -f my_node)
```

## 11. The decision tree for "no messages received"

Most common debug scenario. Walk through this in order.

### Step 1 — does the publisher exist?

```bash
ros2 node info /publisher_node 2>&1 | grep -A 5 "Publishers"
```

If the publisher node isn't listed, it crashed or the launch file didn't start it. Check launch
output:

```bash
# launch logs go to ~/.ros/log/latest_launch/ — find the one for your node.
tail -f ~/.ros/log/latest_launch/<node_name>-*.log
```

### Step 2 — is it actually publishing?

```bash
ros2 topic hz /the_topic
```

If `hz` reports nothing for >5 seconds, the publisher is up but not publishing. Common causes:

- The publisher's input is missing (a callback chain broke earlier).
- The publisher is gated on a parameter that wasn't set.
- The publisher is in a deactivated lifecycle state.

### Step 3 — does the subscriber's QoS match?

```bash
ros2 topic info /the_topic --verbose
```

Read the `QoS profile:` lines for both publisher and subscriber. The subscriber's reliability
must be ≤ the publisher's, and the subscriber's durability must be ≤ the publisher's. See
`communication.md` §QoS Compatibility.

```bash
ros2 doctor --report
```

Look for `Incompatible QoS` events.

### Step 4 — namespacing or remapping mismatch?

```bash
# Check the actual topic both nodes are using.
ros2 node info /publisher_node | grep "/the_topic"
ros2 node info /subscriber_node | grep "/the_topic"
```

If the publisher writes `/the_topic` and the subscriber reads `/robot_a/the_topic` (because
of `PushRosNamespace`), they're on different topics. Add an explicit remapping in the launch
or push both into the same namespace.

### Step 5 — DDS-level isolation?

If publisher and subscriber are on different machines:

- `echo $ROS_DOMAIN_ID` — must match.
- `echo $RMW_IMPLEMENTATION` — should match for full interop.
- `ros2 multicast send` / `ros2 multicast receive` — verify the LAN allows multicast.

### Step 6 — sim time mismatch?

If one side has `use_sim_time: true` and the other has `false`, time-stamped messages from one
look like they're from the future or the past from the other. Check:

```bash
ros2 param get /publisher_node use_sim_time
ros2 param get /subscriber_node use_sim_time
```

### Step 7 — daemon cache stale?

```bash
ros2 daemon stop && sleep 1 && ros2 daemon start
ros2 topic info /the_topic --verbose
```

If the answer changes after this, the daemon was reporting stale info.

### Step 8 — message-level introspection

If everything else looks right but messages aren't reaching the subscriber's callback:

```bash
# Drop a temporary echo at exactly the topic the subscriber claims to listen to.
ros2 topic echo /robot_a/the_topic --no-arr

# If echo sees messages but the node doesn't, the bug is in the node — most often a
# missing add_to_executor or the subscription's callback group is mutually-exclusive
# behind another long-running callback. See node-design.md §Executors.
```
