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
import logging

from flask import request

import util
import work_apis
import work.routes
import dashboard.count
from mobile import blueprint


@blueprint.route('/beacon/get/list', methods=["GET"])
@util.require_login
def m_get_beacon_list():
  _ret = {}
  try:
    _data_list = dashboard.count.tunnel_beacon_list()
    _ret['code'] = 200
    _ret['result'] = _data_list
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get beacon list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)



@blueprint.route('/tunnel/get/<tunnel_id>', methods=["GET"])
@util.require_login
def m_get_tunnel(tunnel_id):
  _ret = {}
  try:
    _data = work.routes.get_tunnel_list(is_exclude=True)
    _data = work_apis.get_tunnel(tunnel_id)
    _ret_data = work.routes._convert_dict_by_tunnel(_data, is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = _ret_data
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get tunnel. ID : %s", tunnel_id)
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/tunnel/get/list', methods=["GET"])
@util.require_login
def m_get_tunnel_list():
  _ret = {}
  try:
    _data = work.routes.get_tunnel_list(is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get tunnel list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/tunnel/get/beacon/<uuid>/<major>/<minor>', methods=["GET"])
@util.require_login
def m_get_tunnel_by_beacon(uuid, major, minor):
  # TODO: Improve
  logging.info("Request get tunnel by beacon. uuid : %s, major, %s, minor : %s",
               uuid, major, minor)
  _ret = {}
  try:
    _data = dashboard.count.tunnel_beacon_list()
    _ret_beacon = {}
    _ret_tunnel = {}
    for _beacon in _data:
      if _beacon['beacon_spec']['uuid'] == uuid and \
          int(_beacon['beacon_spec']['major']) == int(major) and \
          int(_beacon['beacon_spec']['minor']) == int(minor):
        _ret_beacon = _beacon
    if _ret_beacon:
      _tunnel = work_apis.get_tunnel(_ret_beacon['custom']['tunnel_id'])
      _ret_tunnel = work.routes._convert_dict_by_tunnel(_tunnel, is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = _ret_tunnel
    logging.info("Response data : %s", _ret)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get tunnel by beacon.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/blast/get/<blast_id>', methods=["GET"])
@util.require_login
def m_get_blast(blast_id):
  _ret = {}
  try:
    _data = work_apis.get_blast(blast_id)
    _ret_data = work.routes._convert_dict_by_blast(_data, is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = _ret_data
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get blast. ID : %s", blast_id)
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/blast/get/list', methods=["GET"])
@util.require_login
def m_get_blast_list():
  _ret = {}
  try:
    _data = work.routes.get_blast_list(is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get blast list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/blast/get/list/tunnel/<tunnel_id>', methods=["GET"])
@util.require_login
def m_get_blast_list_by_tunnel(tunnel_id):
  _ret = {}
  limit = request.args.get('limit', None)
  try:
    if limit:
      _data = work_apis.get_recent_blast_list_by_tunnel(tunnel_id, limit=limit)
      _data_list = []
      for b in _data:
        _data_list.append(work.routes._convert_dict_by_blast(b, is_exclude=True))
      _ret['code'] = 200
      _ret['result'] = _data_list
      return json.dumps(_ret)
    else:
      _data = work.routes.get_blast_list_by_tunnel(tunnel_id=tunnel_id,
                                                   is_exclude=True)
      _ret['code'] = 200
      _ret['result'] = json.loads(_data)
      return json.dumps(_ret)
  except:
    logging.exception("Raise error while get blast list by tunnel. ID : %s",
                      tunnel_id)
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/blastinfo/get/<blast_info_id>', methods=["GET"])
@util.require_login
def m_get_blast_info(blast_info_id):
  _ret = {}
  try:
    _data = work_apis.get_blast_info(blast_info_id)
    _ret_data = work.routes._convert_dict_by_blast_info(_data)
    _ret['code'] = 200
    _ret['result'] = _ret_data
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get blast info list. ID : %s",
                      blast_info_id)
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/blastinfo/get/list', methods=["GET"])
@util.require_login
def m_get_blast_info_list():
  _ret = {}
  try:
    _data = work.routes.get_blast_info_list()
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get blast info list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/blastinfo/get/blast/<blast_id>', methods=["GET"])
@util.require_login
def m_get_blast_info_by_blast(blast_id):
  _ret = {}
  try:
    _data = work.routes.get_blast_info_by_blast(blast_id=blast_id)
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get blast info by blast. ID : %s",
                      blast_id)
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/work/get/<work_id>', methods=["GET"])
@util.require_login
def m_get_work(work_id):
  _ret = {}
  try:
    _data = work_apis.get_work(work_id)
    _ret_data = work.routes._convert_dict_by_work(_data, is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = _ret_data
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get work. ID : %s",
                      work_id)
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/work/get/list', methods=["GET"])
@util.require_login
def m_get_work_list():
  _ret = {}
  try:
    _data = work.routes.get_work_list(is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get work list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/work/get/list/blast/<blast_id>', methods=["GET"])
@util.require_login
def m_get_work_list_by_blast(blast_id):
  _ret = {}
  try:
    _data = work.routes.get_work_list_by_blast(blast_id=blast_id,
                                               is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get work list by blast. ID : %s",
                      blast_id)
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/work/add', methods=["POST"])
@util.require_login
def m_work_add():
  """{'id': str, 'category': int, 'typ': int, 'blast_id': str}
  """
  _ret = {}
  _work_data = {
    "state": 0,
    "accum_time": 0,
    "p_accum_time": 0
  }
  _data = request.get_json()
  _work_data.update(_data)
  logging.info("Request Work ADD data : %s", _data)
  try:
    ret = work.routes.add_work(work_data=_work_data)
    if json.loads(ret):
      work_data = work_apis.get_work(_work_data['id'])
      _ret['code'] = 200
      _ret['result'] = work.routes._convert_dict_by_work(work_data,
                                                         is_exclude=False)
    else:
      _ret['code'] = 200
      _ret['result'] = False
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while add work.")
    _ret['code'] = 500
    _ret['result'] = False
    return json.dumps(_ret)


@blueprint.route('/work/update', methods=["POST"])
@util.require_login
def m_work_update():
  """{'id': str, 'category': int, 'typ': int, 'blast_id': str,
      'statr_time': datetime, 'finish_time': datetime, 'state': int}
  """
  _ret = {}
  _data = request.get_json()
  logging.info("Request Work UPDATE data : %s", _data)
  try:
    ret = work.routes.update_work(_data)
    if json.loads(ret):
      work_data = work_apis.get_work(_data['id'])
      _ret['code'] = 200
      _ret['result'] = work.routes._convert_dict_by_work(work_data,
                                                         is_exclude=False)
    else:
      _ret['code'] = 200
      _ret['result'] = False
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while update work.")
    _ret['code'] = 500
    _ret['result'] = False
    return json.dumps(_ret)


@blueprint.route('/work/action/start', methods=["POST"])
@util.require_login
def m_work_start():
  """{'id': str, 'category': int, 'typ': int, 'blast_id': str}
  """
  _data = request.get_json()
  logging.info("Request Work START data : %s", _data)
  _ret = {}
  try:
    ret = work.routes.start_work(start_data=_data)
    if json.loads(ret):
      _data = work_apis.get_work(_data['id'])
      _ret_data = work.routes._convert_dict_by_work(_data, is_exclude=True)
      _ret['code'] = 200
      _ret['result'] = _ret_data
    else:
      _ret['code'] = 200
      _ret['result'] = False
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while start work.")
    _ret['code'] = 500
    _ret['result'] = False
    return json.dumps(_ret)


@blueprint.route('/work/action/pause', methods=["POST"])
@util.require_login
def m_work_pause():
  """{'id': str, 'category': int, 'typ': int, 'blast_id': str, 'message': str}
  """
  _data = request.get_json()
  logging.info("Request Work PAUSE data : %s", _data)
  _ret = {}
  try:
    ret = work.routes.stop_work(stop_data=_data)
    if json.loads(ret):
      _data = work_apis.get_work(_data['id'])
      _ret_data = work.routes._convert_dict_by_work(_data, is_exclude=True)
      _ret['code'] = 200
      _ret['result'] = _ret_data
    else:
      _ret['code'] = 200
      _ret['result'] = False
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while pause work.")
    _ret['code'] = 500
    _ret['result'] = False
    return json.dumps(_ret)


@blueprint.route('/work/action/finish', methods=["POST"])
@util.require_login
def m_work_finish():
  """{'id': str, 'category': int, 'typ': int, 'blast_id': str}
  """
  _data = request.get_json()
  logging.info("Request Work FINISH data : %s", _data)
  _ret = {}
  try:
    ret = work.routes.finish_work(finish_data=_data)
    if json.loads(ret):
      _data = work_apis.get_work(_data['id'])
      _ret_data = work.routes._convert_dict_by_work(_data, is_exclude=True)
      _ret['code'] = 200
      _ret['result'] = _ret_data
    else:
      _ret['code'] = 200
      _ret['result'] = False
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while pause work.")
    _ret['code'] = 500
    _ret['result'] = False
    return json.dumps(_ret)


@blueprint.route('/pausehistory/get/list/work/<work_id>', methods=["GET"])
@util.require_login
def m_get_pause_history_list_by_work(work_id):
  _ret = {}
  try:
    _data = work.routes.get_pause_history_list_by_work(work_id)
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get pause history list by work. ID :% s",
                      work_id)
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/activity/get/list', methods=["GET"])
@util.require_login
def m_get_activity_list():
  _ret = {}
  try:
    _data = work.routes.get_activity_list()
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get activity list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/equipment/get/list', methods=["GET"])
@util.require_login
def m_get_equipment_list():
  _ret = {}
  try:
    _data = work.routes.get_equipment_list()
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get equipment list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/operator/get/list', methods=["GET"])
@util.require_login
def m_get_operator_list():
  _ret = {}
  try:
    _data = work.routes.get_operator_list()
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get operator list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/message/get/list', methods=["GET"])
@util.require_login
def m_get_message_list():
  _ret = {}
  try:
    _data = work.routes.get_message_list()
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get message list.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)
