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
import in_apis
import in_config_apis
import dashboard.count
import dash_api_mock


THIRD_BASE_URL = '''http://api.mib.io/v1/'''
BASE_URL = '''http://api.mib.io/i/v1/'''
OFFSET_SEC = 60


def init(app):
  pass


def _get_user_header(is_json=False, org_id=None):
  if org_id:
    _org = in_apis.get_organization(org_id)
    tokens = json.loads(_org.tokens)
  else:
    tokens = json.loads(current_user.organization.tokens)
  token = tokens['access'] if 'access' in tokens else ""
  headers = {
    'Authorization': 'Bearer {}'.format(token)
  }
  if is_json:
    headers['Content-Type'] = 'application/json'
  return headers


def update_scanner(hub_obj):
  """
  :param : hub data (dict)
  :return type : bool
  :ret_content : post body 로 받은 json 데이터에 location이 입력된 hubdata 가 있다.
                    cloud에 post후 성공하면 true, 실패시 false
  """
  try:
    if apis.IS_DEV:
      ret = dash_api_mock.update_hub_location_mock(hub_obj)
      set_device_data([hub_obj], current_user.organization_id)
      return ret
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
        set_device_data([hub_obj], current_user.organization_id)
        return True
      else:
        logging.warning("Failed update scanner location. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return False
  except:
    logging.exception("Raise error while update scanner location. hub : %s",
                      hub_obj)
    return None


def update_cam_location(cam_data):
  try:
    url = "{base}gadgets/{cam_data}".format(base=THIRD_BASE_URL,
                                            cam_data=cam_data['id'])
    headers = _get_user_header(is_json=True)
    data = json.dumps({"custom": cam_data['custom']})
    logging.info("Update cam location request. url : %s, data : %s",
                 url, data)
    resp = requests.post(url, headers=headers, data=data)
    if resp.ok:
      logging.info("update cam location successful. Code : %s, Text : %s",
                   resp.status_code, resp.text)
      return True
    else:
      logging.warning("Failed update cam location. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return False
  except:
    logging.exception("Raise error while update cam location.",
                      cam_data)
    return None


def get_scanner_list(kind, org_id=None):
  """
  :param : kind
  :return type : list of dict
  :ret_content : get_scanner_list()에서 받은 kind로 cloud에 정보를 요청한다.
                      kind 가 일치하는 hub들의 data를 받는다.
  """
  _org_id = org_id if org_id else current_user.organization_id
  if apis.IS_DEV:
    ret = dash_api_mock.scanner_list()
    set_device_data(ret, _org_id)
    return ret
  try:
    url = "{base}hub-kinds/{kind}/hubs".format(base=THIRD_BASE_URL,
                                               kind=kind)
    headers = _get_user_header(org_id=org_id)
    params = {
        'kind': 0,
        'issuer': 1
    }
    logging.info("Get scanner list request. url :%s, params : %s", url, params)
    resp = requests.get(url, headers=headers, params=params)
    if resp.ok:
      scanners = resp.json()
      logging.info("Get scanner list len resp : %s", len(scanners))
      set_device_data(scanners, _org_id)
      return scanners
    else:
      logging.warning("Failed get scanner list. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return []
  except:
    logging.exception("Raise error while get scanner list. url : %s", url)
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
      ret = dash_api_mock.beacon_list()
      set_device_data(ret, current_user.organization_id)
      return ret
    else:
      url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                  pid=product_id)
      headers = _get_user_header()
      logging.info("Get beacon list request. url : %s", url)
      resp = requests.get(url, headers=headers)
      if resp.ok:
        gadgets = resp.json()
        logging.info("Get beacon list resp size : %s", len(gadgets))
        set_device_data(gadgets, current_user.organization_id)
        return gadgets
      else:
        logging.warning("Failed to get beacon list. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return []
  except:
    logging.exception("Raise error while get beacon list. url : %s", url)
    return None


def get_cam_list(product_id):
  try:
    url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                pid=product_id)
    headers = _get_user_header()
    logging.info("Get beacon list request. url : %s", url)
    resp = requests.get(url, headers=headers)
    if resp.ok:
      ret_list = []
      gadgets = resp.json()
      for gadget in gadgets:
        if gadget['hub_id']:
          ret_list.append(gadget)
      logging.info("Get beacon list resp : %s", ret_list)
      set_device_data(ret_list, current_user.organization_id)
      return ret_list
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


def get_detected_beacons(hub_id, query_id=None, org_id=None):
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
  headers = _get_user_header(org_id=org_id)
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
        logging.info("Get detected beacons resp size : %s", len(query_data))
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


def get_refresh_beacon_list(product_id):
  """
  :param : product_id
  :return type : list of dict
  :ret_content : product_id가 일치하는 gadget들의 정보를 받아온다. dict 형식의
                      gadget data들이 list로 만들어져 온다.
  """
  try:
    if apis.IS_DEV:
      ret = dash_api_mock.beacon_list()
      set_device_data(ret, current_user.organization_id, is_force=True)
      return ret
    else:
      url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                  pid=product_id)
      headers = _get_user_header()
      logging.info("Get refresh beacon list request. url : %s", url)
      resp = requests.get(url, headers=headers)
      if resp.ok:
        gadgets = resp.json()
        logging.info("Get refresh beacon list resp size : %s", len(gadgets))
        set_device_data(gadgets, current_user.organization_id, is_force=True)
        return gadgets
      else:
        logging.warning("Failed to get refresh beacon list. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return []
  except:
    logging.exception("Raise error while get refresh beacon list. url : %s", url)
    return None


def set_device_data(data, org_id, is_force=False):
  for device in data:
    ret = dashboard.count.set_device_data_info(device['id'], device,
                                               is_force=is_force)
    if ret:
      in_config_apis.create_or_update_device_data(org_id, device)
  return True
