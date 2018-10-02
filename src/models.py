# -*- coding: utf-8 -*-
#
# Copyright 2017-2018 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


# 3rd party
from flask_login import UserMixin  # noqa : pylint: disable=import-error
from sqlalchemy import ForeignKey  # noqa : pylint: disable=import-error
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text  # noqa : pylint: disable=import-error
from sqlalchemy.orm import relationship  # noqa : pylint: disable=import-error

# self
from base import db, login_manager


# LEVEL
OWNER = 0
MEMBER = 1
TESTER = 2

class User(UserMixin, db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = 'user'

  id = Column(String(75), primary_key=True)
  email = Column(String(75), unique=True, nullable=False)
  name = Column(String(75))
  firebase_user_id = Column(String(75), unique=True)
  email_verified = Column(Boolean, default=False, nullable=False)
  sign_in_provider = Column(String(75))
  photo_url = Column(String(225))
  created_time = Column(DateTime)
  last_access_time = Column(DateTime)
  ip_address = Column(String(75))
  level = Column(Integer)

  organization_id = Column(String(75), ForeignKey('organization.id'))
  permission = relationship('Permission', uselist=False, backref='user')

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.email


@login_manager.user_loader
def user_loader(_id):
  return User.query.get(_id)


class Permission(db.Model):
  __tablename__ = 'permission'

  id = Column(String(75), primary_key=True)
  permission = Column(String(15))
  user_id = Column(String(75), ForeignKey('user.id'))


class Organization(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = 'organization'

  id = Column(String(75), primary_key=True)
  users = Column(Text)  # list, 테스트가 가능한 모든 유저
  products = Column(Text)  # list
  tokens = Column(Text)  # dict
  kinds = Column(Text)  # dict
  # ======= upper cloud data
  name = Column(String(120), unique=True)
  original_name = Column(String(120), unique=True)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)

  user_list = relationship("User", backref='organization', cascade="all, delete")
  product_list = relationship("Product", backref='organization',
                              cascade="all, delete",
                              order_by="desc(Product.last_updated_time)")
  noti_key = relationship("NotiKey", backref='organization', cascade="all, delete")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      # depending on whether value is an iterable or not, we must
      # unpack it's value (when **kwargs is request.form, some values
      # will be a 1-element list)
      if hasattr(value, '__iter__') and not isinstance(value, str):
        # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.name


# stage
STAGE_RELEASE = 0
STAGE_PRE_RELEASE = 1
STAGE_DEV = 2
STAGE_ARCHIVE = 3

# TYPE
PRD_TYPE_BLE = 0
PRD_TYPE_WEB = 1


class Product(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = 'product'

  id = Column(String(75), primary_key=True)
  code = Column(String(75))
  developer_id = Column(String(75))
  key = Column(String(75))
  name = Column(String(75))
  typ = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  organization_id = Column(String(75), ForeignKey('organization.id'))

  product_stage_list = relationship("ProductStage", backref='product', cascade="all, delete")
  tester_list = relationship("Tester", backref='product', cascade="all, delete")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      # depending on whether value is an iterable or not, we must
      # unpack it's value (when **kwargs is request.form, some values
      # will be a 1-element list)
      if hasattr(value, '__iter__') and not isinstance(value, str):
        # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.id


class ProductStage(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = 'product_stage'

  id = Column(String(75), primary_key=True)
  hook_url = Column(String(120))
  hook_client_key = Column(String(120))
  stage = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  product_id = Column(String(75), ForeignKey('product.id'))
  model_list = relationship("Model", backref='product_stage',
                            cascade="all, delete",
                            order_by="desc(Model.last_updated_time)")
  endpoint = relationship('Endpoint', uselist=False, backref='product_stage',
                          cascade="all, delete")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      # depending on whether value is an iterable or not, we must
      # unpack it's value (when **kwargs is request.form, some values
      # will be a 1-element list)
      if hasattr(value, '__iter__') and not isinstance(value, str):
        # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.id


# TYPE
MODEL_TYPE_NRF_51 = 0
MODEL_TYPE_NRF_52 = 1


class Model(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = 'model'

  id = Column(String(75), primary_key=True)
  code = Column(Integer)
  name = Column(String(75))
  typ = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  product_stage_id = Column(String(75), ForeignKey('product_stage.id'))
  firmware_list = relationship("Firmware", backref='model',
                               cascade="all, delete",
                               order_by="desc(Firmware.version)")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      # depending on whether value is an iterable or not, we must
      # unpack it's value (when **kwargs is request.form, some values
      # will be a 1-element list)
      if hasattr(value, '__iter__') and not isinstance(value, str):
        # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.id


class Endpoint(db.Model):

  __tablename__ = 'endpoint'

  id = Column(String(75), primary_key=True)
  version = Column(String(75))
  specifications = Column(Text)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75))
  product_stage_id = Column(String(75), ForeignKey('product_stage.id'))


# state
DEV_STATE = 1
PRODUCTION_STATE = 0

# platform
ANDROID = 1
IOS = 0


class NotiKey(db.Model):

  __tablename__ = 'notikey'

  id = Column(Integer, primary_key=True)
  typ = Column(Integer)
  name = Column(String(75)) # ios : bundle_id, android : package_name
  key = Column(String(225))  # ios : password, android : key
  is_dev = Column(Integer)  # only ios, 0->production, 1->dev
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75), ForeignKey('organization.id'))


class Invite(db.Model):

  __tablename__ = 'invite'

  id = Column(String(75), primary_key=True)
  email = Column(String(75))
  organization_id = Column(String(75))
  product_id = Column(String(75))
  key = Column(String(75))
  level = Column(Integer)
  invited_time = Column(DateTime)
  invited_user = Column(String(75))
  accepted = Column(Integer)
  accepted_time = Column(DateTime)


# Tester Level
TESTER_PRE_RELEASE = 1
TESTER_DEV = 2

class Tester(db.Model):

  __tablename__ = 'tester'

  id = Column(String(75), primary_key=True)
  email = Column(String(75))
  authorized = Column(Boolean, default=False)
  level = Column(Integer)
  organization_id = Column(String(75))
  product_id = Column(String(75), ForeignKey('product.id'))


FIRMWARE_RELEASE = 0
FIRMWARE_PRE_RELEASE = 1
FIRMWARE_DEV = 2
FIRMWARE_ARCHIVE = 3


class Firmware(db.Model):

  __tablename__ = 'firmware'

  id = Column(String(75), primary_key=True)
  version = Column(String(75))
  ep_version = Column(String(75))
  model_code = Column(Integer)
  path = Column(String(225))
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  model_id = Column(String(75), ForeignKey('model.id'))
