from websync import app
app.debug = True
app.secret_key = 'super secret developmentkey, not at all posted on github.'
app.run()