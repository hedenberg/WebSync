import os
from websync import app
from flask import redirect, request, url_for, render_template, make_response
from werkzeug import secure_filename
from websync.database import db_session
from websync.models import Blob

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route("/")
def index():
    return "Blob blob blob.. blob!"

@app.route('/blob', methods=['GET', 'POST'])
def blob():
    if request.method == 'GET':
        return render_template('sampleFileUpload.html', blobs=db_session.query(Blob).order_by(Blob.id))
    elif request.method == 'POST':
        f = request.files['blob']
        fn = secure_filename(f.filename)
        f.save('websync/blobs/' + fn)
        b = Blob(fn)
        db_session.add(b)
        db_session.commit()
        return "Upload a new blob. name:%s" % fn
@app.route('/blob/', methods=['GET', 'POST'])
def blob_redirect():
    return redirect(url_for('blob'))

@app.route('/blob/<int:blob_id>', methods=['GET', 'PUT', 'DELETE'])
def show_user_profile(blob_id):
    if request.method == 'GET':
        blob = db_session.query(Blob).get(blob_id)
        print "Blobid: %d" % blob_id
        print "Blob: id:%d, filename:%s" % (blob.id, blob.filename)
        # tell nginx to server the file and where to find it
        file_size = os.path.getsize('websync/blobs/'+blob.filename)
        print file_size
        response = make_response()
        response.headers['Pragma'] = 'public'
        response.headers['Content-Type'] = 'txt'
        response.headers['Content-Transfer-Encoding'] = 'binary'
        response.headers['Content-Description'] = 'File Transfer'
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % blob.filename
        response.headers['Content-Length'] = file_size
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
