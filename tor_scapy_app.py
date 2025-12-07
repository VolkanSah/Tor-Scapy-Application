#!/usr/bin/env python3
"""
Tor Network Toolkit (TNT) - Multi-OS Tor Demo
Zeigt Tor-Nutzung + Scapy packet crafting
"""

from stem import Signal
from stem.control import Controller
from stem.process import launch_tor_with_config
import socks
import socket
import time
import argparse
import sys
import os
import requests
from requests.exceptions import RequestException

# Optional: Scapy nur wenn verfügbar
try:
    from scapy.all import sr1, IP, ICMP, TCP, conf
    SCAPY_AVAILABLE = True
    conf.verb = 0  # Scapy output reduzieren
except ImportError:
    SCAPY_AVAILABLE = False

# --- Konfiguration ---
SOCKS_PORT = 9050
CONTROL_PORT = 9051
TOR_DATA_DIR = "./tor_data"  # Eigenes Tor-Verzeichnis

class TorController:
    """Managed Tor-Prozess mit sauberer Cleanup"""
    
    def __init__(self):
        self.process = None
        self.controller = None
        
    def start(self):
        """Startet Tor-Prozess und wartet auf Bootstrap"""
        print("[*] Starte Tor-Prozess...")
        
        # DataDirectory für diesen Prozess
        os.makedirs(TOR_DATA_DIR, exist_ok=True)
        
        try:
            self.process = launch_tor_with_config(
                config={
                    'SocksPort': str(SOCKS_PORT),
                    'ControlPort': str(CONTROL_PORT),
                    'DataDirectory': TOR_DATA_DIR,
                },
                init_msg_handler=self._init_msg_handler,
                take_ownership=True,  # Wichtig: Cleanup bei Exit
                timeout=60
            )
            
            # Warte bis Tor bereit ist
            time.sleep(3)
            self._connect_controller()
            print("[✓] Tor ist bereit!\n")
            
        except Exception as e:
            print(f"[!] Tor-Start fehlgeschlagen: {e}")
            self._cleanup()
            raise
    
    def _init_msg_handler(self, line):
        """Zeigt wichtige Tor-Statusmeldungen"""
        if "Bootstrapped" in line:
            print(f"[Tor] {line}")
    
    def _connect_controller(self):
        """Verbindet zum Tor Control Port"""
        try:
            self.controller = Controller.from_port(port=CONTROL_PORT)
            self.controller.authenticate()
            print(f"[✓] Tor Version: {self.controller.get_version()}")
        except Exception as e:
            print(f"[!] Controller-Verbindung fehlgeschlagen: {e}")
            raise
    
    def new_identity(self):
        """Fordert neue Tor-Identity an"""
        if not self.controller:
            print("[!] Kein Controller verbunden")
            return
        
        print("[*] Fordere neue Identität an...")
        self.controller.signal(Signal.NEWNYM)
        time.sleep(5)  # Warte auf neuen Circuit
        print("[✓] Neue Identität aktiv\n")
    
    def get_current_ip(self):
        """Zeigt aktuelle Exit-Node IP"""
        try:
            proxies = {
                'http': f'socks5h://127.0.0.1:{SOCKS_PORT}',
                'https': f'socks5h://127.0.0.1:{SOCKS_PORT}'
            }
            
            resp = requests.get(
                'https://api.ipify.org?format=json',
                proxies=proxies,
                timeout=10
            )
            ip = resp.json().get('ip', 'Unknown')
            print(f"[i] Aktuelle Tor Exit-IP: {ip}")
            return ip
            
        except RequestException as e:
            print(f"[!] IP-Abfrage fehlgeschlagen: {e}")
            return None
    
    def _cleanup(self):
        """Räumt Tor-Prozess auf"""
        if self.controller:
            try:
                self.controller.close()
            except:
                pass
        
        if self.process and self.process.poll() is None:
            print("[*] Beende Tor-Prozess...")
            self.process.terminate()
            self.process.wait(timeout=10)
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self._cleanup()


def demo_tor_request(url="http://check.torproject.org"):
    """Demo: HTTP-Request über Tor"""
    print(f"[*] Demo: HTTP-Request über Tor zu {url}")
    
    proxies = {
        'http': f'socks5h://127.0.0.1:{SOCKS_PORT}',
        'https': f'socks5h://127.0.0.1:{SOCKS_PORT}'
    }
    
    try:
        resp = requests.get(url, proxies=proxies, timeout=15)
        
        if "Congratulations" in resp.text:
            print("[✓] Tor funktioniert! Du nutzt das Tor-Netzwerk.")
        else:
            print("[i] Antwort erhalten:")
            print(resp.text[:200])
        
        print(f"[i] Status Code: {resp.status_code}\n")
        
    except RequestException as e:
        print(f"[!] Request fehlgeschlagen: {e}\n")


def demo_scapy_local(target="8.8.8.8"):
    """Demo: Lokaler ICMP Ping mit Scapy (OHNE Tor)"""
    if not SCAPY_AVAILABLE:
        print("[!] Scapy nicht installiert. Pip: pip install scapy\n")
        return
    
    print(f"[*] Demo: Lokaler ICMP Ping zu {target}")
    print("[i] Hinweis: Läuft NICHT über Tor (ICMP geht nicht über SOCKS)")
    
    # Check für Admin-Rechte
    if os.name == 'nt':  # Windows
        is_admin = os.getuid() == 0 if hasattr(os, 'getuid') else True
    else:  # Unix-like
        is_admin = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    
    if not is_admin:
        print("[!] Benötigt Admin/Root-Rechte für raw sockets!")
        print("[i] Linux/Mac: sudo python script.py")
        print("[i] Windows: Als Administrator ausführen\n")
        return
    
    try:
        # ICMP Echo Request
        pkt = IP(dst=target)/ICMP()
        resp = sr1(pkt, timeout=3, verbose=0)
        
        if resp:
            print(f"[✓] Antwort von {resp.src}")
            print(f"[i] TTL: {resp.ttl}, Type: {resp.type}\n")
        else:
            print(f"[!] Keine Antwort von {target}\n")
            
    except Exception as e:
        print(f"[!] Scapy-Fehler: {e}\n")


def demo_scapy_tcp_syn(target="1.1.1.1", port=80):
    """Demo: TCP SYN-Scan mit Scapy (lokal, OHNE Tor)"""
    if not SCAPY_AVAILABLE:
        return
    
    print(f"[*] Demo: TCP SYN zu {target}:{port}")
    print("[i] Läuft NICHT über Tor\n")
    
    try:
        pkt = IP(dst=target)/TCP(dport=port, flags="S")
        resp = sr1(pkt, timeout=2, verbose=0)
        
        if resp and resp.haslayer(TCP):
            if resp[TCP].flags == "SA":  # SYN-ACK
                print(f"[✓] Port {port} ist OFFEN")
            elif resp[TCP].flags == "RA":  # RST-ACK
                print(f"[i] Port {port} ist GESCHLOSSEN")
        else:
            print(f"[!] Keine Antwort (gefiltert?)\n")
            
    except Exception as e:
        print(f"[!] TCP-Scan Fehler: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="🧅 Tor Network Toolkit - Multi-OS Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python %(prog)s --mode tor              # Nur Tor-Requests
  python %(prog)s --mode scapy            # Nur Scapy-Demos (lokal)
  python %(prog)s --mode full             # Alles zeigen
  python %(prog)s --url https://icanhazip.com
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['tor', 'scapy', 'full'],
        default='full',
        help='Demo-Modus auswählen'
    )
    
    parser.add_argument(
        '--url',
        default='http://check.torproject.org',
        help='URL für Tor-Request'
    )
    
    parser.add_argument(
        '--target',
        default='8.8.8.8',
        help='Ziel-IP für Scapy-Demos'
    )
    
    parser.add_argument(
        '--new-identity',
        action='store_true',
        help='Neue Tor-Identität vor Request anfordern'
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🧅  Tor Network Toolkit (TNT)")
    print("=" * 50 + "\n")
    
    # Scapy-Demos (ohne Tor)
    if args.mode in ['scapy', 'full']:
        demo_scapy_local(args.target)
        demo_scapy_tcp_syn(args.target, 443)
    
    # Tor-Demos
    if args.mode in ['tor', 'full']:
        try:
            with TorController() as tor:
                tor.get_current_ip()
                
                if args.new_identity:
                    tor.new_identity()
                    tor.get_current_ip()
                
                demo_tor_request(args.url)
                
        except KeyboardInterrupt:
            print("\n[!] Abgebrochen durch User")
        except Exception as e:
            print(f"\n[!] Fehler: {e}")
    
    print("=" * 50)
    print("[✓] Demo beendet")
    print("=" * 50)


if __name__ == "__main__":
    main()
