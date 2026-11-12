# The Phishers — Phase 6 Completed Work and Remaining Tasks

**Updated:** 10 November 2026, UAE time.  
**Purpose:** teammate handoff of demonstrated Phase 6 results, current blockers and next actions.  
**Scoring:** no judge-confirmed competition points recorded.

## 1. Overall status

| Component | Demonstrated work | Still needed |
| --- | --- | --- |
| **Criterion 6 — Technical Sophistication: up to 15 pts** | Selective ROS subscriber disruption, unaffected control, recovery, graph comparison and watchdog test in WSL | Final-round evaluation; assigned-robot application if required |
| **Physical robot availability experiment** | Deliberate LiDAR-driver interruption and recovery near 11 Hz | Judge acceptance of method and access route |
| **Physical robot diagnostics investigation** | ROS connections verified, LiDAR at ~11.10 Hz, diagnostics at 1.00 Hz, healthy status and advancing timestamps | Missing-scan freshness behavior remains untested |
| **Physical robot protocol manipulation** | ROS graph and source inspected | Controlled demonstration not performed |
| **Evidence package** | WSL results and previous handoff prepared; physical diagnostic screenshots captured | Include original WSL evidence directory |

**Status:** Phase 6 technical preparation is complete; scoring and final-round demonstration remain pending.

## 2. Completed ROS protocol experiment for Criterion 6

**Environment:** WSL Ubuntu 20.04 on the Windows laptop, real ROS Noetic, synthetic C++ nodes, separate local ROS Master. The experiment did not target the physical robot.

**Method:** a direct XML-RPC `publisherUpdate` call supplied an empty publisher list to one selected subscriber. The publisher and a second control subscriber continued running.

| Stage | Duration | Publisher messages | Target messages | Control messages |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 3.003607 s | 30 | 30 | 30 |
| Interruption | 4.001546 s | 40 | **0** | 40 |
| Recovery | 3.003159 s | 30 | **30** | 30 |
| Recovery watchdog enabled | 4.024969 s | 40 | **30** | 40 |

Additional verified output:

- Overall script status: **PASS**.
- Master registrations unchanged before/during interruption: **true**.
- One watchdog restoration attempt after **0.803878 seconds**.
- Largest observed target-message gap: **5.100125773 seconds**, not an exact intervention-duration measurement.

**Interpretation:** one selected subscriber lost delivery without the Master's recorded registrations changing. Restoring the publisher connection recovered delivery. The watchdog mitigated one further disruption; it did not authenticate updates or prevent repeated manipulation.

**Complexity:** AC:L is the supported interpretation for this method. C++, XML-RPC and automation do not by themselves establish AC:H. Competition sophistication scoring is a separate judge decision.

**Credit:** adapted from [Robot Hacking Manual Tutorial 12](https://github.com/vmayoral/robot_hacking_manual/tree/master/2_writeups/3_robot_exploitation/tutorial12); implementation assisted by ChatGPT.

### Evidence location

Original WSL directory:

```text
/home/hp/hmr-criterion6-lab/20261110-151825-72df731781
```

Preserve `results.json`, `summary.md`, `events.jsonl`, message CSVs, generated C++ source and build/process logs.

Earlier package `phase6-technical-sophistication.zip` contains the script, handoff and transcribed summary, **but not the original WSL evidence directory**. Add that directory before sharing a complete evidence package.

## 3. Completed physical-robot availability experiment

**Environment:** physical Raspberry Pi, Ubuntu 20.04, ROS Noetic, local keyboard/monitor and existing account.

| Stage | Observation |
| --- | --- |
| Baseline | `/scan` approximately 11 Hz |
| Target | `/turtlebot3_lds`, PID `1483` in that session |
| Intervention | Driver deliberately suspended with STOP; CONT scheduled after a ten-second sleep |
| During observation | `no new messages` appeared twice, followed by returning messages |
| Recovery | Scan delivery returned to approximately 11 Hz |

**Result:** one deliberate sensor-service interruption and recovery demonstrated. Ten seconds was the requested pause, not an independently measured outage duration. No complete robot outage or autonomous-mission impact was established.

**Access prerequisite:** existing local account with permission to signal the driver. No credential recovery, authentication bypass or remote exploitation was demonstrated. Rediscover the PID before any future run.

Detailed procedure: `05-availability-competition-runbook-handoff.md`.

## 4. Latest physical-robot diagnostics investigation

**Environment:** physical Raspberry Pi, Ubuntu 20.04, ROS Noetic. **Status:** read-only baseline completed; no physical publisher-list manipulation.

Confirmed on the robot:

- Historical practice IP: `10.10.187.184` (not a finals address).
- ROS Master running locally.
- `/turtlebot3_lds` publishing `/scan`.
- `/turtlebot3_diagnostics` subscribing to `/scan` and publishing `/diagnostics`.
- Diagnostic process PID `1484` in this session.
- Active inbound TCPROS connection from the LiDAR publisher.
- `/diagnostics` message type: `diagnostic_msgs/DiagnosticArray`.
- `/diagnostics` publishers included `/turtlebot3_diagnostics` and `/turtlebot3_core`; no subscribers shown during inspection.

| Measurement | Observed result |
| --- | --- |
| `/scan` rate | Approximately **11.10 Hz** |
| `/diagnostics` rate | **1.00 Hz** |
| LiDAR status | `level: 0`, `Good Condition` |
| IMU status | `level: 0`, `Good Condition` |
| Diagnostic headers | Sequence and timestamps advanced once per second |
| LiDAR connection | Active inbound TCPROS |

Three consecutive diagnostic headers:

| Sequence | Timestamp seconds |
| --- | ---: |
| 8150 | 1794315752 |
| 8151 | 1794315753 |
| 8152 | 1794315754 |

**Interpretation:** diagnostics published fresh messages during normal scan delivery. This does **not** prove the underlying LiDAR health assessment checks for stale readings.

### Source inspection

A source search found the scan callback in:

```text
~/catkin_ws/src/turtlebot3/turtlebot3/turtlebot3_bringup/src/turtlebot3_diagnostics.cpp
```

Near line 100:

```cpp
setDiagnosticsMsg(&lDS_state_, level_, "Lidar Sensor", message_, "HLS-LFCD-LDS");
```

**Not established:** whether a separate timeout detects missing scans or whether the report remains `Good Condition` when delivery stops. No physical subscriber-interruption experiment was executed in this continuation.

## 5. Ideas not executed

| Proposed technique | Status |
| --- | --- |
| Physical-robot XML-RPC publisher-list manipulation | Not performed |
| Physical diagnostics subscriber interruption | Not performed |
| Stale LiDAR health reporting demonstration | Not demonstrated |
| `/tf` corruption | Not performed |
| Fake LiDAR publication | Not performed |
| Motion-command override | Not demonstrated |
| Combined `/tf` → fake scan → motion → waypoint chain | Not performed |
| Mirror / reflective-panel experiment | Not performed |
| AC:H exploitation scenario | No qualifying uncontrolled condition identified or demonstrated |

The WSL publisher-list experiment changed a subscriber's connections; it did not publish fabricated scan data. The physical driver-pause experiment did not override motion.

## 6. Current blockers

| Blocker | Last established state |
| --- | --- |
| Physical protocol experiment | Only read-only graph, diagnostics and source inspection completed |
| Diagnostic freshness behavior | No missing-scan timeout behavior demonstrated |
| Laptop-to-robot access | Earlier handoff reported SSH timeouts; latest work used local Pi terminal |
| Evidence package | Original WSL evidence directory absent from earlier ZIP |
| Competition acceptance | Synthetic ROS demonstration eligibility not confirmed |
| Physical-access scoring | Any penalty remains subject to organizer confirmation |
| Final-round demonstration | Not performed |

Do not assume historical practice addresses or process IDs remain valid. Avoid starting a duplicate ROS Master.

## 7. Next actions, in priority order

1. **Preserve evidence:** include original WSL evidence directory and retain physical LiDAR and diagnostics screenshots.
2. **Confirm judging scope:** synthetic ROS demonstration eligibility, required robot application and any access-method penalty.
3. **Prepare judge explanation:** selective subscriber disruption, unaffected control, unchanged registrations, recovery and watchdog limitations.
4. **Retain diagnostic baseline:** `/scan` ~11.10 Hz, `/diagnostics` 1.00 Hz, `Good Condition`, advancing headers and active connection.
5. **Avoid overclaiming:** physical publisher-list manipulation, stale-health reporting and multi-technique chain remain unverified.
6. **Rehearse authorized final-round demonstration** and prepare evidence presentation.

The optional diagnostics interruption is not required to document the already completed experiments.

## 8. Competition-day requirements

- Use assigned hosts, current addresses and permitted access methods.
- Demonstrate chosen techniques during finals and notify judges promptly.
- Record baseline, intentional effect, recovery, prerequisites and limitations.
- Record judge-awarded points separately from technical observations.
- Acknowledge GenAI use and preserve the full final-round prompt/answer history.
- Poster deadline reported as 12 November 2026; finals as 13 November 2026, 14:00–18:00. Confirm organizer updates, cutoff and timezone.

**Handoff conclusion:** Phase 6 technical preparation is complete. Selective ROS subscriber disruption and recovery were demonstrated in WSL with an unaffected control and recovery watchdog. Separately, physical LiDAR-driver interruption and recovery were demonstrated. The latest physical diagnostics inspection verified normal ROS connections, scan and diagnostic frequencies, health status and advancing timestamps. Physical-robot protocol manipulation, stale-health reporting and the multi-technique chain remain unverified. No judge-confirmed sophistication points have been recorded.

### Source basis

Previous handoff `team-handoff-completed-and-remaining.md` supplies the earlier experiments, measurements and evidence locations. The latest diagnostic measurements and source-code observations come from the terminal screenshots in this conversation. Earlier experiments were not rerun during the latest diagnostics continuation.
