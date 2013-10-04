from websync import app
app.debug = True
#app.host = '0.0.0.0'
app.secret_key = 'super secret developmentkey, not at all posted on github.'

port = 80
if app.debug:
	port = 5000
app.run(host = '0.0.0.0', port=port)