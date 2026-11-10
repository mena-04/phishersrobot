# Phase 4 — Increase Waypoint Duration (Criterion 4: 10 pts)

> **Competition-day command runbook. Not a report.**  
> Use the shortest working path first. Jump to the matching troubleshooting section only when something fails.

## Goal

Prove that the extra wait after a waypoint can be increased.

Known-good practice comparison:

```text
Baseline: wait_duration = 0.0  -> ~0 s extra wait
Changed:  wait_duration = 3.0  -> ~3 s extra wait
Increase:                         ~+3 s
```

The tested source performs a fixed ~4 s maneuver/scan **before** the configurable extra wait.

---

# A. Competition-day fast path

## A1. SSH to the robot

From your laptop:

```bash
ssh ubuntu@<ROBOT_IP>
```

If you do not know the robot IP, obtain it from the robot/team network first. Once connected:

```bash
hostname -I
ip -br addr
```

Do not hard-code a practice-session IP into the competition procedure.

## A2. Set the ROS environment

Run in every Pi terminal used for the physical ROS Master:

```bash
source ~/catkin_ws/devel/setup.bash
export ROS_MASTER_URI=http://localhost:11311
export ROS_IP="$(hostname -I | awk '{print $1}')"
unset ROS_HOSTNAME
export TURTLEBOT3_MODEL=burger
```

Check:

```bash
printf 'MASTER=%s  IP=%s\n' "$ROS_MASTER_URI" "$ROS_IP"
rosnode list
```

If `rosnode list` works, **do not start another `roscore`**.

If it says:

```text
ERROR: Unable to communicate with master!
```

start `roscore` in its own terminal:

```bash
roscore
```

Then leave that terminal running.

## A3. Confirm the competition package

```bash
rospack find hack_my_robot
```

Known practice path:

```text
/home/ubuntu/catkin_ws/src/hack_my_robot_2026
```

If the path differs, use the path returned by `rospack find` in later inspection commands.

## A4. Confirm the wait implementation

```bash
grep -Rn 'wait_duration' ~/catkin_ws/src/hack_my_robot_2026
```

Known tested source:

```python
self.duration = rospy.get_param('~wait_duration', 0.0)
```

Find the actual wait call:

```bash
grep -RnE 'time\.sleep|rospy\.sleep|Waiting for' \
  ~/catkin_ws/src/hack_my_robot_2026/src/hack_my_robot/
```

Known tested branch:

```python
self.client.wait_for_result()
start_scan_response()
rospy.loginfo('Waiting for %f sec...' % self.duration)
time.sleep(self.duration)
```

Fixed maneuver/scan:

```python
rospy.loginfo('Maneuvering! Duration: 4s')
rospy.sleep(4)
```

## A5. Do NOT rely on `rosparam set` before startup

The organizer launch uses `clear_params="true"`, and the node reads `~wait_duration` during initialization.

Therefore prefer **launch-time configuration + mission restart**.

Check the organizer launch:

```bash
cat ~/catkin_ws/src/hack_my_robot_2026/launch/hack_my_robot_complete.launch
```

If it contains:

```xml
clear_params="true"
```

do not assume this will survive startup:

```bash
rosparam set /hack_my_robot/wait_duration 3.0
```

Use the launch helper below instead.

---

# B. Create/verify the Phase 4 launch helper

## B1. Create it if missing

```bash
mkdir -p ~/phase4-timing-lab/launch

cat > ~/phase4-timing-lab/launch/phase4_mission.launch <<'EOF_LAUNCH'
<launch>
  <arg name="wait_duration" default="0.0"/>

  <node pkg="hack_my_robot" type="hack_my_robot_node"
        name="hack_my_robot" output="screen" clear_params="true">
    <param name="goal_frame_id" value="map"/>
    <param name="odom_frame_id" value="odom"/>
    <param name="base_frame_id" value="base_footprint"/>
    <param name="addpose_topic" value="/addpose"/>
    <param name="posearray_topic" value="/waypoints"/>
    <param name="wait_duration" value="$(arg wait_duration)"/>
  </node>
</launch>
EOF_LAUNCH
```

## B2. Validate without running the mission

```bash
python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse('/home/ubuntu/phase4-timing-lab/launch/phase4_mission.launch')
print('PASS: valid XML')
PY
```

```bash
roslaunch --nodes ~/phase4-timing-lab/launch/phase4_mission.launch
```

Expected:

```text
/hack_my_robot
```

Check both configurations:

```bash
roslaunch --dump-params \
  ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=0.0 | grep wait_duration
```

Expected:

```text
/hack_my_robot/wait_duration: 0.0
```

```bash
roslaunch --dump-params \
  ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=3.0 | grep wait_duration
```

Expected:

```text
/hack_my_robot/wait_duration: 3.0
```

If these work, the parameter path is ready.

---

# C. Recommended proof: isolated mock `move_base`

Use this when the criterion only requires proof that the wait increased, or when physical navigation is consuming too much time.

**Never run the mock `move_base` on the physical robot's main Master (`11311`).**

## C1. Terminal A — isolated ROS Master

```bash
source ~/catkin_ws/devel/setup.bash
export ROS_MASTER_URI=http://localhost:11312
export ROS_IP=127.0.0.1
unset ROS_HOSTNAME
roscore -p 11312
```

Leave running.

## C2. Terminals B/C/D — isolated environment

Run in every new mock-test terminal:

```bash
source ~/catkin_ws/devel/setup.bash
export ROS_MASTER_URI=http://localhost:11312
export ROS_IP=127.0.0.1
unset ROS_HOSTNAME
printf 'MASTER=%s  IP=%s\n' "$ROS_MASTER_URI" "$ROS_IP"
rosnode list
```

Before starting test nodes, expected:

```text
/rosout
```

If you see physical nodes such as `/turtlebot3_core`, `/amcl`, or the real `/move_base`, **stop** and fix `ROS_MASTER_URI`.

## C3. Terminal B — create/start mock `move_base`

```bash
mkdir -p ~/phase4-timing-lab

cat > ~/phase4-timing-lab/mock_move_base.py <<'PY'
#!/usr/bin/env python3
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseResult

def execute(goal):
    rospy.loginfo('PHASE4_MOCK: Received waypoint goal')
    rospy.sleep(0.2)
    server.set_succeeded(MoveBaseResult())
    rospy.loginfo('PHASE4_MOCK: Goal succeeded')

rospy.init_node('phase4_mock_move_base')
server = actionlib.SimpleActionServer(
    'move_base', MoveBaseAction, execute_cb=execute, auto_start=False
)
server.start()
rospy.loginfo('PHASE4_MOCK: Ready')
rospy.spin()
PY

python3 ~/phase4-timing-lab/mock_move_base.py
```

Expected:

```text
PHASE4_MOCK: Ready
```

Leave running.

## C4. Terminal D — create one-shot waypoint sender

Do **not** use `rostopic pub -1 /addpose` when you need exactly one waypoint. In practice it produced repeated waypoint messages.

```bash
cat > ~/phase4-timing-lab/send_one_waypoint.py <<'PY'
#!/usr/bin/env python3
import time
import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_msgs.msg import Empty

rospy.init_node('phase4_single_waypoint_sender', anonymous=True)
pub = rospy.Publisher('/addpose', PoseWithCovarianceStamped, queue_size=1)
ready = rospy.Publisher('/path_ready', Empty, queue_size=1)

def wait_subscriber(publisher, name):
    deadline = time.monotonic() + 10.0
    while (not rospy.is_shutdown()
           and publisher.get_num_connections() == 0
           and time.monotonic() < deadline):
        rospy.sleep(0.1)
    if publisher.get_num_connections() == 0:
        raise RuntimeError('Mission is not subscribed to ' + name)

wait_subscriber(pub, '/addpose')
msg = PoseWithCovarianceStamped()
msg.header.stamp = rospy.Time.now()
msg.header.frame_id = 'map'
msg.pose.pose.orientation.w = 1.0
pub.publish(msg)
print('Published exactly one waypoint')

rospy.sleep(1.0)
wait_subscriber(ready, '/path_ready')
ready.publish(Empty())
print('Published path_ready once')
rospy.sleep(0.5)
PY
```

## C5. Terminal D — create GET_PATH wake-up helper

Use **only if** the mission logs both:

```text
Recieved path READY message
Positions written to ...
```

but does not transition to `FOLLOW_PATH`.

```bash
cat > ~/phase4-timing-lab/wakeup.py <<'PY'
#!/usr/bin/env python3
import time
import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped

rospy.init_node('phase4_wakeup', anonymous=True)
pub = rospy.Publisher('/addpose', PoseWithCovarianceStamped, queue_size=1)

deadline = time.monotonic() + 10.0
while (not rospy.is_shutdown()
       and pub.get_num_connections() == 0
       and time.monotonic() < deadline):
    rospy.sleep(0.1)

if pub.get_num_connections() == 0:
    raise RuntimeError('No /addpose subscriber; cannot wake GET_PATH')

msg = PoseWithCovarianceStamped()
msg.header.frame_id = 'map'
msg.header.stamp = rospy.Time.now()
msg.pose.pose.orientation.w = 1.0
pub.publish(msg)
print('Sent one wake-up waypoint')
rospy.sleep(0.5)
PY
```

The wake-up pose becomes another synthetic waypoint. Use the **same procedure in baseline and changed runs** so the comparison remains fair.

---

# D. Baseline run — `wait_duration:=0.0`

## D1. Terminal C — start mission

```bash
roslaunch ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=0.0 2>&1 | tee ~/phase4-timing-lab/baseline-console.log
```

Wait for:

```text
Connected to move_base.
Waiting to recieve waypoints ...
```

## D2. Terminal D — verify parameter

```bash
rosparam get /hack_my_robot/wait_duration
```

Expected:

```text
0.0
```

## D3. Send one waypoint

```bash
python3 ~/phase4-timing-lab/send_one_waypoint.py
```

Expected:

```text
Published exactly one waypoint
Published path_ready once
```

## D4. If GET_PATH hangs

Only after the mission prints both readiness/saved-path messages:

```bash
python3 ~/phase4-timing-lab/wakeup.py
```

## D5. Capture baseline evidence

Look for:

```text
Maneuvering! Duration: 4s
Service finished.
Waiting for 0.000000 sec...
```

Stop the mission with `Ctrl+C` after evidence is captured.

Leave the isolated Master and mock server running for the changed run.

---

# E. Changed run — `wait_duration:=3.0`

## E1. Terminal C — restart mission

```bash
roslaunch ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=3.0 2>&1 | tee ~/phase4-timing-lab/extended-console.log
```

Wait for:

```text
Connected to move_base.
Waiting to recieve waypoints ...
```

## E2. Terminal D — verify parameter

```bash
rosparam get /hack_my_robot/wait_duration
```

Expected:

```text
3.0
```

## E3. Send the same synthetic waypoint procedure

```bash
python3 ~/phase4-timing-lab/send_one_waypoint.py
```

If GET_PATH hangs after readiness/saving:

```bash
python3 ~/phase4-timing-lab/wakeup.py
```

## E4. Capture changed evidence

Look for:

```text
Maneuvering! Duration: 4s
Service finished.
Waiting for 3.000000 sec...
```

Known-good practice timing:

```text
0-second run: wait announcement -> next goal ~= 0.004 s
3-second run: wait announcement -> next goal ~= 3.008 s
increase                                  ~= 3.004 s
```

Stop mission after evidence is captured.

---

# F. Extract evidence quickly

Search all ROS logs:

```bash
grep -RhE \
  'Executing move_base goal|Maneuvering! Duration|Service finished|Waiting for [0-9]|REACHED FINISH GOAL' \
  ~/.ros/log/ | tail -120
```

Check the two console captures:

```bash
grep -E 'Maneuvering! Duration|Service finished|Waiting for [0-9]|Executing move_base goal' \
  ~/phase4-timing-lab/baseline-console.log
```

```bash
grep -E 'Maneuvering! Duration|Service finished|Waiting for [0-9]|Executing move_base goal' \
  ~/phase4-timing-lab/extended-console.log
```

For the criterion, preserve at minimum:

```text
Baseline: Waiting for 0.000000 sec...
Changed:  Waiting for 3.000000 sec...
```

and the surrounding timestamps.

---

# G. Optional physical-stack path

Use this only if you want additional real-TurtleBot evidence or another criterion already requires navigation.

**Do not make successful physical navigation a prerequisite for the timing proof unless the competition rules explicitly require it.**

## G1. Check physical core nodes

```bash
export ROS_MASTER_URI=http://localhost:11311
export ROS_IP="$(hostname -I | awk '{print $1}')"
unset ROS_HOSTNAME

rosnode list
```

Expected hardware nodes include:

```text
/turtlebot3_core
/turtlebot3_diagnostics
/turtlebot3_lds
```

If missing, start the robot bringup in its own terminal:

```bash
source ~/catkin_ws/devel/setup.bash
export TURTLEBOT3_MODEL=burger
export LDS_MODEL=LDS-02
roslaunch turtlebot3_bringup turtlebot3_robot.launch
```

## G2. Check battery before movement

```bash
rostopic echo -n 1 /battery_state/voltage
```

If the robot has been beeping, motors are unresponsive, or voltage is questionable, charge/check power before autonomous movement.

Check kernel power warnings if needed:

```bash
dmesg | grep -iE 'under-voltage|voltage|oom|segfault|killed process' | tail -30
```

Practice observed Raspberry Pi under-voltage messages. Treat them as an observation, not automatically as the cause of another failure.

## G3. Check map

Known practice map:

```bash
ls -lh ~/phase4-maps/practice_2x4.*
cat ~/phase4-maps/practice_2x4.yaml
```

Do **not** use this map if the robot is in a different physical environment.

## G4. Start navigation

```bash
source ~/catkin_ws/devel/setup.bash
export ROS_MASTER_URI=http://localhost:11311
export ROS_IP="$(hostname -I | awk '{print $1}')"
unset ROS_HOSTNAME
export TURTLEBOT3_MODEL=burger

roslaunch turtlebot3_navigation turtlebot3_navigation.launch \
  map_file:=/home/ubuntu/phase4-maps/practice_2x4.yaml \
  open_rviz:=false
```

Leave running.

## G5. Verify navigation before mission launch

```bash
rosnode list | grep -E 'map_server|amcl|move_base|robot_state_publisher'
rosnode ping -c 1 /move_base
timeout 5s rostopic hz /move_base/status
rostopic info /cmd_vel
```

Healthy `/cmd_vel` relationship:

```text
Publisher:  /move_base
Subscriber: /turtlebot3_core
```

Do not trust `/move_base` merely because `rosnode list` contains it. A dead node can remain registered temporarily.

## G6. Check localization before autonomous movement

```bash
timeout 5s rosrun tf tf_echo map odom
```

```bash
timeout 5s rostopic echo -n 1 /amcl_pose/pose/pose
```

```bash
timeout 5s rostopic echo -n 1 /amcl_pose/pose/covariance
```

If AMCL's estimated pose lies in unknown/occupied map space, **do not send an autonomous goal**. Correct localization first (normally with RViz `2D Pose Estimate` or another verified initial-pose method).

## G7. Physical mission baseline/changed launch

Baseline:

```bash
roslaunch ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=0.0 2>&1 | tee ~/phase4-timing-lab/physical-baseline.log
```

Changed:

```bash
roslaunch ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=3.0 2>&1 | tee ~/phase4-timing-lab/physical-extended.log
```

Before sending a waypoint, verify:

```bash
rosnode ping -c 1 /move_base
rosparam get /hack_my_robot/wait_duration
```

Use competition-approved/current waypoint coordinates. **Never reuse old practice coordinates blindly.**

---

# H. Troubleshooting — jump directly to the symptom

## H1. `RLException: roscore cannot run as another roscore/master is already running`

Do not start another Master.

```bash
pgrep -af 'roscore|rosmaster|roslaunch'
rosnode list
```

If the existing Master is healthy, use it.

Only if you intentionally want a complete reset:

```bash
pgrep -af 'roscore|rosmaster|roslaunch|rosrun'
```

Stop known launch terminals with `Ctrl+C` first. Then, if necessary:

```bash
pkill -f roslaunch
pkill -f '/opt/ros/noetic/bin/roscore'
pkill -f '/opt/ros/noetic/bin/rosmaster'
```

Verify:

```bash
pgrep -af 'roscore|rosmaster|roslaunch'
sudo ss -lntp | grep 11311
```

No output means the reset is complete.

**Do not use `killall -a`.**

## H2. `/hack_my_robot/wait_duration` is not set

Check whether the mission node is running:

```bash
rosnode list | grep hack_my_robot
```

If it is not running, the private parameter may not exist. Verify the launch configuration instead:

```bash
roslaunch --dump-params \
  ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=3.0 | grep wait_duration
```

Then launch/restart the mission with the desired value.

## H3. Mission stuck at `Connecting to move_base...`

Do **not** send `/addpose` yet.

```bash
rosnode ping -c 1 /move_base
timeout 3s rostopic hz /move_base/status
rostopic info /move_base/goal
rostopic info /move_base/result
```

If `/move_base` is absent/dead, repair navigation first.

## H4. `/move_base` listed but ping says connection refused

Treat it as dead/stale.

```bash
pgrep -af move_base
rosnode cleanup
```

Answer `y` if asked to remove unreachable registrations.

If the rest of navigation is still running and its parameters remain loaded, restart only `move_base`:

```bash
rosrun move_base move_base __name:=move_base
```

Healthy startup should include:

```text
Created local_planner dwa_local_planner/DWAPlannerROS
odom received!
```

Verify:

```bash
rosnode ping -c 1 /move_base
timeout 5s rostopic hz /move_base/status
rostopic info /cmd_vel
```

## H5. DWA planner fatal error

Symptom:

```text
Failed to create the dwa_local_planner/DWAPlannerROS planner
```

Check:

```bash
rospack find dwa_local_planner
dpkg -l | grep -E 'dwa-local-planner|navigation'
ls -l /opt/ros/noetic/lib/libdwa_local_planner*
```

If genuinely missing and package installation is allowed/Internet is available:

```bash
sudo apt update
sudo apt install ros-noetic-dwa-local-planner
```

Then restart `move_base`/navigation and verify it creates `DWAPlannerROS`.

## H6. `send_one_waypoint.py` says mission is not subscribed to `/addpose`

Example:

```text
RuntimeError: Mission is not subscribed to /addpose
```

The mission has not reached `GET_PATH` yet, often because it is still connecting to `move_base`.

Check mission terminal and:

```bash
rosnode info /hack_my_robot
rosnode ping -c 1 /move_base
```

Do not keep rerunning the sender until the mission says:

```text
Waiting to recieve waypoints via Pose msg on topic /addpose
```

## H7. `/path_ready` received but mission does not enter `FOLLOW_PATH`

Known tested source behavior.

Confirm mission printed:

```text
Recieved path READY message
Positions written to ...
```

Then, for the isolated test:

```bash
python3 ~/phase4-timing-lab/wakeup.py
```

Do not repeatedly publish `/addpose` with `rostopic pub -1`.

## H8. Hundreds of `Recieved new waypoint` lines

Cause encountered in practice: `rostopic pub -1 /addpose ...` stayed alive long enough to deliver repeated messages.

Stop using it.

Use:

```bash
python3 ~/phase4-timing-lab/send_one_waypoint.py
```

If the saved CSV is contaminated and the rules permit resetting it, inspect before deleting/modifying anything:

```bash
wc -l ~/catkin_ws/src/hack_my_robot_2026/saved_path/scan_positions.csv
cat ~/catkin_ws/src/hack_my_robot_2026/saved_path/scan_positions.csv
```

## H9. Goal stuck `status: 1` (`ACTIVE`)

Check:

```bash
rostopic echo -n 1 /move_base/status
rostopic echo -n 1 /cmd_vel
rosnode ping -c 1 /move_base
```

ROS action status reference used during practice:

```text
1 = ACTIVE
2 = PREEMPTED
3 = SUCCEEDED
6 = PREEMPTING
```

If physical navigation is required, diagnose localization/motor/navigation rather than treating an ACTIVE goal as success.

If you intentionally need to cancel:

```bash
rostopic pub -1 /move_base/cancel actionlib_msgs/GoalID "{}"
```

If broad cancel does not resolve it, get the exact goal ID:

```bash
rostopic echo -n 1 /move_base/status
```

Then target that ID:

```bash
rostopic pub -1 /move_base/cancel actionlib_msgs/GoalID \
"{stamp: {secs: 0, nsecs: 0}, id: '<GOAL_ID>'}"
```

Do not claim navigation success unless status reaches `3` and the physical behavior matches.

## H10. Cancellation stuck at `status: 6` (`PREEMPTING`)

Wait briefly and recheck:

```bash
rostopic echo -n 1 /move_base/status
```

If physical navigation is not required for Criterion 4, stop spending time on navigation and use the isolated mock proof instead.

If another criterion requires navigation, troubleshoot it there rather than weakening the timing evidence.

## H11. `move_base` disappears with no ROS `FATAL`

Check process/kernel/resources:

```bash
pgrep -af move_base
free -h
uptime
dmesg | grep -iE 'killed process|out of memory|oom|segfault|under-voltage|voltage' | tail -30
```

Practice showed adequate free memory and no OOM/segfault, but did show earlier under-voltage events. Do not assume causation without evidence.

Clean restart if needed:

```bash
rosnode cleanup
```

then restart navigation or only `move_base` as appropriate.

## H12. Robot does not move although `/cmd_vel` exists

Stop teleop/navigation commands first.

Check:

```bash
rostopic info /cmd_vel
rostopic echo -n 1 /battery_state/voltage
rostopic echo -n 1 /joint_states
rostopic echo -n 1 /diagnostics
```

Motor power topic:

```bash
rostopic info /motor_power
```

If competition procedure permits enabling motor power:

```bash
rostopic pub -1 /motor_power std_msgs/Bool "data: true"
```

Do not keep increasing velocity commands if the robot is not responding.

## H13. AMCL pose is confident but in unknown map space

Check pose:

```bash
timeout 5s rostopic echo -n 1 /amcl_pose/pose/pose
timeout 5s rostopic echo -n 1 /amcl_pose/pose/covariance
```

A small covariance does **not** guarantee the pose is correct.

If using physical autonomous navigation, verify the pose against the map/RViz and correct initial localization before sending goals.

## H14. Ctrl+C produces `ROSInterruptException` / `.message` traceback

Known source issue during shutdown:

```text
AttributeError: 'ROSInterruptException' object has no attribute 'message'
```

The tested source contains logic equivalent to:

```python
if 'timeout exceeded' in e.message:
```

Under Python 3 the observed exception did not have `.message`.

If your timing evidence was printed **before** the shutdown traceback, preserve the evidence and treat the traceback as a shutdown/source bug.

## H15. `vcgencmd get_throttled` gives `VCHI initialization failed`

Do not block the criterion on this command.

Use available checks instead:

```bash
dmesg | grep -iE 'under-voltage|voltage' | tail -20
free -h
```

---

# I. If the parameter route is unavailable

## I1. Search source for hard-coded delay

```bash
find ~/catkin_ws/src -iname '*hack_my_robot*'
```

```bash
grep -RnE 'sleep|rospy\.Duration|wait|duration' \
  ~/catkin_ws/src/hack_my_robot_2026/
```

Inspect the exact code before editing:

```bash
sed -n '1,320p' \
  ~/catkin_ws/src/hack_my_robot_2026/src/hack_my_robot/hack_my_robot.py
```

If competition rules allow a source change, work on a recoverable copy/branch and record exactly what changed.

For the tested competition version, **source editing was unnecessary** because `~wait_duration` already existed.

## I2. Last-resort relay approach

Only consider this if:

- no tunable parameter exists;
- allowed source modification is unavailable; and
- competition rules permit an intermediary.

Inspect interfaces first:

```bash
rostopic list
rosnode info /hack_my_robot
rostopic info /addpose
rostopic type /addpose
```

Do not relay `/cmd_vel` or alter motor-safety paths merely to satisfy the timing criterion.

A previously tested synthetic relay delay of about `1.001 s` was only a proof of concept and was **not equivalent** to the verified post-goal `wait_duration` mechanism.

---

# J. Clean reset procedure

Use only when you intentionally want to discard the current ROS session and start over.

First stop known launch terminals with `Ctrl+C`.

Inspect remaining processes:

```bash
pgrep -af 'roscore|rosmaster|roslaunch|rosrun|move_base|hack_my_robot'
```

If the Master still works:

```bash
rosnode list
```

Clean stale node registrations when appropriate:

```bash
rosnode cleanup
```

If you intentionally need to terminate remaining launch/master processes:

```bash
pkill -f roslaunch
pkill -f '/opt/ros/noetic/bin/roscore'
pkill -f '/opt/ros/noetic/bin/rosmaster'
```

Verify clean state:

```bash
pgrep -af 'roscore|rosmaster|roslaunch'
sudo ss -lntp | grep 11311
```

No output = no remaining ROS Master/listener on `11311`.

Start again with the minimum required terminals.

---

# K. Competition-day evidence checklist

Before leaving Criterion 4, make sure you have:

```text
[ ] Source/parameter showing wait_duration exists
[ ] Baseline launch configured as 0.0
[ ] Baseline log: Waiting for 0.000000 sec...
[ ] Changed launch configured to the increased value
[ ] Changed log: Waiting for 3.000000 sec... (or required value)
[ ] Timestamps/console logs saved
[ ] Same test procedure used for baseline and changed run
[ ] Mock vs physical navigation clearly identified
[ ] No unsupported claim that the robot physically reached a waypoint
```

Quick commands:

```bash
roslaunch --dump-params \
  ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=0.0 | grep wait_duration
```

```bash
roslaunch --dump-params \
  ~/phase4-timing-lab/launch/phase4_mission.launch \
  wait_duration:=3.0 | grep wait_duration
```

```bash
grep -RhE \
  'Maneuvering! Duration|Service finished|Waiting for [0-9]|Executing move_base goal' \
  ~/.ros/log/ | tail -120
```

---

# L. Known-good practice reference — do not blindly reuse

These values are reference points from practice, **not competition-day assumptions**.

```text
Mock baseline wait-to-next-goal:  ~0.004 s
Mock 3 s wait-to-next-goal:      ~3.008 s
Measured increase:               ~3.004 s
```

Real TurtleBot ROS-stack practice also produced:

```text
Waiting for 0.000000 sec...
Waiting for 3.000000 sec...
```

The real-stack 3-second run showed about `3.008 s` before the next goal log, but the physical navigation action had been interrupted/preempted. Therefore these logs prove the timing path executed; they do **not** prove successful autonomous waypoint arrival.

Practice-only map:

```text
/home/ubuntu/phase4-maps/practice_2x4.yaml
```

Practice-only pose used during troubleshooting:

```text
x = 1.7717090105656812
y = 0.690744355080126
z-orientation = 0.4329831218208718
w-orientation = 0.9014020280752935
```

**Never reuse those coordinates unless they are valid for the current map and physical robot pose.**

---

# M. Cleanup after the isolated test

Stop in this order:

1. mission (`hack_my_robot`)
2. mock `move_base`
3. isolated `roscore -p 11312`

Use `Ctrl+C` in each corresponding terminal.

Then restore physical-master environment before doing other robot work:

```bash
export ROS_MASTER_URI=http://localhost:11311
export ROS_IP="$(hostname -I | awk '{print $1}')"
unset ROS_HOSTNAME
rosnode list
```
