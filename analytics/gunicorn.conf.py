bind = ["0.0.0.0:8090"]
capture_output = True
chdir = "./analytics/"
timeout = 120
reload = True
loglevel = "debug"
wsgi_app = "server:api"
