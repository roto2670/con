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
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

# self
from base import db, login_manager


class User(UserMixin, db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = 'user'

  id = Column(String(75), primary_key=True)
  email = Column(String(75), unique=True, nullable=False)
  language = Column(String(15))
  account_ids = Column(Text)  # list
  authorized = Column(Boolean, default=False)
  # ====== upper cloud data
  name = Column(String(75))
  firebase_user_id = Column(String(75), unique=True)
  email_verified = Column(Boolean, default=False, nullable=False)
  sign_in_provider = Column(String(75))
  photo_url = Column(String(225))
  last_access_time = Column(DateTime)
  ip_address = Column(String(75))

  organization_id = Column(String, ForeignKey('organization.id'))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
    return self.email


@login_manager.user_loader
def user_loader(id):
  return User.query.get(id)


class Organization(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = 'organization'

  id = Column(String, primary_key=True)
  users = Column(Text)  # list, 테스트가 가능한 모든 유저
  products = Column(Text)  # list
  tokens = Column(Text)  # dict
  kinds = Column(Text)  # dict
  # ======= upper cloud data
  name = Column(String(120))
  owner = Column(Text)  # list
  member = Column(Text)  # list
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)

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


class Product(db.Model):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  __tablename__ = 'product'

  id = Column(String(75), primary_key=True)
  developer_id = Column(String(75))
  key = Column(String(75))
  hook_url = Column(String(120))
  hook_client_key = Column(String(120))
  # ======= upper cloud data
  name = Column(String(75))
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  organization_id = Column(String, ForeignKey('organization.id'))

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

  id = Column(Integer, primary_key=True)
  version = Column(String(75))
  specifications = Column(Text)
  organization_id = Column(String(75))

  product_id = Column(String(75), ForeignKey('product.id'))


class NotiKey(db.Model):

  __tablename__ = 'notikey'

  id = Column(Integer, primary_key=True)
  android_key = Column(String(75))
  android_package_name = Column(String(75))
  ios_dev_bundle_id = Column(String(75))
  ios_dev_password = Column(String(75))
  ios_production_bundle_id = Column(String(75))
  ios_production_password = Column(String(75))
  organization_id = Column(String(75))

  product_id = Column(String(75), ForeignKey('product.id'))
