#!/bin/bash

# Script to shut down PC running Zorin OS
# Usage: ./shutdown_pc.sh [delay_in_minutes]

echo "PC Shutdown Script for Zorin OS"
echo "================================"

# Default delay is 0 minutes (immediate shutdown)
DELAY=0

# Check if a delay argument was provided
if [ $# -gt 0 ]; then
    DELAY=$1
    echo "Shutting down in $DELAY minutes..."
else
    echo "Shutting down immediately..."
fi

# Execute the shutdown command
# Using sudo to ensure proper permissions
sudo shutdown -h +$DELAY

# If immediate shutdown, we can also use:
# sudo shutdown -h now

echo "Shutdown command sent."
echo "Press Ctrl+C within 10 seconds to cancel"

# Give user a chance to cancel
sleep 10

echo "Shutdown process initiated."
