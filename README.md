# Tor Scapy Application (TSA)

**Tor Scapy Application** is a simple yet powerful tool that combines [Stem](https://stem.torproject.org/) and [Scapy](https://scapy.net/) to send network packets anonymously through the Tor network. It can start a Tor process, connect to it, and rotate your Tor identity on demand. Perfect for network analysis, testing, or just playing with Tor + Python magic.

---

## Features

* Launch a Tor process programmatically
* Connect to an existing Tor controller
* Rotate Tor identities on the fly (NEWNYM signal)
* Send ICMP packets via Tor SOCKS5 proxy
* Easy to customize for your own network tasks

---

## Requirements

* Python 3.x
* [Stem](https://stem.torproject.org/) Python library
* [Scapy](https://scapy.net/) Python library
* Tor installed and running (or launched via script)

---

## Installation

1. Install Python 3.x:
   [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Install required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   *(Make sure requirements.txt includes `stem` and `scapy`)*

3. Install and start Tor:

   * Download from [https://www.torproject.org/](https://www.torproject.org/)
   * Or let the script launch Tor automatically

---

## Usage

Run the app:

```bash
python tor_scapy_app.py
```

or

```bash
python3 tor_scapy_app.py
```

By default, it sends an ICMP (ping) packet to `8.8.8.8` through the Tor network and shows the response.



## Customization

* Modify `start_tor_process()` to add your Tor configs (e.g., ports, bridges)
* Change the `destination_ip` variable in `__main__` to target a different host
* Extend `send_packet_via_tor()` to send other packet types supported by Scapy



## Notes

* The script requires the Tor control port (`9051` by default) to be enabled and accessible
* Identity change takes a few seconds (`time.sleep(5)` after NEWNYM signal)
* Running with root/admin privileges may be needed for sending raw packets
* Use responsibly and respect network policies and laws


## Credits & Support
Visit [https://volkansah.github.io](https://volkansah.github.io) for more projects


## License

This project is licensed under the **MIT License** — do what you want, just keep it cool.
