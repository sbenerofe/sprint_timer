# hardware/gate_sensor.py
import RPi.GPIO as GPIO
import time
from common import config

class GateSensor:
    def __init__(self, pin: int, debounce_time: float, timing_sync=None):
        """Initializes the sensor on the given GPIO pin with high-precision timing."""
        self.pin = pin
        self.debounce_time = debounce_time
        self.last_trigger_time = 0
        self.timing_sync = timing_sync
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def wait_for_trigger(self):
        """Blocks until the sensor is triggered (beam broken) with high precision."""
        GPIO.wait_for_edge(self.pin, GPIO.FALLING)
        current_time = self._get_precise_timestamp()
        
        # Debounce logic
        if (current_time - self.last_trigger_time) > self.debounce_time:
            self.last_trigger_time = current_time
            return current_time
        return None
    
    def _get_precise_timestamp(self) -> float:
        """Get timestamp with maximum precision available."""
        if self.timing_sync:
            return self.timing_sync.get_precise_timestamp()
        else:
            return time.time_ns() if config.USE_NANOSECOND_TIMING else time.time()
    
    def get_timing_mode(self) -> str:
        """Get current timing mode."""
        if self.timing_sync:
            return self.timing_sync.get_current_mode()
        return 'SYSTEM'
    
    def set_timing_sync(self, timing_sync):
        """Set the timing synchronizer for high-precision timing."""
        self.timing_sync = timing_sync
