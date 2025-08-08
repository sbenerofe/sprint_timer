# remote_gate.py
import socket
import time
from hardware.gate_sensor import GateSensor
from hardware.display_driver import TimingDisplay
from common import config
from common.timing_sync import TimingSynchronizer
from common.network import create_gate_trigger_message, parse_message, MSG_GATE_TRIGGER

def main():
    """Main loop for the remote gate with high-precision timing."""
    # Initialize timing synchronizer (slave mode)
    timing_sync = TimingSynchronizer(is_master=False)
    
    # Initialize hardware with timing sync
    sensor = GateSensor(config.SECONDARY_GATE_PIN, config.DEBOUNCE_TIME, timing_sync)
    display = TimingDisplay(config.SECONDARY_DISPLAY_CS_PIN)
    display.show_message("RDY")

    # Set up synchronization callback
    def sync_callback(mode, timestamp):
        print(f"Synchronization event: {mode} at {timestamp}")
        display.show_message("SYNC")

    timing_sync.set_sync_callback(sync_callback)

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((config.PRIMARY_PI_IP, config.NETWORK_PORT))
                display.show_message("CONN")
                print("Connected to primary Pi.")
                
                # Send timing mode information
                current_mode = timing_sync.get_current_mode()
                print(f"Current timing mode: {current_mode}")
                
                while True:
                    # Wait for the gate to be triggered
                    trigger_time = sensor.wait_for_trigger()
                    if trigger_time:
                        print(f"Gate triggered at {trigger_time}")
                        
                        # Create high-precision trigger message
                        message = create_gate_trigger_message(
                            timestamp=trigger_time,
                            gate_id='REMOTE',
                            timing_mode=current_mode
                        )
                        
                        s.sendall(message)
                        display.show_message("TRIG")
                        time.sleep(1) # Show TRIG message briefly
                        display.show_message("RDY")

        except (ConnectionRefusedError, BrokenPipeError, TimeoutError) as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            display.show_message("ERR")
            time.sleep(5)
            display.show_message("RDY")
        finally:
            timing_sync.cleanup()

if __name__ == "__main__":
    main()
