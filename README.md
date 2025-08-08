# Raspberry Pi Sprint Timer - High Precision

A comprehensive sprint timing system built for Raspberry Pi, featuring dual-gate timing, web interface, LED display output, and **high-precision timing synchronization** using GPS and wired fallback modes.

## Features

- **High-Precision Timing**: GPS-based UTC synchronization with microsecond accuracy
- **Dual Timing Modes**: GPS (outdoor) and wired (indoor/GPS-denied) synchronization
- **Dual-Gate Timing**: Start and finish gates with laser break-beam sensors
- **Touchscreen UI**: Intuitive interface for runner selection and system control
- **LED Display**: Real-time timing display using MAX7219 7-segment LED
- **Web Interface**: Fan view and admin panel accessible via web browser
- **Database Storage**: SQLite database for runner and time management
- **Network Communication**: TCP communication between primary and secondary Pi
- **Real-time Updates**: Live data polling and automatic leaderboard updates

## Hardware Requirements

### Primary Raspberry Pi

- Raspberry Pi (3B+ or 4 recommended)
- 7" Official Raspberry Pi Touchscreen Display
- MAX7219 8x8 LED Matrix Display
- Laser break-beam sensor (start gate)
- **GPS module with PPS output** (e.g., NEO-6M, NEO-8M)
- Power supply and case

### Secondary Raspberry Pi

- Raspberry Pi (any model)
- MAX7219 8x8 LED Matrix Display
- Laser break-beam sensor (finish gate)
- **GPS module with PPS output** (e.g., NEO-6M, NEO-8M)
- Power supply and case

### Wiring Requirements

#### GPS Module Connection (Both Pis)

- **Power**: Connect Pi GND to GPS GND, Pi 5V to GPS VCC
- **UART**: Connect Pi GPIO14 (TX) to GPS RX, Pi GPIO15 (RX) to GPS TX
- **PPS**: Connect GPS PPS output to Pi GPIO18

#### Wired Synchronization (Between Pis)

- **Common Ground**: Connect GND pin on master Pi to GND pin on slave Pi
- **Signal Line**: Connect GPIO23 (master) to GPIO24 (slave) with 330Ω series resistor

## Software Requirements

- Python 3.7+
- Required Python packages (see requirements.txt)
- SPI and UART enabled on both Pis
- GPIO access
- **gpsd** and **chrony** for GPS timing

## Installation

1. **Clone or download the project files**

   ```bash
   cd sprint_timer
   ```

2. **Run the installation script**

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Reboot the Raspberry Pi**

   ```bash
   sudo reboot
   ```

4. **Configure network settings**

   - Set up the primary Pi as an access point with IP `192.168.4.1`
   - Configure the secondary Pi to connect to the primary Pi's network

## Configuration

Edit `common/config.py` to customize:

- Network settings (IP addresses, ports)
- GPIO pin assignments
- WiFi credentials
- **GPS and timing mode settings**
- **Timing precision options**

### Timing Mode Configuration

```python
# Timing Mode Configuration
TIMING_MODE = 'GPS'  # Options: 'GPS', 'WIRED', 'AUTO'
AUTO_FALLBACK = True  # Automatically fallback to wired if GPS unavailable
USE_NANOSECOND_TIMING = True  # Use nanosecond precision when available
```

## Usage

### Primary Pi Setup

1. **Run the main application**

   ```bash
   python main_app.py
   ```

2. **Access the web interface**

   - Fan view: `http://192.168.4.1/`
   - Admin panel: `http://192.168.4.1/admin` (username: admin, password: supersecret)

### Secondary Pi Setup

1. **Run the remote gate script**

   ```bash
   python remote_gate.py
   ```

## Timing Modes

### GPS Mode (Primary)

- **Accuracy**: Microsecond-level precision using UTC
- **Use Case**: Outdoor environments with GPS signal
- **Setup**: GPS module connected to UART and PPS pins
- **Operation**: Automatically disciplines system clock to GPS time

### Wired Mode (Fallback)

- **Accuracy**: Nanosecond-level precision for relative timing
- **Use Case**: Indoor environments or GPS-denied areas
- **Setup**: Direct GPIO connection between master and slave Pis
- **Operation**: Master sends synchronization pulse, slave captures timestamp

### Auto Mode

- **Behavior**: Automatically selects GPS if available, falls back to wired
- **Configuration**: Set `TIMING_MODE = 'AUTO'` in config.py

## System Operation

1. **Timing System Initialization**: System checks for GPS lock or wired connection
2. **Runner Selection**: Use the touchscreen UI to select a runner from the list
3. **System Arming**: The system becomes "armed" when a runner is selected
4. **Start Gate**: Runner breaks the laser beam at the start gate
5. **High-Precision Timing**: Real-time elapsed time with microsecond/nanosecond precision
6. **Finish Gate**: Runner breaks the laser beam at the finish gate
7. **Results**: Time is automatically saved to database and displayed

## Web Interface

### Fan View (`/`)

- Real-time current runner display
- Live elapsed time counter
- Last run results
- **Timing system status (mode, GPS status, precision)**
- Leaderboard with statistics

### Admin Panel (`/admin`)

- Manage all runners and their times
- Edit or delete individual time entries
- View comprehensive statistics

## GPS Status Monitoring

### Command Line Tools

```bash
# Check GPS lock status
gpspipe -w -n 10

# Check chrony timing status
chronyc tracking

# Check PPS signal
cat /sys/class/pps/pps0/assert

# Monitor GPS satellites
gpspipe -w | grep GPGGA
```

### Web Interface

The fan view displays real-time GPS status and timing mode information.

## Database Schema

### Runners Table

- `id`: Primary key
- `name`: Runner name (unique)
- `created_at`: Timestamp

### Times Table

- `id`: Primary key
- `runner_id`: Foreign key to runners
- `run_time`: Time in seconds (high precision)
- `run_date`: Timestamp

## Network Protocol

The system uses JSON messages over TCP for communication with high-precision timestamps:

```json
{
  "type": "GATE_TRIGGER",
  "payload": {
    "timestamp": 1234567890123456789,
    "gate_id": "REMOTE",
    "timing_mode": "GPS"
  },
  "timestamp": 1234567890123456789
}
```

## Troubleshooting

### Common Issues

1. **GPS not locking**: Check antenna connection and clear sky view
2. **SPI not working**: Ensure SPI is enabled in raspi-config
3. **GPIO errors**: Run with sudo or add user to gpio group
4. **Network connection**: Check IP addresses and firewall settings
5. **Display not showing**: Verify wiring and SPI configuration
6. **Timing drift**: Check GPS signal quality and chrony status

### GPS Troubleshooting

```bash
# Check if gpsd is running
systemctl status gpsd

# Check GPS device
ls -l /dev/ttyAMA0

# Test GPS communication
gpspipe -r /dev/ttyAMA0

# Check chrony sources
chronyc sources
```

### Debug Mode

Add debug prints to track system state:

```python
print(f"State: {self.state}, Runner: {self.current_runner}")
print(f"Timing Mode: {self.timing_mode}, GPS Status: {self.gps_status}")
```

## Performance Characteristics

### Timing Precision

- **GPS Mode**: Microsecond-level accuracy (1e-6 seconds)
- **Wired Mode**: Nanosecond-level precision for relative timing
- **System Mode**: Millisecond-level precision (fallback)

### Latency

- **GPS Mode**: < 1ms latency for timing events
- **Wired Mode**: < 100μs latency for synchronization
- **Network Mode**: < 10ms latency for remote gate communication

## Customization

### Adding New Sensors

1. Create new sensor class in `hardware/`
2. Update `main_app.py` to handle new sensor type
3. Modify configuration as needed

### Web Interface Customization

- Edit HTML templates in `web/templates/`
- Modify CSS in `web/static/style.css`
- Add new API endpoints in `web/server.py`

### Database Extensions

- Add new tables in `database.py`
- Implement new query functions
- Update web interface to display new data

### Timing System Extensions

- Add new timing sources in `common/timing_sync.py`
- Implement custom synchronization protocols
- Add precision timing analysis tools

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the configuration settings
3. Check the debug output
4. Verify GPS and timing system status
5. Create an issue with detailed information
