# common/timing_sync.py
import time
import threading
import subprocess
import socket
import json
from typing import Optional, Callable
import RPi.GPIO as GPIO
from . import config

class TimingSynchronizer:
    """High-precision timing synchronization using GPS or wired fallback."""
    
    def __init__(self, is_master: bool = True):
        self.is_master = is_master
        self.timing_mode = config.TIMING_MODE
        self.gps_available = False
        self.wired_connected = False
        self.sync_callback = None
        self.start_timestamp = None
        
        # Initialize GPIO for wired mode
        if self.timing_mode in ['WIRED', 'AUTO']:
            self._setup_wired_gpio()
        
        # Initialize GPS if needed
        if self.timing_mode in ['GPS', 'AUTO']:
            self._setup_gps()
    
    def _setup_wired_gpio(self):
        """Setup GPIO pins for wired synchronization."""
        GPIO.setmode(GPIO.BCM)
        
        if self.is_master:
            # Master: setup output pin
            GPIO.setup(config.WIRED_MASTER_OUTPUT_PIN, GPIO.OUT)
            GPIO.output(config.WIRED_MASTER_OUTPUT_PIN, GPIO.LOW)
        else:
            # Slave: setup input pin with interrupt
            GPIO.setup(config.WIRED_SLAVE_INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(config.WIRED_SLAVE_INPUT_PIN, GPIO.RISING, 
                                callback=self._wired_interrupt_handler, bouncetime=100)
    
    def _setup_gps(self):
        """Initialize GPS system."""
        try:
            # Check if gpsd is running
            result = subprocess.run(['systemctl', 'is-active', 'gpsd'], 
                                  capture_output=True, text=True)
            if result.stdout.strip() == 'active':
                self.gps_available = True
                print("GPS system available")
            else:
                print("GPS system not available")
        except Exception as e:
            print(f"GPS setup error: {e}")
    
    def _wired_interrupt_handler(self, channel):
        """Interrupt handler for wired synchronization signal."""
        if not self.is_master and self.sync_callback:
            # Capture timestamp immediately
            timestamp = time.time_ns() if config.USE_NANOSECOND_TIMING else time.time()
            self.start_timestamp = timestamp
            self.sync_callback('WIRED', timestamp)
    
    def wait_for_gps_lock(self, timeout: int = None) -> bool:
        """Wait for GPS lock with timeout."""
        if timeout is None:
            timeout = config.GPS_TIMEOUT_SECONDS
        
        print(f"Waiting for GPS lock (timeout: {timeout}s)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check GPS status using gpspipe
                result = subprocess.run(['gpspipe', '-w', '-n', '10'], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and 'GPGGA' in result.stdout:
                    # Parse GPS data to check satellite count
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if line.startswith('$GPGGA'):
                            parts = line.split(',')
                            if len(parts) >= 8:
                                satellites = int(parts[7]) if parts[7] else 0
                                if satellites >= config.GPS_MIN_SATELLITES:
                                    print(f"GPS lock acquired with {satellites} satellites")
                                    return True
                
                time.sleep(1)
            except Exception as e:
                print(f"GPS check error: {e}")
                time.sleep(1)
        
        print("GPS lock timeout")
        return False
    
    def get_gps_timestamp(self) -> Optional[float]:
        """Get current GPS timestamp with high precision."""
        try:
            # Use chrony to get precise time
            result = subprocess.run(['chronyc', 'tracking'], 
                                  capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                # Parse chrony output for reference time
                for line in result.stdout.split('\n'):
                    if 'Reference time' in line:
                        # Extract timestamp from chrony output
                        # Format: Reference time : Thu Jan 01 00:00:00 1970
                        # This is a simplified parser - in practice you'd need more robust parsing
                        return time.time()
            
            # Fallback to system time
            return time.time_ns() if config.USE_NANOSECOND_TIMING else time.time()
            
        except Exception as e:
            print(f"GPS timestamp error: {e}")
            return None
    
    def send_wired_signal(self):
        """Send wired synchronization signal (master only)."""
        if not self.is_master:
            return
        
        # Capture timestamp immediately before signal
        timestamp = time.time_ns() if config.USE_NANOSECOND_TIMING else time.time()
        self.start_timestamp = timestamp
        
        # Send signal
        GPIO.output(config.WIRED_MASTER_OUTPUT_PIN, GPIO.HIGH)
        time.sleep(0.001)  # 1ms pulse
        GPIO.output(config.WIRED_MASTER_OUTPUT_PIN, GPIO.LOW)
        
        print(f"Wired signal sent at {timestamp}")
        return timestamp
    
    def set_sync_callback(self, callback: Callable):
        """Set callback function for synchronization events."""
        self.sync_callback = callback
    
    def get_current_mode(self) -> str:
        """Get current timing mode."""
        if self.timing_mode == 'AUTO':
            if self.gps_available and self.wait_for_gps_lock(5):
                return 'GPS'
            else:
                return 'WIRED'
        return self.timing_mode
    
    def get_precise_timestamp(self) -> float:
        """Get current timestamp with maximum precision."""
        if self.get_current_mode() == 'GPS':
            gps_time = self.get_gps_timestamp()
            if gps_time:
                return gps_time
        
        # Fallback to system time
        return time.time_ns() if config.USE_NANOSECOND_TIMING else time.time()
    
    def cleanup(self):
        """Cleanup GPIO and other resources."""
        if self.timing_mode in ['WIRED', 'AUTO']:
            if not self.is_master:
                GPIO.remove_event_detect(config.WIRED_SLAVE_INPUT_PIN)
            GPIO.cleanup()
