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

import os
import json
import time
import uuid
import logging
import requests
import datetime
from flask import request, render_template, redirect
from flask import make_response

import util
import constants
import work_apis
import in_config_apis
import dashboard.count
from work import blueprint
from constants import API_SERVER
from constants import WORK_STATE_STOP, WORK_STATE_IN_PROGRESS
from constants import WORK_STATE_FINISH
from apscheduler.schedulers.gevent import GeventScheduler


SCHED_DATA = {}
sched = GeventScheduler()

HEADERS = {
  'Content-Type': 'application/json'
}

BASEPOINT_ADD = '''basepoint.added'''
BASEPOINT_REMOVE = '''basepoint.removed'''
BASEPOINT_UPDATE = '''basepoint.updated'''
TUNNEL_ADD = '''tunnel.added'''
TUNNEL_REMOVE = '''tunnel.removed'''
TUNNEL_UPDATE = '''tunnel.updated'''
BLAST_ADD = '''blast.added'''
BLAST_REMOVE = '''blast.removed'''
BLAST_UPDATE = '''blast.updated'''
BLAST_INFO_ADD = '''blastinfo.added'''
BLAST_INFO_REMOVE = '''blastinfo.removed'''
BLAST_INFO_UPDATE = '''blastinfo.updated'''
WORK_ADD = '''work.added'''
WORK_UPDATE = '''work.updated'''
WORK_REMOVE = '''work.removed'''
WORK_HISTORY_ADD = '''workhistory.added'''
WORK_HISTORY_UPDATE = '''workhistory.updated'''
WORK_HISTORY_REMOVE = '''workhistory.removed'''
PAUSE_HISTORY_ADD = '''pausehistory.added'''
PAUSE_HISTORY_UPDATE = '''pausehistory.updated'''
PAUSE_HISTORY_REMOVE = '''pausehistory.removed'''
WORK_EQUIPMENT_ADD = '''workequipment.added'''
WORK_EQUIPMENT_UPDATE = '''workequipment.updated'''
WORK_EQUIPMENT_REMOVE = '''workequipment.removed'''
MESSAGE_ADD = '''message.added'''
MESSAGE_UPDATE = '''message.updated'''
MESSAGE_REMOVE = '''message.removed'''
TEAM_ADD = '''team.added'''
TEAM_UPDATE = '''team.updated'''
TEAM_REMOVE = '''team.removed'''
ACTIVITY_ADD = '''activity.added'''
ACTIVITY_REMOVE = '''activity.removed'''
ACTIVITY_UPDATE = '''activity.updated'''
INIT_DATA = '''0'''


def _convert_dict_by_basepoint(data):
    return {
        "id": data.id,
        "name": data.name,
        "x_loc": data.x_loc,
        "y_loc": data.y_loc,
        "height": data.height,
        "width": data.width
    }


def _convert_dict_by_tunnel(data, is_exclude=False):
  ret = {
      "id": data.id,
      "name": data.name,
      "section": data.section,
      "part": data.part,
      "category": data.category,
      "direction": data.direction,
      "length": data.length,
      "tunnel_id": data.tunnel_id,
      "b_accum_length": data.b_accum_length,
      "initial_b_time": str(data.initial_b_time).replace(' ', 'T'),
      "left_x_loc": data.left_x_loc,
      "right_x_loc": data.right_x_loc,
      "y_loc": data.y_loc,
      "width": data.width,
      "height": data.height,
      "basepoint_id": data.basepoint_id
  }
  if not is_exclude:
    blast_list = []
    for blast in data.blast_list:
      blast_list.append(_convert_dict_by_blast(blast))
    ret['blast_list'] = blast_list
  return ret


def _convert_dict_by_blast(data, is_exclude=False):
  ret = {
      "id": data.id,
      "left_x_loc": data.left_x_loc,
      "right_x_loc": data.right_x_loc,
      "y_loc": data.y_loc,
      "width": data.width,
      "height": data.height,
      "state": data.state,
      "accum_time": data.accum_time,
      "m_accum_time": data.m_accum_time,
      "s_accum_time": data.s_accum_time,
      "i_accum_time": data.i_accum_time,
      "tunnel_id": data.tunnel_id,
      "blast_info": _convert_dict_by_blast_info(data.blast_info_list[0])
  }
  if not is_exclude:
    work_list = []
    for work in data.work_list:
      work_list.append(_convert_dict_by_work(work))
    ret['work_list'] = work_list
  return ret


def _convert_dict_by_blast_info(data):
  return {
      "id": data.id,
      "explosive_bulk": data.explosive_bulk,
      "explosive_cartridge": data.explosive_cartridge,
      "detonator": data.detonator,
      "drilling_depth": data.drilling_depth,
      "blasting_time": str(data.blasting_time) if data.blasting_time else None,
      "start_point": data.start_point,
      "finish_point": data.finish_point,
      "blasting_length": data.blasting_length,
      "team_id": data.team_id,
      "team_nos": data.team_nos,
      "blast_id": data.blast_id
  }


def _convert_dict_by_work(data, is_exclude=False):
  ret = {
      "id": data.id,
      "category": data.category,
      "typ": data.typ,
      "state": data.state,
      "accum_time": data.accum_time,
      "p_accum_time": data.p_accum_time,
      "last_updated_time": str(data.last_updated_time).replace(' ', 'T'),
      "blast_id": data.blast_id
  }
  if not is_exclude:
    history_list = []
    if len(data.work_history_list) == 2:
      if data.work_history_list[0].state == 1:
        data.work_history_list.append(data.work_history_list[0])
        del data.work_history_list[0]
    for work_history in data.work_history_list:
      history_list.append(_convert_dict_by_work_history(work_history))
    ret['work_history_list'] = history_list
    pause_list = []
    for pause_history in data.pause_history_list:
      pause_list.append(_convert_dict_by_pause_history(pause_history))
    ret['pause_history_list'] = pause_list
    work_equipment_list = []
    for work_equipment in data.work_equipment_list:
      work_equipment_list.append(_convert_dict_by_work_equipment(work_equipment))
    ret['work_equipment_list'] = work_equipment_list
  return ret


def _convert_dict_by_work_history(data):
  return {
      "id": data.id,
      "typ": data.typ,
      "state": data.state,
      "timestamp": str(data.timestamp).replace(' ', 'T'),
      "accum_time": data.accum_time,
      "work_id": data.work_id
  }


def _convert_dict_by_pause_history(data):
  return {
      "id": data.id,
      "start_time": str(data.start_time).replace(' ', 'T'),
      "end_time": str(data.end_time).replace(' ', 'T'),
      "accum_time": data.accum_time,
      "message": data.message,
      "work_id": data.work_id
  }


def _convert_dict_by_activity(data):
  return {
      "id": data.id,
      "name": data.name,
      "category": data.category,
      "activity_id": data.activity_id,
      "file_path": data.file_path,
      "order": data.order
  }


def _convert_dict_by_equipment(data):
  return {
      "id": data.id,
      "name": data.name,
      "category": data.category,
      "equipment_id": data.equipment_id
  }


def _convert_dict_by_operator(data):
  return {
      "id": data.id,
      "name": data.name,
      "operator_id": data.operator_id,
      "department": data.department,
      "category": data.category
  }


def _convert_dict_by_work_equipment(data):
  return {
    "id": data.id,
    "category": data.category,
    "equipment_id": data.equipment_id,
    "operator_id": data.operator_id,
    "accum_time": data.accum_time,
    "p_accum_time": data.p_accum_time,
    "work_id": data.work_id
  }


def _convert_dict_by_message(data):
  return {
      "id": data.id,
      "category": data.category,
      "message": data.message
  }


def _convert_dict_by_team(data):
  return {
      "id": data.id,
      "category": data.category,
      "name": data.name,
      "engineer": data.engineer,
      "member": data.member
  }


@blueprint.route('/basepoint/add', methods=["POST"])
@util.require_login
def add_basepoint():
  data = request.get_json()
  try:
    work_apis.create_basepoint(data)
    send_request(BASEPOINT_ADD, [data])
    return json.dumps(True)
  except:
    logging.exception("Fail to add basepoint.")
    return json.dumps(False)


@blueprint.route('/basepoint/update', methods=["POST"])
@util.require_login
def update_basepoint():
  data = request.get_json()
  try:
    ret = work_apis.update_basepoint(data)
    resp_data = _convert_dict_by_basepoint(ret)
    send_request(BASEPOINT_UPDATE, [resp_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to update basepoint. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/basepoint/remove', methods=["POST"])
@util.require_login
def remove_basepoint():
  data = request.get_json()
  try:
    work_apis.remove_basepoint(data['id'])
    send_request(BASEPOINT_REMOVE, [data['id']])
    return json.dumps(True)
  except:
    logging.exception("Fail to remove basepoint. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/basepoint/get/list', methods=["GET"])
@util.require_login
def get_basepoint_list():
  ret_list = []
  datas = work_apis.get_all_basepoint()
  try:
    for data in datas:
      ret_list.append(_convert_dict_by_basepoint(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get basepoint list.")
    return json.dumps(ret_list)


@blueprint.route('/tunnel/add', methods=["POST"])
@util.require_login
def add_tunnel():
  data = request.get_json()
  try:
    work_apis.create_tunnel(data)
    send_data = work_apis.get_tunnel(data['id'])
    send_request(TUNNEL_ADD, [_convert_dict_by_tunnel(send_data)])
    return json.dumps(True)
  except:
    logging.exception("Fail to add tunnel.")
    return json.dumps(False)


@blueprint.route('/tunnel/update', methods=["POST"])
@util.require_login
def update_tunnel():
  data = request.get_json()
  try:
    ret = work_apis.update_tunnel(data)
    resp_data = _convert_dict_by_tunnel(ret)
    send_request(TUNNEL_UPDATE, [resp_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to update tunnel. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/tunnel/remove', methods=["POST"])
@util.require_login
def remove_tunnel():
  data = request.get_json()
  try:
    work_apis.remove_tunnel(data['id'])
    send_request(TUNNEL_REMOVE, [data['id']])
    return json.dumps(True)
  except:
    logging.exception("Fail to remove tunnel. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/tunnel/get/list/basepoint', methods=["POST"])
@util.require_login
def get_tunnel_list_by_basepoint():
  data = request.get_json()
  ret_list = []
  try:
    datas = work_apis.get_tunnel_list_by_basepoint(data['basepoint_id'])
    for data in datas:
      ret_list.append(_convert_dict_by_tunnel(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get tunnel list by basepoint.")
    return json.dumps(ret_list)


@blueprint.route('/tunnel/get/list', methods=["GET"])
@util.require_login
def get_tunnel_list(is_exclude=False):
  ret_list = []
  datas = work_apis.get_all_tunnel()
  try:
    for data in datas:
      ret_list.append(_convert_dict_by_tunnel(data, is_exclude=is_exclude))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get tunnel list")
    return json.dumps(ret_list)


@blueprint.route('/blast/add', methods=["POST"])
@util.require_login
def add_blast():
  data = request.get_json()
  try:
    # Blast Data
    blast_data = data['blast']
    work_apis.create_blast(blast_data)
    # Blast Info Data
    blast_info_data = data['info']
    work_apis.create_blast_info(blast_info_data)

    blast_data = work_apis.get_blast(blast_data['id'])
    _tunnel_data = work_apis.get_tunnel(blast_data.tunnel_id)
    send_request(BLAST_INFO_ADD, [blast_info_data])
    send_request(BLAST_ADD, [_convert_dict_by_blast(blast_data)])
    send_request(TUNNEL_UPDATE, [_convert_dict_by_tunnel(_tunnel_data)])
    return json.dumps(True)
  except:
    logging.exception("Fail to add blast.")
    return json.dumps(False)


@blueprint.route('/blast/update', methods=["POST"])
@util.require_login
def update_blast():
  data = request.get_json()
  try:
    # TODO:
    ret = work_apis.update_blast(data)
    resp_data = _convert_dict_by_blast(ret)
    send_request(BLAST_UPDATE, [resp_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to update blast. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/blast/remove', methods=["POST"])
@util.require_login
def remove_blast():
  data = request.get_json()
  try:
    tunnel_id = work_apis.get_blast(data['id']).tunnel_id
    work_apis.remove_blast(data['id'])
    send_request(BLAST_REMOVE, [data['id']])
    tunnel_data = work_apis.get_tunnel(tunnel_id)
    _tunnel_data = _convert_dict_by_tunnel(tunnel_data)
    send_request(TUNNEL_UPDATE, [_tunnel_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to remove blast. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/blast/get/list/tunnel', methods=["POST"])
@util.require_login
def get_blast_list_by_tunnel(tunnel_id=None, is_exclude=False):
  _tunnel_id = None
  if tunnel_id:
    _tunnel_id = tunnel_id
  else:
    _data = request.get_json()
    _tunnel_id = _data['tunnel_id']
  ret_list = []
  try:
    datas = work_apis.get_blast_list_by_tunnel(_tunnel_id)
    for data in datas:
      ret_list.append(_convert_dict_by_blast(data, is_exclude=is_exclude))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get blast list by tunnel.")
    return json.dumps(ret_list)


@blueprint.route('/blast/get/list', methods=["GET"])
@util.require_login
def get_blast_list(is_exclude=False):
  ret_list = []
  datas = work_apis.get_all_blast()
  try:
    for data in datas:
      ret_list.append(_convert_dict_by_blast(data, is_exclude=is_exclude))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get blast list.")
    return json.dumps(ret_list)


@blueprint.route('/blastinfo/add', methods=["POST"])
@util.require_login
def add_blast_info():
  data = request.get_json()
  try:
    data = work_apis.create_blast_info(data)
    send_request(BLAST_INFO_ADD, [_convert_dict_by_blast_info(data)])
    return json.dumps(True)
  except:
    logging.exception("Fail to add blast info.")
    return json.dumps(False)


@blueprint.route('/blastinfo/update', methods=["POST"])
@util.require_login
def update_blast_info():
  data = request.get_json()
  _blast_info = data['info']
  _blast = data['blast']
  try:
    old_info = work_apis.get_blast_info(_blast_info['id'])
    old_length = old_info.blasting_length
    old_b_time = old_info.blasting_time

    work_apis.update_blast_info(_blast_info)
    ret = work_apis.update_blast(_blast)
    resp_data = _convert_dict_by_blast(ret)
    send_request(BLAST_INFO_UPDATE, [resp_data])

    init_b_time = ret.tunnel.initial_b_time
    blasting_length = ret.tunnel.b_accum_length
    if not init_b_time:
      init_b_time = ret.blasting_time
    elif init_b_time == old_b_time:
      init_b_time = ret.blasting_time

    if int(old_length) != 0:
      if old_length != _blast_info['blasting_length']:
        blasting_length -= old_length
        blasting_length += _blast_info['blasting_length']
    else:
      blasting_length += _blast_info['blasting_length']
    t_ret = work_apis.update_tunnel_blast_info(ret.tunnel.id,
                                               init_b_time, blasting_length)
    send_request(TUNNEL_UPDATE, [_convert_dict_by_tunnel(t_ret)])
    return json.dumps(True)
  except:
    logging.exception("Fail to update blast info. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/blastinfo/remove', methods=["POST"])
@util.require_login
def remove_blast_info():
  data = request.get_json()
  try:
    work_apis.remove_blast_info(data['id'])
    send_request(BLAST_INFO_REMOVE, [data['id']])
    return json.dumps(True)
  except:
    logging.exception("Fail to remove blast info. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/blastinfo/get/blast', methods=["POST"])
@util.require_login
def get_blast_info_by_blast(blast_id=None):
  _blast_id = None
  if blast_id:
    _blast_id = blast_id
  else:
    data = request.get_json()
    _blast_id = data['blast_id']
  try:
    ret = work_apis.get_blast_info_by_blast(_blast_id)
    return json.dumps(_convert_dict_by_blast_info(ret))
  except:
    logging.exception("Fail to get blast info by blast.")
    return json.dumps({})


@blueprint.route('/blastinfo/get/list', methods=["GET"])
@util.require_login
def get_blast_info_list():
  ret_list = []
  datas = work_apis.get_all_blast_info()
  try:
    for data in datas:
      ret_list.append(_convert_dict_by_blast_info(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get blast info list.")
    return json.dumps(ret_list)


@blueprint.route('/work/add', methods=["POST"])
@util.require_login
def add_work(work_data=None, is_auto=False):
  auto_add = is_auto
  if work_data:
    data = work_data
  else:
    data = request.get_json()
  try:
    #latest_work = work_apis.get_latest_work_by_blast(data['blast_id'])
    #if latest_work:
    #  if latest_work.state != constants.WORK_STATE_COMPLETE:
    #    return json.dumps(False)
    #  else:
    #    work_apis.create_work(data)
    #else:
      # Blast work(first cycle)
    #  work_apis.create_work(data)
    work_apis.create_work(data)
    send_request(WORK_ADD, [data])
    blast_data = work_apis.get_blast(data['blast_id'])
    _blast_data = _convert_dict_by_blast(blast_data)
    send_request(BLAST_UPDATE, [_blast_data])
    if auto_add:
      auto_start_data = {
          'id': data['id'],
          'category': data['category'],
          'typ': data['typ'],
          'blast_id': data['blast_id']
      }
      start_work(auto_start_data)
    return json.dumps(True)
  except:
    logging.exception("Fail to add work.")
    return json.dumps(False)


@blueprint.route('/work/add/completed', methods=["POST"])
@util.require_login
def add_completed_work():
  data = request.get_json()
  try:
    #TODO: send : work -> blast -> start -> finish
    work_apis.create_work(data)
    send_request(WORK_ADD, [data])
    _create_start_work_log(data)
    _create_finish_work_log(data)
    return json.dumps(True)
  except:
    logging.exception("Fail to add work.")
    return json.dumps(False)


def _create_start_work_log(data):
  try:
    history_data = {
        'typ': data['typ'],
        'work_id': data['id']
    }
    latest_work = work_apis.get_latest_work_by_blast(data['blast_id'],
                                                     data['typ'])
    if latest_work and latest_work.work_history_list:
      _data = latest_work.work_history_list[0]
      # Start work History
      history_data['state'] = WORK_STATE_IN_PROGRESS
      history_data['timestamp'] = data['start_time']
      history_data['accum_time'] = 0
      _data = work_apis.create_complete_start_work_history(history_data)
      send_request(WORK_HISTORY_ADD,
                   [_convert_dict_by_work_history(_data)])
    else:
      # Init data
      history_data['state'] = WORK_STATE_IN_PROGRESS
      history_data['timestamp'] = data['start_time']
      history_data['accum_time'] = 0
      pause_time = 0
      _data = work_apis.create_complete_start_work_history(history_data)
      send_request(WORK_HISTORY_ADD,
                  [_convert_dict_by_work_history(_data)])
  except:
    logging.exception("Failed to start work. Data : %s", data)


def _create_finish_work_log(data):
  try:
    history_data = {
        'typ': data['typ'],
        'work_id': data['id']
    }
    latest_work = work_apis.get_latest_work_by_blast(data['blast_id'],
                                                     data['typ'])
    if latest_work and latest_work.work_history_list:
      _data = latest_work.work_history_list[0]
      # Finish work history
      history_data['state'] = WORK_STATE_FINISH
      history_data['timestamp'] = data['finish_time']
      history_data['accum_time'] = data['accum_time']
      _data = work_apis.create_complete_finish_work_history(history_data)
      send_request(WORK_HISTORY_ADD,
                   [_convert_dict_by_work_history(_data)])
      pause_time = 0
      start_time = datetime.datetime.fromtimestamp(data['start_time'])
      end_time = datetime.datetime.fromtimestamp(data['finish_time'])
      work_data = work_apis.update_state_and_accum(data['id'],
                                                   history_data['state'],
                                                   history_data['accum_time'],
                                                   pause_time,
                                                   start_time,
                                                   end_time)
      send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
      if int(data['typ']) == 114:  # finish work, 114 is blasting activity
        blast_data = work_apis.update_blast_state_and_accum(data['blast_id'], 2,
                                                            history_data['accum_time'],
                                                            latest_work.category)
      else:
        blast_data = work_apis.update_blast_state_and_accum(data['blast_id'], 1,
                                                            history_data['accum_time'],
                                                            latest_work.category)
      send_request(BLAST_UPDATE, [_convert_dict_by_blast(blast_data)])
  except:
    logging.exception("Failed to stop work. Data : %s", data)


@blueprint.route('/work/update', methods=["POST"])
@util.require_login
def update_work():
  data = request.get_json()
  try:
    # TODO:
    ret = work_apis.update_work(data)
    resp_data = _convert_dict_by_work(ret)
    blast_data = work_apis.get_blast(ret.blast_id)
    _blast_data = _convert_dict_by_blast(blast_data)
    send_request(WORK_UPDATE, [resp_data])
    send_request(BLAST_UPDATE, [_blast_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to update work. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/work/remove', methods=["POST"])
@util.require_login
def remove_work():
  data = request.get_json()
  try:
    blast_id = work_apis.get_work(data['id']).blast_id
    work_apis.remove_work(data['id'])
    send_request(WORK_REMOVE, [data['id']])
    blast_data = work_apis.get_blast(blast_id)
    _blast_data = _convert_dict_by_blast(blast_data)
    send_request(BLAST_UPDATE, [_blast_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to remove work. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/work/get/list/blast', methods=["POST"])
@util.require_login
def get_work_list_by_blast(blast_id=None, is_exclude=False):
  _blast_id = None
  if blast_id:
    _blast_id = blast_id
  else:
    data = request.get_json()
    _blast_id = data['blast_id']
  ret_list = []
  try:
    datas = work_apis.get_work_list_by_blast(_blast_id)
    for data in datas:
      ret_list.append(_convert_dict_by_work(data, is_exclude=is_exclude))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get work list by blast.")
    return json.dumps(ret_list)


@blueprint.route('/work/get/list', methods=["GET"])
@util.require_login
def get_work_list(is_exclude=False):
  ret_list = []
  try:
    datas = work_apis.get_all_work()
    for data in datas:
      ret_list.append(_convert_dict_by_work(data, is_exclude=is_exclude))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get work list.")
    return json.dumps(ret_list)


@blueprint.route('/workhistory/add', methods=["POST"])
@util.require_login
def add_work_history():
  data = request.get_json()
  try:
    data = work_apis.create_work_history(data)
    send_request(WORK_HISTORY_ADD, [_convert_dict_by_work_history(data)])
    return json.dumps(True)
  except:
    logging.exception("Fail to add work history.")
    return json.dumps(False)


@blueprint.route('/workhistory/update', methods=["POST"])
@util.require_login
def update_work_history():
  data = request.get_json()
  try:
    # TODO:
    ret = work_apis.update_work_history(data)
    resp_data = _convert_dict_by_work_history(ret)
    send_request(WORK_HISTORY_UPDATE,
                 [_convert_dict_by_work_history(resp_data)])
    return json.dumps(True)
  except:
    logging.exception("Fail to update work history. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/workhistory/remove', methods=["POST"])
@util.require_login
def remove_work_history():
  data = request.get_json()
  try:
    work_apis.remove_work_history(data['id'])
    send_request(WORK_HISTORY_REMOVE, [data['id']])
    return json.dumps(True)
  except:
    logging.exception("Fail to remove work history. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/workhistory/get/list/work', methods=["POST"])
@util.require_login
def get_work_history_list_by_work():
  data = request.get_json()
  ret_list = []
  try:
    datas = work_apis.get_work_history_list_by_work(data['work_id'])
    for data in datas:
      ret_list.append(_convert_dict_by_work_history(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get work history list by work.")
    return json.dumps(ret_list)


@blueprint.route('/workhistory/get/list', methods=["GET"])
@util.require_login
def get_work_history_list():
  ret_list = []
  try:
    datas = work_apis.get_all_work_history()
    for data in datas:
      ret_list.append(_convert_dict_by_work_history(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get work history list.")
    return json.dumps(ret_list)


@blueprint.route('/pausehistory/get/list', methods=["GET"])
@util.require_login
def get_pause_history_list():
  data = request.get_json()
  ret_list = []
  try:
    datas = work_apis.get_all_pause_history()
    for data in datas:
      ret_list.append(_convert_dict_by_pause_history(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get pause history list.")
    return json.dumps(ret_list)


@blueprint.route('/pausehistory/get/list/work', methods=["POST"])
@util.require_login
def get_pause_history_list_by_work(work_id=None):
  _work_id = None
  if work_id:
    _work_id = work_id
  else:
    data = request.get_json()
    _work_id = data['work_id']
  ret_list = []
  try:
    datas = work_apis.get_pause_history_list_by_work(_work_id)
    for data in datas:
      ret_list.append(_convert_dict_by_pause_history(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get pause history list by work.")
    return json.dumps(ret_list)


@blueprint.route('/work/start', methods=["POST"])
@util.require_login
def start_work(start_data=None):
  """
  <Manually Start >
    data = {'id': str, 'category': int, 'typ': int, 'blast_id': str}
    -> work_data

  <Auto Start>
    data = {'id': str, 'category': int, 'typ': int, 'blast_id': str,
            'start_time': timestamp}
  """
  if start_data:
    data = start_data
  else:
    data = request.get_json()
  try:
    ret = False
    start_time = None
    history_data = {
        'typ': data['typ'],
        'work_id': data['id']
    }
    latest_work = work_apis.get_latest_work_by_blast(data['blast_id'],
                                                     data['typ'])
    if latest_work and latest_work.work_history_list:
      _data = latest_work.work_history_list[0]
      if _data.state == WORK_STATE_IN_PROGRESS:
        ret = False
      elif _data.state == WORK_STATE_FINISH:
        ret = False
      else:
        # Start work History
        history_data['state'] = WORK_STATE_IN_PROGRESS
        history_data['timestamp'] = work_apis.get_servertime()
        history_data['accum_time'] = _data.accum_time
        _data = work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD,
                     [_convert_dict_by_work_history(_data)])
        # Handle pause data
        pause_time = 0
        if latest_work.pause_history_list:
          _pause_data = latest_work.pause_history_list[0]
          if not _pause_data.end_time:
            pause_time = history_data['timestamp'] - _pause_data.start_time
            pause_time = pause_time.seconds
            work_apis.update_pause_history_end_time(_pause_data.id,
                                                    history_data['timestamp'],
                                                    pause_time)
            send_request(PAUSE_HISTORY_UPDATE,
                         [_convert_dict_by_pause_history(_pause_data)])

        pause_time += latest_work.p_accum_time
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'],
                                                     pause_time)
        send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
        ret = True
    else:
      # Init data
      end_time = None
      activity_list = work_apis.get_same_type_by_blast(data['blast_id'],
                                                        data['typ'])
      if len(activity_list) == 1:
        if 'start_time' in data:
          start_time = datetime.datetime.fromtimestamp(data['start_time'])
          end_time = datetime.datetime.fromtimestamp(time.time() + 5400)
          added_job = sched.add_job(finish_work, trigger='cron', args=[data],
                                    year=end_time.year, month=end_time.month,
                                    day=end_time.day, hour=end_time.hour,
                                    minute=end_time.minute, second=end_time.second)
          history_data['job_id'] = added_job.id

      if len(activity_list) > 1 and data['category'] == '0':
        ret = False
      else:
        history_data['state'] = WORK_STATE_IN_PROGRESS
        history_data['timestamp'] = start_time if start_time else work_apis.get_servertime()
        history_data['accum_time'] = 0
        history_data['auto_end'] = end_time
        pause_time = 0
        _data = work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD,
                    [_convert_dict_by_work_history(_data)])
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'],
                                                     pause_time,
                                                     history_data['timestamp'],
                                                     None)
        send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
        ret = True
    return json.dumps(ret)
  except:
    logging.exception("Failed to start work. Data : %s", data)
    return json.dumps(False)


@blueprint.route('/work/stop', methods=["POST"])
@util.require_login
def stop_work(stop_data=None):
  """
  data = {'id': str, 'category': int, 'typ': int, 'blast_id': str, 'message': str}
  -> work_data
  message : Reason of pause, Message object text
  """
  data = None
  if stop_data:
    data = stop_data
  else:
    data = request.get_json()
  try:
    ret = False
    history_data = {
        'typ': data['typ'],
        'work_id': data['id']
    }
    latest_work = work_apis.get_latest_work_by_blast(data['blast_id'],
                                                     data['typ'])
    if latest_work and latest_work.work_history_list:
      _data = latest_work.work_history_list[0]
      if _data.state == WORK_STATE_IN_PROGRESS:
        # Stop work history
        history_data['state'] = WORK_STATE_STOP
        history_data['timestamp'] = work_apis.get_servertime()
        work_time = history_data['timestamp'] - _data.timestamp
        history_data['accum_time'] = _data.accum_time + \
                                     int(work_time.total_seconds())
        _data = work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD,
                     [_convert_dict_by_work_history(_data)])

        pause_time = 0
        pause_data = {
            "start_time": history_data['timestamp'],
            "end_time": None,
            "accum_time": pause_time,
            "message": data['message'],
            "work_id": data['id']
        }
        _data = work_apis.create_pause_history(pause_data)
        send_request(PAUSE_HISTORY_ADD,
                     [_convert_dict_by_pause_history(_data)])

        # TODO: handle work data
        pause_time += latest_work.p_accum_time
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'],
                                                     pause_time)
        send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
        ret = True
      elif _data.state == WORK_STATE_FINISH:
        ret = False
      else:
        ret = False
    return json.dumps(ret)
  except:
    logging.exception("Failed to stop work. Data : %s", data)
    return json.dumps(False)


@blueprint.route('/work/stop/completed', methods=["POST"])
@util.require_login
def stop_completed_work():
  pre_timestamp = None
  post_timestamp = None
  total_pause_time = 0
  data = request.get_json()
  try:
    work_data = work_apis.get_work(data['work_id'])
    blast_data = work_apis.get_blast(work_data.blast_id)
    start_timestamp = data['start_time']
    end_timestamp = data['end_time']
    data['start_time'] = datetime.datetime.fromtimestamp(data['start_time'])
    data['end_time'] = datetime.datetime.fromtimestamp(data['end_time'])
    pause_data = work_apis.create_pause_history(data)
    send_request(PAUSE_HISTORY_ADD,
                 [_convert_dict_by_pause_history(pause_data)])

    work_history_list = work_apis.get_work_history_list_by_work(data['work_id'])
    for work in work_history_list:
      if work.timestamp > data['start_time']:
        index = work_history_list.index(work)
        pre_timestamp = time.mktime(work_history_list[index - 1].timestamp.
                                    timetuple())
        history_id = work.id
        break

    pre_work_history = work_history_list[index - 1]
    history_data = {}
    history_data['typ'] = data['typ']
    history_data['state'] = WORK_STATE_STOP
    history_data['timestamp'] = data['start_time']
    history_data['work_id'] = data['work_id']
    history_data['accum_time'] = pre_work_history.accum_time +\
                                 start_timestamp - int(pre_timestamp)
    tmp_accum_time = history_data['accum_time']
    work_apis.create_work_history(history_data)

    for work in work_history_list:
      if work.timestamp > data['end_time']:
        index = work_history_list.index(work)
        post_timestamp = time.mktime(work_history_list[index].timestamp.
                                     timetuple())
        history_id = work.id
        break

    history_data = {}
    history_data['typ'] = data['typ']
    history_data['work_id'] = data['work_id']
    if end_timestamp == post_timestamp:
      history_data['id'] = history_id
      history_data['accum_time'] = tmp_accum_time
      work_apis.update_work_history(history_data)
    else:
      history_data['state'] = WORK_STATE_IN_PROGRESS
      history_data['timestamp'] = data['end_time']
      history_data['accum_time'] = tmp_accum_time
      work_apis.create_work_history(history_data)
      history_data = {}
      history_data['id'] = history_id
      history_data['typ'] = data['typ']
      history_data['work_id'] = data['work_id']

      if pre_work_history.state == 1 and pre_work_history.accum_time == 0:
        history_data['accum_time'] = (int(post_timestamp) - end_timestamp) + \
                                     (start_timestamp - int(pre_timestamp))
      else:
        history_data['accum_time'] = pre_work_history.accum_time + \
                                     (int(post_timestamp) - end_timestamp) + \
                                     (start_timestamp - int(pre_timestamp))
      work_apis.update_work_history(history_data)

      pause_list = work_apis.get_pause_history_list_by_work(data['work_id'])
      for pause_data in pause_list:
        total_pause_time += pause_data.accum_time
      work_accum_time = work_data.accum_time - data['accum_time']

    ret_work_data = work_apis.update_state_and_accum(data['work_id'],
                                                     work_data.state,
                                                     work_accum_time,
                                                     total_pause_time)
    send_request(WORK_UPDATE, [_convert_dict_by_work(ret_work_data)])

    ret_blast_data = work_apis.update_blast_state_and_accum(blast_data.id,
                                                            blast_data.state,
                                                            work_accum_time,
                                                            data['category'],
                                                            True)
    send_request(BLAST_UPDATE, [_convert_dict_by_blast(ret_blast_data)])

    return json.dumps(True)
  except:
    logging.exception("Fail to adding stop work data.")
    return json.dumps(False)


@blueprint.route('/work/finish', methods=["POST"])
@util.require_login
def finish_work(finish_data=None):
  """
  data = {'id': str, 'category': int, 'typ': int, 'blast_id': str}
  -> work_data
  """
  auto_finish = None
  if finish_data:
    auto_finish = True
    data = finish_data
  else:
    data = request.get_json()
    his_list = work_apis.get_work_history_list_by_work(data['id'])
    for _history in his_list:
      if _history.typ == 101 or _history.typ == '101':
        if _history.state == 1 and _history.auto_end and _history.job_id:
          if sched.get_job(_history.job_id):
            sched.remove_job(_history.job_id)
  try:
    ret = False
    history_data = {
        'typ': data['typ'],
        'work_id': data['id']
    }
    latest_work = work_apis.get_latest_work_by_blast(data['blast_id'],
                                                     data['typ'])
    if latest_work and latest_work.work_history_list:
      _data = latest_work.work_history_list[0]
      if _data.state == WORK_STATE_IN_PROGRESS:
        # TODO: Not stop then can't finish?
        # Finish work history
        history_data['state'] = WORK_STATE_FINISH
        history_data['timestamp'] = work_apis.get_servertime()
        work_time = history_data['timestamp'] - _data.timestamp
        history_data['accum_time'] = _data.accum_time + \
                                     int(work_time.total_seconds())
        _data = work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD,
                     [_convert_dict_by_work_history(_data)])
        # Handle pause data
        pause_time = 0
        if latest_work.pause_history_list:
          _pause_data = latest_work.pause_history_list[0]
          if not _pause_data.end_time:
            pause_time = history_data['timestamp'] - _pause_data.start_time
            pause_time = pause_time.seconds
            work_apis.update_pause_history_end_time(_pause_data.id,
                                                    history_data['timestamp'],
                                                    pause_time)
            send_request(PAUSE_HISTORY_UPDATE,
                         [_convert_dict_by_pause_history(_pause_data)])

        # TODO: handle work data
        pause_time += latest_work.p_accum_time
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'],
                                                     pause_time,
                                                     None,
                                                     history_data['timestamp'])
        send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
        if data['typ'] == 114:  # finish work
          blast_data = work_apis.update_blast_state_and_accum(data['blast_id'], 2,
                                                              history_data['accum_time'],
                                                              latest_work.category)
        else:
          blast_data = work_apis.update_blast_state_and_accum(data['blast_id'], 1,
                                                              history_data['accum_time'],
                                                              latest_work.category)
        send_request(BLAST_UPDATE, [_convert_dict_by_blast(blast_data)])
        ret = _convert_dict_by_blast(blast_data)
      elif _data.state == WORK_STATE_FINISH:
        # Finish work history
        ret = False
      else:
        # Finish work history
        history_data['state'] = WORK_STATE_FINISH
        history_data['timestamp'] = work_apis.get_servertime()
        history_data['accum_time'] = _data.accum_time
        _data = work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD,
                     [_convert_dict_by_work_history(_data)])
        # Handle pause data
        pause_time = 0
        if latest_work.pause_history_list:
          _pause_data = latest_work.pause_history_list[0]
          if not _pause_data.end_time:
            pause_time = history_data['timestamp'] - _pause_data.start_time
            pause_time = pause_time.seconds
            work_apis.update_pause_history_end_time(_pause_data.id,
                                                    history_data['timestamp'],
                                                    pause_time)
            send_request(PAUSE_HISTORY_UPDATE,
                         [_convert_dict_by_pause_history(_pause_data)])
        # TODO: handle work data
        pause_time += latest_work.p_accum_time
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'],
                                                     pause_time,
                                                     None,
                                                     history_data['timestamp'])
        send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
        # TODO: handle blast data
        if data['typ'] == 114:  # finish work
          blast_data = work_apis.update_blast_state_and_accum(data['blast_id'], 2,
                                                              history_data['accum_time'],
                                                              latest_work.category)
        else:
          blast_data = work_apis.update_blast_state_and_accum(data['blast_id'], 1,
                                                              history_data['accum_time'],
                                                              latest_work.category)
        send_request(BLAST_UPDATE, [_convert_dict_by_blast(blast_data)])
        ret = _convert_dict_by_blast(blast_data)
    start_history = work_apis.get_work_history_have_auto_end(data['id'])
    if start_history:
      start_data = _convert_dict_by_work_history(start_history)
      work_apis.update_work_history(start_data)
    if auto_finish:
      auto_add_data = {
          'id': uuid.uuid4().hex,
          'category': '2',
          'typ': '304',
          'state': 0,
          'accum_time': 0,
          'p_accum_time': 0,
          'blast_id': data['blast_id']
      }
      add_work(work_data=auto_add_data, is_auto=True)
    return json.dumps(ret)
  except:
    logging.exception("Failed to stop work. Data : %s", data)
    return json.dumps(False)


@blueprint.route('/activity/get/list', methods=["GET"])
@util.require_login
def get_activity_list():
  ret_list = []
  try:
    datas = work_apis.get_all_activity()
    for data in datas:
      ret_list.append(_convert_dict_by_activity(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get activity list.")
    return json.dumps(ret_list)


@blueprint.route('/equipment/get/list', methods=["GET"])
@util.require_login
def get_equipment_list():
  ret_list = []
  try:
    datas = work_apis.get_all_equipment()
    for data in datas:
      ret_list.append(_convert_dict_by_equipment(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get equipment list.")
    return json.dumps(ret_list)


@blueprint.route('/operator/get/list', methods=["GET"])
@util.require_login
def get_operator_list():
  ret_list = []
  try:
    datas = work_apis.get_all_operator()
    for data in datas:
      ret_list.append(_convert_dict_by_operator(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get operator list.")
    return json.dumps(ret_list)


@blueprint.route('/message/get/list', methods=["GET"])
@util.require_login
def get_message_list():
  ret_list = []
  try:
    datas = work_apis.get_all_message()
    for data in datas:
      ret_list.append(_convert_dict_by_message(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get message list.")
    return json.dumps(ret_list)


@blueprint.route('/team/get/list', methods=["GET"])
@util.require_login
def get_team_list():
  ret_list = []
  try:
    datas = work_apis.get_all_team()
    for data in datas:
      ret_list.append(_convert_dict_by_team(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get team list.")
    return json.dumps(ret_list)


@blueprint.route('/equipment/info/get/list', methods=["GET"])
@util.require_login
def get_eqiupment_info_list():
  ret_list = []
  try:
    datas = dashboard.count.GADGET_INFO
    return json.dumps(datas)
  except:
    logging.exception("Fail to get equipment info list.")
    return json.dumps(ret_list)


@blueprint.route('/work/equipment/add', methods=["POST"])
@util.require_login
def add_work_equipment():
  data = request.get_json()
  try:
    data = work_apis.create_work_equipment(data)
    send_request(WORK_EQUIPMENT_ADD, [_convert_dict_by_work_equipment(data)])
    return json.dumps(True)
  except:
    logging.exception("Fail to add work equipment.")
    return json.dumps(False)


@blueprint.route('/work/equipment/get/list/work', methods=["POST"])
@util.require_login
def get_work_equipment_by_work():
  data = request.get_json()
  work_id = data['work_id']
  try:
    datas = work_apis.get_work_equipment_list_by_work(work_id)
    ret_list = []
    for data in datas:
      ret_list.append(_convert_dict_by_work_equipment(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to add work equipment.")
    return json.dumps(False)


@blueprint.route('/work/workdata/get/list/work', methods=["POST"])
@util.require_login
def get_work_data_by_work():
  # Return by work operator and work equipment
  data = request.get_json()
  work_id = data['work_id']
  try:
    ret_data = {}
    e_datas = work_apis.get_work_equipment_list_by_work(work_id)
    e_list = []
    for data in e_datas:
      e_list.append(_convert_dict_by_work_equipment(data))
    ret_data['equipment'] = e_list
    return json.dumps(ret_data)
  except:
    logging.exception("Fail to add work data.")
    return json.dumps(False)


def send_request(topic, value):
  url = "{}/work/event".format(API_SERVER)
  data = [
    {
      "topic": topic,
      "value": value,
      "_t": time.time()
    }
  ]
  try:
    logging.info("send request. topic : %s, value : %s", topic, value)
    resp = requests.post(url, headers=HEADERS,
                         data=json.dumps(data, default=_default),
                         verify=False)
    if resp.ok:
      return True
    else:
      logging.warning("Failed to work requests event. "
                      "Topic : %s, Code : %s, Text : %s",
                      topic, resp.status_code, resp.text)
      return False
  except:
    logging.exception("Failed to work requests event. "
                      "topic : %s, url : %s, data : %s",
                      topic, url, data)
    return False


def _default(obj):
  """Default JSON serializer."""
  import calendar, datetime

  if isinstance(obj, datetime.datetime):
    if obj.utcoffset() is not None:
      obj = obj - obj.utcoffset()
    millis = int(
      calendar.timegm(obj.timetuple()) * 1000 +
      obj.microsecond / 1000
    )
    return millis
  raise TypeError('Not sure how to serialize %s' % (obj,))


### { UI API


ACTIVITY_NAME = {
    101: "VENTILATION",
    102: "FIRST MUCKING",
    103: "MECHANICAL_SCALING",
    104: "MENUAL SCALING",
    105: "SECOND MUCKING",
    106: "GEO MAPPING",
    107: "WATER SPRAY",
    108: "SHOTCRETE",
    109: "PROBHOLES",
    110: "BOTTOM CLEANING",
    111: "FACE DRILLING",
    112: "SURVEYING & MARKING",
    113: "CHARGING",
    114: "BLASTING",
    200: "SHOTCRETE",
    201: "ROCK BOLT MARKING",
    202: "ROCK BOLT DRILLING",
    203: "ROCK BOLT INJECTION",
    204: "DRILLING FOR GROUTING",
    205: "GROUTING",
    206: "GROUTING CURING",
    207: "GROUTING CHECK HOLES",
    208: "CORE DRILLING",
    300: "TBM",
    301: "INTERFERENCE",
    302: "EVACUATION",
    303: "EQUIPMENT BREAKEDOWN",
    304: "NO WORK",
    305: "PREPERATION",
    306: "RESOURCE NOT AVAILABLE",
    307: "SHIFT CHANGE",
    308: "EXPLOSIVE_DELIVERY",
    309: "OTHERS",
    310: "NONE",
}
TUNNEL_CATEGORY = {
    100: "TOP HD",
    101: "BOTTOM 1",
    102: "BOTTOM 2"
}
TUNNEL_DIRECTION = {
    0: "EAST",
    1: "WEST",
    2: "ES-EAST",
    3: "ES-WEST",
    4: "WS-EAST",
    5: "WS-WEST"
}
ACTIVITY_CATEGORY = {
    1: "Supporting Work",
    2: "Idling Activity"
}
CSV_INDEX = {
    101: 4,
    102: 5,
    103: 6,
    104: 7,
    105: 8,
    106: 9,
    107: 10,
    108: 11,
    109: 12,
    110: 13,
    111: 14,
    112: 1,
    113: 2,
    114: 3,
    115: 15,
    200: 1,
    201: 2,
    202: 3,
    203: 4,
    204: 5,
    205: 6,
    206: 7,
    207: 8,
    208: 9,
    300: 1,
    301: 2,
    302: 3,
    303: 4,
    304: 9,
    305: 5,
    306: 6,
    307: 7,
    308: 8,
    309: 10,
    310: 11,
}
MAIN_TYPES = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113,
              114, 115]
SUPPORTING_TYPES = [200, 201, 202, 203, 204, 205, 206, 207, 208]
IDLE_TYPES = [300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310]
TUNNEL_TYPE_STR = {
    "C1": "Main Cavern 1",
    "C2": "Main Cavern 2",
    "C3": "Main Cavern 3"
}
MAIN = {
    101: 'main/ventilation.svg',
    102: 'main/first_mucking.svg',
    103: 'main/mechanical_scaling.svg',
    104: 'main/manual_scaling.svg',
    105: 'main/second_mucking.svg',
    106: 'main/geo_mapping.svg',
    107: 'main/water_spray.svg',
    108: 'main/concrete.svg',
    109: 'main/probhole.svg',
    110: 'main/cleaning.svg',
    111: 'main/face_drilling.svg',
    112: 'main/surveying_marking.svg',
    113: 'main/charging.svg',
    114: 'main/blasting.svg',
}
SUPPORTING = {
    200: 'support/support_concrete.svg',
    201: 'support/rockbolt_marking.svg',
    202: 'support/rockbolt_drilling.svg',
    203: 'support/rockbolt_injection.svg',
    204: 'support/drilling_for_grouting.svg',
    205: 'support/grouting.svg',
    206: 'support/grouting_curing.svg',
    207: 'support/grouting_check_holes.svg',
    208: 'support/core_drilling.svg',
}
IDLE = {
    300: 'idle/TBM.svg',
    301: 'idle/interference.svg',
    302: 'idle/evacuation.svg',
    303: 'idle/equipment_breakdown.svg',
    304: 'idle/no_work.svg',
    305: 'idle/preperation.svg',
    306: 'idle/resource_not_available.svg',
    307: 'idle/shift_change.svg',
    308: 'idle/explosive_delivery.svg',
    309: 'idle/others.svg',
    310: 'idle/none.svg',
}


@blueprint.route('/')
@util.require_login
def route_default():
  return render_template("work_home.html")


@blueprint.route('/search/work', methods=["GET", "POST"])
@util.require_login
def get_work_search_page():
  if request.method == "GET":
    activity_list = {}
    activity_list[10000] = "ALL"
    _activity_list = work_apis.get_all_activity()
    for activity in _activity_list:
      activity_list[int(activity.activity_id)] = activity.name
    return render_template("search_work_prepare.html", activity_list=activity_list)
  else:
    tunnel_id = request.form.get('tunnelId')
    tunnel = request.form.get('tunnel')
    activity = request.form.get('activity')
    raw_datetime_list = request.form.get('datetime')
    datetime_list = json.loads(raw_datetime_list)

    page = request.form.get('page')
    next_num = request.form.get('next_num')
    prev_num = request.form.get('prev_num')
    page_num = None
    if page == "1":
      page_num = prev_num
    elif page == "2":
      page_num = next_num

    logging.info("## tid : %s, t : %s, d : %s", tunnel_id, tunnel, activity)
    work_list = work_apis.search(tunnel_id, int(tunnel), int(activity),
                                 datetime_list,
                                 page_num)
    data = {
      "tunnel_id": tunnel_id, "tunnel": tunnel,
      "activity": activity, "datetime": raw_datetime_list,
      "tunnel_category": TUNNEL_CATEGORY, "tunnel_direction": TUNNEL_DIRECTION,
      "activity_name": ACTIVITY_NAME
    }
    start_date = "-".join(datetime_list[0].split(",")[:3])
    start_time = ":".join(datetime_list[0].split(",")[3:])
    end_date = "-".join(datetime_list[1].split(",")[:3])
    end_time = ":".join(datetime_list[1].split(",")[3:])
    start = "{} {}".format(start_date, start_time)
    end = "{} {}".format(end_date, end_time)
    activity_list = {}
    activity_list[10000] = "ALL"
    _activity_list = work_apis.get_all_activity()
    for activity in _activity_list:
      activity_list[int(activity.activity_id)] = activity.name
    return render_template("search_work.html", data=data, work_list=work_list,
                           activity_list=activity_list,
                           start_date=start, end_date=end)


### }


@blueprint.route('/analyze')
@util.require_login
def route_analyze():
  return render_template("work_analyze.html")


@blueprint.route('/reg/activity')
@util.require_login
def route_reg_activity():
  activity_list = work_apis.get_all_activity()
  wip_work_list = work_apis.get_work_list_in_progress()
  wip_work_typ_list = []
  for work in wip_work_list:
    wip_work_typ_list.append(work.typ)
  wip_work_typ_list = list(set(wip_work_typ_list))
  return render_template("reg_activity_list.html",
                         activity_list=activity_list,
                         wip_work_typ_list=wip_work_typ_list)


@blueprint.route('/reg/activity/create', methods=['GET', 'POST'])
@util.require_login
def route_reg_activity_create():
  if request.method == "GET":
    return render_template("create_activity.html",
                           activity_category=ACTIVITY_CATEGORY)
  else:
    name = request.form['name']
    category = request.form['category']
    upload_file = request.files['file']
    file_path = None
    content = upload_file.read()
    last_activity = work_apis.get_activity_by_last_id(category)
    activity_id = int(last_activity.activity_id) + 1
    activity_data = {
       "name": name,
       "category": int(category),
       "activity_id": activity_id
    }
    if content:
      src_path = os.path.dirname(os.path.abspath(__file__))
      base_path = os.path.join(src_path, 'static', 'imgs')
      if not os.path.exists(base_path):
        os.makedirs(base_path)
      file_type = upload_file.filename.split('.')[-1]
      file_name = name.replace(' ', '_') + '.' + file_type

      if int(category) == 1:
        file_path = os.path.join('support', file_name)
      elif int(category) == 2:
        file_path = os.path.join('idle', file_name)
      else:
        file_path = file_name
      total_path = os.path.join(base_path, file_path)
      with open(total_path, 'wb') as f:
        f.write(content)
    else:
      pass
    activity_data['file_path'] = file_path
    work_apis.create_activity(activity_data)
    _data = work_apis.get_activity_by_activity_id(activity_id)
    send_request(ACTIVITY_ADD, [_convert_dict_by_activity(_data)])
    return redirect("/work/reg/activity")


@blueprint.route('/reg/activity/delete/<aid>', methods=['POST'])
@util.require_login
def route_reg_activity_remove(aid):
  activity_data = work_apis.get_activity(aid)
  src_path = os.path.dirname(os.path.abspath(__file__))
  base_path = os.path.join(src_path, 'static', 'imgs')
  last_file_path = activity_data.file_path
  if last_file_path:
    remove_file_path = os.path.join(base_path, last_file_path)
    os.remove(remove_file_path)
  work_apis.remove_activity(aid)
  ret = {
      "activity_id": activity_data.activity_id,
      "category": activity_data.category,
      "name": activity_data.name
  }
  send_request(ACTIVITY_REMOVE, [ret])
  return redirect("/work/reg/activity")


@blueprint.route('/reg/activity/edit/<aid>', methods=['GET', 'POST'])
@util.require_login
def route_reg_activity_edit(aid):
  if request.method == "GET":
    activity_data = work_apis.get_activity(aid)
    return render_template("edit_activity.html",
                           activity_category=ACTIVITY_CATEGORY,
                           activity_data=activity_data)
  else:
    activity_data = work_apis.get_activity(aid)
    name = request.form['name']
    category = request.form['category']
    upload_file = request.files['file']
    file_path = None
    activity_id = None
    content = upload_file.read()
    if int(category) != activity_data.category:
      last_activity = work_apis.get_activity_by_last_id(category)
      activity_id = int(last_activity.activity_id) + 1
    else:
      activity_id = activity_data.activity_id
    update_data = {
        "id": aid,
        "name": name,
        "category": category,
        "activity_id": activity_id
    }
    src_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(src_path, 'static', 'imgs')
    if content:
      src_path = os.path.dirname(os.path.abspath(__file__))
      base_path = os.path.join(src_path, 'static', 'imgs')
      if not os.path.exists(base_path):
        os.makedirs(base_path)
      file_type = upload_file.filename.split('.')[-1]
      file_name = name.replace(' ', '_') + '.' + file_type

      if int(category) == 1:
        file_path = os.path.join('support', file_name)
      elif int(category) == 2:
        file_path = os.path.join('idle', file_name)
      else:
        file_path = file_name
      total_path = os.path.join(base_path, file_path)
      with open(total_path, 'wb') as f:
        f.write(content)
    last_file_path = activity_data.file_path
    if last_file_path:
      remove_file_path = os.path.join(base_path, last_file_path)
      os.remove(remove_file_path)
    update_data['file_path'] = file_path
    ret = work_apis.update_activity(update_data)
    send_request(ACTIVITY_UPDATE, [_convert_dict_by_activity(ret)])
    return redirect("/work/reg/activity")


@blueprint.route('/reg/equipment')
@util.require_login
def route_reg_equipment():
  equipment_list = work_apis.get_all_equipment()
  equipment_info = dashboard.count.GADGET_INFO
  return render_template("reg_equipment_list.html",
                         equipment_list=equipment_list,
                         equipment_info=equipment_info)


@blueprint.route('/reg/equipment/edit/<eid>', methods=['GET', 'POST'])
@util.require_login
def route_reg_equipment_edit(eid):
  if request.method == "GET":
    equipment_info = dashboard.count.GADGET_INFO
    equipment_data = work_apis.get_equipment(eid)
    return render_template("edit_equipment.html",
                           equipment_data=equipment_data,
                           equipment_info=equipment_info)
  else:
    name = request.form['name']
    category = request.form['category']
    equipment_id = request.form['equipment_id']
    equipment_data = {
       "id": eid,
       "name": name,
       "equipment_id" : equipment_id,
       "category": int(category)
    }
    work_apis.update_equipment(equipment_data)
    return redirect("/work/reg/equipment")


@blueprint.route('/reg/equipment/create', methods=['GET', 'POST'])
@util.require_login
def route_reg_equipment_create():
  if request.method == "GET":
    equipment_info = dashboard.count.GADGET_INFO
    return render_template("create_equipment.html",
                           equipment_info=equipment_info)
  else:
    name = request.form['name']
    category = request.form['category']
    equipment_id = request.form['equipmentId']
    equipment_data = {
       "name": name,
       "equipment_id" : equipment_id,
       "category": int(category)
    }
    work_apis.create_equipment(equipment_data)
    return redirect("/work/reg/equipment")


@blueprint.route('/reg/operator')
@util.require_login
def route_reg_operator():
  operator_list = work_apis.get_all_operator()
  equipment_info = dashboard.count.GADGET_INFO
  return render_template("reg_operator_list.html",
                         operator_list=operator_list,
                         equipment_info=equipment_info)


@blueprint.route('/reg/operator/edit/<oid>', methods=['GET', 'POST'])
@util.require_login
def route_reg_operator_edit(oid):
  if request.method == "GET":
    equipment_info = dashboard.count.GADGET_INFO
    operator_data = work_apis.get_operator(oid)
    return render_template("edit_operator.html",
                           operator_data=operator_data,
                           equipment_info=equipment_info)
  else:
    name = request.form['name']
    category = request.form['category']
    operator_id = request.form['operator_id']
    operator_data = {
       "id": oid,
       "name": name,
       "operator_id" : operator_id,
       "category": int(category)
    }
    work_apis.update_operator(operator_data)
    return redirect("/work/reg/operator")


@blueprint.route('/reg/operator/create', methods=['GET', 'POST'])
@util.require_login
def route_reg_operator_create():
  if request.method == "GET":
    equipment_info = dashboard.count.GADGET_INFO
    return render_template("create_operator.html",
                           equipment_info=equipment_info)
  else:
    name = request.form['name']
    operator_id = request.form['operatorId']
    category = request.form['category']
    # department = request.form['department']
    operator_data = {
       "name": name,
       "operator_id" : operator_id,
       "category": int(category)
      #  "department": department
    }
    work_apis.create_operator(operator_data)
    return redirect("/work/reg/operator")


@blueprint.route('/reg/team')
@util.require_login
def route_reg_team():
  team_list = work_apis.get_all_team()
  return render_template("reg_team_list.html",
                         team_list=team_list)


@blueprint.route('/reg/team/create', methods=['GET', 'POST'])
@util.require_login
def route_reg_team_create():
  if request.method == "GET":
    return render_template("create_team.html")
  else:
    # category = request.form['category']
    category = 0
    name = request.form['name']
    engineer = request.form['engineer']
    member = request.form['member']
    team_data = {
        "category": int(category),
        "name": name,
        "engineer": engineer,
        "member": int(member)
    }
    data = work_apis.create_team(team_data)
    send_request(TEAM_ADD, [_convert_dict_by_team(data)])
    return redirect("/work/reg/team")


@blueprint.route('/reg/team/edit/<tid>', methods=['GET', 'POST'])
@util.require_login
def route_reg_team_edit(tid):
  if request.method == "GET":
    team_data = work_apis.get_team(tid)
    return render_template("edit_team.html",
                           team_data=team_data)
  else:
    name = request.form['name']
    engineer = request.form['engineer']
    member = request.form['member']
    team_data = {
       "id": tid,
       "name": name,
       "engineer" : engineer,
       "member": int(member)
    }
    work_apis.update_team(team_data)
    return redirect("/work/reg/team")


@blueprint.route('/reg/message')
@util.require_login
def route_reg_message():
  message_list = work_apis.get_all_message()
  return render_template("reg_message_list.html",
                         message_list=message_list)


@blueprint.route('/reg/message/edit/<mid>', methods=['GET', 'POST'])
@util.require_login
def route_reg_message_edit(mid):
  if request.method == "GET":
    message_data = work_apis.get_message(mid)
    return render_template("edit_message.html",
                           message_data=message_data)
  else:
    message = request.form['message']
    message_data = {
       "id": mid,
       "message": message
    }
    work_apis.update_message(message_data)
    return redirect("/work/reg/message")


@blueprint.route('/reg/message/create', methods=['GET', 'POST'])
@util.require_login
def route_reg_message_create():
  if request.method == "GET":
    return render_template("create_message.html")
  else:
    # category = request.form['category']
    category = 0
    message = request.form['message']
    message_data = {
       "category": int(category),
       "message": message
    }
    data = work_apis.create_message(message_data)
    send_request(MESSAGE_ADD, [_convert_dict_by_message(data)])
    return redirect("/work/reg/message")


@blueprint.route('/search/worklog/download', methods=["POST"])
@util.require_login
def download_work_log():
  tunnel_id = request.form.get('tunnel_id')
  tunnel = request.form.get('tunnel')
  activity = request.form.get('activity')
  raw_datetime_list = request.form.get('datetime')
  datetime_list = json.loads(raw_datetime_list)
  work_log_list = work_apis.csv_work_log(tunnel_id, int(tunnel), int(activity),
                                         datetime_list)

  filename = "Work Search_{}".format(str(in_config_apis.get_servertime()))
  ret_csv_str = csv_str_formatting(work_log_list, tunnel_id)
  return _get_download_csv_response(ret_csv_str, filename)


def csv_str_formatting(work_log_list, tunnel_id):
  csv_str = "\uFEFF"
  csv_str += "Tunnel Type,Tunnel,Date,Time,Explosive Bulk,Explosive Cartridge,"\
             "Detonator Qty,Drilling Depth,Start,Finish,Actual L(m),Date,Time,"\
             "Overall A=(1-2),Excvt.T,SV&MK,CG,Blst,VT,MU,Mc.SC,Mn.SC,MU-2,MP,"\
             "WS,SCT,PH,B.CL,F.DR,U.BK"

  activity_list = work_apis.get_all_activity()
  sup_list = []
  idle_list = []
  for activity in activity_list:
    if activity.category == 1:
      sup_list.append(activity)
    elif activity.category == 2:
      idle_list.append(activity)

  supporting_form = [0 for index in range(len(SUPPORTING_TYPES))]
  idle_form = [0 for index in range(len(IDLE_TYPES))]
  supporting_form.insert(0, "Supporting")
  idle_form.insert(0, "Idle")

  for sup_activity in sup_list:
    if int(sup_activity.activity_id) in ACTIVITY_NAME:
      supporting_form[
        CSV_INDEX[int(sup_activity.activity_id)]] = sup_activity.name
    else:
      supporting_form.append(sup_activity.name)

  for idle_activity in idle_list:
    if int(idle_activity.activity_id) in ACTIVITY_NAME:
      idle_form[CSV_INDEX[int(idle_activity.activity_id)]] = idle_activity.name
    else:
      idle_form.append(idle_activity.name)
  supporting_form = ",".join(supporting_form)
  idle_form = ",".join(idle_form)
  csv_str = csv_str + "," + supporting_form + "," + idle_form + " \n"

  sorted_blast_list = work_apis.get_blast_list_for_csv(tunnel_id)
  if not sorted_blast_list:
    return csv_str

  for _blast in sorted_blast_list:
    blast_list = _blast.tunnel.blast_list
    blast_index = blast_list.index(_blast)
    blast_info = _blast.blast_info_list[0]
    main_work_times = [0 for index in range(16)]
    support_times = [0 for index in range(len(sup_list) + 1)]
    idle_times = [0 for index in range(len(idle_list) + 1)]
    log_data_list = []
    total_data_list = []
    main_total_times = 0
    support_total_times = 0
    idle_total_times = 0

    for log in work_log_list:
      if log.blast.tunnel.id == _blast.tunnel.id and log.blast.id == _blast.id:
        if log.state == constants.WORK_STATE_FINISH:
          if log.typ in MAIN_TYPES:
            main_work_times[CSV_INDEX[log.typ]] += log.accum_time
            main_total_times += log.accum_time
          elif log.typ in SUPPORTING_TYPES:
            support_times[CSV_INDEX[log.typ]] += log.accum_time
            support_total_times += log.accum_time
          elif log.typ in IDLE_TYPES:
            idle_times[CSV_INDEX[log.typ]] += log.accum_time
            idle_total_times += log.accum_time
        log_data_list.append(log)

    for index, main_work_time in enumerate(main_work_times):
      main_work_times[index] = second_to_time_format(main_work_time)
    for index, support_time in enumerate(support_times):
      support_times[index] = second_to_time_format(support_time)
    for index, idle_time in enumerate(idle_times):
      idle_times[index] = second_to_time_format(idle_time)

    if main_total_times or support_total_times or idle_total_times:
      del main_work_times[0]
      del support_times[0]
      del idle_times[0]
      main_work_times.insert(0, second_to_time_format(main_total_times).
                             replace(",", "."))
      support_times.insert(0, second_to_time_format(support_total_times).
                           replace(",", "."))
      idle_times.insert(0, second_to_time_format(idle_total_times).
                        replace(",", "."))
      tunnel_type = _blast.tunnel.section
      total_data_list.append(TUNNEL_TYPE_STR[tunnel_type])
      total_data_list.append(_blast.tunnel.tunnel_id)
      if blast_info.blasting_time:
        total_data_list.append(blast_info.
                               blasting_time.strftime("%Y-%m-%d"))
        total_data_list.append(blast_info.
                               blasting_time.strftime("%I:%M %p"))
      else:
        total_data_list.append("")
        total_data_list.append("")

      if log_data_list:
        total_data_list.append(str(blast_info.explosive_bulk))
        total_data_list.append(str(blast_info.explosive_cartridge))
        total_data_list.append(str(blast_info.detonator))
        total_data_list.append(str(blast_info.drilling_depth))
        total_data_list.append(str(blast_info.start_point))
        total_data_list.append(str(blast_info.finish_point))
        total_data_list.append(str(blast_info.blasting_length))
      else:
        for _index in range(6):
          total_data_list.append(INIT_DATA)

      #TODO: value set == overall indexing
      if len(_blast.tunnel.blast_list) == 1:
        total_data_list.append(INIT_DATA)  # Previous Blasting Date
        total_data_list.append(INIT_DATA)  # Previous Blasting Time
        total_data_list.append(INIT_DATA)  # Overall A=(1-2)
      else:
        if len(_blast.tunnel.blast_list) > blast_index + 1:
          current_blasting_time = blast_list[blast_index].blast_info_list[0].\
              blasting_time
          pre_blasting_time = blast_list[blast_index + 1].blast_info_list[0].\
              blasting_time
          total_data_list.append(pre_blasting_time.strftime("%Y-%m-%d"))
          total_data_list.append(pre_blasting_time.strftime("%I:%M %p"))
          if current_blasting_time and pre_blasting_time:
            overall = current_blasting_time - pre_blasting_time
            overall_ret = second_to_time_format(overall, is_duration=True)
            total_data_list.append(overall_ret)
          else:
            total_data_list.append(INIT_DATA)
        else:
          total_data_list.append(INIT_DATA)
          total_data_list.append(INIT_DATA)
          total_data_list.append(INIT_DATA)

      _row_string = ",".join(total_data_list)
      work_time_str = ",".join(main_work_times)
      support_time_str = ",".join(support_times)
      idle_time_str = ",".join(idle_times)
      csv_str += _row_string + "," + work_time_str + "," + support_time_str +\
                 "," + idle_time_str + "," + "\n"
  return csv_str


def second_to_time_format(value, is_duration=False):
  if is_duration:
    duration = value
  else:
    duration = datetime.timedelta(seconds=value)
  hours = (duration.days * 24) + int((duration.seconds / 3600))
  minutes = round(duration.seconds % 3600 / 60)
  ret = "{hours}:{minutes}".format(hours=hours, minutes=minutes)
  return ret


def _get_download_csv_response(csv_str, filename):
  resp = make_response(csv_str, 200)
  resp.headers['Cache-Control'] = 'no-cache'
  resp.headers['Content-Type'] = 'text/csv'
  resp.headers['Content-Disposition'] = 'attachment; filename={}.csv'.\
      format(filename)
  resp.headers['Content-Length'] = len(csv_str)
  return resp


def init():
  sched_start()
  activity_init()


def sched_start():
  sched.start()
  data_list = work_apis.get_all_work_history_for_auto_end()
  for _data in data_list:
    if _data.auto_end > datetime.datetime.now():
      work = work_apis.get_work(_data.work_id)
      data = {
          'id': work.id,
          'category': work.category,
          'typ': work.typ,
          'blast_id': work.blast_id
      }
      added_job = sched.add_job(finish_work, trigger='cron', args=[data],
                                year=_data.auto_end.year,
                                month=_data.auto_end.month,
                                day=_data.auto_end.day,
                                hour=_data.auto_end.hour,
                                minute=_data.auto_end.minute,
                                second=_data.auto_end.second)
      history_data = {
          'id': _data.id,
          'typ': work.typ,
          'work_id': work.id,
          'job_id': added_job.id,
          'state': WORK_STATE_IN_PROGRESS,
          'timestamp': _data.timestamp,
          'accum_time': work.accum_time,
          'auto_end': _data.auto_end
      }
      work_apis.update_work_history(history_data, True)


def activity_init():
  for activity_id, name in ACTIVITY_NAME.items():
    activity_data = work_apis.get_activity_by_activity_id(activity_id)
    if not activity_data:
      if int(activity_id / 100) == 1:
        category = 0
        file_path = MAIN[activity_id]
      elif int(activity_id / 100) == 2:
        category = 1
        file_path = SUPPORTING[activity_id]
      elif int(activity_id / 100) == 3:
        category = 2
        file_path = IDLE[activity_id]
      data = {
          'name': name,
          'category': category,
          'activity_id': activity_id,
          'file_path': file_path
      }
      work_apis.create_activity(data)
      logging.warning("Activity data saved successfully. %s, %s", activity_id,
                      name)
    else:
      logging.warning("The data already exists. %s, %s", activity_id, name)
