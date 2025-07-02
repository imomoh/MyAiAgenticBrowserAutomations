#!/bin/bash

# Helper script to start Chrome with remote debugging enabled
# This allows the AI agent to connect to your existing Chrome instance

PORT=${1:-9222}

echo "🌐 Starting Chrome with remote debugging on port $PORT"
echo "After Chrome starts, you can run your AI agent with --use-profile flag"
echo ""
echo "Press Ctrl+C to stop Chrome"
echo ""

# Detect OS and start Chrome appropriately
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
        --remote-debugging-port=$PORT \
        --disable-web-security \
        --disable-features=VizDisplayCompositor \
        --disable-background-timer-throttling \
        --disable-backgrounding-occluded-windows \
        --disable-renderer-backgrounding
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    google-chrome \
        --remote-debugging-port=$PORT \
        --disable-web-security \
        --disable-features=VizDisplayCompositor \
        --disable-background-timer-throttling \
        --disable-backgrounding-occluded-windows \
        --disable-renderer-backgrounding
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    "C:\Program Files\Google\Chrome\Application\chrome.exe" \
        --remote-debugging-port=$PORT \
        --disable-web-security \
        --disable-features=VizDisplayCompositor \
        --disable-background-timer-throttling \
        --disable-backgrounding-occluded-windows \
        --disable-renderer-backgrounding
else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "Please start Chrome manually with: --remote-debugging-port=$PORT"
    exit 1
fi