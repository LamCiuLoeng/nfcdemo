# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-10-25
#  @author: cl.lam
#  Description:
###########################################
'''
import os
import traceback
from functools import wraps


from flask import request, redirect, url_for, render_template, session, flash
from flask import current_app as app




__all__ = ['templated', 'login_required']


def templated(template = None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint.replace('.', '/') + '.html'

            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('login', None):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function
