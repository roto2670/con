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
    "custom": {
        "location": location
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
