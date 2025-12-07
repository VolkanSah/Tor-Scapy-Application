# Tor Network Toolkit (TNT)

The Tor Network Toolkit (TNT) is a multi-OS demonstration framework that showcases how to interact with the Tor network programmatically and how to run local packet-crafting operations using Scapy. Tor traffic and Scapy traffic remain strictly separated, as raw ICMP and TCP packets cannot be routed through Tor. 

This project is designed for researchers, analysts, and developers who need a clean, minimal, and reproducible demo setup for Tor automation and local network inspection.

#

## Features

- Launches a Tor process with a dedicated data directory
- Full lifecycle control via context manager (startup, controller authentication, cleanup)
- Requests a new Tor identity (NEWNYM)
- Queries the current Tor exit IP
- Performs HTTP requests via Tor (SOCKS5)
- Local ICMP Echo demo via Scapy
- Local TCP SYN demo via Scapy
- Cross-platform privilege detection for raw sockets


### Requirements

- Python 3.x
- Tor installed on the system or automatically launched
- Python packages:
  - `stem`
  - `requests`
  - `pysocks`
  - `scapy` (optional, only required for local demos)

Install all dependencies with:

```bash
pip install -r requirements.txt
````

---

## Usage

Run the toolkit with default settings:

```bash
python3 tnt.py
```

Select a specific mode:

```bash
python3 tnt.py --mode tor
python3 tnt.py --mode scapy
python3 tnt.py --mode full
```

Use a custom URL for the Tor HTTP request:

```bash
python3 tnt.py --url https://icanhazip.com
```

Request a new Tor identity before performing requests:

```bash
python3 tnt.py --new-identity
```

Change the target for Scapy demos:

```bash
python3 tnt.py --target 1.1.1.1
```

---

### Modes

#### Tor Mode

* Starts a Tor instance
* Connects to the control port
* Gets exit IP
* Optional NEWNYM identity change
* Performs an HTTP request through Tor

#### Scapy Mode

* ICMP Echo Request (local, raw sockets)
* TCP SYN probe (local, raw sockets)
* Does not use Tor

#### Full Mode

Runs both Tor and Scapy demos sequentially.

---

### Notes and Limitations

* ICMP and TCP raw packets cannot be routed through Tor; they are executed locally.
* Raw socket operations require administrator/root privileges.
* NEWNYM requires a short cooldown until a new circuit becomes active.
* The Tor data directory is isolated (`./tor_data`) for reproducibility.
* Ensure that the Tor control port is enabled if you use an external Tor instance.

---

### License

This project is licensed under the GNU General Public License v3 (GPLv3).
You must retain the copyright notice and share modifications under the same license.



### Author

Created by Volkan Sah (Kücükbudak).
More projects: [https://volkansah.github.io](https://volkansah.github.io)




