# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-10-25
#  @author: cl.lam
#  Description:
###########################################
'''
import os
from sqlalchemy.types import Integer, Text
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import relation


from sys2do.model import DeclarativeBase, metadata, DBSession
from sys2do.setting import UPLOAD_FOLDER_PREFIX


class MLocation(DeclarativeBase):
    __tablename__ = 'master_location'

    id = Column(Integer, autoincrement = True, primary_key = True)
    name = Column(Text)
    iso_code = Column(Text)
    code = Column(Text)
    active = Column(Integer, default = 0)

    def __repr__(self): return self.name
    def __str__(self): return self.name
    def __unicode__(self): return self.name


class FileObj(DeclarativeBase):
    __tablename__ = 'file_object'

    id = Column(Integer, autoincrement = True, primary_key = True)
    name = Column(Text)
    path = Column(Text)
    url = Column(Text)
    size = Column(Integer, default = None)
    type = Column(Text)
    remark = Column(Text)

    @property
    def real_path(self):
        return os.path.join(UPLOAD_FOLDER_PREFIX, self.path)



class NFCData(DeclarativeBase):
    __tablename__ = 'nfc_data'

    id = Column(Integer, autoincrement = True, primary_key = True)

    authcode = Column(Text)
    company = Column(Text)
    serial = Column(Integer)
    system_no = Column(Text, default = None)

    registration_date = Column(Text, default = None)
    registered_to_first = Column(Text, default = None)
    registered_to_last = Column(Text, default = None)
    email_address = Column(Text, default = None)
    birthday = Column(Text)
    location_id = Column(Integer, ForeignKey('master_location.id'))
    location = relation(MLocation)
    purchase_place = Column(Text)
    certificate_id = Column(Integer, ForeignKey('file_object.id'))
    certificate = relation(FileObj)
    active = Column(Integer, default = 0)

