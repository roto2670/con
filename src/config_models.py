# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Naran Inc. All rights reserved.
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


class _NoticeBoard(db.Model):
  __tablename__ = '_notice_board'
  id = Column(Integer, primary_key=True)
  title = Column(String(75))
  category = Column(String(75))
  writer = Column(String(75))
  department = Column(String(75))
  file_path = Column(Text)
  created_time = Column(DateTime)
  organization_id = Column(String(75))


class _ScheduleBoard(db.Model):
  __tablename__ = '_schedule_board'
  id = Column(Integer, primary_key=True)
  title = Column(String(75))
  category = Column(String(75))
  writer = Column(String(75))
  department = Column(String(75))
  file_path = Column(Text)
  created_time = Column(DateTime)
  organization_id = Column(String(75))


class _BusSettingData(db.Model):
  __tablename__ = '_bus_setting_data'

  id = Column(Integer, primary_key=True)
  bus_user_id = Column(String(75))
  bus_user_name = Column(String(75))
  bus_beacon_id = Column(String(75))
  bus_beacon_name = Column(String(75))
  last_updated_user = Column(String(75))
  last_updated_time = Column(DateTime)
  organization_id = Column(String(75))


class _EnterenceWorkerLog(db.Model):
  __tablename__ = '_enterence_worker_log'

  id = Column(Integer, primary_key=True)
  inout = Column(Integer)
  access_point = Column(Integer)
  event_type = Column(String(25))
  event_time = Column(DateTime)
  created_time = Column(DateTime)
  worker_id = Column(String(75))
  worker_name = Column(String(75))
  device_id = Column(String(75))
  device_name = Column(String(75))
  text = Column(Text)
  organization_id = Column(String(75))


FACE_STATION_TYPE = 1
SCANNER_TYPE = 2


class _CountDeviceSetting(db.Model):
  __tablename__ = '_count_device_setting'

  id = Column(Integer, primary_key=True)
  typ = Column(Integer)
  device_id = Column(String(75))
  name = Column(String(75))  # Scanner only
  inout = Column(Integer)
  access_point = Column(Integer)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  organization_id = Column(String(75))


class _EntranceEquipLog(db.Model):
  __tablename__ = '_entrance_equip_log'

  id = Column(Integer, primary_key=True)
  inout = Column(Integer)
  access_point = Column(Integer)
  kind = Column(String(25))
  event_time = Column(DateTime)
  created_time = Column(DateTime)
  hub_id = Column(String(75))
  hub_name = Column(String(75))
  gadget_id = Column(String(75))
  gadget_name = Column(String(75))
  text = Column(Text)
  organization_id = Column(String(75))
