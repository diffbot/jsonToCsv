from flask import Flask, request, Response, jsonify, send_from_directory
from flask_apscheduler import APScheduler

import os
import hashlib
import time

import jsonToCsv

app = Flask(__name__)
app.config.from_object(__name__)

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
        return send_from_directory('dist', filename)

    return jsonify(request.data)

# Route for Convert Backend
@app.route('/api/convert', methods=['POST'])
def convert():
    # Check if the POST request has the file part
    if 'json_file' not in request.files:
        return jsonify({"error": "No JSON file attached"}), 400

    # Read and process the JSON file
    json_file = request.files['json_file']
    if json_file and json_file.filename != '' and json_file.filename.endswith('.json'):
        # Save the File
        file_path = os.path.join('uploads', f'{hashlib.md5(str(time.time()).encode("utf-8")).hexdigest()}_{json_file.filename}')
        json_file.save(file_path)
        # Convert the File
        response = Response(jsonToCsv.convert_json_to_csv(file_path), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
        return response
    elif 'json_paste' in request.form:
        # Convert the File
        response = Response(jsonToCsv.convert_json_to_csv(False, json_paste=request.form['json_paste']), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
        return response

    return jsonify({"error": "Unsupported file type"}), 400

if __name__ == '__main__':
    app.run()