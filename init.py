# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-10-25
#  @author: cl.lam
#  Description:
###########################################
'''
import traceback
from sys2do.model import metadata, engine, DBSession

import sys
from sys2do.model import User, NFCData, MLocation


reload(sys)
sys.setdefaultencoding('utf8')

def init():
    try:
        print "create tables"
        metadata.drop_all(engine, checkfirst = True)
        metadata.create_all(engine)

        print "insert default value"
        DBSession.add(User(name = 'demo', password = 'demo'))

        for code in range(9121, 9140):
            DBSession.add(NFCData(authcode = unicode(code), company = 'RoyalDragonVodka',
                                  serial = code - 9000,
                                  ))
        f = open('country.txt', 'r')
        cs = f.readlines()
        f.close()
        for c in cs:
            n, c, iso = c.split('|')
            DBSession.add(MLocation(name = n, iso_code = iso, code = c))

        DBSession.commit()
        print "finish init!"
    except:
        traceback.print_exc()
        DBSession.rollback()



if __name__ == '__main__':
    init()

