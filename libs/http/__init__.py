from .FlaskHttp import FlaskServer
from libs.Thread import threadFactory

def createFlaskApp(listener={}, root="/", **config):
    app = FlaskServer(root, **config)
    thread = threadFactory(app.run, kwargs=listener)
    app.thread = thread
    return app
