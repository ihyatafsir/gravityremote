# GravityRemote

> 🌐 Access your Antigravity AI Agent through any web browser

GravityRemote provides a web-based interface for the Antigravity IDE, allowing you to interact with your AI agent remotely from any device with a browser.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ✨ Features

- **Web-Based IDE Interface** - Full IDE experience in your browser
- **Real Agent Integration** - Embedded Antigravity chat panel
- **File Explorer** - Browse and view workspace files
- **Code Viewer** - Syntax-highlighted file display
- **WebSocket Communication** - Real-time bidirectional messaging
- **Mobile Optimized** - Responsive design with automatic viewport injection

---

## 📋 Prerequisites

- **Antigravity IDE** installed and running
- **Python 3.8+** with `websockets` library
- Network access to the Antigravity instance

```bash
# Install required Python package
pip install websockets
```

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ihyatafsir/gravityremote.git
cd gravityremote
```

### Step 2: Configure Workspace Path (Optional)

Edit `websocket_server.py` to set your workspace directory:

```python
WORKSPACE = "/path/to/your/workspace"  # Default: /root/Documents/REMOTEGRAVITY
```

---

## 🏃 Running GravityRemote

### Option A: Start All Services (Recommended)

```bash
# Start all services in background
python3 websocket_server.py &
python3 http_proxy.py &
python3 proxy_server.py &
python3 -m http.server 9090 &
```

### Option B: Using a Start Script

Create `start.sh`:
```bash
#!/bin/bash
echo "Starting GravityRemote..."

# Kill any existing instances
pkill -f "websocket_server.py" 2>/dev/null
pkill -f "http_proxy.py" 2>/dev/null
pkill -f "proxy_server.py" 2>/dev/null

# Start services
python3 websocket_server.py &
python3 http_proxy.py &
python3 proxy_server.py &
python3 -m http.server 9090 &

echo "GravityRemote is running!"
echo "Access: http://localhost:8890"
```

```bash
chmod +x start.sh
./start.sh
```

---

## 🌐 Accessing the Interface

| URL | Description |
|-----|-------------|
| `http://localhost:8890` | **Main Entry** - Mobile optimized with proxy |
| `http://localhost:9090` | Direct access to web interface |
| `http://localhost:9092` | Antigravity native chat (if available) |

### Remote Access

To access from another device on your network:
1. Replace `localhost` with your machine's IP address
2. Ensure ports 8888, 8889, 8890, 9090 are accessible

```
http://<your-ip>:8890
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Browser                            │
│                  http://localhost:8890                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              HTTP Proxy (Port 8890)                         │
│         - Mobile optimization injection                      │
│         - CORS headers                                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Static Server│  │  WebSocket   │  │  Antigravity │
│  (Port 9090) │  │  (Port 8888) │  │  (Port 9092) │
│  index.html  │  │  File Ops    │  │  Real Agent  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Port Reference

| Port | Service | Description |
|------|---------|-------------|
| 8888 | WebSocket Server | Real-time communication, file operations |
| 8889 | TCP Proxy | Generic TCP forwarding to port 9090 |
| 8890 | HTTP Proxy | Main entry with mobile optimization |
| 9090 | Static Server | Serves the web interface |
| 9092 | Antigravity Chat | Native agent chat (auto-detected) |

---

## 📁 File Structure

```
gravityremote/
├── index.html          # Main IDE web interface
├── websocket_server.py # WebSocket backend + file operations
├── http_proxy.py       # HTTP proxy with mobile injection
├── proxy_server.py     # Async TCP proxy
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── test_*.py           # Test scripts
```

---

## ⚙️ Configuration

### Changing the Workspace

In `websocket_server.py`:
```python
WORKSPACE = "/your/custom/path"
```

### Changing Ports

Edit the respective `PORT` variable in each file:
- `websocket_server.py` - WebSocket port (default: 8888)
- `http_proxy.py` - HTTP proxy port (default: 8890)
- `proxy_server.py` - TCP proxy port (default: 8889)

### Enabling Remote Access

By default, servers bind to `0.0.0.0`, allowing remote connections. Ensure your firewall permits the required ports.

---

## 🔧 Troubleshooting

### "Connection Refused" Error
- Ensure all services are running: `ps aux | grep python`
- Check if Antigravity is running: `ps aux | grep antigravity`

### Agent Chat Not Loading
- Verify Antigravity is running on port 9092
- Check with: `curl http://127.0.0.1:9092`

### WebSocket Disconnects
- Check if `websocket_server.py` is running
- Look for errors: `python3 websocket_server.py` (foreground)

### Files Not Showing
- Verify `WORKSPACE` path exists and is readable
- Check permissions: `ls -la /path/to/workspace`

---

## 🛠️ Development

### Running Tests
```bash
python3 test_proxy.py    # Test TCP proxy
python3 test_input.py    # Test WebSocket input
python3 demo_test.py     # Demo shell commands
```

### Modifying the UI
Edit `index.html` - the interface is built with vanilla HTML/CSS/JavaScript for easy customization.

---

## 📄 License

MIT License - Feel free to use, modify, and distribute.

---

## 🙏 Credits

Built with ❤️ by the Antigravity Agent

**Repository**: [github.com/ihyatafsir/gravityremote](https://github.com/ihyatafsir/gravityremote)
