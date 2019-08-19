# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Naran Inc. All rights reserved.
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

import constants
import dashboard.count
from constants import THIRD_BASE_URL, BASE_URL, REG_HUB_ID


def update_beacon_information(gid, hid, name, kind, moi, ipcam_id):
  url = "{base}gadgets/{gid}".format(base=BASE_URL, gid=gid)
  headers = {
    "Content-Type": "application/json",
    "Src": "{hid}.".format(hid=hid)
  }
  body = {
    "name": name,
    "tags": [kind],
    "custom": {}
  }
  _beacon = dashboard.count.get_beacon(gid)
  _custom = _beacon['custom']
  if int(moi) == 1:
    _custom['is_visible_moi'] = True
  else:
    _custom['is_visible_moi'] = False
  if ipcam_id:
    _custom['ipcamId'] = ipcam_id
  else:
    if 'ipcamId' in _custom:
      del _custom['ipcamId']
  body['custom'] = _custom

  try:
    resp = requests.post(url, headers=headers, data=json.dumps(body))
    if resp.ok:
      logging.info("update beacon information successful. Code : %s, Text : %s",
                   resp.status_code, resp.text)
      return True
    else:
      logging.warning("Failed update beacon information. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return False
  except:
    logging.exception("Raise error while update beacon information. Body : %s",
                      body)
    return None


def update_scanner_information(hid, name, location, count):
  url = "{base}hubs/{hid}".format(base=BASE_URL, hid=hid)
  headers = {
    "Content-Type": "application/json"
  }
  body = {
    "name": name,
    "tags": [location],
    "custom": {
    }
  }
  _scanner = dashboard.count.get_scanner(hid)
  _custom = _scanner['custom']
  if int(count) == 1:
    _custom['is_counted_hub'] = True
  else:
    _custom['is_counted_hub'] = False
  body['custom'] = _custom

  try:
    resp = requests.post(url, headers=headers, data=json.dumps(body))
    if resp.ok:
      logging.info("update scanner information successful. Code : %s, Text : %s",
                   resp.status_code, resp.text)
      return True
    else:
      logging.warning("Failed update scanner information. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return False
  except:
    logging.exception("Raise error while update scanner information. Body : %s",
                      body)
    return None


def register_ipcam(gadget_info):
  hid = REG_HUB_ID
  url = "{base}hubs/{hid}/event".format(base=BASE_URL, hid=hid)
  headers = {
    "Content-Type": "application/json",
    "Src": "{hid}.".format(hid=hid)
  }
  body = {
    "topic": "gadget.added",
    "value": gadget_info
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(body))
    if resp.ok:
      logging.info("register ipcam successful. Code : %s, Text : %s",
                   resp.status_code, resp.text)
      return True
    else:
      logging.warning("Failed register ipcam. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return False
  except:
    logging.exception("Raise error while register ipcam. Body : %s",
                      body)
    return None


def update_ipcam_information(ipcam_id, name, moi, kind, data=None):
  hid = REG_HUB_ID
  url = "{base}gadgets/{ipcam_id}".format(base=BASE_URL, ipcam_id=ipcam_id)
  headers = {
    "Content-Type": "application/json",
    "Src": "{hid}.".format(hid=hid)
  }
  body = {
    "name": name,
    "kind": [kind],
    "custom": {}
  }
  if data:
    body['custom'] = data['custom']
  else:
    _ipcam = dashboard.count.get_ipcam(ipcam_id)
    _custom = _ipcam['custom']
    if int(moi) == 1:
      _custom['is_visible_moi'] = True
    else:
      _custom['is_visible_moi'] = False
    body['custom'] = _custom

  try:
    resp = requests.post(url, headers=headers, data=json.dumps(body))
    if resp.ok:
      logging.info("update ipcam information successful. Code : %s, Text : %s",
                   resp.status_code, resp.text)
      return True
    else:
      logging.warning("Failed update ipcam information. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return False
  except:
    logging.exception("Raise error while update ipcam information. Body : %s",
                      body)
    return None


def remove_ipcam(ipcam_id):
  hid = REG_HUB_ID
  _ipcam = dashboard.count.get_ipcam(ipcam_id)
  url = "{base}hubs/{hid}/event".format(base=BASE_URL, hid=hid)
  headers = {
    "Content-Type": "application/json",
    "Src": "{hid}.".format(hid=hid)
  }
  body = {
    "topic": "gadget.removed",
    "value": _ipcam
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(body))
    if resp.ok:
      logging.info("remove ipcam successful. Code : %s, Text : %s",
                   resp.status_code, resp.text)
      return True
    else:
      logging.warning("Failed remove ipcam. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return False
  except:
    logging.exception("Raise error while remove ipcam. Body : %s",
                      body)
    return None


def get_suprema_device_list():
  try:
    url = "{}/device_list".format(constants.SUPREMA_ADDR)
    resp = requests.get(url)
    return resp.json()
  except:
    logging.exception("Failed to get device list.")
    return {}
