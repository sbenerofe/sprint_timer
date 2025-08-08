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

# GPS Configuration
GPS_UART_TX = 14  # GPIO14 for UART TX
GPS_UART_RX = 15  # GPIO15 for UART RX
GPS_PPS_PIN = 18  # GPIO18 for PPS signal
GPS_DEVICE = '/dev/ttyAMA0'
GPS_SHARED_MEMORY = 0  # gpsd shared memory segment

# Wired Synchronization Configuration
WIRED_MASTER_OUTPUT_PIN = 23  # GPIO23 for master output signal
WIRED_SLAVE_INPUT_PIN = 24    # GPIO24 for slave input signal
WIRED_SIGNAL_RESISTOR = 330   # Ohm resistor for protection

# Timing Mode Configuration
TIMING_MODE = 'GPS'  # Options: 'GPS', 'WIRED', 'AUTO'
AUTO_FALLBACK = True  # Automatically fallback to wired if GPS unavailable

# Application Settings
DATABASE_FILE = 'sprint_times.db'
DEBOUNCE_TIME = 0.3 # Seconds to prevent multiple triggers

# GPS Timeout Settings
GPS_TIMEOUT_SECONDS = 30  # Time to wait for GPS lock
GPS_MIN_SATELLITES = 4    # Minimum satellites for valid GPS
GPS_MAX_AGE = 5.0         # Maximum age of GPS data in seconds

# High Precision Timing
USE_NANOSECOND_TIMING = True  # Use nanosecond precision when available
TIMING_PRECISION = 1e-6       # Target timing precision in seconds
