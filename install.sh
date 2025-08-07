#!/bin/bash

# Sprint Timer Installation Script
echo "Installing Sprint Timer dependencies..."

# Update package list
sudo apt-get update

# Install system dependencies
sudo apt-get install -y python3-pip python3-dev python3-venv

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Enable SPI interface
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Add user to gpio group (if not already added)
sudo usermod -a -G gpio $USER

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. Configure network settings in common/config.py"
echo "3. Run the application: python main_app.py"
echo ""
echo "For the secondary Pi, just run: python remote_gate.py"
