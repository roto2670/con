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

from flask import request
from flask_login import current_user

import apis
import util
import constants
import in_config_apis
from dash import blueprint


@blueprint.route('/location/info', methods=["GET"])
@util.require_login
def get_location_inforamtion():
  """
  :param : None
  :return : infomation of dict
  """
  data = {
      "product_id": "mibsskec",
      "interval": 10,
      "stage": current_user.level
  }
  return json.dumps(data)


@blueprint.route('/worker_log', methods=["GET"])
@util.require_login
def get_entrance_worker_log():
  org_id = current_user.organization_id
  _page_num = request.args.get('page_num')
  _limit = request.args.get('limit', 100)
  log_list = in_config_apis.get_enterence_worker_log_list(org_id,
                                                          page_num=int(_page_num),
                                                          limit=int(_limit))
  new_list = []
  for log in log_list.items:
    trans_dict = log.__dict__
    if '_sa_instance_state' in trans_dict:
      del trans_dict['_sa_instance_state']
    trans_dict['event_time'] = str(trans_dict['event_time'])
    trans_dict['created_time'] = str(trans_dict['created_time'])
    new_list.append(trans_dict)
  return json.dumps(new_list)


@blueprint.route('/worker_log/in/<ap>', methods=["GET"])
@util.require_login
def get_entrance_in_worker_log(ap):
  org_id = current_user.organization_id
  _page_num = request.args.get('page_num')
  _limit = request.args.get('limit', 100)
  log_list = in_config_apis.get_enterence_in_worker_log_list(org_id, int(ap),
                                                             page_num=int(_page_num),
                                                             limit=int(_limit))
  new_list = []
  for log in log_list.items:
    trans_dict = log.__dict__
    if '_sa_instance_state' in trans_dict:
      del trans_dict['_sa_instance_state']
    trans_dict['event_time'] = str(trans_dict['event_time'])
    trans_dict['created_time'] = str(trans_dict['created_time'])
    new_list.append(trans_dict)
  return json.dumps(new_list)


@blueprint.route('/worker_log/out/<ap>', methods=["GET"])
@util.require_login
def get_entrance_out_worker_log(ap):
  org_id = current_user.organization_id
  _page_num = request.args.get('page_num')
  _limit = request.args.get('limit', 100)
  log_list = in_config_apis.get_enterence_out_worker_log_list(org_id, int(ap),
                                                              page_num=int(_page_num),
                                                              limit=int(_limit))
  new_list = []
  for log in log_list.items:
    trans_dict = log.__dict__
    if '_sa_instance_state' in trans_dict:
      del trans_dict['_sa_instance_state']
    trans_dict['event_time'] = str(trans_dict['event_time'])
    trans_dict['created_time'] = str(trans_dict['created_time'])
    new_list.append(trans_dict)
  return json.dumps(new_list)


@blueprint.route('/equip_log', methods=["GET"])
@util.require_login
def get_entrance_equip_log():
  org_id = constants.ORG_ID
  _page_num = request.args.get('page_num')
  _limit = request.args.get('limit', 100)
  log_list = in_config_apis.get_entrance_equip_log_list(org_id,
                                                        page_num=int(_page_num),
                                                        limit=int(_limit))
  new_list = []
  for log in log_list.items:
    trans_dict = log.__dict__
    if '_sa_instance_state' in trans_dict:
      del trans_dict['_sa_instance_state']
    trans_dict['event_time'] = str(trans_dict['event_time'])
    trans_dict['created_time'] = str(trans_dict['created_time'])
    new_list.append(trans_dict)
  return json.dumps(new_list)


@blueprint.route('/equip_log/in/<ap>', methods=["GET"])
@util.require_login
def get_entrance_in_equip_log(ap):
  org_id = constants.ORG_ID
  _page_num = request.args.get('page_num')
  _limit = request.args.get('limit', 100)
  log_list = in_config_apis.get_entrance_in_equip_log_list(org_id, int(ap),
                                                           page_num=int(_page_num),
                                                           limit=int(_limit))
  new_list = []
  for log in log_list.items:
    trans_dict = log.__dict__
    if '_sa_instance_state' in trans_dict:
      del trans_dict['_sa_instance_state']
    trans_dict['event_time'] = str(trans_dict['event_time'])
    trans_dict['created_time'] = str(trans_dict['created_time'])
    new_list.append(trans_dict)
  return json.dumps(new_list)


@blueprint.route('/equip_log/out/<ap>', methods=["GET"])
@util.require_login
def get_entrance_out_equip_log(ap):
  org_id = constants.ORG_ID
  _page_num = request.args.get('page_num')
  _limit = request.args.get('limit', 100)
  log_list = in_config_apis.get_entrance_out_equip_log_list(org_id, int(ap),
                                                            page_num=int(_page_num),
                                                            limit=int(_limit))
  new_list = []
  for log in log_list.items:
    trans_dict = log.__dict__
    if '_sa_instance_state' in trans_dict:
      del trans_dict['_sa_instance_state']
    trans_dict['event_time'] = str(trans_dict['event_time'])
    trans_dict['created_time'] = str(trans_dict['created_time'])
    new_list.append(trans_dict)
  return json.dumps(new_list)
