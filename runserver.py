from websync import app
from websync import views, rabbitmq
import sys, threading
app.debug = True
app.secret_key = 'super secret developmentkey, not at all posted on github.'
port = 80
if app.debug:
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 5000
    try:
        node_ip = str(sys.argv[2])
    except IndexError:
        node_ip = "x:x:x:x"
    try:
        node_id = int(sys.argv[3])
    except IndexError:
        node_id = "1"
views.node_port = port
views.node_ip = node_ip
views.node_id = node_id
try:
    file_sync_thread=threading.Thread(target=rabbitmq.rec_manager, args=(node_id,))
    file_sync_thread.setDaemon(True)
    file_sync_thread.start()
except (KeyboardInterrupt, SystemExit):
    print 'Stopped thread'
app.run(host = '0.0.0.0', port=port, use_reloader=False)