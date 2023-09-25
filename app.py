from flask import Flask, request, Response, jsonify, send_from_directory
from flask_apscheduler import APScheduler

import os
import hashlib
import time
import urllib
import json

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
                return jsonify(response)
            elif request.form.get('json_paste', None):
                response = jsonToCsv.convert_json_to_csv(False, json_paste=request.form['json_paste'], advanced_string=advanced_string)
                return jsonify(response)
            else:
                return jsonify({"error": "No JSON attached"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400
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
            return jsonify({"error": "Unknown Error"}), 400


    return jsonify({"error": "Unsupported file type"}), 400

if __name__ == '__main__':
    app.run()