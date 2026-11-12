# scripts/ — competition-day helpers

Small, parametric ROS Noetic (Python 3, `rospy`) tools referenced by the criterion
runbooks. **Authorized use only:** the team's assigned competition robot in the
organizers' arena. Prefer running them from your laptop over Bob's Wi-Fi — a
**network** vector earns full points; physical access halves them.

| Script | Criterion | What it does |
|---|---|---|
| `inject_waypoints.py` | 3.1 / 3.2 | Publish waypoints to `/addpose`; optionally fire `/path_ready`. |
| `make_path_csv.py` | 3.1 | Generate `scan_positions.csv` lines for the saved-path overwrite route. |
| `drive_cmd_vel.py` | 3.3 | Open-loop `/cmd_vel` drive (bypass avoidance); safety-capped, auto-stop. |
| `fake_scan.py` | 3.3 / 6 | Forge `/scan` (clear or wall) to blind the costmap. |
| `tf_offset.py` | 3.3 / 6 | Publish an offset `map→odom` TF to mislocate the robot. |
| `arena_coords.example.env` | 3.x | Template for live arena coordinates (copy to `arena_coords.env`). |

## Before running anything

```bash
source /opt/ros/noetic/setup.bash
unset ROS_HOSTNAME
export ROS_IP=<YOUR_LAPTOP_IP>
export ROS_MASTER_URI=http://<ROBOT_IP>:11311
export TURTLEBOT3_MODEL=burger
rosnode list            # confirm you see the mission graph
```

Every script accepts `-h/--help`. `inject_waypoints.py` supports `--dry-run`.

## Safety rules for any movement script

- Clear all people, hands and feet from the arena.
- `drive_cmd_vel.py`, `fake_scan.py` and `tf_offset.py` disable or blind normal
  obstacle avoidance. Keep bursts short and speeds low.
- Keep a kill path ready at all times:
  ```bash
  python3 drive_cmd_vel.py --stop
  rostopic pub -1 /motor_power std_msgs/Bool "data: false"   # hard cut
  ```
- Kill any spoofer (`fake_scan.py`, `tf_offset.py`) the instant the demo is
  captured so the real sensor/TF recover.
- Rubric rule 4: only **intentional** effects score — be able to show the judge
  the exact command that caused what they saw.

## Do not commit

`arena_coords.env`, live IPs, the competition map, and the full GenAI
prompt/answer history are kept out of the public repo (see `.gitignore`). Submit
the GenAI history directly to the judges, not via GitHub.
