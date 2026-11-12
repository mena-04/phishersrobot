# Phase 5 — Robot Availability (Criterion 5)

> **Teammate handoff and competition-day command runbook.**  
> The Phishers | 10 November 2026  
> **Status:** partial LiDAR-service interruption and recovery demonstrated in practice. Competition scoring pending.

## Goal

Intentionally interrupt an authorized robot resource, demonstrate the effect, and restore normal service.

| Criterion | Points | Our status |
| --- | ---: | --- |
| 5.1 No availability impact | 0 | Not the observed result |
| 5.2 Reduced performance / resource interruption | 7 | Candidate category for our LiDAR interruption; judge acceptance pending |
| 5.3 Total availability loss | 10 | Not demonstrated |

These outcomes are alternatives. The test used an existing local account through a physically attached console. Confirm that this access method qualifies and whether the physical-access penalty applies.

---

# A. Practice setup

**Run robot commands on the Raspberry Pi**, either through its attached monitor/keyboard or a successful SSH session. Keep the robot stationary, with navigation and teleop inactive during this test.

| Item | Practice value |
| --- | --- |
| Robot / OS / ROS | TurtleBot3 Burger / Ubuntu 20.04 / ROS Noetic |
| Robot IP | `10.10.187.184` |
| ROS Master | `http://10.10.187.184:11311`, running on the Pi |
| Account | `ubuntu` |
| LiDAR node / executable | `/turtlebot3_lds` / `ld08_driver` |
| Scan topic | `/scan` |
| Verified driver PID | `1483` for the tested process only |

**Rediscover the IP and PID on competition day. Never reuse a historical PID without verification.**

Use separate robot consoles for:

1. ROS Master (`roscore`).
2. Hardware bringup.
3. Inspection and intervention.
4. Continuous scan observation for the next run.

Switch text consoles with Alt+F3 / F4 / F5, or Ctrl+Alt+Fn if needed. Log in separately. Leave the Master and bringup consoles running.

---

# B. Commands and results from the completed test

## B1. ROS environment

```bash
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
unset ROS_HOSTNAME
export ROS_IP=10.10.187.184
export ROS_MASTER_URI=http://10.10.187.184:11311
```

The Master was started in its own console:

```bash
roscore
```

Observed confirmation:

```text
started core service [/rosout]
```

Bringup was started in a separate console with the same ROS environment:

```bash
export TURTLEBOT3_MODEL=burger
export LDS_MODEL=LDS-02
roslaunch turtlebot3_bringup turtlebot3_robot.launch --screen
```

Observed confirmation:

```text
process[turtlebot3_lds-2]: started with pid [1483]
FOUND LiDAR_LD08 @port :/dev/ttyUSB0
Connected to OpenCR board!
Calibration End
```

## B2. Baseline and target verification

```bash
timeout 6s rostopic hz /scan
rosnode info /turtlebot3_lds
```

Selected baseline output:

```text
average rate: 11.008
average rate: 11.013
average rate: 11.014
average rate: 11.013
```

Node information confirmed:

```text
Node [/turtlebot3_lds]
 * /scan [sensor_msgs/LaserScan]
Pid: 1483
```

## B3. Interruption

Executed command:

```bash
(kill -STOP 1483 && sleep 10; kill -CONT 1483) &
```

`STOP` suspended the LiDAR driver. `CONT` was scheduled after a ten-second sleep to resume it.

The following observer was started manually after the pause command:

```bash
timeout 6s rostopic hz /scan
```

Observed output:

```text
subscribed to [/scan]
no new messages
no new messages
average rate: 15.696
average rate: 13.412
```

This observation captured both interrupted delivery and returning messages. The temporary higher rate after resumption may reflect buffered data; its cause was not separately measured.

## B4. Recovery

```bash
timeout 6s rostopic hz /scan
```

Observed output:

```text
average rate: 11.008
average rate: 11.013
average rate: 11.036
average rate: 11.030
```

**Result:** scan delivery recovered to approximately its 11 Hz baseline.

**Evidence limits:** one interruption/recovery run; ten seconds was the requested pause, not a precisely measured outage. No autonomous-mission impact, total robot outage, access-control vulnerability, or competition points were demonstrated.

---

# C. Competition-day procedure

**Prepared procedure:** the original test above ran on the robot. The improved logging and cleanup below have been checked locally, but have not been rerun on the robot.

## C1. Confirm scope and access

Before testing, confirm with judges:

- Whether interruption of `/scan` qualifies for Criterion 5.2.
- The permitted account, access route, interruption duration and recovery method.
- Whether a physically attached console affects points.
- Whether sensor loss alone is sufficient or mission impact must also be shown.

If laptop access is available, connect to the assigned host:

```text
ssh -o ConnectTimeout=5 ACCOUNT@ASSIGNED_ROBOT_IP
```

Replace the account/IP with actual assigned values. Linux commands below run **on the robot**, after login. Otherwise use its permitted local console.

## C2. Set the current ROS environment

```bash
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
hostname -I
printf 'MASTER=%s IP=%s\n' "$ROS_MASTER_URI" "$ROS_IP"
```

Use the confirmed event configuration. If the Master is on the Pi, as in practice:

```bash
read -r -p 'Current robot IP: ' ROBOT_IP
export ROS_IP="$ROBOT_IP"
export ROS_MASTER_URI="http://$ROBOT_IP:11311"
unset ROS_HOSTNAME
rosnode list
```

If the Master is on another computer, use its assigned URI instead. Leave a working Master/bringup running; do not launch duplicate stacks. If either is missing, coordinate restoration with the operator before testing.

## C3. Identify the live local LiDAR process

```bash
rosnode info /turtlebot3_lds
read -r -p 'Verified local LiDAR Pid: ' LIDAR_PID
```

Enter the current PID from node information. Then inspect it:

```bash
if [[ "$LIDAR_PID" =~ ^[0-9]+$ ]] && (( LIDAR_PID > 1 )); then
  ps -p "$LIDAR_PID" -o pid=,user=,stat=,comm=,args=
else
  echo 'STOP: invalid PID'
fi
```

Confirm it is the local `ld08_driver` process and that the ROS node URI belongs to this robot. A remote node's PID must not be used with local `kill`. If the driver/model differs, identify the correct target before adapting the procedure.

## C4. Save the baseline

```bash
EVIDENCE="$HOME/phase5-evidence/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$EVIDENCE"
chmod 700 "$HOME/phase5-evidence" "$EVIDENCE"
printf '%s\n' "$EVIDENCE"
date -Is | tee "$EVIDENCE/session-time.txt"
rosnode info /turtlebot3_lds 2>&1 | tee "$EVIDENCE/node-before.txt"
timeout -s INT -k 2s 8s rostopic hz /scan 2>&1 | tee "$EVIDENCE/baseline.txt"
```

Require a stable nonzero baseline. Approximately 11 Hz is the practice reference, not a universal requirement. If scans are already missing, restore normal service before testing.

## C5. Start the observer before the interruption

In another free **robot console**, source ROS and use the same confirmed environment as C2. Then:

```bash
read -r -p 'Existing evidence directory absolute path: ' EVIDENCE
timeout -s INT -k 2s 30s rostopic hz /scan 2>&1 | tee "$EVIDENCE/continuous-scan.txt"
```

Wait for normal rate output, then switch back to the intervention console. If the observer finishes before the action, restart it. Monitoring beforehand avoids missing the interruption while typing.

## C6. Pause and automatically resume

In the intervention console, use its already-verified `LIDAR_PID` and `EVIDENCE` variables. Keep navigation/teleop inactive and the robot stationary.

This guarded version records action times and attempts resumption on normal exit or handled interruption:

```bash
(
  if ! [[ "$LIDAR_PID" =~ ^[0-9]+$ ]] || (( LIDAR_PID <= 1 )); then
    echo 'STOP: invalid PID'
    exit 1
  fi
  if [[ "$(ps -p "$LIDAR_PID" -o comm=)" != 'ld08_driver' ]]; then
    echo 'STOP: PID is not the verified LD08 driver'
    exit 1
  fi
  trap 'kill -CONT "$LIDAR_PID" 2>/dev/null || echo "WARNING: CONT failed; inspect recovery"' EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM HUP
  date -Is
  kill -STOP "$LIDAR_PID" || exit 1
  echo "STOP sent to LiDAR PID $LIDAR_PID; requested pause: 10 seconds"
  sleep 10
  date -Is
  echo 'Attempting CONT through cleanup handler now'
) >> "$EVIDENCE/pause-actions.txt" 2>&1
cat "$EVIDENCE/pause-actions.txt"
```

The guard deliberately refuses executables other than `ld08_driver`. Do not bypass it without identifying the correct event target. Do not restart the target during the pause.

The cleanup handler is not an independent watchdog: shell/host failure or SIGKILL can prevent recovery. Keep a separate recovery console available.

## C7. Verify recovery

```bash
ps -p "$LIDAR_PID" -o pid=,stat=,comm= | tee "$EVIDENCE/process-after.txt"
timeout -s INT -k 2s 8s rostopic hz /scan 2>&1 | tee "$EVIDENCE/recovery.txt"
rosnode list 2>&1 | tee "$EVIDENCE/nodes-after.txt"
```

Require scans to return near baseline and the process to no longer be stopped (`T`). A node remaining listed in ROS does not prove fresh data is arriving.

The observer's rolling average can take time to settle. Preserve the absent-message output and fresh recovery measurement. These commands do not provide a precise outage-duration measurement.

---

# D. Recovery if needed

If the same verified LiDAR process remains paused:

```bash
kill -CONT "$LIDAR_PID"
ps -p "$LIDAR_PID" -o pid=,stat=,comm=
timeout -s INT -k 2s 8s rostopic hz /scan
```

In a new console, the PID variable will not exist automatically. Use the recorded PID only after checking the local process identity. A paused node may not respond to `rosnode info`.

| Symptom | Next action |
| --- | --- |
| `Operation not permitted` | Resolve account permissions and scope; do not automatically add `sudo` |
| `No such process` | Inspect bringup; the process may have exited/restarted. Rediscover its identity |
| Driver resumed but no scans | Inspect bringup errors, `/scan` publisher and `/dev/ttyUSB*` |
| Master unreachable | Verify the configured Master and existing process; do not start another blindly |
| Recovery requires bringup restart | Coordinate with operator, keep motion inactive, stop the known launch and restart one copy |

Do not use broad process kills or power cuts as default recovery.

---

# E. Evidence and judge handover

## E1. Existing evidence

| Screenshot | Evidence |
| --- | --- |
| `image(20261110-104700).jpg` | Bringup and LiDAR PID 1483 |
| `image(20261110-104952).jpg` | Approximately 11 Hz baseline |
| `image(20261110-105045).jpg` | Node identity and PID |
| `image(20261110-105310).jpg` / `image(20261110-105318).jpg` | Same run: deliberate pause, absent messages and recovered rate |

Preserve these original conversation attachments separately; they are not embedded in this file.

## E2. Event checklist

- [ ] Confirm assigned host/account, allowed access method and physical-access treatment.
- [ ] Record current node identity and local PID.
- [ ] Save normal scan baseline.
- [ ] Establish observer before intervention.
- [ ] Record deliberate pause and resumption.
- [ ] Save interrupted-delivery and recovery evidence.
- [ ] Confirm normal service restored.
- [ ] Notify judges immediately and record their actual decision.
- [ ] Retain required full final-round GenAI history and acknowledgment.

Suggested explanation:

> Using the permitted account and access route, we deliberately paused the LiDAR driver. Scan delivery was normal before the action, interrupted during the pause, and recovered near baseline after resumption. We request evaluation as a partial resource-availability impact under Criterion 5.2.

State the actual access prerequisites. Do not claim a vulnerability or remotely obtained access based only on this local-account test.

After recovery, archive the evidence:

```bash
tar -czf "$EVIDENCE.tar.gz" -C "$(dirname "$EVIDENCE")" "$(basename "$EVIDENCE")"
sha256sum "$EVIDENCE.tar.gz"
printf 'Archive: %s.tar.gz\n' "$EVIDENCE"
```

Copy the actual archive to a reachable teammate laptop using the approved transfer route. Keep credentials and sensitive data out of shared/public logs.

---

# F. Remaining work

**Completed:** one deliberate LiDAR scan-delivery interruption and recovery in practice.

**Still needed:** event-scope/access confirmation, rehearsal of the improved evidence procedure, competition-day execution and judge evaluation.

**High impact is not completed.** Before a 5.3 attempt, agree the evaluated resources with judges, establish a working operational baseline, demonstrate complete denial within that scope, and verify recovery. A longer LiDAR pause alone does not establish total robot unavailability. Pre-existing power/navigation failures must not be counted as intentional impact.

---

# G. Verification and references

The original pause/resume command was observed on the practice robot. Bash blocks were syntax-checked. The guarded cleanup procedure was checked with disposable local processes for normal completion, interruption recovery, invalid-PID refusal and wrong-process refusal. Those checks do not substitute for a robot rehearsal or judge acceptance.

- [Organizer scoring and rules](https://github.com/SMART-NYUAD/hack_my_robot_2026/blob/25c06e9ec32fa781219fc8bd672669fc8596dae3/README.md)
- [FIRST CVSS v3.1, section 2.3.3: Availability](https://www.first.org/cvss/v3-1/specification-document)
- [Linux STOP / CONT signal behavior](https://man7.org/linux/man-pages/man7/signal.7.html)
- [Signal permissions and PID targeting](https://man7.org/linux/man-pages/man2/kill.2.html)
- [Bounded observation with timeout](https://man7.org/linux/man-pages/man1/timeout.1.html)

Rules/source semantics cross-checked 10 November 2026. Primary practice evidence: the supplied screenshots and terminal outputs.
