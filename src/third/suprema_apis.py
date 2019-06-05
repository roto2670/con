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

import requests
import apis
import in_config_apis
from dash import routes as dash_routes

SESSION_ID = {}

# Event
IDENTIFY_SUCCESS_FINGERPRINT = "4865"
IDENTIFY_SUCCESS_FACE = "4867"


def get_event_list():
  event_list = [
      {"id": IDENTIFY_SUCCESS_FACE,
       "name": "Face"},
      {"id": IDENTIFY_SUCCESS_FINGERPRINT,
       "name": "Fingerprint"}
  ]
  return event_list


def login_sup_server(_id, password, base_url, org_id):
  try:
    headers = {'Content-Type': 'application/json'}
    if apis.IS_DEV:
      url = "{base}login".format(base="http://skbs1.prota.space/api/")
      data = {
        "User": {
          "login_id": "admin",
          "password": "adminadmin1"
        }
      }
    else:
      data = {
        "User": {
          "login_id": _id,
          "password": password
        }
      }
      url = "{base}login".format(base=base_url)
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.ok:
      SESSION_ID[org_id] = resp.headers['Bs-Session-Id']
      return True
    else:
      logging.warning(
        "Fail to login. Check your ID, Password.  ID : %s, Password : %s",
        _id, password)
      return False
  except:
    logging.exception("Raise error while Log in to Server. ")
    return None


def get_event_logs(config_data, limit=None):
  """
  :query:
    1. limit = 데이터 수량 (1일 경우 최신 데이터 1개, 2일경우 최신데이터 2개)
    2. offset = 데이터 시점 (1일 경우 최신데이터 1개 전 부터 시작)
    ex) limit=3, offset=3  최신데이터 번호 270일 경우
        [267, 266, 265]번 데이터 총 3개가 날아옴.
  :return:
  """
  _limit = limit if limit else "1"
  try:
    url = "{base}api/events/search".format(base=config_data.base_url)
    headers = {'Content-Type': 'application/json',
               'bs-session-id': SESSION_ID[config_data.organization_id]}
    data = {"Query": {"limit": _limit, "offset": "0"}}
    resp = requests.post(url=url, headers=headers, data=json.dumps(data))
    if resp.ok:
      return resp.json()
    elif resp.status_code == 401:
      login_resp = login_sup_server(config_data.suprema_id,
                                    config_data.suprema_pw,
                                    config_data.base_url,
                                    config_data.organization_id)
      if login_resp:
        headers['bs-session-id'] = SESSION_ID[config_data.organization_id]
      else:
        logging.warning(
          "Fail to login. Check your ID, Password.  ID : %s, Password : %s",
          config_data.suprema_id, config_data.suprema_pw)
        return None
      _resp = requests.get(url=url, headers=headers)
      if _resp.ok:
        return resp.json()
      else:
        logging.warning("Fail to get users information cause fail to login")
        return None
    else:
      return None
  except:
    return None


def set_event(org_id):
  config_data = in_config_apis.get_suprema_config_by_org(org_id)
  if config_data:
    evt_log_chk = get_event_logs(config_data, "1")
    if evt_log_chk and evt_log_chk['EventCollection']['rows']:
      chk_data = evt_log_chk['EventCollection']['rows'][0]
      if config_data.last_data_id:
        if int(chk_data['id']) > config_data.last_data_id:
          limit = int(chk_data['id']) - config_data.last_data_id
          rows = _extract_rows(config_data, limit)
          for data in rows:
            if data['event_type_id']['code'] == config_data.event_id:
              user_info = data['user_id']
              dash_routes.set_worker_count(config_data.organization_id,
                                           user_info['user_id'],
                                           user_info['name'])
              last_id = data['id']
          in_config_apis.update_suprema_config_about_last_id(config_data.organization_id,
                                                             last_id)
          return True
        elif config_data.last_data_id == int(chk_data['id']):
          logging.warning("Server has no more event. wait for next event")
          return False
        else:
          logging.warning("Data Sync is not matched please check your log")
          return False
      else:
        in_config_apis.update_suprema_config_about_last_id(config_data.organization_id,
                                                           chk_data['id'])
        logging.warning("Update of Last event ID completed successfully.")
        return True
    else:
      logging.warning("No logs exist on the server.")
      return False
  else:
    logging.warning("api login data is not exist please login first")
    return False


def _extract_rows(config_data, data_limit):
  evt_log = get_event_logs(config_data, data_limit)
  rows = evt_log['EventCollection']['rows']
  rows = sorted(rows, key=lambda k: k['id'])
  return rows

