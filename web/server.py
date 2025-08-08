# web/server.py
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from common import database

app = Flask(__name__)
auth = HTTPBasicAuth()

# Admin credentials
ADMIN_USERS = {
    "admin": "supersecret"
}

@auth.verify_password
def verify_password(username, password):
    if username in ADMIN_USERS and ADMIN_USERS[username] == password:
        return username

# --- Public/Fan Routes ---
@app.route('/')
def fan_view():
    return render_template('fan_view.html')

@app.route('/api/live_data')
def live_data():
    """API endpoint for live data polling by the fan view."""
    # Get shared data from the main application
    shared_data = app.config.get('SHARED_DATA', {})
    return jsonify({
        'current_runner': shared_data.get('current_runner', 'N/A'),
        'elapsed_time': shared_data.get('elapsed_time', '0.00'),
        'last_run': shared_data.get('last_run', {'name': 'N/A', 'time': 0.0}),
        'timing_mode': shared_data.get('timing_mode', 'SYSTEM'),
        'gps_status': shared_data.get('gps_status', 'UNKNOWN')
    })

@app.route('/api/stats')
def stats():
    """API endpoint for fetching all stats."""
    stats_data = database.get_leaderboard_stats()
    return jsonify(stats_data)

@app.route('/api/timing_status')
def timing_status():
    """API endpoint for timing system status."""
    shared_data = app.config.get('SHARED_DATA', {})
    return jsonify({
        'timing_mode': shared_data.get('timing_mode', 'SYSTEM'),
        'gps_status': shared_data.get('gps_status', 'UNKNOWN'),
        'precision': 'nanosecond' if shared_data.get('timing_mode') in ['GPS', 'WIRED'] else 'millisecond'
    })

# --- Admin Routes ---
@app.route('/admin')
@auth.login_required
def admin_dashboard():
    # Fetch all runners and their times for display
    runners = database.get_all_runners()
    # For each runner, fetch their times
    runner_data = []
    for runner_id, name in runners:
        times = database.get_runner_times(runner_id)
        runner_data.append({
            'id': runner_id,
            'name': name,
            'times': times
        })
    return render_template('admin.html', all_data=runner_data)

@app.route('/admin/update_time', methods=['POST'])
@auth.login_required
def admin_update_time():
    data = request.json
    database.update_run_time(data['id'], data['time'])
    return jsonify({'status': 'success'})

@app.route('/admin/delete_time', methods=['POST'])
@auth.login_required
def admin_delete_time():
    data = request.json
    database.delete_run_time(data['id'])
    return jsonify({'status': 'success'})

def run_server(shared_data_object):
    """
    Function to be run in a separate thread from main_app.py
    The shared_data_object will be used to pass live data from the main app.
    """
    # Make shared_data_object accessible to routes
    app.config['SHARED_DATA'] = shared_data_object
    app.run(host='0.0.0.0', port=80, debug=False)
