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


URL_HOST = '''http://tapi.mib.io'''
TEST_URL = URL_HOST + '''/v1/'''
TEST_URL_I = URL_HOST + '''i/v1/'''
BASE_URL = '''http://api.mib.io/v1'''
BASE_URL_I = '''http://api.mib.io/i/v1'''

HEADERS = {}
JSON_HEADERS = {}


TEST_TOKEN = '''c24609a47b9f7615a9acd157ed07af1e'''         #for test
OFFSET_SEC = 60
TEST_HUB_KIND = '''com.thenaran.skec'''                     #for test


def init(app):
  HEADERS['Authorization'] = 'Bearer {}'.format(TEST_TOKEN)
  JSON_HEADERS['Authorization'] = 'Bearer {}'.format(TEST_TOKEN)
  JSON_HEADERS['Content-Type'] = 'application/json'


def add_scanner_location(hub_obj):
  try:
    url = TEST_URL + 'hubs/' + hub_obj['id']
    resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(hub_obj['custom']))
    if resp.ok:
      logging.info("update scanner location successful. Code : %s, Text : %s",
                   resp.status_code, resp.text)
      return True
    else:
      logging.warning("update scanner location Response. Code : %s, Text : %s", resp.status_code, resp.text)
      return False
  except:
    logging.exception("Raise error.")
    return None


def get_scanner_list():
  url = TEST_URL + 'hub-kinds/' + TEST_HUB_KIND + '/hubs?kind=0&issuer=1'
  try:
    resp = requests.get(url, headers=HEADERS)
    if resp.ok:
      scanners = resp.json()
      return scanners
    else:
      logging.warning("Get all scanners Response. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return []
  except:
    logging.exception("Raise error.")
    return None


def get_beacon_list():
  url = TEST_URL + 'products/mibs/gadgets'
  try:
    resp = requests.get(url, headers=HEADERS)
    if resp.ok:
      gadgets = resp.json()
      return gadgets
    else:
      logging.warning("Get all Gadgets Response. Code : %s, Text : %s",
                      resp.status_code, resp.text)
      return []
  except:
    logging.exception("Raise error.")
    return None


def get_detected_beacons(hub_id, query_id=None):
  # end_ts, start_ts = time.time(), time.time() - OFFSET_SEC
  # url = BASE_URL + 'hubs/' + hub_id + '/location?start_ts=' + start_ts + '&end_ts' + end_ts
  # test URL
  #url = 'http://tapi.mib.io/i/v1/hubs/799b9f874bc1c50775233d2a0c00e388/location' \
  #      '?start_ts=1555475970.9703329&end_ts=1555475978.9703329'
  url = 'http://tapi.mib.io/i/v1/hubs/799b9f874bc1c50775233d2a0c00e388/location?start_ts=1555669800.628462&end_ts=1555669812.628462'
  if not query_id:
    try:
      resp = requests.get(url, headers=HEADERS)
      if resp.ok:
        value = resp.json()
        beacons = value['v']
        return beacons
      else:
        logging.warning("Get Detected Beacons Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return {}
    except:
      logging.exception("Raise error.")
      return None
  else:
    query_url = url + '&query_id=' + query_id
    try:
      query_resp = requests.get(query_url, headers=HEADERS)
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
      logging.exception("Raise error.")
      return None


def update_things():
  return None


def add_ip_cam():
  return None


def ip_cam_streaming():
  return None
