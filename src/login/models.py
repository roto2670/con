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

import logging

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean

from base import db, login_manager


class User(UserMixin, db.Model):

  __tablename__ = 'Users'

  id = Column(Integer, primary_key=True)
  name = Column(String(75))
  firebase_user_id = Column(String(75), unique=True)
  email = Column(String(75), unique=True, nullable=False)
  email_verified = Column(Boolean, default=False, nullable=False)
  sign_in_provider = Column(String(75))
  photo_url = Column(String(225))
  developer_id = Column(String(75))

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
