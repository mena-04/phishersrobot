# PHASE 2 — Criterion 2: Sensitive `.ifc` file

**Competition-day command reference — copy and paste, no executable scripts.**

**Source:** *Hack My Robot 2026 — Finals Prep & Cheat Sheet*, **page 3**, “Criterion 2 — Access the sensitive .ifc file (10 pts).” The same document also discusses IFC exfiltration on **page 11** under a different phase and score (15 pts); **confirm the official current scoring and file location** rather than assuming the two descriptions agree.

**Terminal legend:** `KALI` = local Kali VM; `PI` = an SSH session on the assigned Raspberry Pi; `WSL` = Ubuntu 20.04 development environment. Run commands only on team-owned test files or systems and paths explicitly in the organizers' authorized competition scope. Never upload credentials or sensitive IFC data to a public repository.

## 0. Confirm the assigned robot and access

**KALI — inspection (not guaranteed to discover an unknown host):**

```bash
ip -br addr
ip route
ip neigh show
ss -tn state established
```

**KALI — after the assigned robot IP has been confirmed:**

```bash
export ROBOT_IP='REPLACE_WITH_CONFIRMED_IP'
printf 'Robot IP: %s\n' "$ROBOT_IP"
ip route get "$ROBOT_IP"
ping -c 3 "$ROBOT_IP"
nc -vz -w 5 "$ROBOT_IP" 22
ssh ubuntu@"$ROBOT_IP"
```

**PI — identify the machine:**

```bash
whoami
hostname
hostname -I
```

**Status:** Known-IP SSH verified on practice robot. Unknown-IP discovery from scratch and competition credentials are **not verified**. An IP from an earlier day may be stale.

## 1. Identify an authorized IFC file — primary plan route

**PI — workspace inspection:**

```bash
ls -la ~/catkin_ws/src/
find ~/phase2-lab -type f -iname '*.ifc' 2>/dev/null
file ~/phase2-lab/training.ifc
sha256sum ~/phase2-lab/training.ifc
```

**PI — scoped recently changed files (illustrative; NOT TESTED):**

```bash
find ~/phase2-lab -type f -newer /etc/hostname 2>/dev/null
```

**Plan note:** Page 3 proposes filesystem-wide `find / -iname '*.ifc'` and `find / -newer /etc/hostname`. These were **not validated**; use only within an explicitly authorized scope. `/etc/hostname` modification time is an imperfect reference for “recent.” The only successfully located IFC was the team's mock `~/phase2-lab/training.ifc`.

## 2. Copy the authorized file — primary plan route

**KALI — in a local terminal, not the PI SSH shell:**

```bash
export ROBOT_IP='REPLACE_WITH_CONFIRMED_IP'
mkdir -p ~/hack-my-robot/phase2-data
scp ubuntu@"$ROBOT_IP":/home/ubuntu/phase2-lab/training.ifc ~/hack-my-robot/phase2-data/
file ~/hack-my-robot/phase2-data/training.ifc
head -n 5 ~/hack-my-robot/phase2-data/training.ifc
sha256sum ~/hack-my-robot/phase2-data/training.ifc
```

**PI — compare source digest:**

```bash
sha256sum ~/phase2-lab/training.ifc
```

**Verified:** SCP transferred the **214-byte mock** `training.ifc`, the file began with `ISO-10303-21;`, and source/destination SHA-256 hashes matched. The real sensitive IFC has **not** been found or copied.

## 3. Network-transmission fallback — controlled SCP lab

**KALI terminal A — capture the team's own transfer on the tested `eth0` interface:**

```bash
sudo tshark -i eth0 -a duration:30 -f 'tcp port 22' -w /tmp/phase2-scp.pcapng
```

**KALI terminal B — during the capture, repeat the authorized mock transfer:**

```bash
export ROBOT_IP='REPLACE_WITH_CONFIRMED_IP'
scp ubuntu@"$ROBOT_IP":/home/ubuntu/phase2-lab/training.ifc ~/hack-my-robot/phase2-data/
```

**KALI terminal A — after the capture finishes:**

```bash
sudo tshark -r /tmp/phase2-scp.pcapng -q -z io,phs
sudo tshark -r /tmp/phase2-scp.pcapng -Y ssh
sudo tshark -r /tmp/phase2-scp.pcapng -q -z conv,tcp
```

**Verified lab observation:** 67 TCP packets, 9,997 bytes; 36 decoded as SSH. Kali `10.0.2.15:57206` communicated with robot `10.10.187.4:22` for about 5.64 seconds. The visible SSH session used encryption; no plaintext IFC contents were demonstrated.

**NOT VERIFIED:** Whether the real autonomous mission sends an IFC file, whether any such transfer is plaintext, or whether the VM can observe third-party wireless traffic. The plan's `tshark -i wlan0 ...` assumes a wireless interface that this Kali VM **does not have**. Do not use the university network as a packet-interception lab.

## 4. ROS topics and services — fallback inventory

**PI — free SSH terminal; do not type in the terminals occupied by `roscore` or `roslaunch`:**

```bash
source ~/catkin_ws/devel/setup.bash
hostname -I
echo "$ROS_MASTER_URI"
echo "$ROS_IP"
pgrep -af 'roscore|rosmaster|roslaunch|serial_node|ld08_driver'
ss -ltn | grep 11311
```

**PI — if ROS Master is already running, use the current IP in this terminal:**

```bash
export ROS_IP="$(hostname -I | awk '{print $1}')"
export ROS_MASTER_URI="http://$ROS_IP:11311"
rosnode list
rostopic list
rosservice list
```

**PI — inspect standard nodes only when they are running:**

```bash
rosnode info /turtlebot3_core
rosnode info /turtlebot3_lds
```

**Recovery only if no Master is running (dedicated terminal; don't duplicate an existing one):**

```bash
source ~/catkin_ws/devel/setup.bash
export ROS_IP="$(hostname -I | awk '{print $1}')"
export ROS_MASTER_URI="http://$ROS_IP:11311"
roscore
```

**Verified:** Standard nodes included `/turtlebot3_core`, `/turtlebot3_lds`, and `/turtlebot3_diagnostics`; observed services were logging-related. No IFC-serving interface was identified among those nodes. Starting `roscore` alone exposes only `/rosout` and related logging topics/services.

## 5. Inspect the organizer's published ROS package

**WSL — Ubuntu 20.04, not the Raspberry Pi:**

```bash
source ~/catkin_ws/devel/setup.bash
rospack find hack_my_robot
cd "$(rospack find hack_my_robot)"
find launch nodes src -maxdepth 3 -type f
grep -RnE 'rospy\.(Publisher|Subscriber|Service|ServiceProxy)' nodes src
grep -RniE '\.ifc|ifcopenshell|open\(' nodes src launch
grep -RniE '\.ifc|ifcopenshell|IFC4|ISO-10303-21' . --exclude-dir=.git
```

**Verified:** Package located at `/home/mena/catkin_ws/src/hack_my_robot_2026`. The inspected code reads/writes `saved_path/scan_positions.csv` (navigation waypoints, **not** IFC data), and includes `/addpose`, `/waypoints`, `/path_ready`, `/path_reset`, `/start_journey`, and an optional `/image_saver/save` client. The final repository-wide IFC keyword search returned no matches. This does **not** establish the absence of an IFC file on the final competition robot.

## 6. Quick troubleshooting

**KALI — `$` is required to expand the variable:**

```bash
printf 'Robot IP: %s\n' "$ROBOT_IP"
nc -vz -w 5 "$ROBOT_IP" 22
```

**KALI — if a complicated TShark filter fails, use the verified one-line conversation command:**

```bash
sudo tshark -r /tmp/phase2-scp.pcapng -q -z conv,tcp
```

**PI — if `rosnode list` cannot contact Master:**

```bash
hostname -I
echo "$ROS_MASTER_URI"
echo "$ROS_IP"
pgrep -af 'roscore|rosmaster'
ss -ltn | grep 11311
```

## 7. Final plan audit — do not overclaim

| Page 3 plan item | What was actually demonstrated | Status |
|---|---|---|
| SSH access | Practice robot with known credentials | VERIFIED IN LAB |
| Find `.ifc` | Found team's mock file in known directory | VERIFIED IN LAB |
| Recently added files | Scoped example provided, not run | NOT TESTED |
| Copy file with SCP | 214-byte mock IFC transferred | VERIFIED IN LAB |
| Prove retrieval | Matching source/destination SHA-256 | VERIFIED IN LAB |
| Observe transfer on network | Captured team's own SSH/SCP traffic | VERIFIED IN LAB |
| Determine if mission transmits IFC | No mission capture | NOT TESTED |
| Inspect ROS topics/services | Standard ROS nodes enumerated | VERIFIED |
| Inspect custom software | Published source reviewed; no explicit IFC reference | STATIC INSPECTION |
| Retrieve actual sensitive IFC | No real challenge file provided | FINALS ONLY |

**Do not commit** recovered passwords, sensitive IFC contents, private captures, or credentials. The successful training results are preparation evidence, not proof of achieving Criterion 2 in the finals.
