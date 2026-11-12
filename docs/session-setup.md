# Earlier environment and preparation work

This supplements the phase runbooks with setup evidence from the supplied conversation. It covers the earlier Windows/WSL work and the transition to native lab Ubuntu with Docker. These are historical observations, not current device addresses or a new installation guide.

## Windows and WSL

Two WSL distributions caused occasional shell confusion:

| Environment | Recorded context |
| --- | --- |
| Ubuntu 20.04 | User `shaha`; ROS Noetic available at `/opt/ros/noetic`; `rosversion -d` returned `noetic` |
| Ubuntu 22.04 | User `shahad`; Aircrack executables were also checked here; this was not the Noetic environment used for the robot workspace |

Open the intended distribution from **Windows PowerShell**:

```powershell
wsl -d Ubuntu-20.04
```

Inside that WSL shell:

```bash
lsb_release -rs
source /opt/ros/noetic/setup.bash
rosversion -d
```

The conversation confirmed these executable paths after installation:

```text
/usr/sbin/airmon-ng
/usr/sbin/airodump-ng
/usr/sbin/aireplay-ng
/usr/bin/aircrack-ng
/usr/bin/nmap
/usr/bin/tshark
/usr/bin/hashcat
/usr/sbin/john
/usr/bin/hydra
```

The broader initial package suggestions included ROS Noetic desktop/TurtleBot3/navigation/SLAM packages, ROS build tools, networking utilities, and forensic utilities. A suggested package list is not proof that every listed package was installed. `command -v` and `rospack find` outputs are the installation evidence available here.

An early Aircrack package download on Ubuntu 20.04 failed with HTTP 403. Later executable checks succeeded. The handoff context records switching the Ubuntu archive transport to HTTPS; do not migrate Ubuntu releases or mix repositories solely because of an old download failure.

## Local preparation tools and wordlists

The operator extracted `hmr-tools.tar.gz` into the WSL home directory. These paths were confirmed:

```text
~/hmr/tools/cupp/cupp.py
~/hmr/wordlists/common-1k.txt
~/hmr/wordlists/common-10k.txt
~/hmr/wordlists/rockyou.txt
~/hmr/wordlists/rockyou.txt.tar.gz
```

`python3 ~/hmr/tools/cupp/cupp.py -h` worked. The wordlist directory was approximately 185 MB including a 134 MB uncompressed dictionary and its 51 MB archive. The common lists were approximately 7.1 KB and 72 KB. These files were on the user's machine; their bytes were not supplied to this repository update.

A text wordlist is an input file, not an executable. Typing its path produced Permission denied; reading it with `head -n 10 ...` worked. Raw dictionaries and target-specific profiles are not part of the committed handoff.

Later native Ubuntu/Kali phase-1 experiments are already documented in [01-passwords.md](../01-passwords.md). Keep those environments distinct from this WSL history.

## Wireless hardware findings

On the Windows laptop, `netsh wlan show drivers` identified a MediaTek Wi-Fi 6E MT7902. Hardware IDs confirmed it was a PCI device (`VEN_14C3`, `DEV_7902`). `usbipd` was not installed. WSL `iw dev` returned no wireless interfaces.

Installing Aircrack utilities did not establish access to a monitor-capable radio from WSL. USB passthrough does not turn that PCI device into a USB adapter. Support for raw radio operations on that laptop was not demonstrated.

The later repository phase-1 runbook records Intel AX201 monitor-mode and passive-capture preparation on a different, native Ubuntu lab machine. Those later results should not be attributed to the laptop MT7902 or WSL.

## Persistent USB discussion

The operator first considered an 8 GB Ubuntu USB and later showed Rufus with a 64 GB device and an Ubuntu 20.04.6 ISO. Persistence initially showed zero. Persistence or a full installation was needed to retain installed packages and files across a reboot. Creating and boot-testing a particular persistent USB was not established by those screenshots.

The actual Criterion 3 lab session used the desktop's Ubuntu 24.04 installation plus a Noetic container. It was not a verified persistent-USB deployment. The Noetic image and map bind mount are described in [03-path-alteration.md](../03-path-alteration.md).

## ROS workspace preparation in WSL

Repository used:

<https://github.com/SMART-NYUAD/hack_my_robot_2026>

The initial workspace contained two packages with the same package name:

```text
hack_my_robot
hack_my_robot_2026
```

`catkin_make` rejected this duplication. In the later successful build, only `hack_my_robot_2026` was traversed and provided the package named `hack_my_robot`:

```text
rospack find hack_my_robot
/home/shaha/catkin_ws/src/hack_my_robot_2026
```

`rosdep install --from-paths src --ignore-src --rosdistro noetic -r -y` reported dependencies installed, and `catkin_make` completed. An attempted `git clone` into the already populated directory correctly failed; do not repeatedly clone over existing work.

Both `turtlebot3_slam` and `turtlebot3_navigation` were found under `/opt/ros/noetic/share/`. The mission complete launch supplied in chat hardcoded `/home/sxp8070/map.yaml`. The WSL user's own `~/map.yaml` and `~/map.pgm` were absent at that time.

## ROS network repairs before the lab session

Several old robot addresses appeared during practice, including `10.10.187.138` and `10.10.184.50`. At one point the Pi had stale `ROS_MASTER_URI` and `ROS_IP`, no running rosmaster/roslaunch, and no listener on port 11311. Updating shell addresses alone did not start the missing master or bringup.

After correcting the setup and starting the robot stack, the WSL client listed standard topics and received `/scan` at roughly 10 Hz. That demonstrated data reception in that setup. It did not prove arbitrary bidirectional ROS connections on every later network.

General pattern, substituting confirmed current addresses in the correct shell:

```bash
source /opt/ros/noetic/setup.bash
unset ROS_HOSTNAME
export ROS_IP='THIS_MACHINE_REACHABLE_IP'
export ROS_MASTER_URI='http://CONFIRMED_MASTER_IP:11311'
```

## Native desktop and Docker transition

The lab desktop reported Ubuntu 24.04 x86_64, Wayland, no `/opt/ros`, and initially no Docker/Podman. Installing a utility named `rospack` on the host would not install the full Noetic stack.

Docker was installed using Ubuntu's `docker.io` package plus `xauth`. The hello-world container succeeded, and `osrf/ros:noetic-desktop-full` was pulled. A prepared container/image was subsequently used for GUI navigation. The lab session's successful GUI container used host networking, desktop ROS_IP, X11 socket access, software rendering settings, and the `~/hmr-lab:/root/hmr` bind mount.

The precise current container configuration should be inspected before recreation:

```bash
# Desktop host
sudo docker inspect hmr-noetic-gui
```

The original setup used `xhost +si:localuser:root`; remove that allowance after the session with `xhost -si:localuser:root` if it was enabled. Keep GUI display permissions scoped. Reuse the working container rather than recreating it from memory.

The desktop had a ROS Focal APT entry even though it ran Noble; it should be reviewed before future host package changes. The working ROS installation in this session was the container's Ubuntu 20.04 environment.

## File-access practice observed in this conversation

A scoped read-only search on the Pi found:

```text
/home/ubuntu/phase2-lab/training.ifc
```

That was a training file. The later existing [phase-2 runbook](../02-data-access-final.md) records a mock transfer and matching hashes. This early discovery alone did not prove retrieval of a real sensitive competition file.

## Limits

Actual shell history, binary tools, dictionary files, Docker image layers, robot firmware image, map pixels, and mission source checkout are not recreated by these notes. The repository records what was observed or described. Use [the asset inventory](evidence-status.md) to collect the missing lab files and preserve their provenance.
