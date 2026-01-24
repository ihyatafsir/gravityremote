#!/bin/bash
# HAYAT (حياة) - Living Proxy Wrapper
# Concept from Lisan al-Arab: الاستمرار (istimrar) = continuity
# التجدد (tajaddud) = renewal/refreshing

SCRIPT_DIR="/home/absolut7/Documents/26apps/gravityremote"
LOG_FILE="/tmp/hayat-proxy.log"

echo "🌙 HAYAT Proxy Starting - $(date)" >> $LOG_FILE

while true; do
    # Kill any existing proxy
    pkill -9 -f "tcp_forward.py" 2>/dev/null
    sleep 2
    
    echo "✨ Starting tcp_forward.py - $(date)" >> $LOG_FILE
    
    # Start the proxy
    cd $SCRIPT_DIR
    python3 tcp_forward.py >> $LOG_FILE 2>&1
    
    # If we get here, the proxy died
    echo "⚠️ Proxy died, restarting in 5s - $(date)" >> $LOG_FILE
    sleep 5
done
