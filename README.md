# Tor Network Toolkit (TNT)

The Tor Network Toolkit (TNT) is a multi-OS demonstration framework that showcases how to interact with the Tor network programmatically and how to run local packet-crafting operations using Scapy. Tor traffic and Scapy traffic remain strictly separated, as raw ICMP and TCP packets cannot be routed through Tor.

This project is designed for researchers, analysts, and developers who need a clean, minimal, and reproducible demo setup for Tor automation and local network inspection.



## Features

* Launches a Tor process with a dedicated data directory
* Full lifecycle control via context manager (startup, controller authentication, cleanup)
* Requests a new Tor identity (NEWNYM)
* Queries the current Tor exit IP
* Performs HTTP requests via Tor (SOCKS5)
* Local ICMP Echo demo via Scapy
* Local TCP SYN demo via Scapy
* Cross-platform privilege detection for raw sockets

## Requirements

* Python 3.x
* Tor installed on the system or automatically launched
* Python packages:

  * `stem`
  * `requests`
  * `pysocks`
  * `scapy` (optional, only required for local demos)

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Default run:

```bash
python3 tnt.py
```

Modes:

```bash
python3 tnt.py --mode tor
python3 tnt.py --mode scapy
python3 tnt.py --mode full
```

Custom URL:

```bash
python3 tnt.py --url https://icanhazip.com
```

New identity:

```bash
python3 tnt.py --new-identity
```

Change Scapy target:

```bash
python3 tnt.py --target 1.1.1.1
```



## Modes

### Tor Mode

* Starts a Tor instance
* Connects to the control port
* Gets exit IP
* Optional NEWNYM identity change
* Performs an HTTP request through Tor

### Scapy Mode

* ICMP Echo Request (local)
* TCP SYN probe (local)
* Does not use Tor

### Full Mode

Runs both Tor and Scapy demos sequentially.


## Notes and Limitations

* ICMP and TCP raw packets cannot be routed through Tor
* Raw socket operations require admin/root privileges
* NEWNYM requires a short cooldown
* Tor data directory is isolated (`./tor_data`)
* Ensure the Tor control port is enabled for external instances



## ⚠️ Responsible Use / Dual-Use Notice

This toolkit is intended for research, education, debugging, and network analysis in controlled environments.
It demonstrates Tor automation and local packet crafting for privacy research, protocol inspection, and development workflows.

Certain functions (raw sockets, packet crafting, identity rotation) can be considered dual-use.
Use of this software must comply with applicable laws, ethical guidelines, and the Tor Project’s policies.
Do not run Scapy-based operations or traffic analysis against systems you do not own or have explicit permission to test.

Tor traffic in this toolkit is limited to standard HTTP(S) requests.
Scapy traffic is strictly local and never routed through Tor.

Respect the copyright. It is provided as a free learning resource under GPLv3.



## License

This project is licensed under the GNU General Public License v3 (GPLv3).
You must retain the copyright notice and share modifications under the same license.



## Author

Created by Volkan Sah (Kücükbudak).
More projects: [https://volkansah.github.io](https://volkansah.github.io)

