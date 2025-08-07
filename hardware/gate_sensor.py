# hardware/gate_sensor.py
import RPi.GPIO as GPIO
import time

class GateSensor:
    def __init__(self, pin: int, debounce_time: float):
        """Initializes the sensor on the given GPIO pin."""
        self.pin = pin
        self.debounce_time = debounce_time
        self.last_trigger_time = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def wait_for_trigger(self):
        """Blocks until the sensor is triggered (beam broken)."""
        GPIO.wait_for_edge(self.pin, GPIO.FALLING)
        current_time = time.time()
        # Debounce logic
        if (current_time - self.last_trigger_time) > self.debounce_time:
            self.last_trigger_time = current_time
            return current_time
        return None
