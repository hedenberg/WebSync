from websync import app, setPort
import sys
app.debug = True
app.secret_key = 'super secret developmentkey, not at all posted on github.'
port = 80
if app.debug:
	try:
		port = int(sys.argv[1])
	except IndexError:
		port = 5000
setPort(port)
app.run(host = '0.0.0.0', port=port, use_reloader=False)