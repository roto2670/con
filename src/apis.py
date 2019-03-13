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

import requests  # noqa : pylint: disable=import-error


IS_DEV = True
BASE_URL = '''http://api.mib.io/i/v1/'''
HEADERS = {}
JSON_HEADERS = {}


def init(app):
  HEADERS['Authorization'] = 'Bearer {}'.format(app.config.get('TOKEN'))
  JSON_HEADERS['Authorization'] = 'Bearer {}'.format(app.config.get('TOKEN'))
  JSON_HEADERS['Content-Type'] = 'application/json'


# https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.tauhkpflgrmp


# {{{ User


def get_user(email_addr):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.o0rze6j27nlq
  url = BASE_URL + 'users'
  params = {"email": email_addr}
  try:
    if IS_DEV:
      _test_data = {
          'user': {},
          'accounts': [],
          'hubs': [],
          'gadgets': [],
      }
      return _test_data
    else:
      resp = requests.get(url, headers=HEADERS, params=params)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warning("Get User Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def get_gadget_list_by_tester(product_id):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.am4og2rdbcu7
  url = BASE_URL + 'products/' + product_id + "/testers"
  try:
    if IS_DEV:
      _test_data = [
          {'email': 'tester@example.com',
           'stage': 2,
           'gadgets': [
               {
                   'id': 'testgadget_id',
                   'mac': 'testgadget_mac',
                   'name': 'testgadget_name',
                   'kind': 'testgadget_kind',
                   'status': 1,
                   'firmware_version' : '1.3.1',
                   'model_number': 0,
                   'model_name': 'v4',
                   'sdk_version': '0.1',
                   'latest_version': '1.3.1'
               }
           ]},
          {'email': 'tester@example.com',
           'stage': 2,
           'gadgets': [
               {
                   'id': 'testgadget_id_2',
                   'mac': 'testgadget_mac_2',
                   'name': 'testgadget_name_2',
                   'kind': 'testgadget_kind_2',
                   'status': 1,
                   'firmware_version' : '1.0.1',
                   'model_number': 0,
                   'model_name': 'v4',
                   'sdk_version': '0.1',
                   'latest_version': '1.0.1'
               }
           ]}
      ]
      return _test_data
    else:
      resp = requests.get(url, headers=HEADERS)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warning("Register android key Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def get_gadget_list(product_id):
  url = BASE_URL + 'products/' + product_id + "/gadgets"
  try:
    if IS_DEV:
      _test_data = [
          {"id": "b105b0311157d3cc18076a4d3735b292", "mac": "f2d63431da9l",
           "name": "verter Switc\u00c3\u0083\u00c2\u0083\u00c3\u0082\u00c2\u0083\u00c3\u0083\u00c2\u0082\u00c3\u0082\u00c2\u00af\u00c3\u0083\u00c2\u0083\u00c3\u0082\u00c2\u0082\u00c3\u0083\u00c2\u0082\u00c3\u0082\u00c2\u00bf\u00c3\u0083\u00c2\u0083\u00c3\u0082\u00c2\u0082\u00c3\u0083\u00c2\u0082\u00c3\u0082\u00c2\u00bd", "kind": "mibs", "firmware_version": "1.3.0",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f2ba13169156ad1f29da073c51de33d5",
           "account_id": "dib0cf4aa8a37f79f13126e4407f1d75",
           "user_id": "13e4i22166ca428218f87aa8a1759aee", "status": 0,
           "rssi": 0, "battery": 50, "locale": "KR"},
          {"id": "b105b0311357d3cc18076a4d3735b292", "mac": "f2d63431d19l",
           "name": "sh (cca1\u0002", "kind": "mibs", "firmware_version": "1.5.0",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f2ba13169156cd1f29da073c51de33d5",
           "account_id": "dib0cf4a18a37f79f13126e4407f1d75",
           "user_id": "13e4i22166cf428218f87aa8a1759aee", "status": 1,
           "rssi": 0, "battery": 70, "locale": "KR"},
          {"id": "b105b03cc357d3cc18076a4d3735b292", "mac": "f2d63431d193",
           "name": "sh (e9ac\u0001", "kind": "mibs", "firmware_version": "1.0.0",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f2ba14169156cd1f29da073c51de33d5",
           "account_id": "d2b0cf4a18a37f79f13126e4407f1d75",
           "user_id": "13e4222166cf428218f87aa8a1759aee", "status": 1,
           "rssi": 0, "battery": 70, "locale": "US"},
          {"id": "b105b03cc357d3cc18076a4d3735b292", "mac": "f2d63434d193",
           "name": "mibs(a2d6)", "kind": "mibs", "firmware_version": "1.2.9",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f2bac4169156cd1f29da073c51de33d5",
           "account_id": "dbb0cf4a18a37f79f13126e4407f1d75",
           "user_id": "13e4022166cf428218f87aa8a1759aee", "status": 1,
           "rssi": 0, "battery": 100, "locale": "NL"},
          {"id": "b405b03cc357d3cc18076a4d3735b292", "mac": "f2d63434da93",
           "name": "mibs(f2d6)", "kind": "mibs", "firmware_version": "1.1.9",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1bac4169156cd1f29da073c51de33d5",
           "account_id": "dbb0cf4a18a37f79f13126e4407f1d75",
           "user_id": "d3e4022166cf428218f87aa8a1759aee", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'JP'},
          {"id": "1a05b03cc357d3cc18076a4d3735b292", "mac": "f2d23434da9i",
           "name": "Kid's room", "kind": "mibs", "firmware_version": "1.2.1",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1bac4169156cd1f29da073c51de33i5",
           "account_id": "dbb0cf4a18a37f79f13126e440af1d75",
           "user_id": "d3e4022166cf428218f87aa8a17i9aee", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'LV'},
          {"id": "1a05b03cc357d3cc18076a4d3731b292", "mac": "z2d23434da9i",
           "name": "mibs(z2d2)", "kind": "mibs", "firmware_version": "1.1.9",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1bic4169156cd1f29da073c51de33i5",
           "account_id": "ibb0cf4a18a37f79f13126e440af1d75",
           "user_id": "d3e0i22166cf428218f87aa8a17i9aee", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'CA'},
          {"id": "1a05b03c3f57d3cc18076a4d3731b292", "mac": "zfd23434da9i",
           "name": "mibs(zfd2)", "kind": "mibs", "firmware_version": "1.0.9",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1bic4169156cd1f29da073c51dq33i5",
           "account_id": "ibb0cf4a18a37f79f13126eq40af1d75",
           "user_id": "d3e0i22166cf428218f87aa8a7ii9aee", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'AO'},
          {"id": "1a05b03c3f57d3cc18076a4i3731b292", "mac": "afd23434da9i",
           "name": "mibs(afd2)", "kind": "mibs", "firmware_version": "1.0.7",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1b2c4169156cd1f29da073c52dq33i5",
           "account_id": "3bb0cf4a18a37f79f1312zeq40af1d75",
           "user_id": "d3ezi22166cf428218f87aa8z7ii9aee", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'IN'},
          {"id": "1a05b03c3f57d3cc18076a4i3731b202", "mac": "0fd23434da9i",
           "name": "mibs(0fd2)", "kind": "mibs", "firmware_version": "1.0.0",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1b204169156cd1f29da073c52dq33i5",
           "account_id": "0bb0cf4a18a37f79f1312zeq40af1d75",
           "user_id": "d3e0i22166cf428218f87aa8z7ii9aee", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'FI'},
          {"id": "pa05b03c3f57d3cc18076a4i3731b202", "mac": "ppd23434da9i",
           "name": "mibs(ppd2)", "kind": "mibs", "firmware_version": "1.3.5",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1b204169156cd1f29da073c52dq33ip",
           "account_id": "0bb0cf4a18a37f79f1312zeq40af1d7p",
           "user_id": "d3e0i22166cf428218f87aa8z7ii9aep", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'PH'},
          {"id": "pa05b03c3f57dzcc18076a4i3731b202", "mac": "qpd23434da9i",
           "name": "mibs(qpd2)", "kind": "mibs", "firmware_version": "1.3.4",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1b2041691z6cd1f29da073c52dq33ip",
           "account_id": "0bb0cfza18a37f79f1312zeq40af1d7p",
           "user_id": "d3e0i2216zcf428218f87aa8z7ii9aep", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'IT'},
          {"id": "qq05b03c3f57dzcc18076a4i3731b202", "mac": "12d23434da9i",
           "name": "mibs(12d2)", "kind": "mibs", "firmware_version": "1.3.0",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1b204169zz6cd1f29da073c52dq33ip",
           "account_id": "0bb0czza18a37f79f1312zeq40af1d7p",
           "user_id": "d3e0i221z2cf428218f87aa8z7ii9aep", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'GB'},
          {"id": "qq05b03c3f57dzaa18076a4i3731b202", "mac": "1ada3434aa9i",
           "name": "mibs(1ada)", "kind": "mibs", "firmware_version": "1.0.8",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1b204a69zz6cd1f29da073c52dq33ip",
           "account_id": "0ba0czza18a37f79f1312zeq40af1d7p",
           "user_id": "d3e0ia21z2cf428218f87aa8z7ii9aep", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'DE'},
          {"id": "qq05b03c3057dzaa18076a4i3731b202", "mac": "1a0a3434aa9i",
           "name": "mibs(1a0a)", "kind": "mibs", "firmware_version": "1.1.8",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "01b204a69zz6cd1f29da073c52dq33ip",
           "account_id": "pba0czza18a37f79f1312zeq40af1d7p",
           "user_id": "p3e0ia21z2cf428218f87aa8z7ii9aep", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'IE'},
          {"id": "oq05b03c3057dzaa18076a4i3731b202", "mac": "oq0a3434aa9i",
           "name": "mibs(oq0a)", "kind": "mibs", "firmware_version": "1.1.3",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "oqb204a69zz6cd1f29da073c52dq33ip",
           "account_id": "oqa0czza18a37f79f1312zeq40af1d7p",
           "user_id": "oqe0ia21z2cf428218f87aa8z7ii9aep", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'SG'},
          {"id": "oq05b03dd057dzaa18076a4i3731b202", "mac": "oqdd3434aa9i",
           "name": "mibs(oqdd)", "kind": "mibs", "firmware_version": "1.1.4",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "ddb204a69zz6cd1f29da073c52dq33ip",
           "account_id": "dda0czza18a37f79f1312zeq40af1d7p",
           "user_id": "dde0ia21z2cf428218f87aa8z7ii9aep", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'MX'},
          {"id": "z005b03dd057dzaa18076a4i3731b202", "mac": "oz0d3434aa9i",
           "name": "mibs(oz0d)", "kind": "mibs", "firmware_version": "1.1.1",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "ffb204a69zz6cd1f29da073c52dq33ip",
           "account_id": "ffa0czza18a37f79f1312zeq40af1d7p",
           "user_id": "ffe0ia21z2cf428218f87aa8z7ii9aep", "status": 1,
           "rssi": 0, "battery": 0, 'locale': 'VN'},
          {"id": "b405b03cc357d3cc18076a4d3735b2e2", "mac": "f2d63434da93",
           "name": "mibs(ddd6)", "kind": "mibs", "firmware_version": "1.0.9",
           "model_number": None, "model_name": None, "sdk_version": "0.1",
           "hub_id": "f1bac4169156cd1f29da073c51de33e5",
           "account_id": "dbb0cf4a18a37f79f13126e440ef1d75",
           "user_id": "d3e4022166cf428218f87aa8a1759eee", "status": 0,
           "rssi": 0, "battery": 0, 'locale': 'NO'}
      ]
      return _test_data
    else:
      resp = requests.get(url, headers=HEADERS)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warning("Register android key Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


# }}}


def update_android_key(organization_id, kind, secret):
  # kind : package name
  # secret : key
  url = BASE_URL + 'developers/' + organization_id + '/keys/' + kind + "/android"
  data = {
      "secret": secret
  }
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        logging.info("Update android key. url : %s, data : %s", url, data)
        return value['v']
      else:
        logging.warning("Register android key Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def update_ios_key(organization_id, kind, cert, secret, is_dev):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.2q2o6bhvcg6
  # kind : bundle_id
  url = BASE_URL + 'developers/' + organization_id + '/keys/' + kind + "/ios"
  data = {
      "cert": cert,
      "secret": secret,
      "stage": is_dev
  }
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        logging.info("Update ios key. url : %s, data : %s", url, data)
        return value['v']
      else:
        logging.warning("Register android key Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error")
    return None


# {{{ Endpoints


def register_specifications(product_id, version, specification):
  url = BASE_URL + 'products/' + product_id + "/" + version + "/endpoints"
  # TODO: stage
  data = {
      "specification": specification
  }
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warning("Register specification Response Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def call_endpoint(gadget_id, endpoint_name, data):
  url = BASE_URL + "gadgets/" + gadget_id + "/endpoints/" + endpoint_name
  try:
    resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
    if resp.ok:
      value = resp.json()
      return value['v']
    else:
      logging.warning(
          "Call endpoint Response. gadget : %s, endpoint : %s, Code : %s, Text : %s",
          gadget_id, endpoint_name, resp.status_code, resp.text)
      return None
  except:
    logging.exception("Raise error.")
    return None


def get_endpoint_result(gadget_id, task_id):
  url = BASE_URL + "gadgets/" + gadget_id + "/results/" + task_id
  try:
    resp = requests.get(url, headers=HEADERS)
    if resp.ok:
      value = resp.json()
      return value['v']
    else:
      logging.warning("Get endpoint result Response. Code : %s, Text : %s",
                      resp.status_code, resp.text)
  except:
    logging.exception("Raise error.")
    return None


# }}}


# {{{  product


def create_product(product_name, developer_id):
  url = BASE_URL + 'product'
  data = {
      "name": product_name,
      "developer_id": developer_id
  }
  try:
    if IS_DEV:
      _test_data = {
          "id": product_name,
          "developer_id": developer_id,
          "key": "df4f925b5233fc50b1a298e878d85367",
          "hook_url": "",
          "hook_client_key": ""
      }
      # mibp : cac9095c6a3e7764af27b51ca9ec41ee
      # mibs : b9a0d9f2b062bd1d52089f74eb194ae0
      # mibio : df4f925b5233fc50b1a298e878d85367
      return _test_data
    else:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warning("Create product Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def update_about_hook(product_id, stage, hook_url=None, hook_client_key=None):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.9y2x4jt3mifj
  url = BASE_URL + 'products/' + product_id + "/stages/" + str(stage) + "/hook"
  data = {
      "hook_url": hook_url,
      "hook_client_key": hook_client_key
  }

  if IS_DEV:
    _test_data = True
    return _test_data
  else:
    try:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        logging.info("Update about hook. url : %s, data : %s", url, data)
        return value['v']
      else:
        logging.warning("Update about hook Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
    except:
      logging.exception("Raise error.")
      return None


def update_product_stage(product_id, product_stage, model_number_dict, stage):
  url = BASE_URL + 'products/' + product_id + "/stages/" + str(stage)
  data = {
      "models": model_number_dict,
      "hook_url": product_stage.hook_url,
      "hook_client_key": product_stage.hook_client_key
  }

  if IS_DEV:
    _test_data = True
    return _test_data
  else:
    try:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        logging.info("Update product stage. url : %s, data : %s", url, data)
        return value['v']
      else:
        logging.warning("Update product stage Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
    except:
      logging.exception("Raise error.")
      return None


# }}}


# {{{ Model


def create_model(product_id, model_number, model_name):
   # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.fs7h307c0m2e
  url = BASE_URL + 'products/' + product_id + '/models/' + str(model_number)
  data = {
      "display": model_name
  }
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warning("Create model Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


# }}}


# {{{ developer


def create_org(email):
  url = BASE_URL + 'developer'
  data = {
      "email": email,
  }
  try:
    if IS_DEV:
      _test_data = {
          "id" : "993a39cdeed84d72851efe581b9a74ed",
          "users" : [],
          "products": [],
          "tokens": {"access": "d45eb188dd4511251ae7073a447050ad"},
          "kinds": {}
      }
      return _test_data
    else:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warning("Create Organization Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def get_org(organization_id):
  url = BASE_URL + 'developers/' + organization_id
  try:
    if IS_DEV:
      _test_data = {
          "id" : "test_dev",
          "users" : [],
          "products": [],
          "tokens": {"access": "test_dev_access_token"},
          "kinds": {}
      }
      return _test_data
    else:
      resp = requests.get(url, headers=HEADERS)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warning("Create Organization Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


# }}}


# {{{ firmware


def register_firmware(product_id, model_number, firmware_version, firmware_binary):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.x8fr9nhc0l1f
  url = BASE_URL + 'products/' + product_id + '/models/' + str(model_number) \
      + "/firmwares/" + firmware_version
  headers = {
      "Content-Type": "application/octet-stream"
  }
  for key, value in HEADERS.items():
    headers[key] = value
  try:
    if IS_DEV:
      _test_data = "https://test.firmware"
      return _test_data
    else:
      resp = requests.post(url, headers=headers, data=firmware_binary)
      if resp.ok:
        value = resp.json()
        logging.info("Register firmware. url : %s", url)
        return value['v']
      else:
        logging.warning("Register firmware Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def delete_firmware(product_id, model_number, firmware_version):
  url = BASE_URL + 'products/' + product_id + '/models/' + str(model_number) \
      + "/firmwares/" + firmware_version
  try:
    if IS_DEV:
      return True
    else:
      resp = requests.delete(url, headers=HEADERS)
      if resp.ok:
        value = resp.json()
        logging.info("Delete firmware. url : %s", url)
        return value['v']
      else:
        logging.warning("Delete firmware Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error while delete firmware. P: %s, M: %s, F: %s",
                      product_id, model_number, firmware_version)
    return None



# }}}


# {{{  Tester


def register_tester(organization_id, product_id, tester_email, stage):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.pd0151kuq7uk
  url = BASE_URL + 'developers/' + organization_id + "/users/" + tester_email
  data = {
      product_id: stage
  }
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        logging.info("Register tester.  url : %s, data : %s", url, data)
        return value['v']
      elif resp.status_code == 403:
        logging.debug("Status 403. %s user not FTL.", tester_email)
        value = resp.json()
        return value['v']
      else:
        logging.warning("Regsiter tester Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def delete_tester(organization_id, product_id, tester_email):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.ij1rw8ajky3e
  url = BASE_URL + 'developers/' + organization_id + "/users/" + tester_email
  params = {"products": [product_id]}
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.delete(url, headers=HEADERS, params=params)
      if resp.ok:
        value = resp.json()
        logging.info("Delete Tester. url : %s, param : %s", url, params)
        return value['v']
      else:
        logging.warning("Register tester Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


# }}}


LOG_BASE_URL = '''https://cloud-log-tracer-dot-protacloud.appspot.com/'''


def _build_param(**kwargs):
  if not kwargs:
    return ""
  _param = {}
  for key, value in kwargs.items():
    if value:
      _param[key] = value
  return _param


def get_logs(product_id, keyword=None, token=None, limit=None):
  url = LOG_BASE_URL + "products/" + product_id
  params = _build_param(keyword=keyword, token=token, size=limit)
  try:
    if IS_DEV:
      _test_data = []
      return _test_data
    else:
      headers = {}
      resp = requests.get(url, headers=headers, params=params)
      if resp.ok:
        value = resp.json()
        logging.info("Get logs. url : %s", url)
        return value
      else:
        logging.warning("Get logs Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def get_logs_with_gadget(product_id, gadget_id, keyword=None, token=None,
                         limit=None):
  url = LOG_BASE_URL + "products/" + product_id + "/gadgets/" + gadget_id
  params = _build_param(keyword=keyword, token=token, size=limit)
  try:
    if IS_DEV:
      _test_data = []
      return _test_data
    else:
      headers = {}
      resp = requests.get(url, headers=headers, params=params)
      if resp.ok:
        value = resp.json()
        logging.info("Get logs with gadget. url : %s", url)
        return value
      else:
        logging.warning("Get logs with gadget Response. Code : %s, Text : %s",
                        resp.status_code, resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None
