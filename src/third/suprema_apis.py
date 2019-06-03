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

from flask_login import current_user

import requests
import apis

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


def login_sup_server(_id, password, base_url):
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
      SESSION_ID[current_user.organization_id] = resp.headers['Bs-Session-Id']
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
               'bs-session-id': SESSION_ID[current_user.organization_id]}
    data = json.dumps({"Query": {"limit": _limit, "offset": "0"}})
    resp = requests.post(url=url, headers=headers, data=json.dumps(data))
    if resp.ok:
      return resp.json()
    elif resp.status_code == 401:
      login_resp = login_sup_server(config_data.suprema_id,
                                    config_data.suprema_pw,
                                    config_data.base_url)
      if login_resp:
        headers['bs-session-id'] = SESSION_ID[current_user.organization_id]
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
