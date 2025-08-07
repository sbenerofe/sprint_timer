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
    # This needs to get data from the main application.
    # We will solve this by having the main app update a global or shared object.
    # For now, placeholder:
    return jsonify({
        'current_runner': 'Runner A',
        'elapsed_time': '1.23',
        'last_run': {'name': 'Runner B', 'time': 4.56}
    })

@app.route('/api/stats')
def stats():
    """API endpoint for fetching all stats."""
    stats_data = database.get_leaderboard_stats()
    return jsonify(stats_data)

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
