# common/network.py
import json

# Message Types
MSG_GATE_TRIGGER = 'GATE_TRIGGER'
MSG_TIME_SYNC = 'TIME_SYNC'
MSG_CURRENT_RUNNER = 'CURRENT_RUNNER'
MSG_RACE_START = 'RACE_START'
MSG_RACE_FINISH = 'RACE_FINISH'

def create_message(msg_type: str, payload: dict = None) -> bytes:
    """Creates a JSON message and encodes it to bytes for sending over a socket."""
    message = {'type': msg_type, 'payload': payload or {}}
    return json.dumps(message).encode('utf-8')

def parse_message(data: bytes) -> dict:
    """Parses an incoming bytes message into a Python dictionary."""
    return json.loads(data.decode('utf-8'))
