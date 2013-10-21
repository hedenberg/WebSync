import os, socket, subprocess
from manager import app
import datetime, requests
import flask
from flask import redirect, request, url_for, render_template, make_response, flash, json
from werkzeug import secure_filename
from manager.database import db_session
from manager.models import Node, Blob, VM
from manager import rabbitmq
from openstack_manager import add_instance, remove_instance, get_floating, assign_floating

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
        r = requests.get(r'http://jsonip.com')
        ip= r.json()['ip']
        #vms = [("publicvagrant",ip),("localvagrant","10.10.10.15")]
        vms = [ip, "10.10.10.15"]
        vms_db = db_session.query(VM).order_by(VM.id)
        for vm in vms_db:
            vms.append(vm.ip)
            #vms = vms+[(vm.instance, vm.ip)]
        print vms
        return render_template('show_nodes.html', nodes=db_session.query(Node).order_by(Node.id), blobs=db_session.query(Blob).order_by(Blob.id), vms=vms)
    elif request.method == 'POST':
        r = requests.get(r'http://jsonip.com')
        my_ip= r.json()['ip']
        my_ip2 = "10.10.10.15"
        ip = request.form['vms']
        port = request.form['port']
        if is_valid_port(port):
            n = Node(ip,port)
            db_session.add(n)
            db_session.commit()
            if ip==my_ip or ip==my_ip2:
                n.process_id = run_server_on_container("websync", port, ip, n.id)
                db_session.commit()
                flash('Node created.')
            else:
                print "katt"
                n.process_id = run_server_on_openstack("websync", port, ip, n.id)
                db_session.commit()
                flash('Node created.')

        return redirect(url_for('manager'))

@app.route('/node/<int:node_id>', methods=['GET', 'DELETE', 'POST'])
def show_node(node_id):
    node=db_session.query(Node).get(node_id)
    if request.method == 'GET':
        return render_template('show_node.html', node=node)
    elif request.method == 'DELETE':
        #print "Delete node"
        #print "processid: %s" % node.process_id
        r = requests.get(r'http://jsonip.com')
        my_ip= r.json()['ip']
        my_ip2 = "10.10.10.15"
        if node.ip==my_ip or node.ip==my_ip2:
            stop_docker_process(node.process_id)
        else:
            stop_docker_process_openstack(node.ip, node.process_id)
        db_session.delete(node)
        db_session.commit()
        nodes=db_session.query(Node).all()
        if len(nodes) == 0:
            blobs=db_session.query(Blob).order_by(Blob.id)
            for blob in blobs:
                db_session.delete(blob)
            db_session.commit()
            flash('All nodes gone and files removed')
        else:
            flash('Node is removed.')
        return redirect(url_for('manager'))
    elif request.method == 'POST':
        # This should totally never ever happen.. but it needs to support it, don't judge.
        flash('I think I broke something, call my mummy..')
        return render_template('show_nodes.html', node=node)

@app.route('/vms', methods=['GET', 'POST'])
def machines():
    if request.method == 'GET':
        r = requests.get(r'http://jsonip.com')
        ip= r.json()['ip']
        vms=db_session.query(VM).order_by(VM.id)
        return render_template('show_vms.html', vms=vms)
    elif request.method == 'POST':
        instance = (str(add_instance()).split(":"))[1]
        #instance = str(add_instance())
        print "instance: ", instance
        ip = get_floating() 
        assign_floating(instance, ip)
        vm = VM(ip, instance)
        db_session.add(vm)
        db_session.commit()
        flash('Instance created @',ip)
        return redirect(url_for('machines'))

@app.route('/vm/<int:vm_id>', methods=['GET','POST', 'DELETE'])
def show_vm(vm_id):
    vm=db_session.query(VM).get(vm_id)
    if request.method == 'GET':
        return redirect(url_for('machines'))
        #return render_template('show_node.html', node=node)
    elif request.method == 'DELETE':
        #send delete-thingy
        remove_instance(vm.instance,vm.ip)
        db_session.delete(vm)
        db_session.commit()
        flash('Instance is removed.')
        return redirect(url_for('machines'))
    elif request.method == 'POST':
        # This should totally never ever happen.. but it needs to support it, don't judge.
        flash('I think I broke something, call my mummy..')
        return render_template('show_nodes.html', node=node)


def run_server_on_openstack(image, port, ip, node_id):
    return subprocess.check_output(["ssh", "-i", "web_sync2.pem", "core@"+ip, "docker", "run", "-d", "-p", ":"+str(port), image, "python", "/WebSync-master/runserver.py", str(port), str(ip), str(node_id)])

def stop_docker_process_openstack(ip, process_id):
    proc_id = process_id.strip()
    return subprocess.call(["ssh", "-i", "web_sync2.pem", "core@"+ip, "docker","stop",proc_id])

# Never ever ever used. 
def create_docker_image(id):
    name = "websync"+str(id)
    subprocess.call(["sudo","docker","build","-t",name,"."])
    return name

def run_server_on_container(image, port, ip, node_id):
    print ["sudo", "docker", "run", "-d", "-p", ":"+str(port), image, "python", "/WebSync-master/runserver.py", str(port), str(ip), str(node_id)]
    return subprocess.check_output(["sudo", "docker", "run", "-d", "-p", ":"+str(port), image, "python", "/WebSync-master/runserver.py", str(port), str(ip), str(node_id)])

def stop_docker_process(process_id):
    proc_id = process_id.strip()
    return subprocess.call(["sudo","docker","stop",proc_id])

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
    if not is_unique_port(port):
        return False
    try:
        port_int = int(port)
        if ((port_int < 65536) and (port_int>0)):
            return True
        else:
            return False
    except ValueError:
        return False

def is_unique_port(port):
    #nodes=db_session.query(Node).order_by(Node.id)
    #for node in nodes:
    #    if (port == node.port):
    #        return False
    return True

#def manager_receive(msg): 
