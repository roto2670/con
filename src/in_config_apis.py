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
import logging
import datetime

import pytz
from flask_login import current_user  # noqa : pylint: disable=import-error
from sqlalchemy import desc

from base import db
from config_models import _Footer as Footer
from config_models import _SupremaConfig as SupremaConfig
from config_models import _LocationConfig as LocationConfig
from config_models import _EnterenceWorkerLog as EnterenceWorkerLog
from config_models import _CountDeviceSetting as CountDeviceSetting



def get_datetime():
  return datetime.datetime.now(pytz.timezone('UTC'))


# {{{ Footer


def create_footer(text, file_path, file_names, image_uri):
  footer = Footer(id=uuid.uuid4().hex,
                  text=text,
                  file_path=file_path,
                  file_names=json.dumps(file_names),
                  image_uri=image_uri,
                  last_updated_time=get_datetime(),
                  last_updated_user=current_user.email,
                  organization_id=current_user.organization_id)
  db.session.add(footer)
  db.session.commit()


def update_footer(text, file_path, file_names, image_uri):
  footer = get_footer_by_organization(current_user.organization_id)
  footer.text = text
  footer.file_path = file_path
  footer.file_names = json.dumps(file_names)
  footer.image_uri = image_uri
  footer.last_updated_time = get_datetime()
  footer.last_updated_user = current_user.email
  db.session.commit()


def get_footer_by_organization(organization_id):
  footer = Footer.query.filter_by(organization_id=organization_id).one_or_none()
  return footer


# }}}


# {{{ Suprema


def create_suprema_config(base_url, suprema_id, suprema_pw, event_id,
                          client_interval, server_interval,
                          organization_id, last_data_id=None):
  cur_time = get_datetime()
  _last_data_id = last_data_id if last_data_id else 0
  suprema_config = SupremaConfig(base_url=base_url,
                                 suprema_id=suprema_id,
                                 suprema_pw=suprema_pw,
                                 event_id=event_id,
                                 client_interval=client_interval,
                                 server_interval=server_interval,
                                 last_data_id=_last_data_id,
                                 created_time=cur_time,
                                 last_updated_time=cur_time,
                                 last_updated_user=current_user.email,
                                 organization_id=organization_id)
  db.session.add(suprema_config)
  db.session.commit()


def get_suprema_config_by_org(organization_id):
  suprema_config = SupremaConfig.query.\
      filter_by(organization_id=organization_id).one_or_none()
  return suprema_config


def get_all_suprema_config():
  suprema_config_list = SupremaConfig.query.all()
  return suprema_config_list


def update_suprema_config_about_last_id(organization_id, last_data_id):
  suprema_config = get_suprema_config_by_org(organization_id)
  suprema_config.last_data_id = last_data_id
  suprema_config.last_updated_time = get_datetime()
  db.session.commit()


def update_suprema_config(base_url, suprema_id, suprema_pw, event_id,
                          client_interval, server_interval,
                          organization_id):
  suprema_config = get_suprema_config_by_org(organization_id)
  suprema_config.base_url = base_url
  suprema_config.suprema_id = suprema_id
  suprema_config.suprema_pw = suprema_pw
  suprema_config.event_id = event_id
  suprema_config.client_interval = client_interval
  suprema_config.server_interval = server_interval
  suprema_config.last_updated_time = get_datetime()
  suprema_config.last_updated_user = current_user.email
  db.session.commit()


#}}}


#{{{ location


def create_location_config(product_id, kind, client_interval, server_interval,
                           organization_id):
  cur_time = get_datetime()
  location_config = LocationConfig(product_id=product_id,
                                   kind=kind,
                                   client_interval=client_interval,
                                   server_interval=server_interval,
                                   created_time=cur_time,
                                   last_updated_time=cur_time,
                                   last_updated_user=current_user.email,
                                   organization_id=organization_id)
  db.session.add(location_config)
  db.session.commit()


def get_location_config_by_org(organization_id):
  location_config = LocationConfig.query.\
      filter_by(organization_id=organization_id).one_or_none()
  return location_config


def get_all_location_config():
  location_config_list = LocationConfig.query.all()
  return location_config_list


def update_location_config(product_id, kind, client_interval, server_interval,
                           organization_id):
  location_config = get_location_config_by_org(organization_id)
  location_config.event_id = product_id
  location_config.kind = kind
  location_config.client_interval = client_interval
  location_config.server_interval = server_interval
  location_config.last_updated_time = get_datetime()
  location_config.last_updated_user = current_user.email
  db.session.commit()


# }}}


def create_enterence_worker_log(data, text, organization_id):
  cur_time = get_datetime()
  event_time = datetime.datetime.strptime(data['server_datetime'],
                                          "%Y-%m-%dT%H:%M:%S.%fZ")
  log = EnterenceWorkerLog(event_type=data['event_type_id']['code'],
                           event_time=event_time,
                           created_time=cur_time,
                           worker_id=data['user_id']['user_id'],
                           worker_name=data['user_id']['name'],
                           device_id=data['device_id']['id'],
                           device_name=data['device_id']['name'],
                           text=text,
                           organization_id=organization_id)
  db.session.add(log)
  db.session.commit()


def get_enterence_worker_log_list(organization_id, page_num=1, limit=None):
  _limit = limit if limit else 30
  log_list = EnterenceWorkerLog.query.filter_by(organization_id=organization_id).\
      order_by(desc(EnterenceWorkerLog.id)).paginate(page_num, _limit, False)
  return log_list



def create_or_update_count_device_setting(device_id, typ, inout, access_point):
  cur_time = get_datetime()
  setting = get_count_device(device_id)
  if setting:
    setting.inout = inout
    setting.access_point = access_point
    last_updated_time = cur_time
    last_updated_user = current_user.email
  else:
    device_setting = CountDeviceSetting(device_id=device_id,
                                        typ=typ,
                                        inout=inout,
                                        access_point=access_point,
                                        last_updated_time=cur_time,
                                        last_updated_user=current_user.email,
                                        organization_id=current_user.organization_id)
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