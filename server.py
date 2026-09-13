import os
from flask import Flask, request, jsonify, render_template_string, redirect

app = Flask(__name__)

# CONFIGURATION
DASHBOARD_PASSWORD = "MySuperSecretPassword123"  # Your access password
LOG_FILE_PATH = "saved_logs.txt"

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>log-IRQ Private Dashboard</title>
    <style>
        body { font-family: sans-serif; margin: 40px; background-color: #0e1117; color: #c9d1d9; }
        .container { max-width: 800px; margin: 0 auto; background: #161b22; padding: 30px; border-radius: 8px; border: 1px solid #30363d; }
        .header-section { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; padding-bottom: 10px; margin-bottom: 20px; }
        h1 { color: #58a6ff; margin: 0; }
        .log-entry { background: #0d1117; padding: 15px; border-radius: 6px; margin-bottom: 12px; font-family: monospace; border-left: 4px solid #238636; white-space: pre-wrap; color: #e6edf3; }
        .login-box { text-align: center; margin-top: 50px; }
        input[type="password"] { padding: 10px; font-size: 16px; border-radius: 4px; border: 1px solid #30363d; background: #0d1117; color: white; margin-right: 10px; }
        .btn { padding: 10px 20px; font-size: 14px; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-weight: bold; }
        .btn-primary { background: #238636; }
        .btn-primary:hover { background: #2ea043; }
        .btn-danger { background: #da3637; }
        .btn-danger:hover { background: #f85149; }
        .error { color: #f85149; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        {% if authenticated %}
            <div class="header-section">
                <h1>🔒 log-IRQ Private Logs</h1>
                <form method="POST" action="/clear-logs">
                    <input type="hidden" name="auth_password" value="{{ password_token }}">
                    <input type="submit" class="btn btn-danger" value="Clear Logs">
                </form>
            </div>
            <p>Displaying all text submissions captured by the server:</p>
            {% if logs_list %}
                {% for log in logs_list %}
                    <div class="log-entry">{{ log }}</div>
                {% endfor %}
            {% else: %}
                <p style="color: #8b949e;">No logs captured yet.</p>
            {% endif %}
        {% else: %}
            <div class="login-box">
                <h2>log-IRQ Portal</h2>
                <p>Please enter the password to view the logged results.</p>
                {% if error %}<p class="error">{{ error }}</p>{% endif %}
                <form method="POST" action="/dashboard">
                    <input type="password" name="password" placeholder="Enter Password" required>
                    <input type="submit" class="btn btn-primary" value="Unlock">
                </form>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return "<h1>log-IRQ Server is Online 🟢</h1><p>To view your logs, navigate to <a href='/dashboard'>/dashboard</a></p>"

@app.route('/api/v1/log', methods=['POST'])
def receive_log():
    incoming_payload = request.get_json(force=True, silent=True)
    if not incoming_payload or 'content' not in incoming_payload:
        return jsonify({"status": "error"}), 400
        
    raw_text = incoming_payload['content']
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{raw_text}\n---\n")
        
    return jsonify({"status": "success"}), 200

@app.route('/dashboard', methods=['GET', 'POST'])
def view_dashboard():
    error = None
    authenticated = False
    password_token = ""
    logs_list = []

    if request.method == 'POST':
        user_pwd = request.form.get('password')
        if user_pwd == DASHBOARD_PASSWORD:
            authenticated = True
            password_token = DASHBOARD_PASSWORD
        else:
            error = "Invalid Password. Access Denied."

    if authenticated or request.args.get('view') == 'true':
        authenticated = True
        password_token = DASHBOARD_PASSWORD
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                logs_list = [log.strip() for log in f.read().split('---\n') if log.strip()]

    return render_template_string(DASHBOARD_TEMPLATE, authenticated=authenticated, logs_list=logs_list, error=error, password_token=password_token)

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    if request.form.get('auth_password') == DASHBOARD_PASSWORD:
        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)
    return redirect('/dashboard?view=true')
