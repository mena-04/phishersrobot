# The Phishers — status summary (Hack My Robot 2026)

One-page scoreboard for the team. Full detail lives in each criterion's runbook
(see [`README.md`](README.md)); the run order for the day is in
[`COMPETITION-DAY-PLAN.md`](COMPETITION-DAY-PLAN.md).

> **Honest status:** **no judge-confirmed points recorded.** Everything below is
> *preparation* — runbooks, scripts, and practice observations. Mark to judges
> exactly what you demonstrate live versus what is prepared.

## Scoreboard

| # | Criterion | Max | Status | Where |
|---|---|---:|---|---|
| 1 | Passwords (Wi-Fi 10 · PC 10 · SSH 5) | 25 | Prep done; finals values unknown until the day | `01-passwords.md` |
| 2 | Access `.ifc` file on robot | 10 | Command reference ready | `02-data-access-final.md` |
| 3 | Alter path (3.1 · 3.2 · 3.3) | 20 | **Blocked on autonomous nav**; attacks prepared | `03-path-alteration-*`, `03-navigation-prerequisite-*` |
| 4 | Increase waypoint dwell | 10 | Runbook + isolated proof ready | `04-waypoint-duration-*` |
| 5 | Availability (5.2 7 · 5.3 10) | 10 | LiDAR interrupt + recovery shown in practice | `05-availability-*` |
| 6 | Technical sophistication | 15 | ROS disruption demo done (WSL) | `06-technical-sophistication-*` |
| 7 | Creativity (wow) | 10 | Idea bank + framing | `07-creativity-and-bonus.md` |
| 8 | Bonus (poster, defenses) | 15 | Idea bank | `07-creativity-and-bonus.md` |

**Theoretical max ≈ 115 pts** (3.1/3.2/3.3 are alternatives — confirm with judges
whether they stack). Physical-access attacks score **half**.

## Three facts that drive the strategy

1. **LiDAR geometry (Criterion 3).** Scan plane ≈ 20 cm. Human prop = 15 cm →
   *invisible* (3.2 needs no planner hack). Excavator = 25 cm → *visible* →
   avoidance must be defeated (3.3).
2. **Network beats physical.** Join Bob's Wi-Fi and attack the unauthenticated ROS
   graph from your laptop (AV:N = full points). A keyboard/USB on the Pi is
   physical (AV:P = half).
3. **One unauthenticated chain.** Weak Wi-Fi password → flat ROS graph → file read,
   reroute, overload, and denial all fall out of the same foothold. That's the
   story for Criteria 6/7 and the poster.

## What's actually demonstrated (practice), vs prepared

- **Demonstrated in practice:** manual teleop after `motor_power=true`; LiDAR
  interrupt + recovery near 11 Hz (C5); selective ROS subscriber disruption +
  recovery + watchdog in WSL (C6); read-only diagnostics on the robot.
- **Prepared, not yet run end-to-end:** C3 route change (nav blocker first), C3.2/
  C3.3 collisions, C4 on the physical stack, the combined multi-criterion chain.

## Priorities for the day (short version)

1. Wi-Fi (1.1) → network foothold.
2. Lock the floor: `.ifc` (2), dwell (4), PC/SSH creds (1.2/1.3).
3. One path hit (3.2 blind-spot is cheapest high-value) + availability (5.2).
4. Chain narrative + poster for 6/7/8.
Don't gamble locked points chasing the nav blocker if it won't come up.

## Don't forget

- **Poster (A0) due to organizers by end of 12 Nov.**
- **Notify a judge immediately** when an attack works; only **intentional** effects
  score.
- **Acknowledge GenAI** — submit the full prompt/answer history to judges. Keep it
  local; do **not** push it to this repo.
- Keep live IPs, arena coordinates, the map, and captures out of the repo
  (`.gitignore` already does this).
