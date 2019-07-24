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
import dashboard
import in_config_apis
from dash import routes as dash_routes
from constants import ORG_ID, LOCAL_HUB_CLI_ADDR, LOCAL_HUB_CLI_GID


SESSION_ID = {}
LAST_ID_CACHE = {}
ID_PW_CACHE = {}

# Event
IDENTIFY_SUCCESS_FINGERPRINT = "4865"
IDENTIFY_SUCCESS_FACE = "4867"
IDENTIFY_FAIL_FINGERPRINT = "5124"
IDENTIFY_FAIL_FACE = "5125"

VERIFY_SUCCESS_ID_PIN = "4097"
VERIFY_SUCCESS_CARD = "4102"
VERIFY_SUCCESS_CARD_PIN = "4103"

POST = '''post'''
GET = '''get'''

LOCAL_CLI_HEADER = {
    "Authorization": "Bearer console-admin",
    "Content-Type": "application/json"
}


def _send_local_biostar(method, subpath, data_headers=None, data_body=None):
  url = "{base}gadgets/{gid}/sync-endpoints/*".format(base=LOCAL_HUB_CLID_ADDR,
                                                      gid=LOCAL_HUB_CLID_GID)
  body = {
      "key": "smartsystem",
      "otp": 0,
      "args": [],
      "kwargs": {
          "method": method.lower(),
          "subpath": subpath,
          "headers": data_headers,
          "body": ""
      }
  }
  if data_body:
    body['kwargs']['body'] = json.dumps(data_body)

  resp = requests.post(url=url, headers=LOCAL_CLI_HEADER, data=json.dumps(body))
  resp_body = resp.json()
  logging.info("resp : %s", resp_body)
  if resp_body['code'] == 0 and resp_body['status'] == 200:
    return resp_body
  elif resp_body['code'] == 0 and resp_body['status'] == 400:
    _resp_body = json.loads(resp_body['body'])
    if _resp_body['Response']['code'] == "101":
      resp_body['status'] = 401
    else:
      resp_body['status'] = 400
    resp_body['text'] = _resp_body['Response']['message']
    return resp_body
  elif resp_body['code'] == 124:
    resp_body['status'] = 504
    resp_body['text'] = "Server Timeout"
    return resp_body
  else:
    _resp_body = json.loads(resp_body['body'])
    resp_body['status'] = 400
    resp_body['text'] = _resp_body['Response']['message']
    return resp_body


def get_event_list():
  event_list = [
      {"id": IDENTIFY_SUCCESS_FACE,
       "name": "Face"},
      {"id": IDENTIFY_SUCCESS_FINGERPRINT,
       "name": "Fingerprint"}
  ]
  return event_list


def check_login(_id, _pw):
  try:
    headers = {'Content-Type': 'application/json'}
    data = {
      "User": {
        "login_id": _id,
        "password": _pw
      }
    }
    url = "api/login"
    resp = _send_local_biostar(POST, url, headers, data)
    if resp['status'] == 200:
      SESSION_ID[ORG_ID] = resp['headers']['bs-session-id']
      return True
    else:
      logging.warning(
        "Fail to check login. Check your ID, Password. Data : %s", data)
      return False
  except:
    logging.exception("Raise error while Log-in to Server.")
    return None


def login_sup_server():
  try:
    headers = {'Content-Type': 'application/json'}
    if apis.IS_DEV:
      data = {
        "User": {
          # "login_id": "smartsystem",
          # "password": "mproject1"
          "login_id": "admin",
          "password": "admin123!"
        }
      }
    else:
      data = {
        "User": {
          "login_id": ID_PW_CACHE[ORG_ID]['id'],
          "password": ID_PW_CACHE[ORG_ID]['pw']
        }
      }
    url = "api/login"
    resp = _send_local_biostar(POST, url, headers, data)
    if resp['status'] == 200:
      SESSION_ID[ORG_ID] = resp['headers']['bs-session-id']
      return True
    else:
      logging.warning(
        "Fail to login. Check your ID, Password. Data : %s", data)
      return False
  except:
    logging.exception("Raise error while Log-in to Server.")
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
    url = 'api/events/search'
    headers = {'Content-Type': 'application/json',
               'bs-session-id': SESSION_ID[ORG_ID]}
    data = {"Query": {"limit": _limit, "offset": "0"}}
    resp = _send_local_biostar(POST, url, headers, data)
    if resp['status'] == 200:
      return json.loads(resp['body'])
    elif resp['status'] == 401:
      login_resp = login_sup_server()
      if login_resp:
        headers['bs-session-id'] = SESSION_ID[ORG_ID]
      else:
        logging.warning(
            "Fail to login. Check your ID, Password.  ID : %s, Password : %s",
            "a", "b")
        return None
      _resp = _send_local_biostar(POST, url, headers, data)
      if _resp['status'] == 200:
        return json.loads(resp['body'])
      else:
        logging.warning("Failed to retry get event logs. url : %s, code : %s, text : %s",
                        url, _resp['status'], _resp['text'])
        return None
    else:
      logging.warning("Failed to get event logs. url : %s, code : %s, text : %s",
                      url, resp['status'], resp['text'])
      return None
  except:
    logging.exception("Raise error while get event log. id : %s, base url : %s",
                      1, 2)
    return None


def set_last_id_cache(org_id, last_id):
  LAST_ID_CACHE[org_id] = last_id


def set_id_pw(org_id, _id, pw):
  if org_id not in ID_PW_CACHE:
    ID_PW_CACHE[org_id] = {}
  ID_PW_CACHE[org_id]['id'] = _id
  ID_PW_CACHE[org_id]['pw'] = pw


def _set_worker_count(org_id, data):
  user_info = data['user_id']
  print(org_id)
  print("data : ", data)
  if 'user_id' in user_info and 'name' in user_info:
    print("set worker ", user_info)
    dashboard.count.set_worker_count(org_id,
                                     user_info['user_id'],
                                     user_info['name'],
                                     data)


def _extract_rows(config_data, data_limit):
  evt_log = get_event_logs(config_data, data_limit)
  rows = evt_log['EventCollection']['rows']
  rows = sorted(rows, key=lambda k: k['id'])
  return rows


def set_event(org_id):
  if org_id in LAST_ID_CACHE:
    last_data_id = LAST_ID_CACHE[org_id]
    config_data = in_config_apis.get_suprema_config_by_org(org_id)
    evt_log_chk = get_event_logs(config_data, "1")
    logging.info("### evt log chk : %s", evt_log_chk)
    if evt_log_chk and evt_log_chk['EventCollection']['rows']:
      chk_data = evt_log_chk['EventCollection']['rows'][0]
      logging.info("### last data id : %s", last_data_id)
      if last_data_id:
        if int(chk_data['id']) > last_data_id:
          limit = int(chk_data['id']) - last_data_id
          rows = _extract_rows(config_data, limit)
          last_id = None
          for data in rows:
            #if data['event_type_id']['code'] == IDENTIFY_SUCCESS_FACE:
            if data['event_type_id']['code'] == IDENTIFY_SUCCESS_FINGERPRINT:
              _set_worker_count(org_id, data)
            elif data['event_type_id']['code'] == VERIFY_SUCCESS_ID_PIN:
              # BUS STATION
              logging.info("#### pin id success. data : %s", data)
              _set_worker_count(org_id, data)
            elif data['event_type_id']['code'] == VERIFY_SUCCESS_CARD:
              # BUS STATION
              logging.info("#### card success. data : %s", data)
              _set_worker_count(org_id, data)
            elif data['event_type_id']['code'] == VERIFY_SUCCESS_CARD_PIN:
              # BUS STATION
              logging.info("#### card pin success. data : %s", data)
              _set_worker_count(org_id, data)
            last_id = data['id']
          if last_id:
            set_last_id_cache(org_id, int(last_id))
            in_config_apis.update_suprema_config_about_last_id(org_id,
                                                               int(last_id))
          return True
        elif config_data.last_data_id == int(chk_data['id']):
          logging.warning("Server has no more event. wait for next event")
          return False
        else:
          logging.warning("Data Sync is not matched please check your log")
          return False
      else:
        # TODO: last_id_data is 0?
        set_last_id_cache(org_id, int(chk_data['id']))
        in_config_apis.update_suprema_config_about_last_id(org_id,
                                                           int(chk_data['id']))
        logging.warning("Update of Last event ID completed successfully.")
        return True
    else:
      logging.warning("No logs exist on the server.")
      return False
  else:
    logging.warning("api login data is not exist please login first")
    return False


def get_device_list(config_data):
  try:
    url = "api/devices"
    headers = {'Content-Type': 'application/json',
               'bs-session-id': SESSION_ID[ORG_ID]}
    resp = _send_local_biostar(GET, url, headers)
    if resp['status'] == 200:
      return json.loads(resp['body'])
    elif resp['status'] == 401:
      login_resp = login_sup_server()
      if login_resp:
        headers['bs-session-id'] = SESSION_ID[ORG_ID]
      else:
        logging.warning(
            "Fail to login. Check your ID, Password.  ID : %s, Password : %s",
            config_data.suprema_id, config_data.suprema_pw)
        return None
      _resp = _send_local_biostar(GET, url, headers)
      if _resp['status'] == 200:
        return json.loads(resp['body'])
      else:
        logging.warning("Failed to retry get device list. url : %s, code : %s, text : %s",
                        url, _resp['status'], _resp['text'])
        return None
    else:
      logging.warning("Failed to get device list. url : %s, code : %s, text : %s",
                      url, resp['status'], resp['text'])
      return None
  except:
    logging.exception("Raise error while get device list. id : %s, base url : %s",
                      config_data.suprema_id, config_data.base_url)
    return None
