# remote_gate.py
import socket
import time
from hardware.gate_sensor import GateSensor
from hardware.display_driver import TimingDisplay
from common import config
from common.network import create_message, MSG_GATE_TRIGGER

def main():
    """Main loop for the remote gate."""
    sensor = GateSensor(config.SECONDARY_GATE_PIN, config.DEBOUNCE_TIME)
    display = TimingDisplay(config.SECONDARY_DISPLAY_CS_PIN)
    display.show_message("RDY")

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((config.PRIMARY_PI_IP, config.NETWORK_PORT))
                display.show_message("CONN")
                print("Connected to primary Pi.")
                
                while True:
                    # Wait for the gate to be triggered
                    trigger_time = sensor.wait_for_trigger()
                    if trigger_time:
                        print(f"Gate triggered at {trigger_time}")
                        message = create_message(MSG_GATE_TRIGGER, {'timestamp': trigger_time})
                        s.sendall(message)
                        display.show_message("TRIG")
                        time.sleep(1) # Show TRIG message briefly
                        display.show_message("RDY")

        except (ConnectionRefusedError, BrokenPipeError, TimeoutError) as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            display.show_message("ERR")
            time.sleep(5)
            display.show_message("RDY")

if __name__ == "__main__":
    main()
