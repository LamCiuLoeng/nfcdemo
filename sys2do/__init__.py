# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-10-25
#  @author: cl.lam
#  Description:
###########################################
'''
from flask import Flask, Module, request

__all__ = ["app"]

app = Flask(__name__, static_url_path = '/static')
app.config.from_object("sys2do.setting")
# app.threaded = True


# if not app.debug:
#    import logging
#    from themodule import TheHandlerYouWant
#    file_handler = TheHandlerYouWant(...)
#    file_handler.setLevel(logging.WARNING)
#    app.logger.addHandler(file_handler)

if app.config.get("LOGGING_FILE", True):
    import logging, logging.handlers
    file_handler = logging.handlers.TimedRotatingFileHandler(app.config.get("LOGGING_FILE_PATH"), when = 'D', interval = 1, backupCount = 5, encoding = "utf-8", delay = False)
    file_handler.setLevel(app.config.get("LOGGING_LEVEL"))
    file_handler.setFormatter(logging.Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Function:           %(funcName)s
    Time:               %(asctime)s
    Message:            %(message)s
    '''))
    app.logger.addHandler(file_handler)


import views.root
app.register_blueprint(views.root.bpRoot)


#===============================================================================
# import the customize filter and testing
#===============================================================================
import util.filters as filters
for f in filters.__all__ : app.jinja_env.filters[f] = getattr(filters, f)
