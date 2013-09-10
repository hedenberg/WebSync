from websync import app
from flask import redirect, request, url_for, render_template
from werkzeug import secure_filename

@app.route("/")
def index():
	return "Blob blob blob.. blob!"

@app.route('/blob', methods=['GET', 'POST'])
def blob():
	return "All them blobs"

@app.route('/blob/<int:blob_id>', methods=['GET', 'PUT', 'DELETE'])
def show_user_profile(blob_id):
	if request.method == 'GET':
		return 'Blob resource id %s' % blob_id
	elif request.method == 'PUT':
		return "Change that blob"
	elif request.method == 'DELETE':
		return "Delete blob"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('blobs/' + secure_filename(f.filename))
