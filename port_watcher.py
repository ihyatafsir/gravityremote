#!/usr/bin/env python3
"""
Port Watcher for GravityRemote Proxy v2.1

Monitors the Antigravity language_server ports and:
1. Waits for ports to stabilize after IDE restart
2. Polls Agent Tab until chatParams has a valid port
3. Restarts the gravityremote proxy service
"""
import subprocess
import time
import os
import signal
import sys
import re
import json
import base64

CHECK_INTERVAL = 5       # seconds between checks
STABILIZE_CHECKS = 3     # number of consecutive stable checks required
CHATPARAMS_POLL_MAX = 60 # max seconds to wait for valid chatParams

AGENT_TAB_PORT = 9090    # Antigravity Agent Tab port

def get_lsp_ports():
    """Get current language_server ports from ss"""
    try:
        result = subprocess.run(
            ['ss', '-tunlp'],
            capture_output=True,
            text=True,
            timeout=5
        )
        ports = set()
        for line in result.stdout.split('\n'):
            if 'language_server' in line:
                match = re.search(r'127\.0\.0\.1:(\d+)', line)
                if match:
                    ports.add(int(match.group(1)))
        return ports
    except Exception as e:
        print(f"[WARN] Failed to get ports: {e}")
        return set()

def get_chatparams_port():
    """Extract the LSP port from chatParams on port 9090"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-H', 'Cache-Control: no-cache', f'http://127.0.0.1:{AGENT_TAB_PORT}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        match = re.search(r"window\.chatParams\s*=\s*'([A-Za-z0-9+/=]+)'", result.stdout)
        if match:
            params = json.loads(base64.b64decode(match.group(1)))
            url = params.get('languageServerUrl', '')
            port_match = re.search(r':(\d+)/', url)
            if port_match:
                return int(port_match.group(1))
    except Exception as e:
        print(f"[WARN] Failed to get chatParams port: {e}")
    return None

def restart_proxy():
    """Restart the gravityremote systemd service"""
    print("[ACTION] Restarting gravityremote proxy...")
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'restart', 'gravityremote'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("[OK] Proxy restarted successfully")
            return True
        else:
            print(f"[ERROR] Failed to restart: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Restart failed: {e}")
        return False

def wait_for_stable_ports(initial_ports):
    """Wait for ports to stabilize before taking action"""
    print(f"[STABILIZE] Waiting for ports to stabilize...")
    stable_count = 0
    last_ports = initial_ports
    
    for i in range(30):  # Max 30 checks
        time.sleep(CHECK_INTERVAL)
        current_ports = get_lsp_ports()
        
        if current_ports == last_ports and len(current_ports) >= 2:
            stable_count += 1
            print(f"[STABILIZE] Stable {stable_count}/{STABILIZE_CHECKS} - {len(current_ports)} ports")
            if stable_count >= STABILIZE_CHECKS:
                print(f"[STABILIZE] Ports stable!")
                return current_ports
        else:
            stable_count = 0
            if current_ports != last_ports:
                print(f"[STABILIZE] Ports changing: {len(current_ports)} ports")
            last_ports = current_ports
    
    print("[WARN] Ports did not stabilize within timeout")
    return last_ports

def wait_for_valid_chatparams(valid_ports):
    """Poll Agent Tab until chatParams contains a port in valid_ports"""
    print(f"[POLL] Waiting for Agent Tab to update chatParams...")
    start_time = time.time()
    
    while time.time() - start_time < CHATPARAMS_POLL_MAX:
        chatparams_port = get_chatparams_port()
        
        if chatparams_port is not None:
            if chatparams_port in valid_ports:
                print(f"[POLL] chatParams port {chatparams_port} is valid!")
                return True, chatparams_port
            else:
                elapsed = int(time.time() - start_time)
                print(f"[POLL] chatParams port {chatparams_port} still stale ({elapsed}s)...")
        
        time.sleep(3)
    
    print(f"[TIMEOUT] chatParams did not update within {CHATPARAMS_POLL_MAX}s")
    chatparams_port = get_chatparams_port()
    return False, chatparams_port

def main():
    print("=" * 60)
    print("GravityRemote Port Watcher v2.1")
    print("=" * 60)
    print(f"Check interval: {CHECK_INTERVAL}s | Stabilize: {STABILIZE_CHECKS} checks")
    print(f"chatParams poll timeout: {CHATPARAMS_POLL_MAX}s")
    print("Watching for language_server port changes...")
    print()
    
    last_ports = get_lsp_ports()
    print(f"[INIT] Current ports: {sorted(last_ports) if last_ports else 'none'}")
    
    # Initial validation
    chatparams_port = get_chatparams_port()
    if chatparams_port:
        if chatparams_port in last_ports:
            print(f"[INIT] chatParams port {chatparams_port} is valid")
        else:
            print(f"[INIT] chatParams port {chatparams_port} is STALE!")
            print(f"[INIT] Please close/reopen Agent Tab in Antigravity IDE")
    
    def signal_handler(sig, frame):
        print("\n[STOP] Port watcher stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while True:
        time.sleep(CHECK_INTERVAL)
        
        current_ports = get_lsp_ports()
        
        # Detect significant change
        if current_ports != last_ports:
            old_count = len(last_ports)
            new_count = len(current_ports)
            
            # If ports disappeared, wait for them to come back
            if new_count == 0 and old_count > 0:
                print(f"\n[CHANGE] All ports disappeared!")
                last_ports = current_ports
                continue
            
            # If new ports appeared or significant change
            if (old_count == 0 and new_count > 0) or (new_count > 0 and not current_ports.issubset(last_ports)):
                print(f"\n[CHANGE] Port change detected!")
                print(f"  Old: {len(last_ports)} ports | New: {len(current_ports)} ports")
                
                # Wait for stabilization
                stable_ports = wait_for_stable_ports(current_ports)
                
                # Wait for chatParams to update (Agent Tab refresh)
                valid, cp_port = wait_for_valid_chatparams(stable_ports)
                
                if valid:
                    print(f"[SUCCESS] chatParams updated with valid port {cp_port}")
                else:
                    print(f"[WARN] chatParams still stale (port {cp_port})")
                    print(f"[WARN] You may need to close/reopen Agent Tab manually")
                
                # Restart proxy regardless
                restart_proxy()
                
                last_ports = stable_ports
            else:
                last_ports = current_ports

if __name__ == "__main__":
    main()
