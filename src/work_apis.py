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
from work_models import _PauseHistory as PauseHistory
from work_models import _Activity as Activity
from work_models import _Equipment as Equipment
from work_models import _Operator as Operator
from work_models import _WorkEquipment as WorkEquipment
from work_models import _Team as Team
from work_models import _Message as Message
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
                x_loc=data['x_loc'],
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
  _data.x_loc = data['x_loc']
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
  #TODO
  #data.b_accum_length = blasting_length
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


def create_blast(data):
  cur_time = get_servertime()
  data = Blast(id=data['id'],
               x_loc=data['x_loc'],
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
  _data.x_loc = data['x_loc']
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


def update_blast_state_and_accum(blast_id, state, accum_time, category):
  cur_time = get_servertime()
  data = get_blast(blast_id)
  data.state = state
  data.accum_time += accum_time
  if category == 0:
    # Main Work
    data.m_accum_time += accum_time
  elif category == 1:
    # Supporting
    data.s_accum_time += accum_time
  else:
    # Idle Time
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


def get_blast_list_by_tunnel(tunnel_id):
  data_list = Blast.query.filter_by(tunnel_id=tunnel_id).\
      order_by(desc(Blast.created_time)).all()
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
  for _work_history in _work_history_list:
    if _work_history.state == 1:
      start_history = _work_history
    elif _work_history.state == 2:
      finish_history = _work_history
      original_accum_time = finish_history.accum_time
  if 'start_time' in data:
    start_history.timestamp = datetime.datetime.\
        fromtimestamp(data['start_time'])
  if 'finish_time' in data:
    finish_history.timestamp = datetime.datetime.\
        fromtimestamp(data['finish_time'])

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


def update_state_and_accum(work_id, state, accum_time, pause_time):
  cur_time = get_servertime()
  data = get_work(work_id)
  data.state = state
  data.accum_time = accum_time
  data.p_accum_time = pause_time
  data.last_updated_time = cur_time
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
  data = Work.query.filter_by(blast_id=blast_id, typ=typ).all()
  if data:
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
                  created_time=cur_time,
                  last_updated_user=current_user.email,
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


def get_all_activity():
  data_list = Activity.query.all()
  return data_list


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
  data = WorkEquipment(equipment_id=data['equipment_id'],
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


def search(tunnel_id, tunnel, direction, datetime_list, next_num=None):
  st_date = datetime.datetime(*[int(x) for x in datetime_list[0].split(",")])
  end_date = datetime.datetime(*[int(x) for x in datetime_list[1].split(",")])
  filter_list = []
  t_filter_list = [
    WorkHistory.timestamp > st_date,
    WorkHistory.timestamp < end_date
  ]
  if not next_num:
    next_num = 1
  if tunnel_id:
    filter_list.append(Tunnel.tunnel_id == tunnel_id)
  # if worker_name:
  #   filter_list.append(EnterenceWorkerLog.worker_name.like("%" + worker_name + "%"))
  if tunnel != 10000:
    filter_list.append(Tunnel.category == tunnel)
  if direction != 10000:
    filter_list.append(Tunnel.direction == direction)
  try:
    work_list = db.session.query(WorkHistory).filter(*t_filter_list).\
        join(Work).join(Blast).join(Tunnel).filter(*filter_list).\
        paginate(int(next_num), 100, False)
    return work_list
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


def csv_work_log(tunnel_id, tunnel, direction, datetime_list):
  st_date = datetime.datetime(*[int(x) for x in datetime_list[0].split(",")])
  end_date = datetime.datetime(*[int(x) for x in datetime_list[1].split(",")])
  filter_list = []
  t_filter_list = [
    WorkHistory.timestamp > st_date,
    WorkHistory.timestamp < end_date
  ]
  if tunnel != 10000:
    filter_list.append(Tunnel.category == tunnel)
  if direction != 10000:
    filter_list.append(Tunnel.direction == direction)
  log_list = db.session.query(WorkHistory).filter(*t_filter_list). \
              join(Work).join(Blast).join(Tunnel).filter(*filter_list). \
              order_by(Tunnel.tunnel_id, WorkHistory.created_time).all()
  return log_list
