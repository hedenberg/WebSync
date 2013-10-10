import os, socket
from manager import app
import datetime
import flask
from flask import redirect, request, url_for, render_template, make_response, flash
from werkzeug import secure_filename
from manager.database import db_session
from manager.models import Node

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

@app.route('/', methods=['GET', 'POST'])
def manager():
    if request.method == 'GET':
        return render_template('show_nodes.html', nodes=db_session.query(Node).order_by(Node.id))
    elif request.method == 'POST':
        ip = request.form['vms']
        print "ip", ip
        port = request.form['port']
        if is_valid_port(port):
            n = Node(ip+':'+port)
            db_session.add(n)
            db_session.commit()
            flash('Node created kinda.')
        return redirect(url_for('manager'))

@app.route('/node/<int:node_id>', methods=['GET', 'DELETE', 'POST'])
def show_node(node_id):
    node=db_session.query(Node).get(node_id)
    if request.method == 'GET':
        return render_template('show_node.html', node=node)
    elif request.method == 'DELETE':
        db_session.delete(node)
        db_session.commit()
        flash('Node is removed.')
        return redirect(url_for('manager'))
    elif request.method == 'POST':
        # This should totally never ever happen.. but it needs to support it, don't judge.
        flash('I think I broke something, call my mummy..')
        return render_template('show_file.html', node=node)

def is_valid_ip_and_port(ip_port):
    ip_port_split = ip_port.split(':', 1)
    ip = ip_port_split[0]
    try:
        port = ip_port_split[1]
        if is_valid_ip(ip):
            if is_valid_port(port):
                return True
            else:
                flash('Invalid port')
                return False
        else:
            flash('Invalid IP')
            return False
    except IndexError:
        flash('No Port given')
        return False
    return False

def is_valid_ip(ip):
    if ip=="localhost":
            return True
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def is_valid_port(port):
    try:
        port_int = int(port)
        if ((port_int < 65536) and (port_int>0)):
            return True
        else:
            return False
    except ValueError:
        return False