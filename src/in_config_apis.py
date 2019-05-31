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


def update_suprema_config_about_last_id(organization_id, last_data_id):
  suprema_config = get_suprema_config_by_org(organization_id)
  suprema_config.last_data_id = last_data_id
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


def create_location_config(product_id, client_interval, server_interval,
                           organization_id):
  cur_time = get_datetime()
  location_config = LocationConfig(product_id=product_id,
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


def update_location_config(product_id, client_interval, server_interval,
                           organization_id):
  location_config = get_location_config_by_org(organization_id)
  location_config.event_id = product_id
  location_config.client_interval = client_interval
  location_config.server_interval = server_interval
  location_config.last_updated_time = get_datetime()
  location_config.last_updated_user = current_user.email
  db.session.commit()


# }}}
