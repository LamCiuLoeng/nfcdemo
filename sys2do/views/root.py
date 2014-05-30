# -*- coding: utf-8 -*-
import traceback
import os
import random
from datetime import datetime as dt, timedelta
import subprocess
import urllib
import platform

from flask import g, render_template, flash, session, redirect, url_for, request
from flask.blueprints import Blueprint
from flask.views import View
from flask.helpers import send_file

from sqlalchemy.sql.expression import select
from sqlalchemy import and_

from sys2do import app
from sys2do.model import DBSession

from sys2do.util.decorator import templated, login_required
from sys2do.util.common import _g, _gp, _gl, _info, _error, _debug, _gs, \
    sendEmail, advancedSendMail

from sys2do.views import BasicView
from sys2do.model import User, NFCData, MLocation, FileObj
from sys2do.setting import TEMPLATE_FOLDER, WEBSITE_HOST, UPLOAD_FOLDER_PREFIX, \
    TMP_FOLDER, UPLOAD_FOLDER_URL, UPLOAD_FOLDER


__all__ = ['bpRoot']

bpRoot = Blueprint('bpRoot', __name__)


MSG_TYPE_INFO = 'INFO'
MSG_TYPE_WARN = 'WARNING'
MSG_TYPE_ERROR = 'ERROR'


class RootView(BasicView):


    def index(self):
        code = _g('code')
        if not code :
            return render_template('result.html', msg = 'No auth code supplied!', msg_type = MSG_TYPE_WARN)

        q = DBSession.query(NFCData).filter(NFCData.authcode == code)

        if q.count() != 1:
            return render_template('result.html', msg = 'The auth code does not exist!', msg_type = MSG_TYPE_WARN)
        r = q.one()
        if r.registration_date:
            return render_template('result.html',
                                   msg = 'The auth code has been registered!',
                                   msg_type = MSG_TYPE_INFO,
                                   obj = r)
        else:
            ls = DBSession.query(MLocation).filter(and_(MLocation.active == 0)).order_by(MLocation.name)
            return render_template('form.html', obj = r, locations = ls)



    def s(self):
        _debug('come into save')
        id, registered_to_first, registered_to_last, email, birthday_y, birthday_m, birthday_d, location_id, purchase_place = _gs('id', 'registered_to_first', 'registered_to_last', 'email', 'birthday_y', 'birthday_m', 'birthday_d', 'location_id', 'purchase_place')

        if not all([id, registered_to_first, registered_to_last, email, birthday_y, birthday_m, location_id]):
            return render_template('result.html', msg = 'Not all the info is supplied!', msg_type = MSG_TYPE_WARN)

        try:
            r = DBSession.query(NFCData).get(id)
            r.system_no = self._assign_no()
            r.registration_date = dt.now().strftime('%Y-%m-%d')
            r.registered_to_first = registered_to_first
            r.registered_to_last = registered_to_last
            r.email_address = email
            r.birthday = '%s-%s-%s' % (birthday_y , birthday_m , birthday_d)
            r.location_id = location_id
            r.purchase_place = purchase_place

            _debug('go to certificate')

            f = self._create_certificate(r)
            if not f : raise Exception('Error when creating certificate')
            self._send_email(r, f)

            DBSession.commit()
            return render_template('result.html',
                                   msg = 'Update the record successfully!',
                                   msg_type = MSG_TYPE_INFO,
                                   obj = r)
        except:
            traceback.print_exc()
            DBSession.rollback()
            return render_template('result.html', msg = 'Error occur on the server side!', msg_type = MSG_TYPE_ERROR)


    @templated('certificate.html')
    def c(self):
        _debug('come into C')
        nf, nl, d, c, s = _gs('nf', 'nl', 'd', 'c', 's')
        return {'registered_to_first' : nf,
                'registered_to_last' : nl,
                'registration_date' :d,
                'system_no' : c,
                'serial' : s}


    def _assign_no(self):
        _debug('come into assign no')
        return '%s%.4d' % (dt.now().strftime("%Y%m%d%H%M%S"), random.randint(1, 10000))


    def _create_certificate(self, nfcdata):
        _debug('come into certificate')

        try:
            params = {
                      'nf' : nfcdata.registered_to_first,
                      'nl' : nfcdata.registered_to_last,
                      'd' : nfcdata.registration_date,
                      'c' : nfcdata.system_no,
                      's' : nfcdata.serial,
                      }
            url = '%s/c?%s' % (WEBSITE_HOST, urllib.urlencode(params))

            file_dir = os.path.join(UPLOAD_FOLDER_PREFIX, UPLOAD_FOLDER)
            if not os.path.exists(file_dir):    os.makedirs(file_dir)
            filename = '%s_%s.pdf' % (dt.now().strftime("%Y%m%d%H%M%S"), random.randint(1, 1000))
            f = os.path.join(file_dir, filename)


            (bit, os_type) = platform.architecture()
            snapshotjs = os.path.join(UPLOAD_FOLDER_PREFIX, 'static', 'tools', 'phantomjs', 'cert.js')
            snapshotjs = snapshotjs.replace('\\', '/')


            if os_type.startswith('Windows'):
                phantomjs = os.path.join(UPLOAD_FOLDER_PREFIX, 'static', 'tools', 'phantomjs', 'phantomjs.exe')
                phantomjs = phantomjs.replace('\\', '/')
                cmd = "%s %s %s %s" % (phantomjs, snapshotjs, url, f)
            else:
                phantomjs = os.path.join(UPLOAD_FOLDER_PREFIX, 'static', 'tools', 'phantomjs', 'phantomjs')
                cmd = "%s %s '%s' %s" % (phantomjs, snapshotjs, url, f)

            _debug(phantomjs)
            _debug(snapshotjs)

            _debug(cmd)

            # Usage: phantomjs.exe snapshot.js URL positions   img_dir
            if os_type.startswith('Windows'):
                sp = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            else:
                sp = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
            while 1:
                if sp.poll() is not None: break
            _debug('finish the PDF')
            fileobj = FileObj(name = filename,
                              path = os.path.join(UPLOAD_FOLDER, filename),
                              url = '%s/%s' % (UPLOAD_FOLDER_URL, filename),
                              size = os.path.getsize(f),
                              type = 'PDF',
                              )
            DBSession.add(fileobj)
            return fileobj
        except:
            traceback.print_exc()
            return None


    def _send_email(self, nfcdata, certificate):
        _debug('come to send email')

        try:
            send_from = 'r-track@r-pac.com.hk'
            send_to = [nfcdata.email_address]
            subject = 'Register Successfully'

            class DTO(object): pass
            k = DTO()
            k.file_path = certificate.real_path
            k.file_name = 'certificate.pdf'
            files = [k, ]
            template = os.path.join(TEMPLATE_FOLDER, 'email.html')
            f = open(template)
            content = "".join(f.readlines())
            f.close()
            html = content % (nfcdata.registration_date, '%s %s' % (nfcdata.registered_to_first, nfcdata.registered_to_last),
                              nfcdata.email_address,
                              nfcdata.birthday, nfcdata.location, nfcdata.purchase_place, nfcdata.system_no)
            advancedSendMail(send_from = send_from, send_to = send_to, subject = subject,
                             text = None, html = html, files = files)
            return True
        except:
            traceback.print_exc()
            return False


    @templated('login.html')
    def login(self):
        pass


    def check_login(self):
        try:
            u = DBSession.query(User).filter(and_(User.active == 0, User.name == _g('name'))).one()
        except:
            _error(traceback.print_exc())
            return redirect('/login?errorcode=1')
        else:
            if not _g('password'):
                return redirect('/login?errorcode=2')

            if not u.validate_password(_g('password')):
                return redirect('/login?errorcode=3')
            else:
                # fill the info into the session
                session['login'] = True
                session['user_profile'] = u.populate()
                permissions = set()
                for g in u.groups:
                    for p in g.permissions:
                        permissions.add(p.name)
                session['user_profile']['groups'] = [g.name for g in u.groups]
                session['user_profile']['permissions'] = list(permissions)
                u.last_login = dt.now()
                session.permanent = True
                DBSession.commit()
                return redirect('/report')


    def logout(self):
        session.pop('login', None)
        session.pop('user_profile', None)
        return redirect('/login')



    @login_required
    @templated('report.html')
    def report(self):
        subq = select([MLocation.name, MLocation.id]).where(and_(MLocation.active == 0)).alias()
        data = DBSession.query(NFCData, subq.c.name).outerjoin((subq, subq.c.id == NFCData.location_id)).filter(and_(NFCData.active == 0)).order_by(NFCData.authcode)
        return {'data' : data}

    @login_required
    def export(self):
        subq = select([MLocation.name, MLocation.id]).where(and_(MLocation.active == 0)).alias()
        data = DBSession.query(NFCData, subq.c.name).outerjoin((subq, subq.c.id == NFCData.location_id)).filter(and_(NFCData.active == 0)).order_by(NFCData.authcode)

        from openpyxl import Workbook
        wb = Workbook(optimized_write = True)
        ws = wb.create_sheet()
        ws.append(['AuthCode', 'Company', 'Serial', 'Registration Date', 'Registered To', 'E-mail Address', 'Birthday', 'Location', 'Purchase Place'])
        for (nfc, n) in data :
            ws.append(map(lambda v: v or '', [nfc.authcode, nfc.company, nfc.serial, nfc.registration_date, '%s %s' % (nfc.registered_to_first or '', nfc.registered_to_last or ''),
                       nfc.email_address, nfc.birthday, n, nfc.purchase_place]))

        if not os.path.exists(TMP_FOLDER): os.makedirs(TMP_FOLDER)
        current = dt.now()
        tempFileName = os.path.join(TMP_FOLDER, "report_tmp_%s_%d.xlsx" % (current.strftime("%Y%m%d%H%M%S"), random.randint(0, 1000)))

        wb.save(tempFileName)
        return send_file(tempFileName, as_attachment = True)


bpRoot.add_url_rule('/', view_func = RootView.as_view('view'), defaults = {'action':'index'})
bpRoot.add_url_rule('/<action>', view_func = RootView.as_view('view'))
