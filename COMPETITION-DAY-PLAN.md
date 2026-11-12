# Competition-day plan — 13 Nov 2026 (2:00–6:00 PM, NYUAD)

A run order across all criteria. Timeboxes are suggestions — adapt live. **Lock the
reliable points first; attempt the high-value, riskier ones second.** Notify a
judge the instant any attack works, and record whether each was delivered over the
**network** (full points) or via **physical** access (half).

> Prereqs the night before: laptop with ROS Noetic + aircrack-ng/CUPP ready;
> `scripts/` cloned; `arena_coords.env` created (empty template filled on the day);
> GenAI capture running so you can submit the full prompt/answer history.

---

## 2:00–2:30 — Setup

- [ ] Join the arena, power the robot, confirm it boots and the mission launches.
- [ ] Get the **live** robot IP and your laptop IP. Write them into
      `scripts/arena_coords.env`. **Never reuse old IPs.**
- [ ] Source ROS and confirm `rosnode list` shows the mission graph (`/addpose`,
      `/waypoints`, `/move_base/status`, `/scan`).
- [ ] In RViz, confirm localization and read off `map`-frame coordinates of the
      baseline waypoints, the **human** prop and the **excavator** prop →
      `arena_coords.env`.

## 2:30 onward — Competition (judged)

### Track A — the 20-minute Wi-Fi race (Criterion 1.1, 10 pts) — do FIRST
- [ ] Capture/crack Bob's Wi-Fi before the 20-min announcement
      (`01-passwords.md` §1.1). If you miss it, request the password and proceed —
      you lose only 1.1, not the rest.
- [ ] Once on the network, **everything else becomes a network attack.**

### Track B — reliable floor (lock these next)
- [ ] **1.2 / 1.3** — Bob's PC password from the personal elements (CUPP list),
      robot SSH creds (`01-passwords.md`). [25 pts criterion]
- [ ] **Criterion 2** — pull the `.ifc` file off the robot
      (`02-data-access-final.md`). [10]
- [ ] **Criterion 4** — inflate waypoint dwell / overload
      (`04-waypoint-duration-competition-runbook-final.md`). [10]

### Track C — path (Criterion 3) — needs autonomous nav working
- [ ] **First** clear the nav blocker (`03-navigation-prerequisite-handoff.md`):
      Pi↔desktop `move_base` reachability, localization, one clean autonomous goal.
      *If nav can't be made to run, 3.x can't score — don't sink the whole session
      into it; bank the other criteria.*
- [ ] **3.1** reroute, no collision (`inject_waypoints.py` → `/path_ready`). [10]
- [ ] **3.2** hit the human — place a waypoint beyond the 15 cm prop; LiDAR is
      blind to it. [15]
- [ ] **3.3** hit the excavator — defeat avoidance (fake `/scan`, or
      `max_obstacle_height`, or `/cmd_vel`). [20]
- [ ] Take whichever of 3.1/3.2/3.3 you can do **reliably** (confirm with judges
      whether they stack).

### Track D — availability (Criterion 5)
- [ ] **5.2** low impact — deliberate LiDAR-driver interrupt + recovery
      (`05-availability-competition-runbook.md`). [7]
- [ ] Only attempt **5.3** total loss if you've agreed the scope with judges. [10]

### Track E — sophistication / creativity (Criteria 6, 7, 8)
- [ ] Narrate the **single unauthenticated kill chain** (`07-creativity-and-bonus.md`).
- [ ] Have the CVSS table and the before/after RViz shots ready.
- [ ] Optional combined one-action demo — only if each piece already works.

## Throughout
- [ ] For **every** success: call a judge, show it live, state network vs physical.
- [ ] Record evidence as you go (video, RViz, terminal, the exact command).
- [ ] Keep a kill path ready: `drive_cmd_vel.py --stop` /
      `rostopic pub -1 /motor_power std_msgs/Bool "data: false"`.

## 5:00–6:00 — Poster
- [ ] Present the poster (10 min). Kill-chain diagram + before/after evidence +
      CVSS + mitigations (feeds Criteria 7 & 8).
- [ ] **Submit the full GenAI prompt/answer history to the judges.**

---

### Priority if time is short
1. Wi-Fi (1.1) → network foothold.
2. `.ifc` (2) + dwell (4) + SSH/PC creds (1.2/1.3) — reliable, high floor.
3. One path hit (3.2 blind-spot is the cheapest high-value) + availability (5.2).
4. Chain narrative + poster for 6/7/8.
Don't gamble locked points chasing nav if it won't come up.
