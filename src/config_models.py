
# -*- coding: utf-8 -*-
#
# Copyright 2017-2019 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|

# 3rd party
from sqlalchemy import ForeignKey  # noqa : pylint: disable=import-error
from sqlalchemy import Column, DateTime, String, Text, Integer  # noqa : pylint: disable=import-error

from base import db


class _Footer(db.Model):
  __tablename__ = '_footer'

  id = Column(String(75), primary_key=True)
  text = Column(String(75))
  file_path = Column(String(225))
  file_names = Column(String(225))
  image_uri = Column(Text)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75))


class _SupremaConfig(db.Model):
  __tablename__ = '_suprema_config'

  id = Column(Integer, primary_key=True)
  base_url = Column(String(75))
  suprema_id = Column(String(75))
  suprema_pw = Column(String(75))
  event_id = Column(String(25))
  client_interval = Column(Integer)
  server_interval = Column(Integer)
  last_data_id = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75))


class _LocationConfig(db.Model):
  __tablename__ = '_location_config'

  id = Column(Integer, primary_key=True)
  client_interval = Column(Integer)
  server_interval = Column(Integer)
  product_id = Column(String(75))
  kind = Column(String(75))
  file_path = Column(String(225))
  file_names = Column(String(225))
  image_uri = Column(Text)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75))


class _EnterenceWorkerLog(db.Model):
  __tablename__ = '_enterence_worker_log'

  id = Column(Integer, primary_key=True)
  event_type = Column(String(25))
  event_time = Column(DateTime)
  created_time = Column(DateTime)
  worker_id = Column(String(75))
  worker_name = Column(String(75))
  device_id = Column(String(75))
  device_name = Column(String(75))
  text = Column(Text)
  organization_id = Column(String(75))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      if hasattr(value, '__iter__') and not isinstance(value, str):
        value = value[0]
      setattr(self, property, value)


class _CountDeviceSetting(db.Model):
  __tablename__ = '_count_device_setting'

  id = Column(Integer, primary_key=True)
  device_id = Column(String(75))
  inout = Column(Integer)
  access_point = Column(Integer)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75))
