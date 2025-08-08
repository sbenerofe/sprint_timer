# common/network.py
import json
import time

# Message Types
MSG_GATE_TRIGGER = 'GATE_TRIGGER'
MSG_TIME_SYNC = 'TIME_SYNC'
MSG_CURRENT_RUNNER = 'CURRENT_RUNNER'
MSG_RACE_START = 'RACE_START'
MSG_RACE_FINISH = 'RACE_FINISH'
MSG_TIMING_MODE = 'TIMING_MODE'
MSG_GPS_STATUS = 'GPS_STATUS'
MSG_WIRED_SYNC = 'WIRED_SYNC'

def create_message(msg_type: str, payload: dict = None) -> bytes:
    """Creates a JSON message and encodes it to bytes for sending over a socket."""
    message = {
        'type': msg_type, 
        'payload': payload or {},
        'timestamp': time.time_ns() if hasattr(time, 'time_ns') else time.time()
    }
    return json.dumps(message).encode('utf-8')

def parse_message(data: bytes) -> dict:
    """Parses an incoming bytes message into a Python dictionary."""
    return json.loads(data.decode('utf-8'))

def create_timing_message(timing_mode: str, timestamp: float, precision: float = None) -> bytes:
    """Creates a high-precision timing message."""
    payload = {
        'timing_mode': timing_mode,
        'timestamp': timestamp,
        'precision': precision or 1e-6
    }
    return create_message(MSG_TIME_SYNC, payload)

def create_gate_trigger_message(timestamp: float, gate_id: str, timing_mode: str = None) -> bytes:
    """Creates a gate trigger message with high-precision timestamp."""
    payload = {
        'timestamp': timestamp,
        'gate_id': gate_id,
        'timing_mode': timing_mode or 'SYSTEM'
    }
    return create_message(MSG_GATE_TRIGGER, payload)
