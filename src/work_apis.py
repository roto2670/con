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

import logging
import datetime
from flask_login import current_user  # noqa : pylint: disable=import-error

from sqlalchemy import desc

from base import db
from work_models import _BasePoint as BasePoint 
from work_models import _Tunnel as Tunnel
from work_models import _Blast as Blast
from work_models import _BlastInfo as BlastInfo
from work_models import _Work as Work
from work_models import _WorkHistory as WorkHistory


def get_servertime():
  return datetime.datetime.now().replace(microsecond=0)


def create_basepoint(data):
  cur_time = get_servertime()
  data = BasePoint(id=data['id'],
                   name=data['name'],
                   x_loc=data['x_loc'],
                   y_loc=data['y_loc'],
                   width=data['width'],
                   height=data['height'],
                   created_time=cur_time,
                   last_updated_time=cur_time)
                   #last_updated_user=current_user.email)
  db.session.add(data)
  db.session.commit()


def update_basepoint(data):
  # TODO:
  _id = None
  cur_time = get_servertime()
  data = get_basepoint(_id)
  data.last_updated_time = cur_time
  db.session.commit()
  return data


def remove_basepoint(_id):
  ret = get_basepoint(_id)
  logging.info("### ret : %s", ret)
  if ret:
    try:
      db.session.delete(ret)
      db.session.commit()
    except:
      logging.exception("#### ")


def get_basepoint(_id):
  data = BasePoint.query.filter_by(id=_id).one_or_none()
  return data


def get_all_basepoint():
  data_list = BasePoint.query.all()
  return data_list


def create_tunnel(data):
  cur_time = get_servertime()
  data = Tunnel(id=data['id'],
                name=data['name'],
                direction=data['direction'],
                x_loc=data['x_loc'],
                y_loc=data['y_loc'],
                width=data['width'],
                height=data['height'],
                created_time=cur_time,
                last_updated_time=cur_time,
                #last_updated_user=current_user.email,
                basepoint_id=data['basepoint_id'])
  db.session.add(data)
  db.session.commit()


def update_tunnel(data):
  # TODO:
  _id = None
  cur_time = get_servertime()
  data = get_tunnel(_id)
  data.last_updated_time = cur_time
  db.session.commit()
  return data


def remove_tunnel(_id):
  ret = get_tunnel(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_tunnel(_id):
  data = Tunnel.query.filter_by(id=_id).one_or_none()
  return data


def get_tunnel_list_by_basepoint(basepoint_id):
  data_list = Tunnel.query.filter_by(basepoint_id=basepoint_id).all()
  return data_list


def get_all_tunnel():
  data_list = Tunnel.query.all()
  return data_list


def create_blast(data):
  cur_time = get_servertime()
  data = Blast(id=data['id'],
               x_loc=data['x_loc'],
               y_loc=data['y_loc'],
               width=data['width'],
               height=data['height'],
               state=data['state'],
               accum_time=data['accum_time'],
               created_time=cur_time,
               last_updated_time=cur_time,
               #last_updated_user=current_user.email,
               tunnel_id=data['tunnel_id'])
  db.session.add(data)
  db.session.commit()


def update_blast(data):
  # TODO:
  _id = None
  cur_time = get_servertime()
  data = get_blast(_id)
  data.last_updated_time = cur_time
  db.session.commit()
  return data


def update_blast_state_and_accum(blast_id, state, accum_time):
  cur_time = get_servertime()
  data = get_blast(blast_id)
  logging.info("#### data : %s", data)
  logging.info("#### data : %s", data.accum_time)
  data.state = state
  data.accum_time += accum_time
  data.last_updated_time = cur_time
  #_data.last_updated_user = currrent_user.email
  db.session.commit()
  return data


def remove_blast(_id):
  ret = get_blast(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_blast(_id):
  data = Blast.query.filter_by(id=_id).one_or_none()
  return data


def get_blast_list_by_tunnel(tunnel_id):
  data_list = Blast.query.filter_by(tunnel_id=tunnel_id).\
      order_by(desc(Blast.created_time)).all()
  return data_list


def get_all_blast():
  data_list = Blast.query.order_by(desc(Blast.created_time)).all()
  return data_list


def create_blast_info(data):
  cur_time = get_servertime()
  data = BlastInfo(id=data['id'],
                   explosive=data['explosive'],
                   detonator=data['detonator'],
                   drilling_depth=data['drilling_depth'],
                   blasting_time=data['blasting_time'],
                   start_point=data['start_point'],
                   finish_point=data['finish_point'],
                   blasting_length=data['blasting_length'],
                   created_time=cur_time,
                   last_updated_time=cur_time,
                   #last_updated_user=current_user.email,
                   blast_id=data['blast_id'])
  db.session.add(data)
  db.session.commit()


def update_blast_info(data):
  # TODO:
  _id = None
  cur_time = get_servertime()
  data = get_blast_info(_id)
  data.last_updated_time = cur_time
  db.session.commit()
  return data


def remove_blast_info(_id):
  ret = get_blast_info(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_blast_info(_id):
  data = BlastInfo.query.filter_by(id=_id).one_or_none()
  return data


def get_blast_info_by_blast(blast_id):
  data = BlastInfo.query.filter_by(blast_id=blast_id).one_or_none()
  return data


def get_all_blast_info():
  data_list = BlastInfo.query.all()
  return data_list


def create_work(data):
  cur_time = get_servertime()
  data = Work(id=data['id'],
              category=data['category'],
              typ=data['typ'],
              state=data['state'],
              accum_time=data['accum_time'],
              created_time=cur_time,
              last_updated_time=cur_time,
              #last_updated_user=current_user.email,
              blast_id=data['blast_id'])
  db.session.add(data)
  db.session.commit()


def update_work(data):
  # TODO:
  _id = None
  cur_time = get_servertime()
  _data = get_work(_id)
  _data.last_updated_time = cur_time
  db.session.commit()
  return _data


def update_state_and_accum(work_id, state, accum_time):
  cur_time = get_servertime()
  data = get_work(work_id)
  logging.info("#### data : %s", data)
  data.state = state
  data.accum_time = accum_time
  data.last_updated_time = cur_time
  #_data.last_updated_user = currrent_user.email
  db.session.commit()
  return data


def remove_work(_id):
  ret = get_work(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_work(_id):
  data = Work.query.filter_by(id=_id).one_or_none()
  return data


def get_latest_work_by_blast(blast_id, typ):
  data = Work.query.filter_by(blast_id=blast_id, typ=typ).all()
  logging.info("#### data : %s", data)
  for _data in data:
    logging.info("### _Ddd : %s, %s, %s", _data.typ, _data.state, _data.created_time)
  if data:
    logging.info("### history : %s", data[0].work_history_list)
    return data[0]
  else:
    return None


def get_work_list_by_blast(blast_id):
  data_list = Work.query.filter_by(blast_id=blast_id).\
      order_by(desc(Work.created_time)).all()
  return data_list


def get_all_work():
  data_list = Work.query.order_by(desc(Work.created_time)).all()
  return data_list


def create_work_history(data):
  cur_time = get_servertime()
  data = WorkHistory(typ=data['typ'],
                     state=data['state'],
                     timestamp=data['timestamp'],
                     accum_time=data['accum_time'],
                     created_time=cur_time,
                     #last_updated_user=current_user.email,
                     work_id=data['work_id'])
  db.session.add(data)
  db.session.commit()


def update_work_history(data):
  # TODO:
  _id = None
  cur_time = get_servertime()
  data = get_work_history(_id)
  data.last_updated_time = cur_time
  db.session.commit()
  return data


def remove_work_history(_id):
  ret = get_work_history(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_work_history(_id):
  data = WorkHistory.query.filter_by(id=_id).one_or_none()
  return data

def get_work_history_list_by_work(work_id):
  data_list = WorkHistory.query.filter_by(work_id=work_id).all()
  return data_list


def get_all_work_history():
  data_list = WorkHistory.query.all()
  return data_list

