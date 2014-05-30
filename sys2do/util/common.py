# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-10-25
#  @author: cl.lam
#  Description:
###########################################
'''
import smtplib
import os
from email import Encoders
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header
from functools import wraps

from flask import g, request
from flask import current_app as app
from flask.templating import render_template

__all__ = ['_g', '_gs', '_gl', '_gp', '_debug', '_info', '_error',
           'templated', 'sendEmail', 'advancedSendMail']


def _g(name, default = None):
    return request.values.get(name, default) or None

def _gs(*name_list):
    return [_g(name) for name in name_list]

def _gl(name):
    return request.form.getlist(name)

def _gp(prefix):
    return sorted([(k, v or None) for k, v in request.values.items() if k.startswith(prefix)], cmp = lambda x, y: cmp(x[0], y[0]))


_debug = lambda msg : app.logger.debug(msg)

_info = lambda msg : app.logger.debug(msg)

_error = lambda msg : app.logger.debug(msg)


def templated(template = None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
#                template_name = request.endpoint.replace('.', '/') + '.html'
                template_name = "%s.html" % f.__name__
                _self = args[0]
                if getattr(_self, 'template_dir', None):
                    template_name = '%s/%s' % (_self.template_dir, template_name)

            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx

            return render_template(template_name, **ctx)
        return decorated_function
    return decorator


def sendEmail(send_from, send_to, subject, text, cc_to = [], files = [], server = "192.168.42.14"):
    assert type(send_to) == list
    assert type(files) == list

    msg = MIMEMultipart()
    msg.set_charset("utf-8")
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)

    if cc_to:
        assert type(cc_to) == list
        msg['cc'] = COMMASPACE.join(cc_to)
        send_to.extend(cc_to)

    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject.replace("\n", ' ')

    msg.attach(MIMEText(text))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        if isinstance(f, basestring):
            part.set_payload(open(f, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % Header(os.path.basename(f), 'utf-8'))
        elif hasattr(f, "file_path") and hasattr(f, "file_name"):
            part.set_payload(open(f.file_path, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % Header(f.file_name, 'utf-8'))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()



def advancedSendMail(send_from, send_to, subject, text, html, cc_to = [], files = [], server = "192.168.42.14"):
    assert type(send_to) == list
    assert type(files) == list

    if not text and not html:
        raise "No content to send!"
    elif text and not html :
        msg = MIMEText(text, "plain", _charset = 'utf-8')  # fix the default encoding problem
    elif not text and html:
        msg = MIMEText(html, "html", _charset = 'utf-8')  # fix the default encoding problem
    else:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(text, "plain", _charset = 'utf-8'))
        msg.attach(MIMEText(html, "html", _charset = 'utf-8'))

    msg.set_charset("utf-8")
    if len(files) > 0 :
        tmpmsg = msg
        msg = MIMEMultipart()
        msg.attach(tmpmsg)

    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)

    if cc_to:
        assert type(cc_to) == list
        msg['cc'] = COMMASPACE.join(cc_to)
        send_to.extend(cc_to)

    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject

    for f in files:
        part = MIMEBase('application', "octet-stream")
        if isinstance(f, basestring):
            part.set_payload(open(f, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % Header(os.path.basename(f), 'utf-8'))
        elif hasattr(f, "file_path") and hasattr(f, "file_name"):
            part.set_payload(open(f.file_path, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % Header(f.file_name, 'utf-8'))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
