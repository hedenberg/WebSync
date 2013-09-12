import os
from websync import app
from flask import redirect, request, url_for, render_template, make_response, flash
from werkzeug import secure_filename
from websync.database import db_session
from websync.models import Blob

# Removes database session at shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/")
def index():
    return "Blob blob blob.. blob!"

@app.route('/blob', methods=['GET', 'POST'])
def blob():
    if request.method == 'GET':
        return render_template('show_files.html', blobs=db_session.query(Blob).order_by(Blob.id))
    elif request.method == 'POST':
        # Adding a new file
        f = request.files['blob']
        fn = secure_filename(f.filename)
        # Saves the file 
        f.save('websync/blobs/' + fn)
        # Adds information about the file in the database
        b = Blob(fn)
        db_session.add(b)
        db_session.commit()
        flash('File upload successful')
        return render_template('show_files.html', blobs=db_session.query(Blob).order_by(Blob.id))

@app.route('/blob/', methods=['GET', 'POST'])
def blob_redirect():
    return redirect(url_for('blob'))

@app.route('/blob/<int:blob_id>', methods=['GET', 'PUT', 'DELETE'])
def show_user_profile(blob_id):
    if request.method == 'GET':
        # Download file!
        # Retrieve file information from database using id
        blob = db_session.query(Blob).get(blob_id)
        # Build a response that will return the file to the user
        file_size = os.path.getsize('websync/blobs/'+blob.filename)
        response = make_response()
        response.headers['Pragma'] = 'public'
        response.headers['Content-Type'] = 'txt'
        response.headers['Content-Transfer-Encoding'] = 'binary'
        response.headers['Content-Description'] = 'File Transfer'
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % blob.filename
        response.headers['Content-Length'] = file_size
        # Load file data to the response
        with open ("websync/blobs/"+blob.filename, "r") as blob_data:
            response.data = blob_data.read()
        return response
    elif request.method == 'PUT':
        return "Change that blob"
    elif request.method == 'DELETE':
        return "Delete blob"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('blobs/' + secure_filename(f.filename))
