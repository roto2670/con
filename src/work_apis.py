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
from sqlalchemy import desc, or_

from base import db
from work_models import _BasePoint as BasePoint
from work_models import _Tunnel as Tunnel
from work_models import _Blast as Blast
from work_models import _BlastInfo as BlastInfo
from work_models import _Work as Work
from work_models import _WorkHistory as WorkHistory
from work_models import _PauseHistory as PauseHistory
from work_models import _Activity as Activity
from work_models import _Equipment as Equipment
from work_models import _Operator as Operator
from work_models import _WorkEquipment as WorkEquipment
from work_models import _Team as Team
from work_models import _Message as Message
from work_models import _ChargingActInfo as ChargingActInfo
from work_models import _BlastingActInfo as BlastingActInfo
from constants import WORK_STATE_STOP, WORK_STATE_IN_PROGRESS, WORK_STATE_FINISH

MAIN_TYPES = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113,
              114, 115]
SUPPORTING_TYPES = [200, 201, 202, 203, 204, 205, 206, 207, 208]
IDLE_TYPES = [300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310]


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
                   last_updated_time=cur_time,
                   last_updated_user=current_user.email)
  db.session.add(data)
  db.session.commit()


def update_basepoint(data):
  # TODO:
  _id = data['id']
  cur_time = get_servertime()
  _data = get_basepoint(_id)
  _data.name = data['name']
  _data.last_updated_time = cur_time
  data.last_updated_user = current_user.email
  db.session.commit()
  return _data


def remove_basepoint(_id):
  ret = get_basepoint(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


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
                section = data['section'],
                part = data['part'],
                category=data['category'],
                direction=data['direction'],
                length=data['length'],
                tunnel_id=data['tunnel_id'],
                b_accum_length=data['b_accum_length'],
                initial_b_time=data['initial_b_time'],
                left_x_loc=data['left_x_loc'],
                right_x_loc=data['right_x_loc'],
                y_loc=data['y_loc'],
                width=data['width'],
                height=data['height'],
                created_time=cur_time,
                last_updated_time=cur_time,
                last_updated_user=current_user.email,
                basepoint_id=data['basepoint_id'])
  db.session.add(data)
  db.session.commit()


def update_tunnel(data):
  # TODO:
  _id = data['id']
  cur_time = get_servertime()
  _data = get_tunnel(_id)
  _data.name = data['tunnelName']
  _data.section = data['tunnelSection']
  _data.part = data['tunnelPart']
  _data.category = data['category']
  _data.direction = data['tunnelDirection']
  _data.length = data['tunnelLength']
  _data.tunnel_id = data['tunnelId']
  _data.left_x_loc = data['left_x_loc']
  _data.right_x_loc = data['right_x_loc']
  _data.y_loc = data['y_loc']
  _data.width = data['width']
  _data.height = data['height']
  _data.last_updated_time = cur_time
  db.session.commit()
  return _data


def update_tunnel_blast_info(_id, initial_b_time, blasting_length):
  cur_time = get_servertime()
  data = get_tunnel(_id)
  data.initial_b_time = initial_b_time
  data.b_accum_length = blasting_length
  data.last_updated_time = cur_time
  db.session.commit()
  return data


def update_b_acuum_length_by_add_blast(tunnel_id, length):
  data = get_tunnel(tunnel_id)
  data.b_accum_length += length
  db.session.commit()
  return data


def update_b_acuum_length_by_remove_blast(tunnel_id, length):
  data = get_tunnel(tunnel_id)
  data.b_accum_length -= length
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


def get_all_tunnel_by_sort():
  data_list = Tunnel.query.order_by(Tunnel.tunnel_id).all()
  return data_list


def get_all_tunnel_for_csv():
  ret = {
      "C1": {},
      "C2": {},
      "C3": {}}
  data_list = Tunnel.query.order_by(Tunnel.section).all()
  for data in data_list:
    for blast in data.blast_list:
      if blast.blast_info_list[0].blasting_time:
        ret[data.section][blast] = blast.blast_info_list[0].blasting_time.\
            strftime("%Y-%m-%d, %H:%M:%S")
      else:
        ret[data.section][blast] = "0"
  return ret


def get_blast_list_for_csv(tunnel_id):
  if tunnel_id:
    blast_list = db.session.query(Blast).join(Tunnel).\
        filter_by(tunnel_id=tunnel_id).\
        order_by(Tunnel.section, Blast.blasting_time).all()
  else:
    blast_list = db.session.query(Blast).join(Tunnel).\
        order_by(Tunnel.section, Blast.blasting_time).all()
  return blast_list


def create_blasting_detail(data):
  _data = BlastingActInfo(blasting_time=data['blasting_time'],
                          start_point=data['start_point'],
                          finish_point=data['finish_point'],
                          blasting_length=data['blasting_length'],
                          blast_id=data['blast_id'],
                          work_id=data['work_id'])
  db.session.add(_data)
  db.session.commit()


def update_blasting_detail(data):
  _data = get_blasting_data_by_work_id(data['work_id'])
  _data.blasting_time = data['blasting_time'],
  _data.start_point = data['start_point'],
  _data.finish_point = data['finish_point'],
  _data.blasting_length = data['blasting_length'],
  _data.blast_id = data['blast_id'],
  _data.work_id = data['work_id']
  db.session.commit()


def get_blasting_data_by_work_id(work_id):
  data = BlastingActInfo.query.filter_by(work_id=work_id).one_or_none()
  return data


def get_blasting_data_by_blast_id(blast_id, blasting_id):
  data = BlastingActInfo.query.filter_by(blast_id=blast_id, work_id=blasting_id).\
    one_or_none()
  return data


def get_all_blasting():
  data_list = BlastingActInfo.query.all()
  return data_list


def create_charging_detail(data):
  _data = ChargingActInfo(explosive_bulk=data['explosive_bulk'],
                          explosive_cartridge=data['explosive_cartridge'],
                          detonator=data['detonator'],
                          drilling_depth=data['drilling_depth'],
                          team_id=data['team_id'],
                          team_nos=data['team_nos'],
                          blast_id=data['blast_id'],
                          work_id=data['work_id'])
  db.session.add(_data)
  db.session.commit()


def update_charging_detail(data):
  _data = get_charging_data_by_work_id(data['work_id'])
  _data.explosive_bulk = data['explosive_bulk'],
  _data.explosive_cartridge = data['explosive_cartridge'],
  _data.detonator = data['detonator'],
  _data.drilling_depth = data['drilling_depth'],
  _data.team_id = data['team_id'],
  _data.team_nos = data['team_nos']
  db.session.commit()


def get_all_charging():
  data_list = ChargingActInfo.query.all()
  return data_list


def get_charging_data_by_work_id(work_id):
  data = ChargingActInfo.query.filter_by(work_id=work_id).one_or_none()
  return data


def get_charging_data_by_blast_id(blast_id, charging_id):
  data = ChargingActInfo.query.filter_by(blast_id=blast_id, work_id=charging_id).\
    one_or_none()
  return data


def create_blast(data):
  cur_time = get_servertime()
  data = Blast(id=data['id'],
               left_x_loc=data['left_x_loc'],
               right_x_loc=data['right_x_loc'],
               y_loc=data['y_loc'],
               width=data['width'],
               height=data['height'],
               state=data['state'],
               accum_time=data['accum_time'],
               m_accum_time=data['m_accum_time'],
               s_accum_time=data['i_accum_time'],
               i_accum_time=data['s_accum_time'],
               created_time=cur_time,
               last_updated_time=cur_time,
               last_updated_user=current_user.email,
               tunnel_id=data['tunnel_id'])
  db.session.add(data)
  db.session.commit()


def update_blast(data):
  # TODO:
  _id = data['id']
  cur_time = get_servertime()
  _data = get_blast(_id)
  _data.left_x_loc = data['left_x_loc']
  _data.right_x_loc = data['right_x_loc']
  _data.y_loc = data['y_loc']
  _data.width = data['width']
  _data.height = data['height']
  _data.state = data['state']
  _data.accum_time = data['accum_time']
  _data.m_accum_time = data['m_accum_time']
  _data.s_accum_time = data['i_accum_time']
  _data.i_accum_time = data['s_accum_time']
  _data.last_updated_time = cur_time
  db.session.commit()
  return _data


def update_blast_state_and_accum(blast_id, state, accum_time, category,
                                 completed=None):
  cur_time = get_servertime()
  data = get_blast(blast_id)
  data.state = state
  if completed:
    data.accum_time = accum_time
    if category == 0:
      # Main Work
      data.m_accum_time = accum_time
    elif category == 1:
      # Supporting
      data.s_accum_time = accum_time
    else:
      # Idle Time
      data.i_accum_time = accum_time
  else:
    data.accum_time += accum_time
    if category == 0:
      data.m_accum_time += accum_time
    elif category == 1:
      data.s_accum_time += accum_time
    else:
      data.i_accum_time += accum_time
  data.last_updated_time = cur_time
  data.last_updated_user = current_user.email
  db.session.commit()
  return data


def remove_blast(_id):
  ret = get_blast(_id)
  if ret:
    blast_info = get_blast_info_by_blast(_id)
    db.session.delete(blast_info)
    db.session.delete(ret)
    db.session.commit()


def get_blast(_id):
  data = Blast.query.filter_by(id=_id).one_or_none()
  return data


def get_latest_blast_by_tunnel(tunnel_id):
  data = Blast.query.filter_by(tunnel_id=tunnel_id).\
    order_by(desc(Blast.created_time)).all()
  if data:
    return data[0]
  else:
    return None


def get_previous_blast_id(tunnel_id, blast_id):
  id_list = []
  data_list = Blast.query.filter_by(tunnel_id=tunnel_id).\
    order_by(Blast.blasting_time).all()
  for data in data_list:
    id_list.append(data.id)
  blast_index = id_list.index(blast_id)
  if blast_index == 0:
    return None
  else:
    return id_list[blast_index - 1]


def get_next_blast_id(tunnel_id, blast_id):
  id_list = []
  data_list = Blast.query.filter_by(tunnel_id=tunnel_id).\
    order_by(Blast.blasting_time).all()
  for data in data_list:
    id_list.append(data.id)
  blast_index = id_list.index(blast_id)
  if blast_index == len(id_list)-1:
    return None
  else:
    return id_list[blast_index + 1]


def get_blast_list_by_tunnel(tunnel_id):
  data_list = Blast.query.filter_by(tunnel_id=tunnel_id).\
      order_by(desc(Blast.created_time)).all()
  return data_list


def get_recent_blast_list_by_tunnel(tunnel_id, limit=3):
  data_list = Blast.query.filter_by(tunnel_id=tunnel_id).\
      order_by(desc(Blast.created_time)).limit(limit).all()
  return data_list


def get_all_blast():
  data_list = Blast.query.order_by(desc(Blast.created_time)).all()
  return data_list


def create_blast_info(data):
  cur_time = get_servertime()
  if data['blasting_date'] and data['blasting_time']:
    blasting_time = data['blasting_date'] + " " + data['blasting_time']
  else:
    blasting_time = None
  _data = BlastInfo(id=data['id'],
                    explosive_bulk=data['explosive_bulk'],
                    explosive_cartridge=data['explosive_cartridge'],
                    detonator=data['detonator'],
                    drilling_depth=data['drilling_depth'],
                    blasting_time=blasting_time,
                    start_point=data['start_point'],
                    finish_point=data['finish_point'],
                    blasting_length=data['blasting_length'],
                    team_id=data['team_id'],
                    team_nos=data['team_nos'],
                    created_time=cur_time,
                    last_updated_time=cur_time,
                    last_updated_user=current_user.email,
                    blast_id=data['blast_id'])
  db.session.add(_data)
  blast_data = get_blast(data['blast_id'])
  blast_data.blasting_time = blasting_time
  db.session.commit()
  return data


def update_blast_info(data):
  # TODO:
  _id = data['id']
  cur_time = get_servertime()
  _data = get_blast_info(_id)
  _data.explosive_bulk = data['explosive_bulk']
  _data.explosive_cartridge = data['explosive_cartridge']
  _data.detonator = data['detonator']
  _data.drilling_depth = data['drilling_depth']
  _data.blasting_time = data['blasting_time']
  _data.start_point = data['start_point']
  _data.finish_point = data['finish_point']
  _data.blasting_length = data['blasting_length']
  _data.team_id = data['team_id']
  _data.team_nos = data['team_nos']
  _data.last_updated_time = cur_time
  blast_data = get_blast(_data.blast_id)
  blast_data.blasting_time = _data.blasting_time
  db.session.commit()
  return _data


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
              p_accum_time=data['p_accum_time'],
              created_time=cur_time,
              last_updated_time=cur_time,
              last_updated_user=current_user.email,
              blast_id=data['blast_id'])
  db.session.add(data)
  db.session.commit()


def update_work(data):
  # TODO:
  _id = data['id']
  cur_time = get_servertime()
  _data = get_work(_id)
  _work_history_list = get_work_history_list_by_work(_id)
  _blast_data = get_blast(data['blast_id'])
  original_accum_time = 0
  start_history = None
  finish_history = None
  for _work_history in _work_history_list:
    if _work_history.state == 1:
      start_history = _work_history
    elif _work_history.state == 2:
      finish_history = _work_history
      original_accum_time = finish_history.accum_time

  if not start_history or not finish_history:
    logging.warning("Can not find start or finish history. id : %s", _id)
    return False

  if 'start_time' in data:
    start_time = datetime.datetime.fromtimestamp(data['start_time'])
    start_history.timestamp = start_time
    _data.start_time = start_time
  if 'finish_time' in data:
    finish_time = datetime.datetime.fromtimestamp(data['finish_time'])
    finish_history.timestamp = finish_time
    _data.end_time = finish_time

  finish_history.accum_time = data['finish_time'] - data['start_time']
  _data.accum_time = data['finish_time'] - data['start_time']

  if data['typ'] in MAIN_TYPES:
    _blast_data.m_accum_time = _blast_data.m_accum_time - original_accum_time +\
                               _data.accum_time
  elif data['typ'] in SUPPORTING_TYPES:
    _blast_data.s_accum_time = _blast_data.s_accum_time - original_accum_time +\
                                _data.accum_time
  elif data['typ'] in IDLE_TYPES:
    _blast_data.i_accum_time = _blast_data.i_accum_time - original_accum_time +\
                               _data.accum_time
  _blast_data.accum_time = _blast_data.m_accum_time + _blast_data.s_accum_time \
                           + _blast_data.i_accum_time
  _data.category = data['category']
  _data.state = data['state']
  _data.last_updated_time = cur_time
  db.session.commit()
  return _data


def update_state_and_accum(work_id, state, accum_time, pause_time,
                           start_time=None, end_time=None):
  cur_time = get_servertime()
  data = get_work(work_id)
  data.state = state
  data.accum_time = accum_time
  data.p_accum_time = pause_time
  data.last_updated_time = cur_time
  data.start_time = start_time if start_time else data.start_time
  data.end_time = end_time if end_time else data.end_time
  data.last_updated_user = current_user.email
  db.session.commit()
  return data


def remove_work(_id):
  ret = get_work(_id)
  if ret:
    blast_data = get_blast(ret.blast_id)
    if ret.category == 0:
      blast_data.m_accum_time -= ret.accum_time
    elif ret.category == 1:
      blast_data.s_accum_time -= ret.accum_time
    else:
      blast_data.i_accum_time -= ret.accum_time
    blast_data.accum_time -= ret.accum_time
    work_history_list = get_work_history_list_by_work(_id)
    work_equipment_list = get_work_equipment_list_by_work(_id)
    pause_history_list =  get_pause_history_list_by_work(_id)
    for work_history in work_history_list:
      db.session.delete(work_history)
    for work_equipment in work_equipment_list:
      db.session.delete(work_equipment)
    for pause_history in pause_history_list:
      db.session.delete(pause_history)
    if ret.typ == 114:
      blast_data.state = 1
    db.session.delete(ret)
    db.session.commit()


def get_work(_id):
  data = Work.query.filter_by(id=_id).one_or_none()
  return data


def get_latest_work_by_blast(blast_id, typ):
  data = Work.query.filter_by(blast_id=blast_id, typ=typ).\
    order_by(desc(Work.created_time)).all()
  if data:
    return data[0]
  else:
    return None


def get_same_type_by_blast(blast_id, typ):
  data = Work.query.filter_by(blast_id=blast_id, typ=typ).all()
  return data


def get_work_list_by_blast(blast_id):
  data_list = Work.query.filter_by(blast_id=blast_id).\
      order_by(desc(Work.created_time)).all()
  return data_list


def get_charging_id_by_blast(blast_id):
  data = Work.query.filter_by(blast_id=blast_id, typ=113).one_or_none()
  return data.id


def get_blasting_id_by_blast(blast_id):
  data = Work.query.filter_by(blast_id=blast_id, typ=114).one_or_none()
  return data.id


def get_work_list_in_progress():
  data_list = Work.query.filter_by(state=1).all()
  return data_list


def get_all_work():
  data_list = Work.query.filter(or_(Work.state == 1, Work.state == 2)).all()
  return data_list


def create_work_history(data):
  cur_time = get_servertime()
  if 'auto_end' in data:
    auto_end = data['auto_end']
  else:
    auto_end = None
  if 'job_id' in data:
    job_id = data['job_id']
  else:
    job_id = None
  data = WorkHistory(typ=data['typ'],
                     state=data['state'],
                     timestamp=data['timestamp'],
                     accum_time=data['accum_time'],
                     created_time=cur_time,
                     auto_end=auto_end,
                     job_id=job_id,
                     last_updated_user=current_user.email,
                     work_id=data['work_id'])
  db.session.add(data)
  db.session.commit()
  return data


def create_complete_start_work_history(data):
  cur_time = get_servertime()
  start_time = datetime.datetime.fromtimestamp(int(data['timestamp']))
  data = WorkHistory(typ=data['typ'],
                     state=WORK_STATE_IN_PROGRESS,
                     timestamp=start_time,
                     accum_time=data['accum_time'],
                     created_time=cur_time,
                     last_updated_user=current_user.email,
                     work_id=data['work_id'])
  db.session.add(data)
  db.session.commit()
  return data


def create_complete_finish_work_history(data):
  cur_time = get_servertime()
  finish_time = datetime.datetime.fromtimestamp(int(data['timestamp']))
  data = WorkHistory(typ=data['typ'],
                     state=WORK_STATE_FINISH,
                     timestamp=finish_time,
                     accum_time=data['accum_time'],
                     created_time=cur_time,
                     last_updated_user=current_user.email,
                     work_id=data['work_id'])
  db.session.add(data)
  db.session.commit()
  return data


def update_work_history(data, sched=None):
  # TODO:
  if 'auto_end' in data:
    auto_end = data['auto_end']
  else:
    auto_end = None
  if 'job_id' in data:
    job_id = data['job_id']
  else:
    job_id = None
  _id = data['id']
  cur_time = get_servertime()
  _data = get_work_history(_id)
  _data.last_updated_time = cur_time
  _data.typ = data['typ']
  _data.state = data['state'] if 'state' in data else _data.state
  _data.timestamp = data['timestamp'] if 'timestamp' in data else _data.timestamp
  _data.accum_time = data['accum_time']
  _data.auto_end = auto_end
  _data.job_id = job_id
  if not sched:
    _data.last_updated_user = current_user.email
  db.session.commit()
  return _data


def remove_work_history(_id):
  ret = get_work_history(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_work_history(_id):
  data = WorkHistory.query.filter_by(id=_id).one_or_none()
  return data


def get_work_history_list_by_work(work_id):
  data_list = WorkHistory.query.filter_by(work_id=work_id).\
      order_by(WorkHistory.timestamp).all()
  return data_list


def get_finish_work_history_by_work(work_id):
  data = WorkHistory.query.filter_by(work_id=work_id, state=2).one_or_none()
  return data


def get_work_history_have_auto_end(work_id):
  data = None
  data_list = WorkHistory.query.filter_by(work_id=work_id, state=1).\
      order_by(WorkHistory.timestamp).all()
  for _data in data_list:
    if _data.auto_end:
      data = _data
  return data


def get_all_work_history():
  data_list = WorkHistory.query.all()
  return data_list


def get_all_work_history_for_auto_end():
  data_list = []
  _data_list = WorkHistory.query.filter_by(state=1).all()
  for data in _data_list:
    if data.auto_end:
      data_list.append(data)
  return data_list


def create_pause_history(data):
  cur_time = get_servertime()
  data = PauseHistory(start_time=data['start_time'],
                      end_time=data['end_time'],
                      accum_time=data['accum_time'],
                      message=data['message'],
                      created_time=cur_time,
                      last_updated_user=current_user.email,
                      work_id=data['work_id'])
  db.session.add(data)
  db.session.commit()
  return data


def update_pause_history_end_time(_id, end_time, pause_time):
  # TODO:
  cur_time = get_servertime()
  data = get_pause_history(_id)
  data.end_time = end_time
  data.accum_time += pause_time
  data.last_updated_time = cur_time
  db.session.commit()
  return data


def remove_pause_history(_id):
  ret = get_pause_history(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_pause_history(_id):
  data = PauseHistory.query.filter_by(id=_id).one_or_none()
  return data


def get_pause_history_list_by_work(work_id):
  data_list = PauseHistory.query.filter_by(work_id=work_id).all()
  return data_list


def get_all_pause_history():
  data_list = PauseHistory.query.all()
  return data_list


def create_activity(data):
  cur_time = get_servertime()
  data = Activity(name=data['name'],
                  category=data['category'],
                  activity_id=data['activity_id'],
                  file_path=data['file_path'],
                  created_time=cur_time,
                  last_updated_user=current_user.email if current_user else "Auto",
                  last_updated_time=cur_time)
  db.session.add(data)
  db.session.commit()


def remove_activity(_id):
  ret = get_activity(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_activity(_id):
  data = Activity.query.filter_by(id=_id).one_or_none()
  return data


def get_activity_by_activity_id(activity_id):
  data = Activity.query.filter_by(activity_id=activity_id).one_or_none()
  return data


def get_activity_by_last_id(category):
  data_list = Activity.query.filter_by(category=category).\
      order_by(desc(Activity.activity_id)).all()
  return data_list[0]


def get_all_activity():
  data_list = Activity.query.all()
  return data_list


def get_all_main_activity():
  data_list = Activity.query.filter_by(category=0).\
      order_by(Activity.activity_id).all()
  return data_list


def get_all_support_activity():
  data_list = Activity.query.filter_by(category=1).\
      order_by(Activity.activity_id).all()
  return data_list


def get_all_idle_activity():
  data_list = Activity.query.filter_by(category=2).\
      order_by(Activity.activity_id).all()
  return data_list


def update_activity(data):
  cur_time = get_servertime()
  _data = get_activity(data['id'])
  _data.name = data['name']
  _data.category = data['category']
  _data.activity_id = data['activity_id']
  _data.file_path = data['file_path']
  _data.last_updated_time = cur_time
  _data.last_updated_user = current_user.email
  db.session.commit()
  return _data


def create_operator(data):
  cur_time = get_servertime()
  data = Operator(name=data['name'],
                  operator_id=data['operator_id'],
                  # department=data['department'],
                  category=data['category'],
                  created_time=cur_time,
                  last_updated_user=current_user.email,
                  last_updated_time=cur_time)
  db.session.add(data)
  db.session.commit()


def update_operator(data):
  cur_time = get_servertime()
  _data = get_operator(data['id'])
  _data.name = data['name']
  _data.category = data['category']
  _data.operator_id = data['operator_id']
  _data.last_updated_time = cur_time
  _data.last_updated_user = current_user.email
  db.session.commit()


def create_equipment(data):
  cur_time = get_servertime()
  data = Equipment(name=data['name'],
                   category=data['category'],
                   equipment_id=data['equipment_id'],
                   created_time=cur_time,
                   last_updated_user=current_user.email,
                   last_updated_time=cur_time)
  db.session.add(data)
  db.session.commit()


def update_equipment(data):
  cur_time = get_servertime()
  _data = get_equipment(data['id'])
  _data.name = data['name']
  _data.category = data['category']
  _data.equipment_id = data['equipment_id']
  _data.last_updated_time = cur_time
  _data.last_updated_user = current_user.email
  db.session.commit()


def remove_equipment(_id):
  ret = get_equipment(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_equipment(_id):
  data = Equipment.query.filter_by(id=_id).one_or_none()
  return data


def get_all_equipment():
  data_list = Equipment.query.all()
  return data_list


def remove_operator(_id):
  ret = get_operator(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_operator(_id):
  data = Operator.query.filter_by(id=_id).one_or_none()
  return data


def get_all_operator():
  data_list = Operator.query.all()
  return data_list


def create_work_equipment(data):
  cur_time = get_servertime()
  data = WorkEquipment(category=data['category'],
                       equipment_id=data['equipment_id'],
                       operator_id=data['operator_id'],
                       accum_time=data['accum_time'],
                       p_accum_time=data['p_accum_time'],
                       created_time=cur_time,
                       last_updated_user=current_user.email,
                       last_updated_time=cur_time,
                       work_id=data['work_id'])
  db.session.add(data)
  db.session.commit()
  return data


def remove_work_equipment(_id):
  ret = get_work_equipment(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_work_equipment(_id):
  data = WorkEquipment.query.filter_by(id=_id).one_or_none()
  return data


def get_work_equipment_list_by_work(work_id):
  data = WorkEquipment.query.filter_by(work_id=work_id).all()
  return data


def get_all_work_equipment():
  data_list = WorkEquipment.query.all()
  return data_list


def search(tunnel_id, tunnel, activity, datetime_list, next_num=None):
  st_date = datetime.datetime(*[int(x) for x in datetime_list[0].split(",")])
  end_date = datetime.datetime(*[int(x) for x in datetime_list[1].split(",")])
  all_work_query = db.session.query(Work)
  filter_list = []
  t1_filter_list = [
    Work.state == 1,
    Work.start_time > st_date,
    Work.start_time < end_date,
  ]
  t2_filter_list = [
    Work.state == 2,
    Work.start_time > st_date,
    Work.end_time < end_date,
  ]
  if not next_num:
    next_num = 1
  if tunnel_id:
    filter_list.append(Tunnel.tunnel_id == tunnel_id)
  if tunnel != 10000:
    filter_list.append(Tunnel.category == tunnel)
  if activity != 10000:
    t1_filter_list.append(Work.typ == activity)
    t2_filter_list.append(Work.typ == activity)
  t1_query = all_work_query.filter(*t1_filter_list)
  t2_query = all_work_query.filter(*t2_filter_list)
  base_query = t1_query.union(t2_query).order_by(Work.start_time)

  try:
    work_list = base_query.join(Blast).join(Tunnel).filter(*filter_list)
    return work_list.paginate(int(next_num), 100, False)
  except:
    logging.exception("Raise Error by Search.")


def create_team(data):
  cur_time = get_servertime()
  data = Team(category=data['category'],
              name=data['name'],
              engineer=data['engineer'],
              member=data['member'],
              created_time=cur_time,
              last_updated_user=current_user.email,
              last_updated_time=cur_time)
  db.session.add(data)
  db.session.commit()
  return data


def update_team(data):
  cur_time = get_servertime()
  _data = get_team(data['id'])
  _data.name = data['name']
  _data.engineer = data['engineer']
  _data.member = data['member']
  _data.last_updated_time = cur_time
  _data.last_updated_user = current_user.email
  db.session.commit()


def remove_team(_id):
  ret = get_team(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_team(_id):
  data = Team.query.filter_by(id=_id).one_or_none()
  return data


def get_all_team():
  data_list = Team.query.all()
  return data_list


def create_message(data):
  cur_time = get_servertime()
  data = Message(category=data['category'],
                 message=data['message'],
                 created_time=cur_time,
                 last_updated_user=current_user.email,
                 last_updated_time=cur_time)
  db.session.add(data)
  db.session.commit()
  return data


def update_message(data):
  cur_time = get_servertime()
  _data = get_message(data['id'])
  _data.message = data['message']
  _data.last_updated_time = cur_time
  _data.last_updated_user = current_user.email
  db.session.commit()


def remove_message(_id):
  ret = get_message(_id)
  if ret:
    db.session.delete(ret)
    db.session.commit()


def get_message(_id):
  data = Message.query.filter_by(id=_id).one_or_none()
  return data


def get_all_message():
  data_list = Message.query.all()
  return data_list


def csv_work_log(tunnel_id, tunnel, activity, datetime_list):
  st_date = datetime.datetime(*[int(x) for x in datetime_list[0].split(",")])
  end_date = datetime.datetime(*[int(x) for x in datetime_list[1].split(",")])
  all_work_query = db.session.query(Work)
  filter_list = []
  t1_filter_list = [
    Work.state == 1,
    Work.start_time > st_date,
    Work.start_time < end_date,
  ]
  t2_filter_list = [
    Work.state == 2,
    Work.start_time > st_date,
    Work.end_time < end_date,
  ]
  if tunnel_id:
    filter_list.append(Tunnel.tunnel_id == tunnel_id)
  if tunnel != 10000:
    filter_list.append(Tunnel.category == tunnel)
  if activity != 10000:
    t1_filter_list.append(Work.typ == activity)
    t2_filter_list.append(Work.typ == activity)
  t1_query = all_work_query.filter(*t1_filter_list)
  t2_query = all_work_query.filter(*t2_filter_list)
  base_query = t1_query.union(t2_query).order_by(Work.start_time)

  log_list = base_query.join(Blast).join(Tunnel). \
    filter(*filter_list).all()
  return log_list
