# -*- coding: utf-8 -*-
from flask.views import View
from flask.helpers import url_for
from sys2do import app
from sys2do.model import DBSession


__all__ = ['BasicView']



class BasicView(View):
    methods = ['GET', 'POST']
#    decorators = [login_required]

    def default(self):  return url_for('.view', action = 'index')

    def dispatch_request(self, action):
        return getattr(self, action)()



'''
@app.before_request
def before_request():  #occur before the request
    from sys2do.util.common import _debug
    pass




@app.teardown_request
def teardown_request(exception):  #if error occur on the controller
    from sys2do.util.common import _debug
    if exception is not None:
        _debug("--------come into teardown_request")
        DBSession.rollback()


@app.after_request
def after_request(response):  #if error occur on the controller
    from sys2do.util.common import _debug
    return response
'''