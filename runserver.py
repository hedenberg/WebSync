from websync import app
from websync import views
import sys
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
app.run(host = '0.0.0.0', port=port, use_reloader=False)