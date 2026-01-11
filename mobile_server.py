#!/usr/bin/env python3
"""
GravityRemote Mobile Server - Port 8893
Dark mobile-friendly version with IDE restart capability
"""

import http.server
import socketserver
import subprocess
import json
import os
import psutil
from urllib.parse import urlparse

PORT = 8893
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MobileHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        # Serve mobile.html as default
        if parsed.path == '/' or parsed.path == '/mobile':
            self.path = '/mobile.html'
        elif parsed.path == '/api/stats':
            return self.handle_stats()
        
        return super().do_GET()
    
    def handle_stats(self):
        """Return CPU and RAM usage for retro display"""
        try:
            cpu = int(psutil.cpu_percent(interval=0.1))
            ram = int(psutil.virtual_memory().used / 1024 / 1024)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {'cpu': cpu, 'ram': ram}
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/restart-ide':
            return self.handle_restart_ide()
        elif parsed.path == '/api/agent-mode':
            return self.handle_agent_mode()
        
        self.send_error(404, 'Not Found')
    
    def handle_agent_mode(self):
        """Send Ctrl+E to open Agent Mode in IDE"""
        print("[Mobile Server] Agent Mode requested (Ctrl+E)")
        
        try:
            # Use xdotool to send Ctrl+E to the active window
            result = subprocess.run(
                ['xdotool', 'key', 'ctrl+e'],
                capture_output=True,
                text=True
            )
            
            print(f"[Mobile Server] xdotool result: {result.returncode}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'message': 'Agent Mode signal sent (Ctrl+E)'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"[Mobile Server] Agent mode error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': False,
                'message': str(e)
            }
            self.wfile.write(json.dumps(response).encode())
    
    def handle_restart_ide(self):
        """Restart the Antigravity IDE process"""
        print("[Mobile Server] Restart IDE requested")
        
        try:
            # Find and kill language_server processes
            result = subprocess.run(
                ['pkill', '-f', 'language_server'],
                capture_output=True,
                text=True
            )
            
            # Log the result
            print(f"[Mobile Server] pkill result: {result.returncode}")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'message': 'IDE restart signal sent',
                'note': 'The IDE should restart automatically'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"[Mobile Server] Restart error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': False,
                'message': str(e)
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[Mobile:{PORT}] {args[0]}")


def main():
    print(f"""
╔════════════════════════════════════════╗
║   GravityRemote Mobile Server          ║
║   Port: {PORT}                            ║
║   Theme: Dark                          ║
║   Features: IDE Restart, Touch-friendly║
╚════════════════════════════════════════╝
    """)
    
    with socketserver.TCPServer(("", PORT), MobileHandler) as httpd:
        print(f"[Mobile Server] Running on http://0.0.0.0:{PORT}")
        print(f"[Mobile Server] Mobile UI: http://localhost:{PORT}/mobile")
        print(f"[Mobile Server] Restart API: POST /api/restart-ide")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Mobile Server] Shutting down...")


if __name__ == '__main__':
    main()
