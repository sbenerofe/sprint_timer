# common/database.py
import sqlite3
from datetime import datetime
from .config import DATABASE_FILE

def initialize_db():
    """Creates the database and tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    # Runners table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Times table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            runner_id INTEGER,
            run_time REAL NOT NULL,
            run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (runner_id) REFERENCES runners (id)
        )
    ''')
    conn.commit()
    conn.close()

def add_runner(name: str) -> int:
    """Adds a new runner to the database. Returns the runner's ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO runners (name) VALUES (?)', (name,))
        runner_id = cursor.lastrowid
        conn.commit()
        return runner_id
    except sqlite3.IntegrityError:
        # Runner already exists
        cursor.execute('SELECT id FROM runners WHERE name = ?', (name,))
        return cursor.fetchone()[0]
    finally:
        conn.close()

def get_all_runners() -> list:
    """Returns a list of tuples with (id, name) for all runners."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM runners ORDER BY name')
    runners = cursor.fetchall()
    conn.close()
    return runners

def add_run_time(runner_id: int, time: float):
    """Adds a new run time for a specific runner."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO times (runner_id, run_time) VALUES (?, ?)', (runner_id, time))
    conn.commit()
    conn.close()

def get_runner_times(runner_id: int) -> list:
    """Returns all run times for a specific runner."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, run_time, run_date FROM times WHERE runner_id = ? ORDER BY run_date DESC', (runner_id,))
    times = cursor.fetchall()
    conn.close()
    return times

def delete_run_time(time_id: int):
    """Deletes a specific run time entry."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM times WHERE id = ?', (time_id,))
    conn.commit()
    conn.close()

def update_run_time(time_id: int, new_time: float):
    """Updates a specific run time entry."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE times SET run_time = ? WHERE id = ?', (new_time, time_id))
    conn.commit()
    conn.close()

def get_leaderboard_stats() -> dict:
    """
    Returns a dictionary with leaderboard statistics:
    {
        'fastest_single_run': (name, time),
        'fastest_average_time': (name, avg_time),
        'most_runs': (name, run_count),
        'top_10_fastest': [(name, time), ...]
    }
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Fastest single run
    cursor.execute('''
        SELECT r.name, t.run_time 
        FROM times t 
        JOIN runners r ON t.runner_id = r.id 
        ORDER BY t.run_time ASC 
        LIMIT 1
    ''')
    fastest_single = cursor.fetchone()
    
    # Fastest average time (minimum 3 runs)
    cursor.execute('''
        SELECT r.name, AVG(t.run_time) as avg_time, COUNT(t.id) as run_count
        FROM times t 
        JOIN runners r ON t.runner_id = r.id 
        GROUP BY r.id, r.name 
        HAVING COUNT(t.id) >= 3
        ORDER BY avg_time ASC 
        LIMIT 1
    ''')
    fastest_avg = cursor.fetchone()
    
    # Most runs
    cursor.execute('''
        SELECT r.name, COUNT(t.id) as run_count
        FROM times t 
        JOIN runners r ON t.runner_id = r.id 
        GROUP BY r.id, r.name 
        ORDER BY run_count DESC 
        LIMIT 1
    ''')
    most_runs = cursor.fetchone()
    
    # Top 10 fastest runs
    cursor.execute('''
        SELECT r.name, t.run_time 
        FROM times t 
        JOIN runners r ON t.runner_id = r.id 
        ORDER BY t.run_time ASC 
        LIMIT 10
    ''')
    top_10 = cursor.fetchall()
    
    conn.close()
    
    return {
        'fastest_single_run': fastest_single if fastest_single else (None, None),
        'fastest_average_time': fastest_avg if fastest_avg else (None, None),
        'most_runs': most_runs if most_runs else (None, None),
        'top_10_fastest': top_10
    }
