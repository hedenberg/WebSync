import os
from websync import app
import datetime
import flask
from flask import redirect, request, url_for, render_template, make_response, flash
from werkzeug import secure_filename
from websync.database import db_session
from websync.models import Blob
from websync.rabbitmq import emit_log, receive_logs

# Removes database session at shutdown
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Fix for custom HTTP methods
# http://flask.pocoo.org/snippets/1/
@app.before_request
def before_request():
    method = request.form.get('_method', '').upper()
    if method:
        request.environ['REQUEST_METHOD'] = method
        ctx = flask._request_ctx_stack.top
        ctx.url_adapter.default_method = method
        assert request.method == method

@app.route('/blob', methods=['GET', 'POST'])
def blob():
    if request.method == 'GET':
        return render_template('show_files.html', blobs=db_session.query(Blob).order_by(Blob.id))
    elif request.method == 'POST':
        # Adding a new file
        f = request.files['blob']
        fn = secure_filename(f.filename)
        # Saves the file 
        try:
            f.save('websync/blobs/' + fn)
        except Exception, e:
            f.save('/WebSync-master/websync/blobs/' + fn)
        # Adds information about the file in the database
        b = Blob(fn)
        db_session.add(b)
        db_session.commit()
        flash('File upload successful.')
        return redirect(url_for('blob'))
        #return render_template('show_files.html', blobs=db_session.query(Blob).order_by(Blob.id))

# Right as diverse pathes leden the folk the righte wey to Rome.
@app.route("/")
def index():
    return redirect(url_for('blob'))

@app.route('/blob/', methods=['GET', 'POST'])
def blob_redirect():
    return redirect(url_for('blob'))

@app.route('/blob/<int:blob_id>', methods=['GET', 'PUT', 'DELETE', 'POST'])
def show_blob(blob_id):
    blob=db_session.query(Blob).get(blob_id)
    if request.method == 'GET':
        return render_template('show_file.html', blob=blob)
    elif request.method == 'PUT':
        # Adding a new file
        fn = blob.filename
        f = request.files['blob']
        fn_new = secure_filename(f.filename)
        if not fn == fn_new:
            flash('File name not the same')
            return render_template('show_file.html', blob=blob)
        else:
            
            try:
                # Delete old file
                os.remove("websync/blobs/%s"%fn)
                f.save('websync/blobs/' + fn)
            except Exception, e:
                os.remove("/WebSync-master/websync/blobs/%s"%fn)
                f.save('/WebSync-master/websync/blobs/' + fn)

            # Adds information about the file in the database
            blob.last_change = datetime.datetime.now()
            flash('File update successful.')
            return render_template('show_file.html', blob=blob)
    elif request.method == 'DELETE':
        try:
            os.remove("websync/blobs/%s"%blob.filename)
        except Exception, e:
            os.remove("/WebSync-master/websync/blobs/%s"%blob.filename)
        db_session.delete(blob)
        db_session.commit()
        flash('File is removed.')
        return redirect(url_for('blob'))
    elif request.method == 'POST':
        # This should totally never ever happen.. but it needs to support it, don't judge.
        flash('I think I broke something, call my mummy..')
        return render_template('show_file.html', blob=db_session.query(Blob).get(blob_id))

@app.route('/blob/<int:blob_id>/download', methods=['GET'])
def dowload_blob(blob_id):
    if request.method == 'GET':
        # Download file!
        # Retrieve file information from database using id
        blob = db_session.query(Blob).get(blob_id)
        # Build a response that will return the file to the user
        try:
            file_size = os.path.getsize('websync/blobs/'+blob.filename)
        except Exception, e:
            file_size = os.path.getsize('/WebSync-master/websync/blobs/'+blob.filename)
        #file_size = os.path.getsize('WebSync-master/websync/blobs/'+blob.filename)
        #file_size = os.path.getsize('websync/blobs/'+blob.filename)
        
        response = make_response()
        response.headers['Pragma'] = 'public'
        response.headers['Content-Type'] = 'txt'
        response.headers['Content-Transfer-Encoding'] = 'binary'
        response.headers['Content-Description'] = 'File Transfer'
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % blob.filename
        response.headers['Content-Length'] = file_size
        # Load file data to the response
        try:    
            with open ("websync/blobs/"+blob.filename, "r") as blob_data:
                response.data = blob_data.read()
        except Exception, e:
            with open ("/WebSync-master/websync/blobs/"+blob.filename, "r") as blob_data:
                response.data = blob_data.read()
        return response

