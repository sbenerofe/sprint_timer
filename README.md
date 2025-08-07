# Raspberry Pi Sprint Timer

A comprehensive sprint timing system built for Raspberry Pi, featuring dual-gate timing, web interface, and LED display output.

## Features

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
- Power supply and case

### Secondary Raspberry Pi

- Raspberry Pi (any model)
- MAX7219 8x8 LED Matrix Display
- Laser break-beam sensor (finish gate)
- Power supply and case

## Software Requirements

- Python 3.7+
- Required Python packages (see requirements.txt)
- SPI enabled on both Pis
- GPIO access

## Installation

1. **Clone or download the project files**

   ```bash
   cd sprint_timer
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Enable SPI on both Raspberry Pis**

   ```bash
   sudo raspi-config
   # Navigate to Interface Options > SPI > Enable
   ```

4. **Configure network settings**
   - Set up the primary Pi as an access point with IP `192.168.4.1`
   - Configure the secondary Pi to connect to the primary Pi's network

## Configuration

Edit `common/config.py` to customize:

- Network settings (IP addresses, ports)
- GPIO pin assignments
- WiFi credentials
- Application settings

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

## System Operation

1. **Runner Selection**: Use the touchscreen UI to select a runner from the list
2. **Arming**: The system becomes "armed" when a runner is selected
3. **Start Gate**: Runner breaks the laser beam at the start gate
4. **Timing**: Real-time elapsed time is displayed on both LED displays and web interface
5. **Finish Gate**: Runner breaks the laser beam at the finish gate
6. **Results**: Time is automatically saved to database and displayed

## Web Interface

### Fan View (`/`)

- Real-time current runner display
- Live elapsed time counter
- Last run results
- Leaderboard with statistics

### Admin Panel (`/admin`)

- Manage all runners and their times
- Edit or delete individual time entries
- View comprehensive statistics

## Database Schema

### Runners Table

- `id`: Primary key
- `name`: Runner name (unique)
- `created_at`: Timestamp

### Times Table

- `id`: Primary key
- `runner_id`: Foreign key to runners
- `run_time`: Time in seconds
- `run_date`: Timestamp

## Network Protocol

The system uses JSON messages over TCP for communication:

```json
{
  "type": "GATE_TRIGGER",
  "payload": {
    "timestamp": 1234567890.123
  }
}
```

## Troubleshooting

### Common Issues

1. **SPI not working**: Ensure SPI is enabled in raspi-config
2. **GPIO errors**: Run with sudo or add user to gpio group
3. **Network connection**: Check IP addresses and firewall settings
4. **Display not showing**: Verify wiring and SPI configuration

### Debug Mode

Add debug prints to track system state:

```python
print(f"State: {self.state}, Runner: {self.current_runner}")
```

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
4. Create an issue with detailed information
