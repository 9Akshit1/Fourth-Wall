#!/bin/bash
# ORV Study Buddy Setup Script for Raspberry Pi Zero 2W

echo "Setting up ORV Study Buddy..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-pygame python3-rpi.gpio

# Install additional Python packages
pip3 install --user pygame RPi.GPIO

# Create application directory
mkdir -p /home/pi/orv_study_buddy
mkdir -p /home/pi/orv_study_data

# Copy the main application (you'll need to put the Python file here)
# cp orv_study_buddy.py /home/pi/orv_study_buddy/

# Make the script executable
chmod +x /home/pi/orv_study_buddy/orv_study_buddy.py

# Create systemd service for auto-start (optional)
sudo tee /etc/systemd/system/orv-study-buddy.service > /dev/null <<EOF
[Unit]
Description=ORV Study Buddy
After=graphical-session.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/orv_study_buddy
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 /home/pi/orv_study_buddy/orv_study_buddy.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical-session.target
EOF

# Enable the service (uncomment if you want auto-start)
# sudo systemctl enable orv-study-buddy.service

echo "Setup complete!"
echo "To run manually: python3 /home/pi/orv_study_buddy/orv_study_buddy.py"
echo "To enable auto-start: sudo systemctl enable orv-study-buddy.service"