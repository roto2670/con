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
import work.routes
from mobile import blueprint


@blueprint.route('/beacon/get/list', methods=["GET"])
@util.require_login
def m_get_beacon_list():
  return json.dumps("WIP")


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
  return json.dumps("WIP")


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
  try:
    _data = work.routes.get_blast_list_by_tunnel(tunnel_id=tunnel_id,
                                                 is_exclude=True)
    _ret['code'] = 200
    _ret['result'] = json.loads(_data)
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while get blast list by tunnel.")
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
    logging.exception("Raise error while get blast info by blast.")
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
    logging.exception("Raise error while get work list by blast.")
    _ret['code'] = 500
    _ret['result'] = []
    return json.dumps(_ret)


@blueprint.route('/work/action/start', methods=["POST"])
@util.require_login
def m_work_start():
  """{'id': str, 'category': int, 'typ': int, 'blast_id': str}
  """
  _data = request.get_json()
  _ret = {}
  try:
    ret = work.routes.start_work(start_data=_data)
    if json.loads(ret):
      _ret['code'] = 200
      _ret['result'] = True
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
  _ret = {}
  try:
    ret = work.routes.stop_work(stop_data=_data)
    if json.loads(ret):
      _ret['code'] = 200
      _ret['result'] = True
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
  _ret = {}
  try:
    ret = work.routes.finish_work(finish_data=_data)
    if json.loads(ret):
      _ret['code'] = 200
      _ret['result'] = True
    else:
      _ret['code'] = 200
      _ret['result'] = False
    return json.dumps(_ret)
  except:
    logging.exception("Raise error while pause work.")
    _ret['code'] = 500
    _ret['result'] = False
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
