# Evidence and asset inventory

Index assembled 13 November 2026. Dates and addresses inside older runbooks are historical practice references. The original Criterion 3 record covers 7 November; its PDF was prepared 8 November. Team phase-4/5 documents contain later work and should be read on their own terms.

## Included in this update

| Item | Origin / scope |
| --- | --- |
| `README.md` | New index linking all five phase runbooks and stating recorded preparation status |
| `03-path-alteration.md` | Criterion 3 continuation guide reconstructed from the supplied conversation and its handoff |
| `docs/handoffs/Criterion_3_Continuation_Handoff.pdf` | Original nine-page PDF generated in this conversation, retained as a dated historical handoff |
| `docs/session-setup.md` | Earlier WSL, wireless hardware, package/workspace, ROS networking, and desktop/container setup notes |
| `docs/evidence-status.md` | This inventory and the lab transfer checklist |
| `.gitignore` | Local build/cache/archive and private-evidence exclusions for future commits |

The existing `01-passwords.md`, `02-data-access-final.md`, `04-waypoint-duration-competition-runbook-final.md`, and `05-availability.md` are retained as the team's phase documents. This update does not re-run their experiments or replace their results with the older Criterion 3 session.

## Assets still on the operator's lab equipment

| Asset | Last known location | Availability here |
| --- | --- | --- |
| Fresh map pair | Desktop `~/hmr-lab/map_fresh.yaml`, `map_fresh.pgm`; container `/root/hmr/` | Locations confirmed in chat; bytes not supplied |
| Original map pair | Desktop `~/hmr-lab/map.yaml`, `map.pgm` | Locations confirmed in chat; bytes not supplied |
| Prepared Docker image | Lab desktop `hmr-noetic:prepared` | Image not transferred |
| GUI container state | Lab desktop `hmr-noetic-gui` | Not a portable artifact in this repository |
| WSL mission checkout | `/home/shaha/catkin_ws/src/hack_my_robot_2026` | Successful build observed; checkout not supplied |
| Other team mission workspaces | Paths documented in phase 2 and phase 4 | Inspect the appropriate machine; not assumed identical to WSL |
| ROS logs and recordings | Operator's `~/.ros/log/` and local evidence directories | Terminal excerpts are summarized; raw archives not supplied |
| Phase-1 capture / candidate files | Practice machines described in `01-passwords.md` | Keep private or synthetic; not bundled |
| Mock IFC and SCP evidence | Paths described in `02-data-access-final.md` | Not copied into this update |
| Phase-4 timing helper and logs | Paths/code described in the phase-4 runbook | Runbook retained; exact local files not separately imported |
| Phase-5 screenshots and logs | Names/directories described in `05-availability.md` | Runbook retained; original screenshot bytes not imported |
| Full GenAI interaction history | Original conversation/export | Not a complete transcript in this repository |

No result should be promoted from planned to demonstrated merely because a command appears in a runbook. Raw sensitive IFCs, credentials, private packet captures, or third-party personal data should not be published with this public project.

## Optional transfer from the lab desktop

These are prepared backup commands, not actions completed by this repository update. They run on the **lab desktop host**, outside Docker.

```bash
# Inspect before exporting
ls -lh ~/hmr-lab/map*.yaml ~/hmr-lab/map*.pgm
sudo docker inspect -f '{{json .Mounts}}' hmr-noetic-gui

# Map backup: use only if all named files exist
tar -czf ~/criterion3-maps.tar.gz -C ~/hmr-lab \
  map.yaml map.pgm map_fresh.yaml map_fresh.pgm
sha256sum ~/criterion3-maps.tar.gz
```

Transfer the map pair or archive through the team's approved route, inspect YAML image paths, and only then add appropriate non-sensitive maps to the repository. Do not create fake replacement maps.

Optional container snapshot, after reviewing its contents for credentials and private files:

```bash
sudo docker commit hmr-noetic-gui hmr-noetic:handoff
sudo docker save -o ~/hmr-noetic-handoff.tar hmr-noetic:handoff
```

Docker image exports can be large. The exported image excludes bind-mounted map files, so transfer those separately. An image archive does not retain host-network, display, mount, or environment configuration as an executable deployment procedure. Save the inspected runtime configuration for the next operator. Do not add the image archive to ordinary Git history.

## Corrections to earlier suggestions

- The early cheat sheets are planning documents with inconsistent topic types and scoring claims. They were not imported as verified runbooks.
- The mission trigger topics must be checked against the actual source; historical `Bool` examples were not established as correct. Similarly, do not assume `/addpose` is `PoseStamped`.
- Phase 4's existing later runbook documents a real `~wait_duration` parameter in the version it tested. An earlier unverified suggestion is not equivalent to that evidence. The parameter is read at initialization, and `clear_params=true` affects configuration strategy.
- Source/trigger behavior is version-dependent. Later phase-4 code/log results do not fix the earlier Pi-to-desktop network connection by implication.
- Sensor height alone did not establish a guaranteed collision outcome, and no collision result was demonstrated here.
- Manual movement resumed after motor torque was enabled; this does not establish that USB power was the sole cause of every motion failure.
- The connected master, a complete TF chain, and an ACTIVE action goal each establish different facts. None alone proves physical autonomous travel.

## Retain evaluation evidence

For each real demonstration, record the scope, device identity, current addresses, code revision, actual commands, baseline, intervention, measured outcome, recovery, and judge decision. A mock experiment, a synthetic password profile, and a training IFC should remain labelled as such. Preserve any full AI history required by the event separately; this repository summary is not that export.
