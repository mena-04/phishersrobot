# Phase 1 — Passwords (Criterion 1: 25 points)

> **Purpose:** A self-contained, command-by-command preparation playbook for the Hack My Robot 2026 password criterion. Use only on equipment and accounts you own or are explicitly authorized to test. This page is **not** evidence that any competition password has been recovered.
>
> **Status:** Selected preparation checks completed for 1.1, 1.2 and 1.3; competition-specific password objectives remain unverified. Commands marked *planned* have not been run.

**Use:** Work through the relevant criterion in order. Commands are copied into the specified machine, not the Cisco console unless explicitly stated. Do not run a command merely because it appears here; confirm the host and authorization first.

## At a glance

| Part | Points | Preparation demonstrated | Still unverified |
|---|---:|---|---|
| 1.1 — Wi-Fi password | 10 | Intel AX201 monitor mode, passive packet capture, public training EAPOL inspection | Competition AP handshake and password; packet injection |
| 1.2 — Bob's PC password | 10 | CUPP installed; fictional profile generated a candidate list | Bob's actual PC login and competition password |
| 1.3 — Robot SSH credentials | 5 | SSH reachability and login with known, authorized practice credentials; mock file-format exercises | Discovery of unknown finals credentials and any protected file on Bob's actual PC |

**Read the scope before starting:** The preparation sheet describes a 20-minute Wi-Fi race, a social-engineering PC password challenge, and robot SSH credentials. Those are *competition tasks*, not blanket permission to test university networks, nearby access points, real people's accounts, or unrelated hosts. The walkthrough below confines hands-on procedures to passive observation, isolated labs, authorized access, and local synthetic data.

---

## 1.1 — Wi-Fi password (10 points)

### Section 1 — Confirm the native Ubuntu wireless environment

**Where:** Native Ubuntu on the Dell OptiPlex 5490 AIO. **Not:** the Raspberry Pi, Windows WSL or the Cisco switch console.

Check the OS, driver, adapter, and wireless interfaces:

```bash
cat /etc/os-release
uname -r
lspci -nnk | grep -A 4 -i 'network controller'
iw dev
iw list
```

Check that capture utilities are installed:

```bash
command -v tshark
command -v dumpcap
command -v aircrack-ng
command -v airmon-ng
```

**Previously verified:** Ubuntu 24.04.4, Intel AX201 with `iwlwifi`, and advertised monitor-mode support.

**Check:** In `iw list`, look for `monitor` under **Supported interface modes**. This indicates monitor-mode capability, **not** successful packet injection.

### Section 2 — Inspect interfaces without disrupting campus Wi-Fi

**Where:** Native Ubuntu.

```bash
nmcli device status
iw dev
ip -br addr
```

If `mon0` already exists, inspect it without changing the wireless connection:

```bash
iw dev mon0 info
ip -br link show mon0
```

**Note:** Creating or switching a monitor interface can interrupt Wi-Fi connectivity. Do not make interface-mode changes on university equipment or a shared production network. Use your own isolated wireless lab when that capability must be retested.

### Section 3 — Recheck a known, isolated lab capture

**Prerequisite:** A capture file recorded from your own lab, or a publicly released training capture. Do not capture or publish unrelated people's network traffic.

Inspect file metadata and a brief protocol summary:

```bash
capinfos lab-capture.pcapng
tshark -r lab-capture.pcapng -q -z io,phs
```

Inspect EAPOL frames in an authorized sample:

```bash
tshark -r lab-capture.pcapng -Y eapol \
  -T fields -e frame.number -e frame.time_relative \
  -e wlan.sa -e wlan.da -e eapol.type
```

**Previously verified:**

- A 10-second Dumpcap run recorded **154 frames** with **0 reported drops** for that run.
- A separate 10-second TShark run decoded **65 frames**: **59 data** and **6 management** frames.
- A **public training capture** showed four EAPOL messages consistent with a WPA2 four-way exchange.

**Interpretation:** A capture tool decoding EAPOL frames is *not* proof that the competition access point's handshake was captured, that a password was recovered, or that the wireless adapter supports injection.

### Section 4 — How the competition sheet's Wi-Fi approach maps to our results

The preparation sheet proposes identifying the assigned access point, capturing a WPA2 handshake, checking a short common-password list, and (as an optional active technique) deauthentication. Its suggested 20-minute window is a competition rule to verify on the day, not a tested performance result. We **did not complete** that live competition workflow and did **not** verify packet injection.

For a legitimate isolated test environment, confirm the access point's configuration in its administration interface, use your own client to connect normally, and observe the protocol metadata. Avoid deauthentication or authentication-guessing against campus or third-party networks. A worked password-cracking or deauthentication command sequence is intentionally not reproduced in this public playbook.

**Test boundaries:**

- A Cisco **wired switch alone** cannot create a Wi-Fi network or WPA2 handshake.
- An isolated WPA2-Personal access point plus a test client is needed for realistic wireless protocol observation.
- A Wi-Fi-enabled Ubuntu computer can potentially act as an AP if `iw list` reports **AP** support; a separate receiver is preferable for monitoring.
- Leave any lab AP disconnected from the university LAN/WAN.

### Section 5 — Known issues and checkpoints

| Observation | Meaning / response |
|---|---|
| `monitor` listed in `iw list` | Monitor mode is advertised; injection not established |
| Capture contains EAPOL frames | Authentication traffic is visible in that **specific** capture |
| Aireplay-ng returned `channel -1` | Injection test did **not** pass; do not bypass restrictions on a shared network |
| Only Cisco switch is available | Use it for wired SSH practice, not WPA2 handshake exercises |
| Competition SSID/password not obtained | Keep 1.1 marked **not verified** |

**Checkpoint 1.1:** [x] Wireless readiness and training analysis. [ ] Competition-specific Wi-Fi objective.

---

## 1.2 — Bob's PC password (10 points)

### Section 6 — Verify the existing CUPP installation

**Where:** Kali Linux in the local practice VM.

```bash
cd ~/hack-my-robot/password-lab/cupp
python3 cupp.py --help
```

**Previously verified:** CUPP starts and displays its help. No target account needs to be contacted for this check.

### Section 7 — Recheck the fictional-profile exercise

**Where:** Kali Linux. Use **only fictional details** in a local practice profile.

The completed practice exercise produced `alex.txt`. Check that the saved data is present:

```bash
cd ~/hack-my-robot/password-lab/cupp
ls -lh alex.txt
wc -l alex.txt
sort -u alex.txt | wc -l
grep -Fx 'alex1990' alex.txt
```

**Previously observed:** After deduplication, the fictional profile contained **1,078 unique candidates**, including the synthetic example `alex1990`.

If you want a harmless miniature demonstration of permutations without generating or testing a real person's passwords:

```bash
python3 - <<'PY'
import itertools
items = ['alpha', 'beta', 'demo']
for values in itertools.permutations(items, 2):
    print('-'.join(values))
PY
```

This produces sample strings locally. It does not test logins or prove password recovery.

### Section 8 — Understand the competition sheet's suggested workflow

The sheet mentions an organizer-provided list of personal elements, possible interaction with a character named Bob, and generating combinations before trying the authorized challenge login. It also suggests local or remote authentication, but neither path has been tested against the competition machine. **None of those competition-specific inputs or login results is available in our preparation evidence.**

During the event, first verify the organizers' explicit rules and the permitted authentication workflow. Keep any supplied personal data out of public GitHub documentation. Do not publish target-specific candidate lists, automated guessing workflows, real credentials, or unauthorized account-access steps.

**Checkpoint 1.2:** [x] CUPP works; synthetic preparation completed. [ ] Actual competition PC objective.

---

## 1.3 — Robot SSH credentials (5 points)

### Section 9 — Check an authorized robot or lab host

**Where:** Kali or native Ubuntu, whichever is legitimately connected to the assigned lab network.

Identify local network configuration without scanning third-party networks:

```bash
ip -br addr
ip route
ip neigh show
ss -tn state established
```

Set the address of the **assigned** practice robot or lab host:

```bash
export ROBOT_IP='REPLACE_WITH_ASSIGNED_IP'
```

Check connectivity:

```bash
ping -c 3 "$ROBOT_IP"
nc -vz -w 5 "$ROBOT_IP" 22
```

**Expected:** If the host and SSH service are reachable, `ping` may receive replies and `nc` should report that TCP port 22 is open. ICMP replies may be disabled, so the SSH port check is the more direct test.

The practice robot's address changed during our experiments. Do **not** reuse a historical IP as though it were the finals address.

### Section 10 — Log in using only authorized credentials

```bash
ssh ubuntu@"$ROBOT_IP"
```

Use only credentials supplied or authorized for that practice device. The competition sheet mentions a TurtleBot3 example account, but **a documented default is not evidence that a finals robot retains it**.

**Previously verified:** A successful SSH login to the practice robot using known authorized credentials. This does not establish recovery of an unknown password.

### Section 11 — Explore credential-file *formats* using local synthetic files

The preparation sheet suggests checking documented default credentials on the assigned robot and, if necessary, looking for a protected credential file on Bob's PC. We have not verified the competition robot's default account or access to Bob's PC. It mentions file searches, type identification, metadata, Base64, and printable strings as possible investigative techniques. The preparation sheet mentions possible protected data on Bob's PC. The exact file name, path, protection method and content were **not** verified. Do not treat these examples as instructions to search or extract credentials from a real computer.

**Where:** Kali or Ubuntu, in your own local scratch directory. This creates no genuine secrets.

```bash
mkdir -p ~/phase1-local-file-lab
cd ~/phase1-local-file-lab
printf 'DEMO_ONLY_NOT_A_PASSWORD\n' > sample.txt
chmod 600 sample.txt
ls -l sample.txt
file sample.txt
sha256sum sample.txt
```

Demonstrate reversible Base64 encoding of the fake string:

```bash
base64 sample.txt > sample.b64
base64 -d sample.b64 > decoded.txt
cmp sample.txt decoded.txt && echo 'Local round-trip passed'
```

Check a local file's type and printable text:

```bash
file sample.b64
strings sample.b64
```

**Previously verified in separate local exercises:** permissions, Base64 decoding, OpenSSL encryption/decryption and byte-for-byte comparisons on **mock** files. None of these constitutes retrieval of competition credentials.

### Section 12 — If using the optional isolated Cisco-switch lab

**Use this only when wired network practice is genuinely needed.** It is not required to document Phase 1, and a switch does not fix the robot's motor issue.

```text
Ubuntu PC 1 -- Ethernet -- Cisco switch -- Ethernet -- Ubuntu PC 2 or TurtleBot3 Pi
                              (no campus uplink)
```

A headless Raspberry Pi does not need a monitor if its Ethernet interface is already configured and reachable. A plain switch generally provides no DHCP service. Do not assume an IP address exists just because a cable is connected.

PC 1's Ethernet adapter was observed as `eno1`. If both endpoints use a **verified** `eno1` interface and you administer them, temporary example addresses on the isolated wired subnet are:

```bash
# PC 1 only
sudo ip link set eno1 up
sudo ip addr add 192.168.50.10/24 dev eno1
ip -4 addr show dev eno1
```

```bash
# PC 2 only — replace eno1 if this machine uses another interface
sudo ip link set eno1 up
sudo ip addr add 192.168.50.20/24 dev eno1
ip -4 addr show dev eno1
```

Then on PC 1:

```bash
ping -c 3 192.168.50.10
ping -c 3 192.168.50.20
```

If a computer cannot ping its **own** assigned address, check that the address exists in `ip -4 addr show dev eno1` before investigating the switch. NetworkManager may also manage or reset the connection. These temporary settings do not survive every reboot or reconnect.

**Our lab status:** The switch-only network was **not** brought to a successful two-host ping demonstration. Do not report that it passed. Continuing this optional networking exercise is not necessary to complete the preparation guide.

**Checkpoint 1.3:** [x] Known-credential SSH access; synthetic file-format tests. [ ] Unknown finals credentials.

---

## Section 13 — Predicted next commands (NOT YET TESTED)

The following are **prepared commands, not observed results**. Use them only on your own isolated equipment or on systems explicitly assigned by the organizers. They are designed to verify lab readiness and inspect evidence; they do not automate login guessing, force wireless disconnections, or recover credentials from third-party systems.

### 13A — Wi-Fi: check whether an offline AP lab is possible

**Where:** Native Ubuntu machine with a Wi-Fi adapter. A wired Cisco switch alone is insufficient.

```bash
# Examine AP and monitor capabilities without changing the radio
iw list | sed -n '/Supported interface modes:/,/Band 1:/p'

# Identify the adapter and the active network connection
iw dev
nmcli device status

# Verify available lab tools
for tool in iw hostapd tshark dumpcap capinfos; do
  command -v "$tool" || echo "MISSING: $tool"
done
```

**Expected:** `AP` in supported modes if you plan to host a lab AP on that adapter; `monitor` if you plan to use a separate adapter for passive monitoring. The presence of a mode is not proof two modes work concurrently.

If you already have a **public training PCAP** or a capture from your own AP/client, inspect only that file:

```bash
export CAPTURE='REPLACE_WITH_OWN_OR_PUBLIC_CAPTURE.pcapng'
capinfos "$CAPTURE"
tshark -r "$CAPTURE" -Y 'eapol' \
  -T fields -e frame.number -e frame.time_relative -e wlan.sa -e wlan.da
```

**Expected:** Frame metadata only if the sample contains EAPOL traffic. No EAPOL frames means this capture does not establish that an authentication exchange was observed.

### 13B — Bob's PC: prepare a synthetic account-lab checklist

**Where:** Your own Kali/Ubuntu practice machine. These commands validate tools and generate **fake** training input, not target-specific passwords.

```bash
python3 --version
cd ~/hack-my-robot/password-lab/cupp
python3 cupp.py --help
```

Inspect a fictional candidate file if it exists:

```bash
if [ -f alex.txt ]; then
  wc -l alex.txt
  sort -u alex.txt | wc -l
  grep -Fx 'alex1990' alex.txt
else
  echo 'Synthetic alex.txt not found; do not claim this check passed.'
fi
```

For competition day, first confirm which **organizer-provided login interface and account** are in scope and whether the rules permit attempts. Do not treat the example candidate file as a list for a real account. The prepared commands above are for readiness only; an actual password result must be recorded separately.

### 13C — Robot SSH: confirm assigned endpoint and authentication method

**Where:** Kali or Ubuntu connected to an **authorized** lab network.

```bash
export ROBOT_IP='REPLACE_WITH_ASSIGNED_IP'

# Read-only local interface and route inventory
ip -br addr
ip route get "$ROBOT_IP"

# Verify TCP reachability without password attempts
nc -vz -w 5 "$ROBOT_IP" 22

# Confirm which SSH client is installed
ssh -V
```

If you have **valid credentials issued for the specific device**, connect interactively:

```bash
ssh -o ConnectTimeout=5 ubuntu@"$ROBOT_IP"
```

**Expected:** A host-key verification prompt on first legitimate connection, followed by whatever authorized authentication the device requires. A timeout means network/port reachability needs checking; `Permission denied` means authentication did not succeed. Neither outcome proves the username or password in the event is known.

### 13D — Protected-file formats: local dummy-data inspection

**Where:** An isolated directory containing only files you created.

```bash
mkdir -p ~/phase1-local-file-lab
cd ~/phase1-local-file-lab
printf 'SYNTHETIC_TEST_DATA_ONLY\n' > example.txt
base64 example.txt > example.b64
file example.txt example.b64
sha256sum example.txt
base64 -d example.b64 | sha256sum
```

Optional image metadata exercise, **only with an image you own**:

```bash
command -v exiftool
# After copying your own test image into this directory:
# exiftool example.jpg
```

**Expected:** Matching hashes for the original dummy text and its decoded Base64 representation. These steps do **not** establish that a real organizer file exists or can be decoded.

### 13E — Record evidence without exposing secrets

```bash
mkdir -p ~/phase1-evidence
{
  date -Is
  uname -a
  printf '\nInterface summary:\n'
  ip -br link
} > ~/phase1-evidence/local-readiness.txt
```

Review the output before sharing. Do not include raw real-world credentials, host fingerprints tied to private systems, private captures, or personal data in a public GitHub repository.

**Checkpoint:** Every command in Section 13 is **PLANNED / NOT VERIFIED** until actually executed. Add results and timestamps only after testing.

---

## Section 14 — Competition-day decision checklist (planned, not verified)

| If you encounter... | First check | Record as evidence |
|---|---|---|
| Assigned Wi-Fi challenge | Confirm organizer scope, SSID/BSSID, authorized equipment, and available time | Tool versions, sanitized passive-capture metadata, outcome without password |
| Bob's assigned PC | Confirm which login interface and authentication attempts the rules allow | Interface type, authorization constraints, success/failure without secrets |
| Assigned robot SSH | Confirm assigned address, route, port 22, and permitted login method | Reachability, sanitized SSH outcome |
| Protected sample file supplied for analysis | Work on an authorized copy and identify its format before choosing a parser | File type, non-sensitive metadata, hashes |
| Missing hardware, inaccessible target, or uncertain permission | Stop that branch; use the preparation evidence and note the blocker | `NOT VERIFIED` with reason |

**Do not infer competition success from a public EAPOL sample, fictional CUPP candidate list, or known-credential practice SSH login.**

---

## Section 15 — Evidence hygiene and GitHub checklist

**Never commit:** actual passwords, private authentication captures, personal profile data, SSH private keys, credential dumps or real target wordlists. Use neutral screenshots or sanitized command output if supporting evidence is required.

- [x] 1.1: Confirm wireless driver and monitor capability.
- [x] 1.1: Confirm passive capture and public training EAPOL analysis.
- [ ] 1.1: Complete the organizer-authorized competition Wi-Fi challenge.
- [x] 1.2: Verify CUPP and fictional profile experiment.
- [ ] 1.2: Complete the competition PC challenge.
- [x] 1.3: Verify connection to an authorized practice SSH host.
- [x] 1.3: Test local mock credential-file formats.
- [ ] 1.3: Complete the competition robot credential challenge.

## Section 16 — Stop/cleanup and final status

Close SSH sessions with:

```bash
exit
```

Delete only the synthetic example files you created, after checking their names:

```bash
ls -la ~/phase1-local-file-lab
rm -i ~/phase1-local-file-lab/sample.txt \
      ~/phase1-local-file-lab/sample.b64 \
      ~/phase1-local-file-lab/decoded.txt \
      ~/phase1-local-file-lab/example.txt \
      ~/phase1-local-file-lab/example.b64
```

Missing-file warnings are harmless. Never use a broad wildcard or delete competition evidence as part of cleanup.

**Final assessment:** Phase 1 has **substantial preparation evidence**, but **0 of 3 competition-specific password recoveries have been verified**. Awarding any of the 25 points depends on the event's actual outcomes and judging rules.
