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
from flask_login import current_user

import util
import constants
import in_config_apis
from dash import blueprint
from dashboard import count

SERVER_ADDR = {}


def set_server_addr(local_addr):
  SERVER_ADDR['internal'] = local_addr.strip()


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
  req_host = request.headers['Host']
  req_host = req_host.strip().split(":")[0]
  if req_host == SERVER_ADDR['internal']:
    data['internal'] = True
  else:
    data['internal'] = False
  return json.dumps(data)


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


@blueprint.route('/gadget/count/list', methods=["GET"])
def get_gadget_count_list():
  in_tunnel_list = []
  ap1_list = count.get_all_equips(1)
  ap2_list = count.get_all_equips(2)
  data = {
      "at1": {
          "1":[], "2":[], "3":[], "4":[], "5":[], "6":[], "7":[], "8":[], "9":[], "10":[],
          "11":[], "12":[], "13":[], "14":[], "15":[], "16":[], "17":[], "18":[], "19":[]
      },
      "at2": {
          "1":[], "2":[], "3":[], "4":[], "5":[], "6":[], "7":[], "8":[], "9":[], "10":[],
          "11":[], "12":[], "13":[], "14":[], "15":[], "16":[], "17":[], "18":[], "19":[]
      },
      "other": {
          "1":[], "2":[], "3":[], "4":[], "5":[], "6":[], "7":[], "8":[], "9":[], "10":[],
          "11":[], "12":[], "13":[], "14":[], "15":[], "16":[], "17":[], "18":[], "19":[]
      },
      "kind": count.SHOT_GADGET_INFO
  }
  for k, e in ap1_list.items():
    if isinstance(e, dict):
      data['at1'][e['tag']].append(e)
      in_tunnel_list.append(k)

  for k, e in ap2_list.items():
    if isinstance(e, dict):
      data['at2'][e['tag']].append(e)
      in_tunnel_list.append(k)
  detect_gadget_list = count.get_all_gadget_count_equips()
  for e in detect_gadget_list:
    if e['id'] not in in_tunnel_list:
      value = {"device_name": e['name'], "tag": e['tags'][0],
               "event_time": str(in_config_apis.get_servertime())}
      data['other'][value['tag']].append(value)
  return json.dumps(data)

