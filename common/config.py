# common/config.py

# Network Configuration
PRIMARY_PI_IP = '192.168.4.1'  # Static IP for the Primary Pi Access Point
NETWORK_PORT = 9999
WIFI_SSID = 'SprintTimerNet'
WIFI_PASSWORD = 'runfast' # Set to None for an open network

# Hardware Pin Configuration (using BCM numbering)
# Primary Pi
PRIMARY_GATE_PIN = 17
PRIMARY_DISPLAY_CS_PIN = 8 # SPI Chip Select for MAX7219

# Secondary Pi
SECONDARY_GATE_PIN = 17
SECONDARY_DISPLAY_CS_PIN = 8

# Application Settings
DATABASE_FILE = 'sprint_times.db'
DEBOUNCE_TIME = 0.3 # Seconds to prevent multiple triggers
