# Phase 7 — Creativity (Criterion 7, 0–10) & Bonus (Criterion 8, up to 15)

> Criterion 6 scores *how sophisticated* your methods are; Criterion 7 scores the
> *"wow"/out-of-the-box* factor; Criterion 8 is open bonus (and the poster feeds
> both 7 and 8). This page is an **idea bank + framing guide**, not a claim that
> any of it has been demonstrated. Pick the few you can actually show live and
> document on the poster.

---

## 1. The single strongest story: one unauthenticated chain, end to end

The judges reward a coherent narrative more than scattered tricks. Frame
everything as **one kill chain against operator "Bob"**, each link an
unauthenticated weakness:

1. **Weak Wi-Fi** — Bob kept a *common* password (Criterion 1.1). You join his
   5 GHz network.
2. **Flat, unauthenticated ROS graph** — once on the network, the ROS master and
   every topic/service/param are open. No auth, no encryption.
3. From that single foothold you then:
   - **read the sensitive `.ifc`** off the robot (Criterion 2),
   - **reroute** the truck (Criterion 3.1),
   - **exploit sensor blind-spots** to hit the human (3.2),
   - **defeat avoidance** to hit the excavator (3.3),
   - **overload** the hauling cycle by inflating waypoint dwell (Criterion 4),
   - **deny availability** of the LiDAR/robot (Criterion 5).

The "wow" is that **all of it falls out of one weak password + an insecure
middleware** — exactly the real-world lesson of ROS 1 security. Put this chain
diagram on the poster.

---

## 2. Headline creative moves (high wow-per-effort)

### 2.1 "The safety sensor can't see the hazard" (ties to 3.2)
A 15 cm object sits **below** the 20 cm LiDAR plane, so LiDAR-only obstacle
avoidance is **structurally blind** to it — no hacking of the planner required,
just geometry. Demonstrate the robot confidently driving into something its safety
system swears isn't there. Strong, counter-intuitive, easy to show.

### 2.2 "Turn the robot's own safety setting against it" (ties to 3.3)
Instead of brute-forcing through the excavator, set
`global_costmap/obstacle_layer/max_obstacle_height` to ~0.1 m via
`dynamic_reconfigure`. The 25 cm excavator is now "too tall to be real" and is
filtered out as noise — the robot's **own** safety parameter erases the hazard.
Elegant and memorable.

### 2.3 Sensor-spoofing as integrity attack (ties to 3.3 / Criterion 6)
Out-publish the real `/scan` with a forged clear scan (`scripts/fake_scan.py`).
Show RViz: real obstacle present → you start the spoofer → obstacle vanishes →
robot drives through. Makes the "no authentication on sensor data" point vividly.

### 2.4 Record-and-replay (rosbag) attack
Capture legitimate mission traffic, then **replay** it to re-trigger behaviour
without "earning" it live:
```bash
rosbag record -O attack.bag /addpose /waypoints /path_ready /start_journey /cmd_vel
rosbag play attack.bag --topics /cmd_vel        # replay a recorded motion
```
Good "wow": the operator sees commands they never issued.

### 2.5 Simultaneous multi-criterion hit
Script a single button that, in sequence, injects a route (3), inflates dwell (4),
then suspends the LiDAR driver (5) — one action, three criteria, narrated live.
(Build it only once each piece works alone; don't risk the reliable points.)

---

## 3. Bonus (Criterion 8) — go beyond "attacker"

Bonus rewards range. The scenario is written around Bob the operator, which invites
a **blue-team / "how Bob should have secured it"** section that most teams skip:

- **Fix the chain you broke.** For each attack, one concrete mitigation:
  - WPA3 + a non-common Wi-Fi password; network/VLAN isolation for the robot.
  - Change default robot creds (`ubuntu:turtlebot`); key-only SSH.
  - Move to **ROS 2 + SROS2 / DDS security** (authentication, encryption, access
    control on topics) — the real answer to the flat-graph problem.
  - **Scan plausibility / sensor-fusion** (cross-check LiDAR against a second
    sensor or expected map) to catch spoofed `/scan`.
  - A **second low obstacle sensor** (bumper / low IR / sonar) to cover the
    sub-LiDAR blind spot that defeats 3.2.
  - TF sanity checks / rejecting duplicate `map→odom` publishers.
- **Quantify with CVSS v3.1.** Score each finding (AV/AC/PR/UI → C/I/A) using the
  same spec the rubric cites. A clean CVSS table shows rigor and directly supports
  Criteria 5 and 6.
- **Poster craft.** The poster is judged and feeds 7/8. A clear one-glance kill-
  chain diagram + before/after RViz shots + a CVSS table reads as "wow". Poster
  template and A0 size are in the rules; **due to organizers by end of 12 Nov**.
- **Reproducibility.** A tidy repo (this one) with runbooks + parametric scripts +
  evidence index is itself bonus-worthy and separates you from teams with ad-hoc
  notes.

---

## 4. Physical-access creative ideas (half points — label them clearly)

Allowed, but any goal reached through physical access is **half** points, so use
these for the *wow/creativity* story, not for the core score:

- **Mirror / reflective panel** held in the LiDAR plane to bend or blank returns
  (a physical analogue of `fake_scan.py`).
- Covering/uncovering a prop to flip it between "seen" and "unseen".

Keep the network-delivered versions as your scoring path and present the physical
ones as illustrative extras.

---

## 5. What to actually attempt (priority)

1. Lock the **reliable floor**: 1.1 Wi-Fi, 2 (.ifc), 3.1 reroute, 4 dwell.
2. Add one **high-value, reliable** headline: 3.2 (blind-spot) or 3.3 (spoof /
   max_obstacle_height), plus 5.2 availability.
3. Wrap it in the **one-chain narrative** + **CVSS table** + a **mitigations**
   section on the poster for Criteria 6/7/8.
4. Only if the above is solid, attempt the **combined one-action** demo (2.5).

**Do not overclaim.** Everything here is proposed; mark on the poster and to judges
exactly what you demonstrated live versus what is design/intent. Keep the full
GenAI prompt/answer history for submission.
