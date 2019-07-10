
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


class _Organization(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = '_organization'

  id = Column(String(75), primary_key=True)
  users = Column(Text)  # list, 테스트가 가능한 모든 유저
  products = Column(Text)  # list
  tokens = Column(Text)  # dict
  kinds = Column(Text)  # dict
  # ======= upper cloud data
  name = Column(String(120), unique=True)
  topside_logo_path = Column(String(225))
  original_name = Column(String(120), unique=True)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)

  user_list = relationship("_User", backref='organization', cascade="all, delete")
  product_list = relationship("_Product", backref='organization',
                              cascade="all, delete",
                              order_by="desc(_Product.last_updated_time)")
  noti_key = relationship("_NotiKey", backref='organization', cascade="all, delete")
  domain_list = relationship("_Domain", backref='organization', cascade="all, delete")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.name


# User LEVEL
OWNER = 0
MEMBER = 1
TESTER = 2

# level
SK_ADMIN = 0
SK_NORMAL = 1
SK_HQ = 3
ADNOC_SITE = 4
ADNOC_HQ = 5
MOI = 6


class _User(UserMixin, db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = '_user'

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

  organization_id = Column(String(75), ForeignKey('_organization.id'))

  permission = relationship('_Permission', uselist=False, backref='user')

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.email


@login_manager.user_loader
def user_loader(_id):
  return _User.query.get(_id)


class _Permission(db.Model):
  __tablename__ = '_permission'

  id = Column(String(75), primary_key=True)
  permission = Column(String(15))

  user_id = Column(String(75), ForeignKey('_user.id'))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


# state
DEV_STATE = 1
PRODUCTION_STATE = 0

# platform
ANDROID = 1
IOS = 0


class _NotiKey(db.Model):

  __tablename__ = '_notikey'

  id = Column(String(75), primary_key=True)
  typ = Column(Integer)
  name = Column(String(75)) # ios : bundle_id, android : package_name
  key = Column(String(225))  # ios : password, android : key
  is_dev = Column(Integer)  # only ios, 0->production, 1->dev
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75), ForeignKey('_organization.id'))
  permission_list = relationship("_NkModelPermission", backref='notikey',
                                 cascade="all, delete")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


# stage
STAGE_RELEASE = 0
STAGE_PRE_RELEASE = 1
STAGE_DEV = 2

# TYPE
PRD_TYPE_BLE = 0
PRD_TYPE_WEB = 1


class _Product(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = '_product'

  id = Column(String(75), primary_key=True)
  code = Column(String(75))
  developer_id = Column(String(75))
  key = Column(String(75))
  name = Column(String(75))
  parent_product_id = Column(String(75))
  typ = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  organization_id = Column(String(75), ForeignKey('_organization.id'))

  model_list = relationship('_Model', backref='product', cascade="all, delete",
                            order_by="desc(_Model.last_updated_time)")
  endpoint_list = relationship('_Endpoint', backref='product', cascade="all, delete",
                               order_by="desc(_Endpoint.last_updated_time)")
  tester_list = relationship('_Tester', backref='product', cascade="all, delete")
  history_list = relationship('_History', backref='product', cascade="all, delete",
                              order_by="desc(_History.last_updated_time)")
  subdomain_list = relationship('_SubDomain', backref='product', cascade="all, delete",
                                order_by="desc(_SubDomain.created_time)")
  forkproduct_list = relationship('_ForkProduct', backref='product', cascade="all, delete")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.id


class _ForkProduct(db.Model):

  __tablename__ = '_forkproduct'

  id = Column(String(75), primary_key=True)
  model_id = Column(String(75))
  target_email = Column(String(75))
  target_organization = Column(String(75))
  key = Column(String(75))
  sent_user = Column(String(75))
  accepted_user = Column(String(75))
  created_time = Column(DateTime)
  accepted_time = Column(DateTime)
  product_id = Column(String(75), ForeignKey('_product.id'))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.id


class _Endpoint(db.Model):

  __tablename__ = '_endpoint'

  id = Column(String(75), primary_key=True)
  version = Column(String(75))
  specifications = Column(Text)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75))
  product_id = Column(String(75), ForeignKey('_product.id'))


# Tester Level
TESTER_PRE_RELEASE = 1
TESTER_DEV = 2

class _Tester(db.Model):

  __tablename__ = '_tester'

  id = Column(String(75), primary_key=True)
  email = Column(String(75))
  authorized = Column(Boolean, default=False)
  level = Column(Integer)
  organization_id = Column(String(75))
  product_id = Column(String(75), ForeignKey('_product.id'))


class _History(db.Model):

  __tablename__ = '_history'

  id = Column(String(75), primary_key=True)
  model_id = Column(String(75))
  firmware_id = Column(String(75))
  endpoint_id = Column(String(75))
  hook_url = Column(String(120))
  hook_client_key = Column(String(120))
  stage = Column(Integer)
  created_time = Column(DateTime)
  created_stage_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  product_id = Column(String(75), ForeignKey('_product.id'))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


# TYPE
MODEL_TYPE_NRF_51 = 0
MODEL_TYPE_NRF_52 = 1


class _Model(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = '_model'

  id = Column(String(75), primary_key=True)
  code = Column(Integer)
  name = Column(String(75))
  typ = Column(Integer)
  parent_model_id = Column(String(75))
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  product_id = Column(String(75), ForeignKey('_product.id'))
  firmware_list = relationship("_Firmware", backref='model',
                               cascade="all, delete",
                               order_by="desc(_Firmware.version)")
  permission_list = relationship("_NkModelPermission", backref='model',
                                 cascade="all, delete")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.id


class _NkModelPermission(db.Model):

  __tablename__ = '_nk_model_permission'

  id = Column(String(75), primary_key=True)
  permission = Column(Integer)
  has_code = Column(Boolean, default=False)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  noti_key_id = Column(String(75), ForeignKey('_notikey.id'))
  model_id = Column(String(75), ForeignKey('_model.id'))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


FIRMWARE_RELEASE = 0
FIRMWARE_PRE_RELEASE = 1
FIRMWARE_DEV = 2
FIRMWARE_ARCHIVE = 3


class _Firmware(db.Model):

  __tablename__ = '_firmware'

  id = Column(String(75), primary_key=True)
  version = Column(String(75))
  ep_version = Column(String(75))
  model_code = Column(Integer)
  hex_path = Column(String(225))
  json_path = Column(String(225))
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  is_removed = Column(Boolean, default=False)
  model_id = Column(String(75), ForeignKey('_model.id'))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


class _ProductStage(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = '_product_stage'

  id = Column(String(75), primary_key=True)
  hook_url = Column(String(120))
  hook_client_key = Column(String(120))
  stage = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  product_id = Column(String(75), ForeignKey('_product.id'))
  stage_info_list = relationship("_StageInfo", backref='product_stage',
                                 cascade="all, delete",
                                 order_by="desc(_StageInfo.created_time)")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.id


class _StageInfo(db.Model):
  __tablename__ = '_stage_info'

  id = Column(String(75), primary_key=True)
  model_id = Column(String(75))
  endpoint_id = Column(String(75))
  firmware_id = Column(String(75))
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  product_stage_id = Column(String(75), ForeignKey('_product_stage.id'))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


class _Invite(db.Model):
  __tablename__ = '_invite'

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

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


class _EmailAuth(db.Model):
  __tablename__ = '_email_auth'

  id = Column(String(75), primary_key=True)
  email = Column(String(75))
  key = Column(String(75))
  user_id = Column(String(75))
  is_confirm = Column(Boolean, default=False, nullable=False)
  sent_time = Column(DateTime)
  accepted_time = Column(DateTime)

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


class _ReferrerInfo(db.Model):
  __tablename__ = '_referrer_info'

  id = Column(String(75), primary_key=True)
  user = Column(String(75))
  ip_address = Column(String(75))
  referrer = Column(String(225))
  user_agent = Column(String(225))
  accept_language = Column(String(225))
  accepted_time = Column(DateTime)

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


class _Domain(db.Model):
  __tablename__ = '_domain'

  id = Column(String(75), primary_key=True)
  domain = Column(String(75))
  request_ip_address = Column(String(75))
  accepted = Column(Boolean, default=False)
  request_user = Column(String(75))
  files_path = Column(String(225))
  created_time = Column(DateTime)
  accepted_time = Column(DateTime)
  accepted_user = Column(String(75))
  organization_id = Column(String(75), ForeignKey('_organization.id'))
  subdomain_list = relationship("_SubDomain", backref='domain', cascade="all, delete")

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


class _SubDomain(db.Model):
  __tablename__ = '_sub_domain'

  id = Column(String(75), primary_key=True)
  gadget_id = Column(String(75))
  subname = Column(String(75))
  domain_name = Column(String(75))
  request_ip_address = Column(String(75))
  accepted = Column(Boolean, default=False)
  created_time = Column(DateTime)
  accepted_time = Column(DateTime)
  accepted_user = Column(String(75))
  organization_id = Column(String(75))
  domain_id = Column(String(75), ForeignKey('_domain.id'))
  product_id = Column(String(75), ForeignKey('_product.id'))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)
