# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-10-25
#  @author: cl.lam
#  Description:
###########################################
'''
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#from flup.server.fcgi import WSGIServer
from sys2do import app


if __name__ == '__main__':
    app.run(host = 'localhost', port = 9000, threaded = True)

#    WSGIServer(app, bindAddress = ("localhost", 8001)).run()
