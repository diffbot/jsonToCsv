from dotenv import load_dotenv

from flask import Flask, request, Response, jsonify, send_from_directory, make_response, session
from flask_apscheduler import APScheduler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, generate_csrf

import os
import hashlib
import time, datetime
import urllib
import json
import sqlite3
import secrets

import jsonToCsv

app = Flask(__name__)
app.config.from_object(__name__)

if APP_SECRET := os.getenv("APP_SECRET", None):
    app.secret_key = APP_SECRET
else:
    print(" * Running jsonToCsv in local mode")
    # Generate a secret key for local mode. This key will not persist between reloads.
    app.secret_key = secrets.token_hex()

# CSRF
csrf = CSRFProtect(app)

# Secure session cookies
app.config['SESSION_COOKIE_SECURE'] = True

# Really basic rate limiting to avoid taking down the app by bad actors
limiter = Limiter(
    get_remote_address, 
    app=app, 
    storage_uri='memory://'
    )

# Scheduler to Auto-Delete files in /uploads
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

@scheduler.task('cron', id='delete_uploads', minute='0', hour='*')
def delete_uploads():
    try:
        files = os.listdir('uploads')
        for file in files:
            file_path = os.path.join('uploads', file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")

# Route for Frontend
@app.route('/', defaults=dict(filename=None))
@app.route('/<path:filename>', methods=['GET'])
def index(filename):
    filename = filename or 'index.html'
    if request.method == 'GET':
        response = make_response(send_from_directory('dist', filename))
        response.set_cookie('csrftoken', generate_csrf(), secure=True)
        return response

    return jsonify(request.data)

# Validates and Expires 1 Hour Sessions
def validate_session(session_datetime, hrs=1):
    if session_datetime:
        time_elapsed = datetime.datetime.now(datetime.timezone.utc) - session_datetime
        if time_elapsed > datetime.timedelta(hours=hrs):
            return False
        else:
            return True
    else:
        return False


# Route for Convert API
@app.route('/api/convert', methods=['POST'])
@limiter.limit("1/second", error_message='Rate limit exceeded')
def convert():

    # Get Form Data
    selected_ontology_string = request.form.get('selected_ontology')
    file_name = request.form.get('file_name')
    advanced_string = request.form.get('advanced')
    if selected_ontology_string:
        selected_ontology_string = urllib.parse.unquote(selected_ontology_string)
    if not advanced_string:
        advanced = {
            "allAttributes": request.form.get('allAttributes', False)
        }
        advanced_string = json.dumps(advanced)

    # Form Step 1: Get Ontology Based on File
        # Save json_file or json_paste
        # Generate Ontology
        # Return ontology and file_name
    if not selected_ontology_string and not file_name:
        try:
            # Read and process the JSON file
            json_file = request.files.get('json_file', None)
            if json_file and json_file.filename != '' and json_file.filename.endswith('.json'):
                # Save the File
                file_name = f'{hashlib.md5(str(time.time()).encode("utf-8")).hexdigest()}_{json_file.filename}'
                file_path = os.path.join('uploads', file_name)
                json_file.save(file_path)
                response = jsonToCsv.convert_json_to_csv(file_path, advanced_string=advanced_string)
                response.update({'file_name': file_name})
                session['guestbook_available'] = datetime.datetime.now(datetime.timezone.utc)
                return jsonify(response)
            elif request.form.get('json_paste', None):
                response = jsonToCsv.convert_json_to_csv(False, json_paste=request.form['json_paste'], advanced_string=advanced_string)
                session['guestbook_available'] = datetime.datetime.now(datetime.timezone.utc)
                return jsonify(response)
            else:
                return jsonify({"error": "No JSON attached", "code": 400}), 400
        except Exception as e:
            return jsonify({"error": str(e), "code": 400}), 400
    # Form Step 2: Use Selected Ontology and File Path to Generate CSV
        # Parse selected ontology and file path
        # Check if file exists
        # Generate CSV based on selected ontology and file path
        # Return CSV as stream
    else:
        file_path = os.path.join('uploads', file_name)
        file_exists = os.path.isfile(file_path)
        if file_exists:
            response = Response(jsonToCsv.convert_json_to_csv(file_path, selected_ontology_string=selected_ontology_string, advanced_string=advanced_string), mimetype='text/csv')
            response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
            return response
        elif request.form.get('json_paste', None):
            response = Response(jsonToCsv.convert_json_to_csv(False, json_paste=request.form['json_paste'], selected_ontology_string=selected_ontology_string, advanced_string=advanced_string), mimetype='text/csv')
            response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
            return response
        else:
            return jsonify({"error": "Unknown Error", "code": 400}), 400

    return jsonify({"error": "Unsupported file type", "code": 400}), 400

# Instantiates Guestbook DB
def get_db_connection():
    conn = sqlite3.connect('guestbook.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route for Guestbook API
@app.route('/api/guestbook', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'GET':
        if validate_session(session.get('guestbook_available', None), hrs=1):
            try:
                conn = get_db_connection()
                results = conn.execute('SELECT author, created, location, message FROM posts ORDER BY created DESC LIMIT 10').fetchall()
                conn.close()
                posts = [dict(row) for row in results]
                return jsonify({"posts": posts})
            except Exception as e:
                print(e)
                return jsonify({"success": True})
        else:
            return jsonify({"success": True})
    elif request.method == 'POST':
        author = request.form.get('name', 'Anonymous')
        location = request.form.get('location', '')
        message = request.form.get('message')

        if not author:
            author = "Anonymous"

        if not location:
            location = "Somewhere"

        if not message:
            return jsonify({"error": "You silly goose! You have to write a note to sign the guestbook.", "code": 400}), 400
        elif validate_session(session.get('guestbook_posted', None), hrs=168):
            return jsonify({"error": "You've already signed the guestbook!", "code": 403}), 403
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (author, location, message) VALUES (?, ?, ?)',
                         (author, location, message))
            conn.commit()
            conn.close()
            session['guestbook_posted'] = datetime.datetime.now(datetime.timezone.utc)
            return jsonify({"success": True})

if __name__ == '__main__':
    app.run()