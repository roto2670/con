
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
from sqlalchemy import Column, DateTime, String, Text  # noqa : pylint: disable=import-error

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
