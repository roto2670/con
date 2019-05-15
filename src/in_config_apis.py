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
