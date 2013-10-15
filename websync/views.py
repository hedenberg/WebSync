import os
import sys
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
        # Adds information about the file in the database
        f_size = sys.getsizeof(f) 
        f_blob = f.read()
        b = Blob(fn,f_blob, f_size)
        db_session.add(b)
        db_session.commit()
        flash('File upload successful.')
        return redirect(url_for('blob'))

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
            # Adds information about the file in the database
            f_size = sys.getsizeof(f) 
            f_blob = f.read()
            blob.last_change = datetime.datetime.now()
            blob.lob = f_blob
            blob.file_size = f_size
            flash('File update successful.')
            return render_template('show_file.html', blob=blob)
    elif request.method == 'DELETE':
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
        response = make_response()
        response.headers['Pragma'] = 'public'
        response.headers['Content-Type'] = 'txt'
        response.headers['Content-Transfer-Encoding'] = 'binary'
        response.headers['Content-Description'] = 'File Transfer'
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % blob.filename
        response.headers['Content-Length'] = blob.file_size
        response.data = blob.lob
        return response

