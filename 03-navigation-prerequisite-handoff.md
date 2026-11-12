# Phase 3 (prerequisite) — Autonomous navigation bring-up

> **Status:** continuation guide, **not** a completed scoring result. Autonomous
> physical movement was **not** demonstrated in the last lab session (7 Nov).
> Before any Criterion 3 route-change attempt can score, the robot must first
> drive an autonomous goal. This page is the recovery/diagnosis path to get there.
>
> **Scope:** Authorized TurtleBot3 Criterion 3 practice on the team's assigned
> robot and lab desktop only. Confirm current IPs and process state before
> running anything — equipment may have restarted.

Source: *Criterion 3 continuation handoff* compiled 8 Nov 2026 (Asia/Dubai) from
the 7 Nov lab session. The route-change attack itself lives in
`03-path-alteration-competition-runbook.md`; **this** file is only the
navigation prerequisite.

---

## 1. Where things stood (last observed)

| Item | Last observed result |
|---|---|
| Manual remote keyboard control | Worked after publishing `motor_power=true` |
| Map and navigation | Saved map exists; AMCL and `move_base` initialized |
| Local costmap | ~7 Hz after forcing full grids and restarting `move_base`; RViz OK |
| Navigation goal | Accepted as ACTIVE; desktop published `angular.z=1.0`, `linear.x=0.0` |
| Physical autonomous movement | **Not demonstrated** — robot stayed stationary |
| Confirmed blocker | Pi `rosnode ping /move_base` timed out; no inbound `cmd_vel` connection on `turtlebot3_core` |
| Criterion 3.1 scoring demo | **Not completed** — baseline and altered routes not yet run |

**Root symptom:** goals reach the desktop planner, but the **Pi cannot reach the
desktop `move_base` XML-RPC endpoint**. Receiving scans/odom on the desktop does
*not* prove the reverse direction works.

**First action for the next operator:** continue the reverse-connection diagnosis
(Section 3). Do **not** start by remapping, reflashing firmware, changing random
parameters, or drawing more pose arrows.

---

## 2. Environment and retained files

> **Practice values — confirm live on competition day. Never reuse a historical IP/PID.**

| Location | Details |
|---|---|
| Pi / robot | Ubuntu 20.04.6 ARM64; ROS Noetic; TurtleBot3 Burger; OpenCR fw v1.2.6; LDS-02. Last IP `10.10.184.153` |
| Lab desktop | Ubuntu 24.04 x86_64; Wayland; last IP `10.10.169.186`; Docker bridge `172.17.0.1`; no native Noetic |
| Docker | Container `hmr-noetic-gui`; image `hmr-noetic:prepared`; base `osrf/ros:noetic-desktop-full`; network mode `host` |
| ROS master | `http://10.10.184.153:11311` on the Pi |

**Know which terminal you are on:**

```text
Desktop host: dslab@dslab-OptiPlex-5490-AIO:~$
Docker shell: root@dslab-OptiPlex-5490-AIO:/#
Pi via SSH:   ubuntu@ubuntu:~$
```

ROS commands for the desktop belong **inside Docker**. A new Docker shell needs
`source /opt/ros/noetic/setup.bash`. Desktop shell startup errors about missing
Noetic/catkin are stale host config, not a broken container.

**Maps** (`map.yaml`/`map.pgm`, `map_fresh.yaml`/`map_fresh.pgm`):
container `/root/hmr/` ↔ desktop `/home/dslab/hmr-lab/`. **Use
`/root/hmr/map_fresh.yaml`** (384×384 cells, 0.05 m/cell, origin (-10,-10)).
Localization remains unconfirmed; the map has incomplete/doubled outlines.

---

## 3. Current blocker — diagnose in this order

### A. Desktop host: inspect the listener

```bash
hostname -I
sudo ufw status
sudo docker inspect -f '{{.HostConfig.NetworkMode}}' hmr-noetic-gui
sudo ss -lntp | grep move_base
```

Confirmed earlier: desktop IP `10.10.169.186`, UFW inactive, Docker network
`host`. **The `ss` listener check is the outstanding result.** Record the
listening addresses and ports — ROS node ports change after every restart.

### B. Pi SSH: test the return connection

```bash
source /opt/ros/noetic/setup.bash
unset ROS_HOSTNAME
export ROS_IP=10.10.184.153
export ROS_MASTER_URI=http://10.10.184.153:11311
ping -c 3 10.10.169.186
rosnode info /move_base
timeout -s INT -k 2 8 rosnode ping -c 1 /move_base
```

The ping-to-node attempt last **timed out**. Capture the advertised URI from
`rosnode info` and compare its host/port with the desktop listener. If needed,
test raw TCP to that exact port from the Pi with Python
`socket.create_connection`. An ICMP ping alone is not sufficient.

### Interpretation

- **Wrong advertised IP** → fix `ROS_IP`/`ROS_HOSTNAME` in the shell that
  launches the node, then restart that node.
- **Listener only on loopback** → investigate node environment/binding.
- **Correct listener but remote TCP blocked** → investigate host filtering,
  routing, and campus network policy *with the lab admin*. Do not assume UFW is
  the only filter or disable protections blindly.

ROS1 uses the master **plus** per-node XML-RPC **plus** dynamically assigned
TCPROS ports. Making only port 11311 reachable is **not** enough. Running the
navigation stack *on the Pi* is a possible fallback if resources/packages permit
(not yet attempted/validated).

**Pass condition before autonomous testing:** Pi `rosnode ping /move_base`
succeeds; `turtlebot3_core` shows an incoming `/cmd_vel` connection to
`move_base`; a bounded test command reaches the Pi; motors still respond. Then
recheck localization and attempt a short clear goal.

---

## 4. Restart recipe — Pi and motors (after a shutdown only)

```bash
# 1) Desktop: connect to Pi
ssh ubuntu@10.10.184.153

# 2) Pi: bringup (leave running)
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
unset ROS_HOSTNAME
export ROS_IP=10.10.184.153
export ROS_MASTER_URI=http://10.10.184.153:11311
export TURTLEBOT3_MODEL=burger
export LDS_MODEL=LDS-02
roslaunch turtlebot3_bringup turtlebot3_robot.launch --screen
# expect: /dev/ttyACM0 @115200, "Connected to OpenCR board!", "Calibration End",
#         LiDAR LD08 @ /dev/ttyUSB0
```

```bash
# 3) Separate Pi SSH: manual sanity test (stop navigation / cancel goals first;
#    clear floor space; check battery — earlier it ran on USB only)
source /opt/ros/noetic/setup.bash
unset ROS_HOSTNAME
export ROS_IP=10.10.184.153
export ROS_MASTER_URI=http://10.10.184.153:11311
export TURTLEBOT3_MODEL=burger
rostopic pub -1 /motor_power std_msgs/Bool "data: true"
roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
# click inside teleop; w ×3, wait ~1 s, s; a brief 'a' to test turning, then s.
# teleop has NO obstacle avoidance. Press s then Ctrl+C before returning to nav.
```

What this proves: motors move after `motor_power=true`. What it does **not**
prove: that the *desktop* navigation publisher can reach the Pi — a teleop node
launched over SSH runs *on the Pi* and skips the cross-machine link.

---

## 5. Restart recipe — desktop navigation (inside Docker)

```bash
# Desktop host: enter the EXISTING container (do not create a blank one)
sudo docker start hmr-noetic-gui
sudo docker exec -it hmr-noetic-gui bash
```

```bash
# Docker shell: start navigation (leave running; start RViz separately)
source /opt/ros/noetic/setup.bash
unset ROS_HOSTNAME
export ROS_IP=10.10.169.186
export ROS_MASTER_URI=http://10.10.184.153:11311
export TURTLEBOT3_MODEL=burger
rosparam set /move_base/local_costmap/always_send_full_costmap true
rosparam set /move_base/global_costmap/always_send_full_costmap true
roslaunch turtlebot3_navigation turtlebot3_navigation.launch \
  map_file:=/root/hmr/map_fresh.yaml open_rviz:=false
```

**If grid publication stalls again** (selective restart that worked last session —
does not fix network reachability; never run two `move_base`):

```bash
rosservice call /request_nomotion_update "{}"
rosnode kill /move_base
rosparam set /move_base/local_costmap/always_send_full_costmap true
rosparam set /move_base/global_costmap/always_send_full_costmap true
rosrun move_base move_base __name:=move_base
```

**Verify from another sourced Docker shell:**

```bash
timeout -s INT -k 2 6 rostopic hz /move_base/local_costmap/costmap
timeout -s INT -k 2 6 rosrun tf tf_echo map base_footprint
```

---

## 6. RViz localization and a bounded goal test

```bash
# another Docker shell
source /opt/ros/noetic/setup.bash
unset ROS_HOSTNAME
export ROS_IP=10.10.169.186
export ROS_MASTER_URI=http://10.10.184.153:11311
rviz -d /opt/ros/noetic/share/turtlebot3_navigation/rviz/turtlebot3_navigation.rviz \
  __name:=rviz_check
```

- Fixed Frame = `map`. Keep Map, RobotModel, LaserScan visible. The green arrows
  are the AMCL particle cloud (possible poses) — **not** laser returns; hide them
  when comparing scan to walls.
- **2D Pose Estimate:** click-hold at the robot's *actual physical* map location,
  drag toward its front, release. One arrow only; arrow length is not distance.
  Last session: bin = curved scan feature, wall behind robot = straight feature,
  ~1.11 m. **Do not** publish a fake static map→odom transform to hide a
  localization error.

```bash
rostopic info /initialpose          # /rviz_check publishes, /amcl subscribes
rosservice call /request_nomotion_update "{}"
```

**Only after network + localization pass:** enable Local Map ▸ Costmap (expect
Map OK / Transform OK, nonzero dims), select **2D Nav Goal**, pick a short clear
destination ahead, drag for heading, release. Watch physical travel and stopping.

**Cancel and inspect:**

```bash
rostopic pub -1 /move_base/cancel actionlib_msgs/GoalID "{}"
timeout -s INT -k 2 5 rostopic echo -n 1 /move_base/status
timeout -s INT -k 2 5 rostopic echo /cmd_vel
# status: 0 pending 1 active 2 preempted 3 succeeded 4 aborted 5 rejected
# no movement + nonzero cmd_vel -> delivery/torque check
# zero cmd_vel -> planner/status/log check
# a cancelled goal is NOT proof the robot physically stopped — verify.
```

---

## 7. Troubleshooting cautions (do not carry forward as fact)

- IMU ~198 Hz but no `sensor_state` → serial traffic exists; check
  motor/encoder comms. The firmware skips `sensor_state` when wheel-encoder reads
  fail — a *plausible* secondary issue, not a confirmed diagnosis. Do **not**
  reflash firmware repeatedly without evidence.
- "Publishers: None on `cmd_vel`" → teleop must stay running while inspecting.
- Master accessible but `move_base` unreachable → ROS graph access ≠ direct node
  access; check advertised address and dynamic ports.
- Do **not**: infer clock skew from two `date` calls around a password prompt;
  assume battery % is calibrated; blame all nav failures on power; install ROS1
  Focal packages natively on the Noble host; apply WSL commands to the desktop.

Useful Pi diagnostics:

```bash
ls -l /dev/ttyACM* /dev/ttyUSB*
timeout -s INT -k 2 5 rostopic hz /imu
timeout -s INT -k 2 5 rostopic echo -n 1 /sensor_state
timeout -s INT -k 2 5 rostopic echo -n 1 /battery_state
rosnode info /turtlebot3_core
```

---

## 8. Confirm the mission package (needed before any route change)

```bash
rospack find hack_my_robot
roscd hack_my_robot
cat launch/hack_my_robot_complete.launch
rostopic info /addpose          # expected PoseWithCovarianceStamped
rostopic info /waypoints        # expected PoseArray
rostopic info /path_ready       # expected std_msgs/Empty
rostopic info /start_journey    # expected std_msgs/Empty
```

The supplied launch hardcodes `map_file=/home/sxp8070/map.yaml` — override it or
expose a map arg to use `/root/hmr/map_fresh.yaml`. WSL previously built the
package under `~/catkin_ws/src/hack_my_robot_2026`; its presence in the lab
Docker container is **unconfirmed**. Do not launch a second navigation stack.

**References:** ROBOTIS OpenCR eManual; `github.com/ROBOTIS-GIT/OpenCR`;
competition repo `github.com/SMART-NYUAD/hack_my_robot_2026`. Original lab
logs/screenshots remain the evidence for observed results.
