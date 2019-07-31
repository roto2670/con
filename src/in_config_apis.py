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

import json
import uuid
import datetime

import pytz
from flask_login import current_user  # noqa : pylint: disable=import-error
from sqlalchemy import desc

from base import db
from constants import ORG_ID
from config_models import _EnterenceWorkerLog as EnterenceWorkerLog
from config_models import _CountDeviceSetting as CountDeviceSetting
from config_models import _EntranceEquipLog as EntranceEquipLog
from config_models import _BusSettingData as BusSettingData


def get_datetime():
  return datetime.datetime.now(pytz.timezone('UTC'))


def create_enterence_worker_log(inout, access_point, data, text,
                                organization_id):
  cur_time = get_datetime()
  event_time = datetime.datetime.strptime(data['server_datetime'],
                                          "%Y-%m-%dT%H:%M:%S.%fZ")
  log = EnterenceWorkerLog(event_type=data['event_type_id']['code'],
                           event_time=event_time,
                           inout=inout,
                           access_point=access_point,
                           created_time=cur_time,
                           worker_id=data['user_id']['user_id'],
                           worker_name=data['user_id']['name'],
                           device_id=data['device_id']['id'],
                           device_name=data['device_id']['name'],
                           text=text,
                           organization_id=organization_id)
  db.session.add(log)
  db.session.commit()
  return {
    "id": log.id,
    "event_type": log.event_type,
    "event_time": str(log.event_time),
    "inout": log.inout,
    "access_point": log.access_point,
    "created_time": str(log.created_time),
    "worker_id": log.worker_id,
    "worker_name": log.worker_name,
    "device_id": log.device_id,
    "device_name": log.device_name,
    "text": log.text,
    "organization_id": log.organization_id
  }


def get_enterence_worker_log_list(organization_id, page_num=1, limit=None):
  _limit = limit if limit else 30
  log_list = EnterenceWorkerLog.query.filter_by(organization_id=organization_id).\
      order_by(desc(EnterenceWorkerLog.id)).paginate(page_num, _limit, False)
  return log_list


def get_enterence_in_worker_log_list(organization_id, access_point, page_num=1,
                                     limit=None):
  _limit = limit if limit else 30
  log_list = EnterenceWorkerLog.query.filter_by(organization_id=organization_id,
                                                access_point=access_point,
                                                inout=1).\
      order_by(desc(EnterenceWorkerLog.id)).paginate(page_num, _limit, False)
  return log_list


def get_enterence_out_worker_log_list(organization_id, access_point, page_num=1,
                                      limit=None):
  _limit = limit if limit else 30
  log_list = EnterenceWorkerLog.query.filter_by(organization_id=organization_id,
                                                access_point=access_point,
                                                inout=2).\
      order_by(desc(EnterenceWorkerLog.id)).paginate(page_num, _limit, False)
  return log_list


def create_or_update_count_device_setting(device_id, typ, inout, access_point,
                                          name=""):
  cur_time = get_datetime()
  setting = get_count_device(device_id)
  if setting:
    if name:
      setting.name = name
    setting.inout = inout
    setting.access_point = access_point
    last_updated_time = cur_time
    #last_updated_user = current_user.email
    last_updated_user = ""
  else:
    device_setting = CountDeviceSetting(device_id=device_id,
                                        name=name,
                                        typ=typ,
                                        inout=inout,
                                        access_point=access_point,
                                        last_updated_time=cur_time,
                                        last_updated_user="",
                                        organization_id=ORG_ID)
    db.session.add(device_setting)
  db.session.commit()


def get_count_device_setting(typ, org_id=None):
  _org_id = org_id if org_id else current_user.organization_id
  _list = CountDeviceSetting.query.filter_by(typ=typ,
                                             organization_id=_org_id).all()
  return _list


def get_count_device(device_id):
  c_device = CountDeviceSetting.query.filter_by(device_id=device_id).one_or_none()
  return c_device


def delete_count_device_setting(device_id):
  device_setting = get_count_device(device_id)
  if device_setting:
    db.session.delete(device_setting)
    db.session.commit()


def reset_count_device_setting(device_id):
  device_setting = get_count_device(device_id)
  if device_setting:
    device_setting.inout = 0
    device_setting.access_point = 0
    device_setting.last_update_user = current_user.email
    device_setting.last_updated_time = get_datetime()
    db.session.commit()



def create_entrance_equip_log(inout, access_point, kind, hub_id,
                              hub_name, gadget_id, gadget_name, text,
                              organization_id):
  cur_time = get_datetime()
  log = EntranceEquipLog(inout=inout,
                         access_point=access_point,
                         kind=kind,
                         event_time=cur_time,
                         created_time=cur_time,
                         hub_id=hub_id,
                         hub_name=hub_name,
                         gadget_id=gadget_id,
                         gadget_name=gadget_name,
                         text=text,
                         organization_id=organization_id)
  db.session.add(log)
  db.session.commit()
  return {
    "id": log.id,
    "inout": log.inout,
    "access_point": log.access_point,
    "kind": log.kind,
    "event_time": str(log.event_time),
    "created_time": str(log.created_time),
    "hub_id": log.hub_id,
    "hub_name": log.hub_name,
    "gadget_id": log.gadget_id,
    "gadget_name": log.gadget_name,
    "text": log.text,
    "organization_id": log.organization_id
  }


def get_entrance_equip_log_list(organization_id, page_num=1, limit=None):
  _limit = limit if limit else 30
  log_list = EntranceEquipLog.query.filter_by(organization_id=organization_id).\
    order_by(desc(EntranceEquipLog.created_time)).paginate(page_num, _limit, False)
  return log_list


def get_entrance_in_equip_log_list(organization_id, access_point, page_num=1,
                                   limit=None):
  _limit = limit if limit else 30
  log_list = EntranceEquipLog.query.filter_by(organization_id=organization_id,
                                              access_point=access_point,
                                              inout=1).\
    order_by(desc(EntranceEquipLog.created_time)).paginate(page_num, _limit, False)
  return log_list


def get_entrance_out_equip_log_list(organization_id, access_point, page_num=1,
                                    limit=None):
  _limit = limit if limit else 30
  log_list = EntranceEquipLog.query.filter_by(organization_id=organization_id,
                                              access_point=access_point,
                                              inout=2).\
    order_by(desc(EntranceEquipLog.created_time)).paginate(page_num, _limit, False)
  return log_list


def create_or_update_bus_setting_data(bus_user_id, bus_user_name, bus_beacon_id,
                                      bus_beacon_name, org_id):
  cur_time = get_datetime()
  ret = get_bus_setting_data(bus_user_id, bus_beacon_id, org_id)
  if ret:
    ret.bus_user_id = bus_user_id
    ret.bus_user_name = bus_user_name
    ret.bus_beacon_id = bus_beacon_id
    ret.bus_beacon_name = bus_beacon_name
    ret.last_updated_user = current_user.email
    ret.last_update_time = cur_time
  else:
    bus = BusSettingData(bus_user_id=bus_user_id,
                         bus_user_name=bus_user_name,
                         bus_beacon_id=bus_beacon_id,
                         bus_beacon_name=bus_beacon_name,
                         last_updated_user=current_user.email,
                         last_updated_time=cur_time,
                         organization_id=org_id)
    db.session.add(bus)
  db.session.commit()


def get_bus_setting_data(bus_user_id, bus_beacon_id, org_id):
  bus_data = BusSettingData.query.filter_by(bus_user_id=bus_user_id,
                                            bus_beacon_id=bus_beacon_id,
                                            organization_id=org_id).one_or_none()
  return bus_data


def get_bus_setting_data_by_id(_id, org_id):
  bus_data = BusSettingData.query.filter_by(id=_id,
                                            organization_id=org_id).one_or_none()
  return bus_data


def get_bus_setting_data_list(org_id=None):
  _org_id = org_id if org_id else current_user.organization_id
  bus_list = BusSettingData.query.filter_by(organization_id=_org_id).all()
  return bus_list


def delete_bus_setting_data(_id, org_id):
  ret = get_bus_setting_data_by_id(_id, org_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()
