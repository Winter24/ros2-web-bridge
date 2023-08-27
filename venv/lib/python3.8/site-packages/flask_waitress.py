import waitress

from flask import current_app
from paste.translogger import TransLogger
from functools import partial, update_wrapper


class FlaskWaitress(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('PORT', '5000')
        app.config.setdefault('SERVER_ADDRESS', '*')
        command_func = update_wrapper(
                           partial(self.waitress_serve, app),
                           self.waitress_serve)
        app.cli.command()(command_func)

    def waitress_serve(self, app):
        port = current_app.config['PORT']
        address = current_app.config['SERVER_ADDRESS']
        bind = '{address}:{port}'.format(address=address, port=port)
        return waitress.serve(TransLogger(app), listen=bind)
