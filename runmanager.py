from manager import app
import sys, threading
from manager import rabbitmq
app.debug = True
app.secret_key = 'super secret developmentkey, not at all posted on github.'
port = 80
if app.debug:
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 8000
try:
    file_sync_thread=threading.Thread(target=rabbitmq.rec_update)
    file_sync_thread.setDaemon(True)
    file_sync_thread.start()
except (KeyboardInterrupt, SystemExit):
    print 'Stopped thread'
app.run(host = '0.0.0.0', port=port, use_reloader=False)