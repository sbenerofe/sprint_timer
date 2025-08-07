# ui/app_ui.py
import tkinter as tk
from tkinter import simpledialog, messagebox

class SprintTimerUI(tk.Tk):
    def __init__(self, app_callbacks):
        super().__init__()
        self.title("Sprint Timer")
        self.geometry("800x480") # For the official 7" display
        self.app_callbacks = app_callbacks # Callbacks to the main application logic

        # Data variables
        self.runner_list_var = tk.StringVar()
        self.current_runner_var = tk.StringVar(value="No Runner Selected")
        self.elapsed_time_var = tk.StringVar(value="0.00")
        self.last_run_time_var = tk.StringVar(value="--.--")

        # Create main frames
        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame for runner selection and status
        left_frame = tk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right frame for stats and controls
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # -- Left Frame Widgets --
        # Title
        tk.Label(left_frame, text="Runner Selection", font=('Helvetica', 16, 'bold')).pack(pady=(0, 10))

        # Listbox for runner names
        listbox_frame = tk.Frame(left_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(listbox_frame, text="Available Runners:").pack(anchor=tk.W)
        self.runner_listbox = tk.Listbox(listbox_frame, listvariable=self.runner_list_var, height=8)
        self.runner_listbox.pack(fill=tk.BOTH, expand=True)
        self.runner_listbox.bind('<<ListboxSelect>>', self.on_runner_select)
        
        # Scrollbar for listbox
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.runner_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.runner_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(button_frame, text="Set Current Runner", command=self.on_set_runner, 
                 bg='#4CAF50', fg='white', font=('Helvetica', 12)).pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(button_frame, text="Add New Runner", command=self.on_add_runner,
                 bg='#2196F3', fg='white', font=('Helvetica', 12)).pack(fill=tk.X)
        
        # Status section
        status_frame = tk.Frame(left_frame)
        status_frame.pack(fill=tk.X)
        
        tk.Label(status_frame, text="Current Runner:", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W)
        tk.Label(status_frame, textvariable=self.current_runner_var, 
                font=('Helvetica', 18, 'bold'), fg='#FF5722').pack(anchor=tk.W)
        
        # -- Right Frame Widgets --
        # Title
        tk.Label(right_frame, text="Sprint Timer", font=('Helvetica', 24, 'bold')).pack(pady=(0, 20))
        
        # Big elapsed time display
        time_frame = tk.Frame(right_frame)
        time_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(time_frame, text="Elapsed Time:", font=('Helvetica', 16)).pack()
        tk.Label(time_frame, textvariable=self.elapsed_time_var, 
                font=('Courier', 60, 'bold'), fg='#4CAF50').pack()
        
        # Last run time display
        last_run_frame = tk.Frame(right_frame)
        last_run_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(last_run_frame, text="Last Run:", font=('Helvetica', 14)).pack()
        tk.Label(last_run_frame, textvariable=self.last_run_time_var, 
                font=('Helvetica', 24), fg='#FF9800').pack()
        
        # Reset button
        tk.Button(right_frame, text="RESET TIMER", command=self.app_callbacks['reset_timer'],
                 bg='#F44336', fg='white', font=('Helvetica', 16, 'bold'), height=2).pack(fill=tk.X, pady=(20, 0))

    def on_runner_select(self, event):
        # Logic to handle listbox selection
        # No action, just updates selection visual
        pass

    def on_set_runner(self):
        # Get selection from listbox and call the main app callback
        selection = self.runner_listbox.curselection()
        if selection:
            # Get the runner data from the listbox
            runner_data = self.runner_listbox.get(selection[0])
            # Parse the runner data (assuming format: "ID: Name")
            try:
                runner_id = int(runner_data.split(':')[0].strip())
                runner_name = runner_data.split(':', 1)[1].strip()
                self.app_callbacks['set_runner'](runner_id, runner_name)
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Invalid runner selection")

    def on_add_runner(self):
        # Use simpledialog to get a new runner name
        name = simpledialog.askstring("New Runner", "Enter runner's name:")
        if name:
            self.app_callbacks['add_runner'](name)

    def update_runner_list(self, runners):
        # runners is a list of (id, name) tuples
        # Clear and update the listbox
        self.runner_listbox.delete(0, tk.END)
        for runner_id, name in runners:
            self.runner_listbox.insert(tk.END, f"{runner_id}: {name}")

    def update_current_runner(self, name):
        self.current_runner_var.set(name)

    def update_elapsed_time(self, time_str):
        self.elapsed_time_var.set(time_str)

    def update_last_run_time(self, time_str):
        self.last_run_time_var.set(time_str)
