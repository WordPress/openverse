bind = ["0.0.0.0:8001"]
capture_output = True
chdir = "./ingestion_server/"
timeout = 120
reload = True
loglevel = "debug"
wsgi_app = "api:api"
