# main_app.py
import time
import socket
import threading
from ui.app_ui import SprintTimerUI
from hardware.gate_sensor import GateSensor
from hardware.display_driver import TimingDisplay
from common import config, database
from common.network import parse_message, MSG_GATE_TRIGGER
from web import server

# Application states
STATE_IDLE = 'IDLE'
STATE_ARMED = 'ARMED' # Ready for a run
STATE_RUNNING = 'RUNNING'
STATE_FINISHED = 'FINISHED'

class MainApplication:
    def __init__(self):
        # App state
        self.state = STATE_IDLE
        self.current_runner = None # (id, name)
        self.start_time = 0
        self.finish_time = 0
        
        # Shared data for the web server
        self.shared_web_data = {
            'current_runner': 'N/A',
            'elapsed_time': '0.00',
            'last_run': {'name': 'N/A', 'time': 0.0}
        }

        # Initialize components
        database.initialize_db()
        self.local_gate = GateSensor(config.PRIMARY_GATE_PIN, config.DEBOUNCE_TIME)
        self.display = TimingDisplay(config.PRIMARY_DISPLAY_CS_PIN)
        
        # UI setup
        app_callbacks = {
            'set_runner': self.set_runner,
            'add_runner': self.add_runner,
            'reset_timer': self.reset_system,
        }
        self.ui = SprintTimerUI(app_callbacks)
        
        # Start background threads
        threading.Thread(target=self.network_listener, daemon=True).start()
        threading.Thread(target=self.local_gate_handler, daemon=True).start()
        threading.Thread(target=self.ui_updater, daemon=True).start()
        threading.Thread(target=server.run_server, args=(self.shared_web_data,), daemon=True).start()

    def run(self):
        """Starts the Tkinter main loop."""
        self.refresh_runner_list()
        self.reset_system()
        self.ui.mainloop()

    # --- State Machine and Logic ---
    def set_runner(self, runner_id, runner_name):
        if self.state in [STATE_IDLE, STATE_FINISHED]:
            self.current_runner = (runner_id, runner_name)
            self.state = STATE_ARMED
            self.ui.update_current_runner(runner_name)
            self.shared_web_data['current_runner'] = runner_name
            self.display.show_message("RDY")
            print(f"Armed for runner: {runner_name}")

    def start_run(self, timestamp):
        if self.state == STATE_ARMED:
            self.state = STATE_RUNNING
            self.start_time = timestamp
            print(f"Run started at {self.start_time}")

    def finish_run(self, timestamp):
        if self.state == STATE_RUNNING:
            self.state = STATE_FINISHED
            self.finish_time = timestamp
            run_time = self.finish_time - self.start_time
            print(f"Run finished. Time: {run_time:.2f}s")
            
            # Save to DB
            if self.current_runner:
                database.add_run_time(self.current_runner[0], run_time)
            
            # Update UI and displays
            self.ui.update_last_run_time(f"{run_time:.2f}")
            self.display.show_time(run_time)
            # update shared web data
            self.shared_web_data['last_run'] = {'name': self.current_runner[1], 'time': run_time}

    def reset_system(self):
        self.state = STATE_IDLE if not self.current_runner else STATE_ARMED
        self.start_time = 0
        self.finish_time = 0
        self.ui.update_elapsed_time("0.00")
        self.ui.update_last_run_time("--.--")
        self.shared_web_data['elapsed_time'] = "0.00"
        self.display.clear()
        print("System reset.")

    # --- Handlers and Threads ---
    def local_gate_handler(self):
        """Thread to monitor the local gate."""
        while True:
            timestamp = self.local_gate.wait_for_trigger()
            if timestamp:
                self.handle_gate_trigger('local', timestamp)

    def network_listener(self):
        """Thread to listen for connections from the remote gate."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', config.NETWORK_PORT))
            server_socket.listen(1)
            print(f"Network listener started on port {config.NETWORK_PORT}")
            
            while True:
                try:
                    client_socket, address = server_socket.accept()
                    print(f"Remote gate connected from {address}")
                    
                    # Handle the connection in a separate thread
                    threading.Thread(target=self.handle_remote_connection, 
                                  args=(client_socket,), daemon=True).start()
                except Exception as e:
                    print(f"Network listener error: {e}")

    def handle_remote_connection(self, client_socket):
        """Handle a connection from the remote gate."""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = parse_message(data)
                if message['type'] == MSG_GATE_TRIGGER:
                    timestamp = message['payload']['timestamp']
                    self.handle_gate_trigger('remote', timestamp)
                    
        except Exception as e:
            print(f"Remote connection error: {e}")
        finally:
            client_socket.close()

    def handle_gate_trigger(self, source, timestamp):
        """Unified logic for handling a trigger from any gate."""
        print(f"Trigger from {source} gate at {timestamp}")
        # Logic based on system configuration (which gate is start/stop)
        # For now, assume local is start and remote is stop.
        if source == 'local' and self.state == STATE_ARMED:
            self.start_run(timestamp)
        elif source == 'remote' and self.state == STATE_RUNNING:
            self.finish_run(timestamp)

    def ui_updater(self):
        """Thread to periodically update the UI time display."""
        while True:
            if self.state == STATE_RUNNING:
                elapsed = time.time() - self.start_time
                time_str = f"{elapsed:.2f}"
                self.ui.update_elapsed_time(time_str)
                self.display.show_time(elapsed)
                self.shared_web_data['elapsed_time'] = time_str
            time.sleep(0.05) # Update 20 times per second

    # --- UI Callbacks ---
    def add_runner(self, name):
        # Add to DB and refresh the UI list
        try:
            database.add_runner(name)
            self.refresh_runner_list()
            print(f"Added runner: {name}")
        except Exception as e:
            print(f"Error adding runner: {e}")
    
    def refresh_runner_list(self):
        runners = database.get_all_runners()
        self.ui.update_runner_list(runners)


if __name__ == "__main__":
    app = MainApplication()
    app.run()
