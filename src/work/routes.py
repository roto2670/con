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
import time
import uuid
import logging
import requests
from flask import request

import util
import constants
import work_apis
from work import blueprint
from constants import API_SERVER
from constants import WORK_STATE_STOP, WORK_STATE_IN_PROGRESS
from constants import WORK_STATE_FINISH

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


def _convert_dict_by_basepoint(data):
    return {
        "id": data.id,
        "name": data.name,
        "x_loc": data.x_loc,
        "y_loc": data.y_loc,
        "height": data.height,
        "width": data.width
    }


def _convert_dict_by_tunnel(data):
  return {
      "id": data.id,
      "name": data.name,
      "direction": data.direction,
      "x_loc": data.x_loc,
      "y_loc": data.y_loc,
      "width": data.width,
      "height": data.height,
      "basepoint_id": data.basepoint_id
  }


def _convert_dict_by_blast(data):
  return {
      "id": data.id,
      "x_loc": data.x_loc,
      "y_loc": data.y_loc,
      "width": data.width,
      "height": data.height,
      "state": data.state,
      "accum_time": data.accum_time,
      "tunnel_id": data.tunnel_id,
      "blast_info": _convert_dict_by_blast_info(data.blast_info_list[0])
  }


def _convert_dict_by_blast_info(data):
  return {
      "id": data.id,
      "explosive": data.explosive,
      "detonator": data.detonator,
      "drilling_depth": data.drilling_depth,
      "blasting_time": data.blasting_time,
      "start_point": data.start_point,
      "finish_point": data.finish_point,
      "blasting_length": data.blasting_length,
      "blast_id": data.blast_id
  }


def _convert_dict_by_work(data):
  ret = {
      "id": data.id,
      "category": data.category,
      "typ": data.typ,
      "state": data.state,
      "accum_time": data.accum_time,
      "blast_id": data.blast_id
  }
  history_list = []
  for work_history in data.work_history_list:
    history_list.append(_convert_dict_by_work_history(work_history))
  ret['work_history_list'] = history_list
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


@blueprint.route('/basepoint/add', methods=["POST"])
#@util.require_login
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
#@util.require_login
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
#@util.require_login
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
#@util.require_login
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
#@util.require_login
def add_tunnel():
  data = request.get_json()
  try:
    work_apis.create_tunnel(data)
    send_request(TUNNEL_ADD, [data])
    return json.dumps(True)
  except:
    logging.exception("Fail to add tunnel.")
    return json.dumps(False)


@blueprint.route('/tunnel/update', methods=["POST"])
#@util.require_login
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
#@util.require_login
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
#@util.require_login
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
#@util.require_login
def get_tunnel_list():
  ret_list = []
  datas = work_apis.get_all_tunnel()
  try:
    for data in datas:
      ret_list.append(_convert_dict_by_tunnel(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get tunnel list")
    return json.dumps(ret_list)


@blueprint.route('/blast/add', methods=["POST"])
#@util.require_login
def add_blast():
  data = request.get_json()
  try:
    # Blast Data
    blast_data = data['blast']
    work_apis.create_blast(blast_data)
    send_request(BLAST_ADD, [blast_data])
    # Blast Info Data
    blast_info_data = data['info']
    work_apis.create_blast_info(blast_info_data)
    send_request(BLAST_INFO_ADD, [blast_info_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to add blast.")
    return json.dumps(False)


@blueprint.route('/blast/update', methods=["POST"])
#@util.require_login
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
#@util.require_login
def remove_blast():
  data = request.get_json()
  try:
    work_apis.remove_blast(data['id'])
    send_request(BLAST_REMOVE, [data['id']])
    return json.dumps(True)
  except:
    logging.exception("Fail to remove blast. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/blast/get/list/tunnel', methods=["POST"])
#@util.require_login
def get_blast_list_by_tunnel():
  data = request.get_json()
  ret_list = []
  try:
    datas = work_apis.get_blast_list_by_tunnel(data['tunnel_id'])
    for data in datas:
      ret_list.append(_convert_dict_by_blast(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get blast list by tunnel.")
    return json.dumps(ret_list)


@blueprint.route('/blast/get/list', methods=["GET"])
#@util.require_login
def get_blast_list():
  ret_list = []
  datas = work_apis.get_all_blast()
  try:
    for data in datas:
      for w in data.work_list:
        logging.info("### typ : %s, created : %s", w.typ, w.created_time)
      ret_data = _convert_dict_by_blast(data)
      ret_list.append(_convert_dict_by_blast(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get blast list.")
    return json.dumps(ret_list)


@blueprint.route('/blastinfo/add', methods=["POST"])
#@util.require_login
def add_blast_info():
  data = request.get_json()
  try:
    work_apis.create_blast_info(data)
    send_request(BLAST_INFO_ADD, [data])
    return json.dumps(True)
  except:
    logging.exception("Fail to add blast info.")
    return json.dumps(False)


@blueprint.route('/blastinfo/update', methods=["POST"])
#@util.require_login
def update_blast_info():
  data = request.get_json()
  try:
    # TODO: 
    ret = work_apis.update_blast_info(data)
    resp_data = _convert_dict_by_blast_info(ret) 
    send_request(BLAST_INFO_UPDATE, [resp_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to update blast info. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/blastinfo/remove', methods=["POST"])
#@util.require_login
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
#@util.require_login
def get_blast_info_by_blast():
  data = request.get_json()
  try:
    ret = work_apis.get_blast_info_by_blast(data['blast_id'])
    return json.dumps(_convert_dict_by_blast_info(ret))
  except:
    logging.exception("Fail to get blast info by blast.")
    return json.dumps({})


@blueprint.route('/blastinfo/get/list', methods=["GET"])
#@util.require_login
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
#@util.require_login
def add_work():
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
    return json.dumps(True)
  except:
    logging.exception("Fail to add work.")
    return json.dumps(False)


@blueprint.route('/work/update', methods=["POST"])
#@util.require_login
def update_work():
  data = request.get_json()
  try:
    # TODO: 
    ret = work_apis.update_work(data)
    resp_data = _convert_dict_by_work(ret)
    send_request(WORK_UPDATE, [resp_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to update work. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/work/remove', methods=["POST"])
#@util.require_login
def remove_work():
  data = request.get_json()
  try:
    work_apis.remove_work(data['id'])
    send_request(WORK_REMOVE, [data['id']])
    return json.dumps(True)
  except:
    logging.exception("Fail to remove work. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/work/get/list/blast', methods=["POST"])
#@util.require_login
def get_work_list_by_blast():
  data = request.get_json()
  ret_list = []
  try:
    datas = work_apis.get_work_list_by_blast(data['blast_id'])
    for data in datas:
      ret_list.append(_convert_dict_by_work(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get work list by blast.")
    return json.dumps(ret_list)


@blueprint.route('/work/get/list', methods=["GET"])
#@util.require_login
def get_work_list():
  ret_list = []
  try:
    datas = work_apis.get_all_work()
    for data in datas:
      ret_list.append(_convert_dict_by_work(data))
    return json.dumps(ret_list)
  except:
    logging.exception("Fail to get work list.")
    return json.dumps(ret_list)


@blueprint.route('/workhistory/add', methods=["POST"])
#@util.require_login
def add_work_history():
  data = request.get_json()
  try:
    work_apis.create_work_history(data)
    send_request(WORK_HISTORY_ADD, [data])
    return json.dumps(True)
  except:
    logging.exception("Fail to add work history.")
    return json.dumps(False)


@blueprint.route('/workhistory/update', methods=["POST"])
#@util.require_login
def update_work_history():
  data = request.get_json()
  try:
    # TODO: 
    ret = work_apis.update_work_history(data)
    resp_data = _convert_dict_by_work_history(ret)
    send_request(WORK_HISTORY_UPDATE, [resp_data])
    return json.dumps(True)
  except:
    logging.exception("Fail to update work history. id : %s", data['id'])
    return json.dumps(False)


@blueprint.route('/workhistory/remove', methods=["POST"])
#@util.require_login
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
#@util.require_login
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
#@util.require_login
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


@blueprint.route('/work/start', methods=["POST"])
#@util.require_login
def start_work():
  """
  data = {'id': str, 'category': int, 'typ': int, 'blast_id': str}
  -> work_data
  """
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
        ret = False
      elif _data.state == WORK_STATE_FINISH:
        ret = False
      else:
        # Start work History
        history_data['state'] = WORK_STATE_IN_PROGRESS
        history_data['timestamp'] = work_apis.get_servertime()
        history_data['accum_time'] = _data.accum_time
        work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD, [history_data])
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'])
        send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
        ret = True
    else:
      # Init data
      history_data['state'] = WORK_STATE_IN_PROGRESS
      history_data['timestamp'] = work_apis.get_servertime()
      history_data['accum_time'] = 0
      work_apis.create_work_history(history_data)
      send_request(WORK_HISTORY_ADD, [history_data])
      work_data = work_apis.update_state_and_accum(data['id'],
                                                   history_data['state'],
                                                   history_data['accum_time'])
      send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
      ret = True
    return json.dumps(ret)
  except:
    logging.exception("Failed to start work. Data : %s", data)
    return json.dumps(False)


@blueprint.route('/work/stop', methods=["POST"])
#@util.require_login
def stop_work():
  """
  data = {'id': str, 'category': int, 'typ': int, 'blast_id': str}
  -> work_data
  """
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
        history_data['accum_time'] = _data.accum_time + work_time.seconds
        work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD, [history_data])
        # TODO: handle work data
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'])
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


@blueprint.route('/work/finish', methods=["POST"])
#@util.require_login
def finish_work():
  """
  data = {'id': str, 'category': int, 'typ': int, 'blast_id': str}
  -> work_data
  """
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
        # TODO: Not stop then can't finish?
        # Finish work history
        history_data['state'] = WORK_STATE_FINISH
        history_data['timestamp'] = work_apis.get_servertime()
        work_time = history_data['timestamp'] - _data.timestamp
        history_data['accum_time'] = _data.accum_time + work_time.seconds
        work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD, [history_data])
        # TODO: handle work data
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'])
        send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
        ret = True
      elif _data.state == WORK_STATE_FINISH:
        ret = False
      else:
        # Finish work history
        history_data['state'] = WORK_STATE_FINISH
        history_data['timestamp'] = work_apis.get_servertime()
        history_data['accum_time'] = _data.accum_time
        work_apis.create_work_history(history_data)
        send_request(WORK_HISTORY_ADD, [history_data])
        # TODO: handle work data
        work_data = work_apis.update_state_and_accum(data['id'],
                                                     history_data['state'],
                                                     history_data['accum_time'])
        send_request(WORK_UPDATE, [_convert_dict_by_work(work_data)])
        # TODO: handle blast data
        if data['typ'] == 111:
          blast_data = work_apis.update_blast_state_and_accum(data['blast_id'], 2,
                                                              history_data['accum_time'])
        else:
          blast_data = work_apis.update_blast_state_and_accum(data['blast_id'], 1,
                                                              history_data['accum_time'])
        send_request(BLAST_UPDATE, [_convert_dict_by_blast(blast_data)])
        ret = True
    return json.dumps(ret)
  except:
    logging.exception("Failed to stop work. Data : %s", data)
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
