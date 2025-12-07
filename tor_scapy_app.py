#!/usr/bin/env python3
"""
Tor Network Toolkit (TNT) - Multi-OS Tor Demo
Demonstrates Tor usage + Scapy packet crafting (separated, since ICMP via Tor is not possible)
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

# Optional: Scapy only if available
try:
    from scapy.all import sr1, IP, ICMP, TCP, conf
    SCAPY_AVAILABLE = True
    conf.verb = 0  # Reduce Scapy output
except ImportError:
    SCAPY_AVAILABLE = False

# --- Configuration ---
SOCKS_PORT = 9050
CONTROL_PORT = 9051
TOR_DATA_DIR = "./tor_data"  # Separate Tor data directory

class TorControlManager:
    """Manages the Tor process with clean startup and cleanup using a context manager."""
    
    def __init__(self):
        self.process = None
        self.controller = None
        
    def start_tor_process(self):
        """Starts the Tor process and waits for bootstrap."""
        print("[*] Starting Tor process...")
        
        # Create DataDirectory for this process
        os.makedirs(TOR_DATA_DIR, exist_ok=True)
        
        try:
            self.process = launch_tor_with_config(
                config={
                    'SocksPort': str(SOCKS_PORT),
                    'ControlPort': str(CONTROL_PORT),
                    'DataDirectory': TOR_DATA_DIR,
                },
                init_msg_handler=self._init_msg_handler,
                take_ownership=True,  # Important: Ensures cleanup on exit
                timeout=60
            )
            
            # Wait until Tor is ready
            time.sleep(3)
            self._connect_controller()
            print("[✓] Tor is ready!\n")
            
        except Exception as e:
            print(f"[!] Tor startup failed: {e}")
            self._cleanup()
            raise
    
    def _init_msg_handler(self, line):
        """Displays important Tor status messages."""
        if "Bootstrapped" in line:
            print(f"[Tor] {line}")
    
    def _connect_controller(self):
        """Connects to the Tor Control Port."""
        try:
            self.controller = Controller.from_port(port=CONTROL_PORT)
            self.controller.authenticate()
            print(f"[✓] Tor Version: {self.controller.get_version()}")
        except Exception as e:
            print(f"[!] Controller connection failed: {e}")
            raise
    
    def request_new_identity(self):
        """Signals Tor to switch to a new identity (NEWNYM)."""
        if not self.controller:
            print("[!] No controller connected")
            return
        
        print("[*] Requesting new identity...")
        self.controller.signal(Signal.NEWNYM)
        time.sleep(5)  # Wait for new circuit
        print("[✓] New identity is active\n")
    
    def get_exit_ip(self):
        """Displays the current Tor Exit Node IP using a Tor-proxied request."""
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
            print(f"[i] Current Tor Exit IP: {ip}")
            return ip
            
        except RequestException as e:
            print(f"[!] IP query failed: {e}")
            return None
    
    def _cleanup(self):
        """Cleans up and terminates the Tor process."""
        if self.controller:
            try:
                self.controller.close()
            except:
                pass
        
        if self.process and self.process.poll() is None:
            print("[*] Terminating Tor process...")
            self.process.terminate()
            self.process.wait(timeout=10)
    
    def __enter__(self):
        self.start_tor_process()
        return self
    
    def __exit__(self, *args):
        self._cleanup()


def run_tor_request_demo(url="http://check.torproject.org"):
    """Demo: Performs an HTTP request via Tor."""
    print(f"[*] Demo: HTTP Request via Tor to {url}")
    
    proxies = {
        'http': f'socks5h://127.0.0.1:{SOCKS_PORT}',
        'https': f'socks5h://127.0.0.1:{SOCKS_PORT}'
    }
    
    try:
        resp = requests.get(url, proxies=proxies, timeout=15)
        
        if "Congratulations" in resp.text:
            print("[✓] Tor is working! You are using the Tor network.")
        else:
            print("[i] Response received:")
            print(resp.text[:200])
        
        print(f"[i] Status Code: {resp.status_code}\n")
        
    except RequestException as e:
        print(f"[!] Request failed: {e}\n")


def check_admin_privileges():
    """Cross-platform check for elevated privileges (root/admin)."""
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:  # Unix-like (Linux, macOS, BSD)
            return os.geteuid() == 0
    except Exception:
        return False


def run_scapy_icmp_demo(target="8.8.8.8"):
    """Demo: Local ICMP Ping using Scapy (WITHOUT Tor)."""
    if not SCAPY_AVAILABLE:
        print("[!] Scapy not installed. Install with: pip install scapy\n")
        return
    
    print(f"[*] Demo: Local ICMP Ping to {target}")
    print("[i] Note: Running LOCALLY (ICMP does not route via SOCKS)")
    
    if not check_admin_privileges():
        print("[!] Requires Admin/Root privileges for raw sockets!")
        if os.name == 'nt':
            print("[i] Windows: Run as Administrator (right-click → 'Run as administrator')")
        else:
            print("[i] Linux/Mac: Run with sudo (e.g., sudo python3 script.py)")
        print()
        return
    
    try:
        # ICMP Echo Request
        pkt = IP(dst=target)/ICMP()
        resp = sr1(pkt, timeout=3, verbose=0)
        
        if resp:
            print(f"[✓] Reply from {resp.src}")
            print(f"[i] TTL: {resp.ttl}, Type: {resp.type}\n")
        else:
            print(f"[!] No reply from {target}\n")
            
    except Exception as e:
        print(f"[!] Scapy error: {e}\n")


def run_scapy_tcp_syn_demo(target="1.1.1.1", port=80):
    """Demo: TCP SYN scan using Scapy (local, WITHOUT Tor)."""
    if not SCAPY_AVAILABLE:
        return
    
    print(f"[*] Demo: TCP SYN to {target}:{port}")
    print("[i] Note: Running LOCALLY\n")
    
    if not check_admin_privileges():
        print("[!] Requires Admin/Root privileges for raw sockets!")
        print("[i] Skipping TCP SYN demo\n")
        return
    
    try:
        pkt = IP(dst=target)/TCP(dport=port, flags="S")
        resp = sr1(pkt, timeout=2, verbose=0)
        
        if resp and resp.haslayer(TCP):
            flags = resp[TCP].flags
            if flags == "SA":  # SYN-ACK
                print(f"[✓] Port {port} is OPEN\n")
            elif flags == "RA":  # RST-ACK
                print(f"[i] Port {port} is CLOSED\n")
            else:
                print(f"[i] Received TCP flags: {flags}\n")
        else:
            print(f"[!] No response (filtered?)\n")
            
    except Exception as e:
        print(f"[!] TCP Scan error: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="🧅 Tor Network Toolkit - Multi-OS Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python %(prog)s --mode tor             # Run Tor-only requests
  python %(prog)s --mode scapy           # Run Scapy-only demos (local)
  python %(prog)s --mode full            # Run all demos
  python %(prog)s --url https://icanhazip.com
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['tor', 'scapy', 'full'],
        default='full',
        help='Select the demo mode to run'
    )
    
    parser.add_argument(
        '--url',
        default='http://check.torproject.org',
        help='URL for the Tor HTTP request'
    )
    
    parser.add_argument(
        '--target',
        default='8.8.8.8',
        help='Target IP for Scapy demos'
    )
    
    parser.add_argument(
        '--new-identity',
        action='store_true',
        help='Request a new Tor identity before the request'
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🧅  Tor Network Toolkit (TNT)")
    print("=" * 50 + "\n")
    
    # Scapy Demos (local, without Tor)
    if args.mode in ['scapy', 'full']:
        run_scapy_icmp_demo(args.target)
        run_scapy_tcp_syn_demo(args.target, 443)
    
    # Tor Demos
    if args.mode in ['tor', 'full']:
        try:
            # Using the Context Manager (with ... as ...) ensures cleanup
            with TorControlManager() as tor:
                # Show initial Exit IP
                tor.get_exit_ip()
                
                if args.new_identity:
                    tor.request_new_identity()
                    # Show new Exit IP after requesting new identity
                    tor.get_exit_ip()
                
                run_tor_request_demo(args.url)
                
        except KeyboardInterrupt:
            print("\n[!] Operation cancelled by user.")
        except Exception as e:
            print(f"\n[!] An error occurred: {e}")
    
    print("=" * 50)
    print("[✓] Demo finished")
    print("=" * 50)


if __name__ == "__main__":
    main()
