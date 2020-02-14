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

from sqlalchemy import Column, DateTime, String, Integer, Float  # noqa : pylint: disable=import-error
from sqlalchemy import ForeignKey  # noqa : pylint: disable=import-error
from sqlalchemy.orm import relationship  # noqa : pylint: disable=import-error
from base import db


class _BasePoint(db.Model):
  __tablename__ = '_basepoint'
  __bind_key__ = 'smart_work'

  id = Column(String(75), primary_key=True)
  name = Column(String(75))
  x_loc = Column(Float)
  y_loc = Column(Float)
  width = Column(Float)
  height = Column(Float)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  tunnel_list = relationship("_Tunnel", backref="basepoint",
                             cascade="all, delete")


class _Tunnel(db.Model):
  __tablename__ = '_tunnel'
  __bind_key__ = 'smart_work'

  id = Column(String(75), primary_key=True)
  name = Column(String(75))
  direction = Column(Integer)
  x_loc = Column(Float)
  y_loc = Column(Float)
  width = Column(Float)
  height = Column(Float)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  basepoint_id = Column(String(75), ForeignKey('_basepoint.id'))
  blast_list = relationship("_Blast", backref="tunnel",
                            cascade="all, delete",
                            order_by="desc(_Blast.created_time)")


class _Blast(db.Model):
  __tablename__ = '_blast'
  __bind_key__ = 'smart_work'

  id = Column(String(75), primary_key=True)
  x_loc = Column(Float)
  y_loc = Column(Float)
  width = Column(Float)
  height = Column(Float)
  state = Column(Integer)
  accum_time = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  tunnel_id = Column(String(75), ForeignKey('_tunnel.id'))
  blast_info_list = relationship("_BlastInfo", backref="blast",
                                 cascade="all, delete")
  work_list = relationship("_Work", backref="blast",
                            cascade="all, delete",
                            order_by="desc(_Work.created_time)")


class _BlastInfo(db.Model):
  __tablename__ = '_blast_info'
  __bind_key__ = 'smart_work'

  id = Column(String(75), primary_key=True)
  explosive = Column(Float)
  detonator = Column(Float)
  drilling_depth = Column(Float)
  blasting_time = Column(DateTime)
  start_point = Column(Float)
  finish_point = Column(Float)
  blasting_length = Column(Float)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  blast_id = Column(String(75), ForeignKey('_blast.id'))


class _Work(db.Model):
  __tablename__ = '_work'
  __bind_key__ = 'smart_work'

  id = Column(String(75), primary_key=True)
  category = Column(Integer)
  typ = Column(Integer)
  state = Column(Integer)
  accum_time = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  blast_id = Column(String(75), ForeignKey('_blast.id'))
  work_history_list = relationship("_WorkHistory", backref="work",
                                    cascade="all, delete",
                                    order_by="desc(_WorkHistory.created_time)")


class _WorkHistory(db.Model):
  __tablename__ = '_work_history'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  typ = Column(Integer)
  state = Column(Integer)
  timestamp = Column(DateTime)
  accum_time = Column(Integer)
  created_time = Column(DateTime)
  last_updated_user = Column(String(75))
  work_id = Column(String(75), ForeignKey('_work.id'))

