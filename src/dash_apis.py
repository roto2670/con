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
  """
  :param : hub data (dict)
  :return type : bool
  :ret_content : post body 로 받은 json 데이터에 location이 입력된 hubdata 가 있다.
                    cloud에 post후 성공하면 true, 실패시 false
  """
  try:
    if apis.IS_DEV:
      return dash_api_mock.update_hub_location_mock(hub_obj)
    else:
      url = "{base}hubs/{hub_id}".format(base=THIRD_BASE_URL,
                                         hub_id=hub_obj['id'])
      headers = _get_user_header(is_json=True)
      data = json.dumps({"custom": hub_obj['custom']})
      logging.info("Update scanner location request. url : %s, data : %s",
                   url, data)
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
  """
  :param : None
  :return type : list of dict
  :ret_content : noti key에 있는 kind를 확인하여 kind를 _get_scanner_list로 넘긴다.
  """
  if apis.IS_DEV:
    return dash_api_mock.scanner_list()
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
  """
  :param : kind
  :return type : list of dict
  :ret_content : get_scanner_list()에서 받은 kind로 cloud에 정보를 요청한다.
                      kind 가 일치하는 hub들의 data를 받는다.
  """
  try:
    url = "{base}hub-kinds/{kind}/hubs".format(base=THIRD_BASE_URL,
                                              kind=kind)
    headers = _get_user_header()
    params = {
        'kind': 0,
        'issuer': 1
    }
    logging.info("Get scanner list request. url :%s, params : %s", url, params)
    resp = requests.get(url, headers=headers, params=params)
    if resp.ok:
      scanners = resp.json()
      logging.info("Get scanner list resp : %s", scanners)
      return scanners
    else:
      logging.warning("Failed get scanner list. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return []
  except:
    logging.exception("Raise error while get scanner list. url : %s, params : %s",
                      url, params)
    return None


def get_beacon_list(product_id):
  """
  :param : product_id
  :return type : list of dict
  :ret_content : product_id가 일치하는 gadget들의 정보를 받아온다. dict 형식의
                      gadget data들이 list로 만들어져 온다.
  """
  try:
    if apis.IS_DEV:
      return dash_api_mock.beacon_list()
    else:
      url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                  pid=product_id)
      headers = _get_user_header()
      logging.info("Get beacon list request. url : %s", url)
      resp = requests.get(url, headers=headers)
      if resp.ok:
        gadgets = resp.json()
        logging.info("Get beacon list resp : %s", gadgets)
        return gadgets
      else:
        logging.warning("Failed to get beacon list. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return []
  except:
    logging.exception("Raise error while get beacon list. url : %s", url)
    return None


def get_beacon_info(beacon_id):
  """
  :param : beacon_id(gadget_id)
  :return type : dict
  :ret_content : beacon_id 일치하는 gadget의 정보를 받아온다. dict형식의 단일 data를 받는다.
  """
  try:
    if apis.IS_DEV:
      return dash_api_mock.beacon_info(beacon_id)
    else:
      url = "{base}gadgets/{bid}".format(base=BASE_URL, bid=beacon_id)
      headers = _get_user_header()
      logging.info("Get beacon info request. url : %s", url)
      resp = requests.get(url, headers=headers)
      if resp.ok:
        ret = resp.json()
        logging.info("Get beacon info resp : %s", ret)
        return ret['v']
      else:
        logging.warning("Failed to get beacon info. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return {}
  except:
    logging.exception("Raise error while get beacon info. url : %s", url)
    return None


def get_detected_hubs(gadget_id, query_id=None):
  """
  :param : gadget_id, query_id
  :return type : dict
  :ret_content : gadget id를 가진 gadget이 어떤 hub에 어느정도 거리로 탐지되었는지에 대한
                  data를 전달 받는다 data는 최대 30개를 받으며 query id를 입력하여 get할 경우
                  최초 30개 이후 연속된 data를 받는다.
  """
  if apis.IS_DEV:
    return dash_api_mock.make_get_detected_hubs(gadget_id)
  url = "{base}gadgets/{gid}/location".format(base=BASE_URL, gid=gadget_id)
  end_ts = time.time()
  start_ts = end_ts - OFFSET_SEC
  params = {
      'start_ts': start_ts,
      'end_ts': end_ts
  }
  headers = _get_user_header()
  try:
    if not query_id:
      logging.info("Get detected hubs requests. url : %s, params : %s",
                   url, params)
      resp = requests.get(url, headers=headers, params=params)
      if resp.ok:
        value = resp.json()
        beacons = value['v']
        logging.info("Get detected hubs resp : %s", beacons)
        return beacons
      else:
        logging.warning("Failed to Get Detected Beacons Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return {}
    else:
      params['query_id'] = query_id
      logging.info("Get detected hubs requests. url : %s, params : %s",
                   url, params)
      query_resp = requests.get(url, headers=headers, params=params)
      if query_resp.ok:
        query_val = query_resp.json()
        query_data = query_val['v']
        logging.info("Get detected hubs resp : %s", query_data)
        if query_data:
          return query_data
        else:
          query_data['query_id'] = None
          return query_data
      else:
        logging.warning("Failed to Get Detected Beacons Response. Code : %s, Text : %s",
                        query_resp.status_code, query_resp.text)
        return {}
  except:
    logging.exception("Raise error while detected hub. url : %s, params : %s",
                      url, params)
    return None


def get_detected_beacons(hub_id, query_id=None):
  """
  :param : hub_id, query_id
  :return type : dict
  :ret_content : hub id를 가진 hub에 어떤 gadget이 어느정도 거리로 탐지되었는지에 대한
                  data를 전달 받는다 data는 최대 30개를 받으며 query id를 입력하여 get할 경우
                  최초 30개 이후 연속된 data를 받는다.
  """
  if apis.IS_DEV:
    return dash_api_mock.make_get_detected_beacons(hub_id)
  url = "{base}hubs/{hid}/location".format(base=BASE_URL, hid=hub_id)
  end_ts = time.time()
  start_ts = end_ts - OFFSET_SEC
  params = {
      'start_ts': start_ts,
      'end_ts': end_ts
  }
  headers = _get_user_header()
  try:
    if not query_id:
      logging.info("Get detected beacons request. url : %s, params : %s",
                   url, params)
      resp = requests.get(url, headers=headers, params=params)
      if resp.ok:
        value = resp.json()
        beacons = value['v']
        logging.info("Get detected beacons resp : %s", beacons)
        return beacons
      else:
        logging.warning("Failed to Get Detected Beacons Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return {}
    else:
      params['query_id'] = query_id
      logging.info("Get detected beacons request. url : %s, params : %s",
                   url, params)
      query_resp = requests.get(url, headers=headers, params=params)
      if query_resp.ok:
        query_val = query_resp.json()
        query_data = query_val['v']
        logging.info("Get detected beacons resp : %s", query_data)
        if query_data:
          return query_data
        else:
          query_data['query_id'] = None
          return query_data
      else:
        logging.warning("Failed to Get Detected Beacons Response. Code : %s, Text : %s",
                        query_resp.status_code, query_resp.text)
        return {}
  except:
    logging.exception("Raise error while get detected beacons. url : %s, params : %s",
                      url, params)
    return None
