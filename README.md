# The Phishers — Hack My Robot 2026

Team repository for **SMART-NYUAD "Hack My Robot 2026"** (CSAW'26 MENA).
Target: a TurtleBot3 Burger (ROS Noetic) acting as an autonomous quarry dump
truck. Each criterion has its own command runbook; competition-day helper scripts
live in [`scripts/`](scripts/).

> **Authorization & scope.** Everything here is for the team's **assigned
> competition robot** in the organizers' arena, and for the team's own practice
> equipment. Nothing in this repo is permission to test university networks,
> other access points, real people's accounts, or any unrelated host. Keep live
> IPs, the arena map, competition coordinates, and the GenAI prompt/answer history
> **out** of this public repo (see `.gitignore`).
>
> **No scored results are claimed here.** These are *preparation runbooks*.
> Each file marks what was demonstrated in practice versus what is prepared but
> unverified. Don't present a prepared step as a scored one.

---

## Scenario (from the organizers)

The TurtleBot is an autonomous dump truck running a 4-waypoint load/haul routine in
a quarry. Material loaded ∝ dwell time at each waypoint. Operator **Bob** monitors
it from an on-site office over a 5 GHz Wi-Fi router. His Wi-Fi password is a
*common* one he refused to change; his PC password combines personal elements
(revealed at the start of finals); he SSHes to the robot and saved the credentials
in a file he "made more secure" (a hint is provided).

## Scoring criteria

| # | Criterion | Max pts | Runbook | Status |
|---|---|---:|---|---|
| 1 | Passwords (1.1 Wi-Fi 10 · 1.2 Bob's PC 10 · 1.3 robot SSH 5) | 25 | [`01-passwords.md`](01-passwords.md) | prep done; finals values unverified |
| 2 | Access sensitive `.ifc` file on robot (Yes/No) | 10 | [`02-data-access-final.md`](02-data-access-final.md) | command reference ready |
| 3 | Alter path — 3.1 reroute 10 · 3.2 hit human 15 · 3.3 hit excavator 20 | up to 20 | [`03-path-alteration-competition-runbook.md`](03-path-alteration-competition-runbook.md) + [`03-navigation-prerequisite-handoff.md`](03-navigation-prerequisite-handoff.md) | **blocked on autonomous nav**; attack prepared |
| 4 | Increase waypoint dwell (overload) (Yes/No) | 10 | [`04-waypoint-duration-competition-runbook-final.md`](04-waypoint-duration-competition-runbook-final.md) | runbook + isolated proof ready |
| 5 | Availability (5.2 low 7 · 5.3 total 10) | up to 10 | [`05-availability-competition-runbook.md`](05-availability-competition-runbook.md) | LiDAR interrupt+recovery shown in practice |
| 6 | Technical sophistication | 0–15 | [`06-technical-sophistication-handoff.md`](06-technical-sophistication-handoff.md) | WSL ROS disruption demo done |
| 7 | Creativity (wow) | 0–10 | [`07-creativity-and-bonus.md`](07-creativity-and-bonus.md) | idea bank + framing |
| 8 | Bonus (incl. poster, defenses) | up to 15 | [`07-creativity-and-bonus.md`](07-creativity-and-bonus.md) | idea bank |

**Key technical fact (Criterion 3):** LiDAR plane ≈ **20 cm**. Human prop = **15 cm**
→ *invisible* (3.2 needs no planner hack). Excavator prop = **25 cm** → *visible* →
avoidance must be defeated (3.3).

## Two rules that change your score

- **Physical access halves points.** A keyboard/monitor/USB on the Pi is a
  *physical* vector (AV:P) → half. Doing the same thing **over Bob's Wi-Fi** from
  your laptop is *network* (AV:N) → full. **Prefer the network path everywhere.**
- **Only intentional effects score.** If the robot disconnects or collides due to a
  fault, it's worth nothing — be ready to show the judge the exact command behind
  what they saw, and notify a judge the moment an attack works.

## Repository map

```
README.md                                    this index
SUMMARY.md                                   one-page scoreboard / status
COMPETITION-DAY-PLAN.md                      minute-by-minute run order for 13 Nov
01-passwords.md                              Criterion 1
02-data-access-final.md                      Criterion 2
03-navigation-prerequisite-handoff.md        Criterion 3 — get autonomous nav working first
03-path-alteration-competition-runbook.md    Criterion 3 — 3.1 / 3.2 / 3.3 attacks
04-waypoint-duration-competition-runbook-final.md   Criterion 4
05-availability-competition-runbook.md       Criterion 5
06-technical-sophistication-handoff.md       Criterion 6
07-creativity-and-bonus.md                   Criteria 7 & 8
scripts/                                      parametric ROS helpers (see scripts/README.md)
docs/session-setup.md                         earlier WSL / wireless / ROS-network setup history
docs/evidence-status.md                       asset inventory + lab transfer checklist
docs/handoffs/Criterion_3_Continuation_Handoff.pdf   original 9-page Criterion 3 handoff (8 Nov)
```

## Quick start on competition day

```bash
# laptop, joined to Bob's Wi-Fi:
source /opt/ros/noetic/setup.bash
unset ROS_HOSTNAME
export ROS_IP=<YOUR_LAPTOP_IP>
export ROS_MASTER_URI=http://<ROBOT_IP>:11311   # confirm live; never reuse an old IP
export TURTLEBOT3_MODEL=burger
rosnode list            # confirm you can see the mission graph
```

Then follow `COMPETITION-DAY-PLAN.md`.

## Timeline

- **Poster due to organizers: end of 12 Nov 2026** (A0; template in the rules).
- **Finals: 13 Nov 2026**, 2–6 PM at NYUAD — 2:00 setup, 2:30–5:00 compete/judge,
  5:00–6:00 poster presentations (10 min/team).
- **GenAI must be acknowledged**: submit the full prompt/answer history to judges
  at the end. Keep it locally; do **not** push it here.

## Team

The Phishers — Shahad Mohamed Rikas, Mena Abdelmoneim, Tehsin Shaik,
Besmala Eldjabri (Khalifa University).

Competition repo: <https://github.com/SMART-NYUAD/hack_my_robot_2026>
