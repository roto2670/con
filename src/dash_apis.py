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
import logging

import requests
from flask_login import current_user

import apis
import dash_api_mock


THIRD_BASE_URL = '''http://api.mib.io/v1/'''
BASE_URL = '''http://api.mib.io/i/v1/'''

OFFSET_SEC = 60


def init(app):
  pass


def _get_user_header(is_json=False):
  tokens = json.loads(current_user.organization.tokens)
  token = tokens['access'] if 'access' in tokens else ""
  headers = {
    'Authorization': 'Bearer {}'.format(token)
  }
  if is_json:
    headers['Content-Type'] = 'application/json'
  return headers


def update_scanner_location(hub_obj):
  try:
    if apis.IS_DEV:
      hub_list = dash_api_mock.MOCK_HUB_LIST
      for hub in hub_list:
        if hub['id'] == hub_obj['id']:
          hub['custom'] = hub_obj['custom']
          return True
      return False
    else:
      url = "{base}hubs/{hub_id}".format(base=THIRD_BASE_URL,
                                         hub_id=hub_obj['id'])
      headers = _get_user_header(is_json=True)
      data = json.dumps({"custom": hub_obj['custom']})
      resp = requests.post(url, headers=headers, data=data)
      if resp.ok:
        logging.info("update scanner location successful. Code : %s, Text : %s",
                    resp.status_code, resp.text)
        return True
      else:
        logging.warning("Failed update scanner location. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return False
  except:
    logging.exception("Raise error while update scanner location. hub : %s",
                      hub_obj)
    return None


def get_scanner_list():
  if apis.IS_DEV:
    return dash_api_mock.MOCK_HUB_LIST
  else:
    # TODO: Fixed this logic
    kind_list = []
    for noti_key in current_user.organization.noti_key:
      kind_list.append(noti_key.name)

    scanner_list = []
    for kind in kind_list:
      ret = _get_scanner_list(kind)
      if ret:
        scanner_list += ret
    return scanner_list


def _get_scanner_list(kind):
  try:
    if apis.IS_DEV:
      return dash_api_mock.MOCK_HUB_LIST
    else:
      url = "{base}hub-kinds/{kind}/hubs".format(base=THIRD_BASE_URL,
                                                kind=kind)
      headers = _get_user_header()
      params = {
          'kind': 0,
          'issuer': 1
      }
      resp = requests.get(url, headers=headers, params=params)
      if resp.ok:
        scanners = resp.json()
        return scanners
      else:
        logging.warning("Failed get scanner list. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return []
  except:
    logging.exception("Raise error while get scanner list.")
    return None


def get_beacon_list(product_id):
  try:
    if apis.IS_DEV:
      return dash_api_mock.MOCK_BEACON_LIST
    else:
      url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                  pid=product_id)
      headers = _get_user_header()
      resp = requests.get(url, headers=headers)
      if resp.ok:
        gadgets = resp.json()
        return gadgets
      else:
        logging.warning("Failed to get beacon list. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return []
  except:
    logging.exception("Raise error while get beacon list. pid : %s",
                      product_id)
    return None


def get_beacon_info(beacon_id):
  try:
    if apis.IS_DEV:
      beacon_list = dash_api_mock.MOCK_BEACON_LIST
      for beacon in beacon_list:
        if beacon['id'] == beacon_id:
          return beacon
      return None
    else:
      url = "{base}gadgets/{bid}".format(base=BASE_URL, bid=beacon_id)
      headers = _get_user_header()
      resp = requests.get(url, headers=headers)
      if resp.ok:
        ret = resp.json()
        return ret['v']
      else:
        logging.warning("Failed to get beacon info. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return {}
  except:
    logging.exception("Raise error while get beacon info. beacon id : %s",
                      beacon_id)
    return None


def get_detected_hubs(uuid, product_id, query_id=None):
  if apis.IS_DEV:
    return dash_api_mock.MOCK_GET_DETECTED_HUBS

  beacon_list = get_beacon_list(product_id)
  if not beacon_list:
    logging.warning("Fail to get beacon list")
    return None

  gadget_id = None
  for beacon in beacon_list:
    if beacon['beacon_spec'] and 'uuid' in beacon['beacon_spec']:
      if beacon['beacon_spec']['uuid'] == uuid:
        gadget_id = beacon['id']
        break
      else:
        logging.warning("Can't find uuid is not matched")
  if not gadget_id:
    logging.warning("Not mateched gadget id. uuid : %s, list : %s",
                    uuid, beacon_list)
    return None

  try:
    url = "{base}gadgets/{gid}/location".format(base=BASE_URL, gid=gadget_id)
    end_ts = time.time()
    start_ts = end_ts - OFFSET_SEC
    params = {
        'start_ts': start_ts,
        'end_ts': end_ts
    }
    headers = _get_user_header()
    if not query_id:
      resp = requests.get(url, headers=headers, params=params)
      if resp.ok:
        value = resp.json()
        beacons = value['v']
        return beacons
      else:
        logging.warning("Get Detected Beacons Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return {}
    else:
      params['query_id'] = query_id
      query_resp = requests.get(url, headers=headers, params=params)
      if query_resp.ok:
        query_val = query_resp.json()
        query_data = query_val['v']
        if query_data:
          return query_data
        else:
          query_data['query_id'] = None
          return query_data
      else:
        logging.warning("Get Detected Beacons Response. Code : %s, Text : %s",
                        query_resp.status_code, query_resp.text)
        return {}
  except:
    logging.exception("Raise error while detected hub. uuid : %s", uuid)
    return None



def get_detected_beacons(hub_id, query_id=None):
  if apis.IS_DEV:
    return dash_api_mock.MOCK_GET_DETECTED_BEACONS

  try:
    url = "{base}hubs/{hid}/location".format(base=BASE_URL, hid=hub_id)
    end_ts = time.time()
    start_ts = end_ts - OFFSET_SEC
    params = {
        'start_ts': start_ts,
        'end_ts': end_ts
    }
    headers = _get_user_header()
    if not query_id:
      resp = requests.get(url, headers=headers, params=params)
      if resp.ok:
        value = resp.json()
        beacons = value['v']
        return beacons
      else:
        logging.warning("Get Detected Beacons Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return {}
    else:
      params['query_id'] = query_id
      query_resp = requests.get(url, headers=headers, params=params)
      if query_resp.ok:
        query_val = query_resp.json()
        query_data = query_val['v']
        if query_data:
          return query_data
        else:
          query_data['query_id'] = None
          return query_data
      else:
        logging.warning("Get Detected Beacons Response. Code : %s, Text : %s",
                        query_resp.status_code, query_resp.text)
        return {}
  except:
    logging.exception("Raise error while get detected beacons. hid : %s",
                      hub_id)
    return None
