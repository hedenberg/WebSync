from manager import app
import sys
app.debug = True
app.secret_key = 'super secret developmentkey, not at all posted on github.'
#Andreas är sämst i halva världen.
port = 80
if app.debug:
	try:
		port = int(sys.argv[1])
	except IndexError:
		port = 8000
app.run(host = '0.0.0.0', port=port)