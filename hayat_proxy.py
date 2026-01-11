#!/usr/bin/env python3
"""
HAYAT (حياة) - Living Self-Healing Proxy for Gravity Remote
============================================================
Named after the Arabic word for "Life" - this proxy stays alive through:
- الاستمرار (istimrar) - Continuity: Never give up, always restart
- التجدد (tajaddud) - Renewal: Detect IDE restarts and refresh config
- المراقبة (al-muraqaba) - Monitoring: Watch for health failures

v1.0 - Initial implementation
"""

import subprocess
import time
import os
import sys
import re
import signal
import socket
import threading

# Configuration
CHECK_INTERVAL = 10      # Seconds between health checks
RESTART_DELAY = 5        # Seconds to wait before restart
MAX_CONSECUTIVE_FAILS = 3  # Failures before restart

# Port configuration
UI_PORT = 8890
MOBILE_PORT = 8892
LSP_PORT = 8891

class HayatProxy:
    """Self-Healing Gravity Remote Proxy"""
    
    def __init__(self):
        self.proxy_process = None
        self.running = True
        self.consecutive_fails = 0
        self.current_csrf = None
        self.current_lsp_port = None
        
        # Handle termination gracefully
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
    
    def handle_signal(self, signum, frame):
        """Graceful shutdown"""
        print(f"\n[HAYAT] Received signal {signum}, shutting down...")
        self.running = False
        if self.proxy_process:
            self.proxy_process.terminate()
        sys.exit(0)
    
    def log(self, message):
        """Log with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def get_csrf_token(self):
        """Extract CSRF token from language_server process"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'language_server' in line and 'csrf_token' in line and 'workspace_id' in line:
                    match = re.search(r'csrf_token\s+([a-f0-9-]+)', line)
                    if match:
                        return match.group(1)
        except Exception as e:
            self.log(f"[WARN] Failed to get CSRF: {e}")
        return None
    
    def get_lsp_port(self):
        """Find the LSP port that responds to HTTPS"""
        try:
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=5)
            ports = []
            for line in result.stdout.split('\n'):
                if 'language_server' in line:
                    match = re.search(r'127\.0\.0\.1:(\d+)', line)
                    if match:
                        ports.append(int(match.group(1)))
            
            # Return the first port (usually the main LSP)
            return ports[0] if ports else None
        except Exception as e:
            self.log(f"[WARN] Failed to get LSP port: {e}")
        return None
    
    def check_port_bound(self, port):
        """Check if our proxy is bound to a port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def health_check(self):
        """Check if proxy is healthy"""
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                 f'http://127.0.0.1:{MOBILE_PORT}/'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() == '200'
        except:
            return False
    
    def detect_config_change(self):
        """Detect if IDE config (CSRF/LSP port) has changed"""
        new_csrf = self.get_csrf_token()
        new_lsp = self.get_lsp_port()
        
        if new_csrf and new_csrf != self.current_csrf:
            self.log(f"[التجدد] CSRF token changed: {new_csrf[:20]}...")
            self.current_csrf = new_csrf
            return True
        
        if new_lsp and new_lsp != self.current_lsp_port:
            self.log(f"[التجدد] LSP port changed: {new_lsp}")
            self.current_lsp_port = new_lsp
            return True
        
        return False
    
    def start_proxy(self):
        """Start the tcp_forward.py proxy"""
        self.log("[الاستمرار] Starting tcp_forward.py...")
        
        # Kill any existing proxy
        subprocess.run(['pkill', '-9', '-f', 'tcp_forward.py'], 
                      capture_output=True, timeout=5)
        time.sleep(2)
        
        # Start new proxy
        script_dir = os.path.dirname(os.path.abspath(__file__))
        proxy_script = os.path.join(script_dir, 'tcp_forward.py')
        
        self.proxy_process = subprocess.Popen(
            ['python3', proxy_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=script_dir
        )
        
        # Wait for it to start
        time.sleep(3)
        
        # Update current config
        self.current_csrf = self.get_csrf_token()
        self.current_lsp_port = self.get_lsp_port()
        
        if self.check_port_bound(MOBILE_PORT):
            self.log(f"[✓] Proxy started on ports {UI_PORT}, {MOBILE_PORT}, {LSP_PORT}")
            return True
        else:
            self.log("[✗] Proxy failed to bind to ports")
            return False
    
    def restart_proxy(self, reason="unknown"):
        """Restart the proxy with reason logging"""
        self.log(f"[المراقبة] Restarting proxy - reason: {reason}")
        
        if self.proxy_process:
            self.proxy_process.terminate()
            try:
                self.proxy_process.wait(timeout=5)
            except:
                self.proxy_process.kill()
        
        time.sleep(RESTART_DELAY)
        return self.start_proxy()
    
    def run(self):
        """Main HAYAT loop - keeps proxy alive"""
        self.log("=" * 60)
        self.log("HAYAT (حياة) Self-Healing Proxy v1.0")
        self.log("=" * 60)
        self.log("Concepts: الاستمرار (continuity) | التجدد (renewal) | المراقبة (monitoring)")
        self.log("=" * 60)
        
        # Initial start
        if not self.start_proxy():
            self.log("[WARN] Initial start failed, retrying...")
            time.sleep(RESTART_DELAY)
            self.start_proxy()
        
        # Main monitoring loop
        while self.running:
            try:
                time.sleep(CHECK_INTERVAL)
                
                # Check for config changes (IDE restart)
                if self.detect_config_change():
                    self.restart_proxy("IDE config changed")
                    self.consecutive_fails = 0
                    continue
                
                # Health check
                if not self.health_check():
                    self.consecutive_fails += 1
                    self.log(f"[المراقبة] Health check failed ({self.consecutive_fails}/{MAX_CONSECUTIVE_FAILS})")
                    
                    if self.consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                        self.restart_proxy("consecutive health failures")
                        self.consecutive_fails = 0
                else:
                    if self.consecutive_fails > 0:
                        self.log("[✓] Health restored")
                    self.consecutive_fails = 0
                
            except Exception as e:
                self.log(f"[ERROR] Loop error: {e}")
                time.sleep(RESTART_DELAY)


if __name__ == '__main__':
    hayat = HayatProxy()
    hayat.run()
