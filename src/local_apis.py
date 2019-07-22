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

from constants import THIRD_BASE_URL, BASE_URL


def update_beacon_information(gid, hid, name, kind, moi):
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
  if int(moi) == 1:
    body['custom']['is_visible_moi'] = True
  else:
    body['custom']['is_visible_moi'] = False

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
  if int(count) == 1:
    body['custom']['is_counted_hub'] = True
  else:
    body['custom']['is_counted_hub'] = False
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
  hid = '''bc298b66bd67a950a49bdd64b09d37a0'''  # Galaxy A30
  #hid = '''8cfbf561ef3d4a63f11e3cac862b20fd''' # V20(LG).NaranTest
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


def update_ipcam_information(ipcam_id, name, moi):
  hid = '''bc298b66bd67a950a49bdd64b09d37a0'''  # Galaxy A30
  #hid = '''8cfbf561ef3d4a63f11e3cac862b20fd''' # V20(LG).NaranTest
  url = "{base}gadgets/{ipcam_id}".format(base=BASE_URL, ipcam_id=ipcam_id)
  headers = {
    "Content-Type": "application/json",
    "Src": "{hid}.".format(hid=hid)
  }
  body = {
    "name": name,
    "custom": {}
  }
  if int(moi) == 1:
    body['custom']['is_visible_moi'] = True
  else:
    body['custom']['is_visible_moi'] = False

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