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
  section = Column(String(75))
  part = Column(String(75))
  category = Column(Integer)
  direction = Column(Integer)
  length = Column(Float)
  tunnel_id = Column(String(75))
  b_accum_length = Column(Float)
  initial_b_time = Column(DateTime)
  left_x_loc = Column(Float)
  right_x_loc = Column(Float)
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
  left_x_loc = Column(Float)
  right_x_loc = Column(Float)
  y_loc = Column(Float)
  width = Column(Float)
  height = Column(Float)
  state = Column(Integer)
  accum_time = Column(Integer)
  m_accum_time = Column(Integer)
  s_accum_time = Column(Integer)
  i_accum_time = Column(Integer)
  blasting_time = Column(DateTime)
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
  explosive_bulk = Column(Float)
  explosive_cartridge = Column(Float)
  detonator = Column(Float)
  drilling_depth = Column(Float)
  blasting_time = Column(DateTime)
  start_point = Column(Float)
  finish_point = Column(Float)
  blasting_length = Column(Float)
  team_id = Column(Integer)
  team_nos = Column(Integer)
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
  p_accum_time = Column(Integer)
  created_time = Column(DateTime)
  start_time = Column(DateTime)
  end_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  blast_id = Column(String(75), ForeignKey('_blast.id'))
  work_history_list = relationship("_WorkHistory", backref="work",
                                   cascade="all, delete",
                                   order_by="desc(_WorkHistory.timestamp), "
                                            "desc(_WorkHistory.created_time)")
  pause_history_list = relationship("_PauseHistory", backref="work",
                                    cascade="all, delete",
                                    order_by="desc(_PauseHistory.created_time)")
  work_equipment_list = relationship("_WorkEquipment", backref="work",
                                     cascade="all, delete",
                                     order_by="asc(_WorkEquipment.created_time)")


class _WorkHistory(db.Model):
  __tablename__ = '_work_history'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  typ = Column(Integer)
  state = Column(Integer)
  timestamp = Column(DateTime)
  accum_time = Column(Integer)
  auto_end = Column(DateTime)
  job_id = Column(String(75))
  created_time = Column(DateTime)
  last_updated_user = Column(String(75))
  work_id = Column(String(75), ForeignKey('_work.id'))


class _PauseHistory(db.Model):
  __tablename__ = '_pause_history'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  start_time = Column(DateTime)
  end_time = Column(DateTime)
  accum_time = Column(Integer)
  message = Column(String(512))
  created_time = Column(DateTime)
  last_updated_user = Column(String(75))
  work_id = Column(String(75), ForeignKey('_work.id'))


class _Activity(db.Model):
  __tablename__ = '_activity'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  name = Column(String(75))
  category = Column(Integer)
  activity_id = Column(Integer)
  file_path = Column(String(75))
  order = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))


class _Equipment(db.Model):
  __tablename__ = '_equipment'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  name = Column(String(75))
  category = Column(Integer)
  equipment_id = Column(String(75))
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))


class _Operator(db.Model):
  __tablename__ = '_operator'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  name = Column(String(75))
  operator_id = Column(String(75))
  department = Column(String(75))
  category = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))


class _WorkEquipment(db.Model):
  __tablename__ = '_work_equipment'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  category = Column(String(75))
  equipment_id = Column(String(75))
  operator_id = Column(String(75))
  accum_time = Column(Integer)
  p_accum_time = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))
  work_id = Column(String(75), ForeignKey('_work.id'))


class _Team(db.Model):
  __tablename__ = '_team'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  category = Column(Integer)
  name = Column(String(75))
  engineer = Column(String(75))
  member = Column(Integer)
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))


class _Message(db.Model):
  __tablename__ = '_message'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  category = Column(Integer)
  message = Column(String(125))
  created_time = Column(DateTime)
  last_updated_time = Column(DateTime)
  last_updated_user = Column(String(75))


class _ChargingActInfo(db.Model):
  __tablename__ = '_chargingactinfo'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  explosive_bulk = Column(Float)
  explosive_cartridge = Column(Float)
  detonator = Column(Float)
  drilling_depth = Column(Float)
  team_id = Column(Integer)
  team_nos = Column(Integer)
  work_id = Column(String(75))
  blast_id = Column(String(75))


class _BlastingActInfo(db.Model):
  __tablename__ = '_blastingactinfo'
  __bind_key__ = 'smart_work'

  id = Column(Integer, primary_key=True)
  blasting_time = Column(DateTime)
  start_point = Column(Float)
  finish_point = Column(Float)
  blasting_length = Column(Float)
  work_id = Column(String(75))
  blast_id = Column(String(75))