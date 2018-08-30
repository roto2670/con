# -*- coding: utf-8 -*-
#
# Copyright 2017-2018 Naran Inc. All rights reserved.
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


IS_DEV = True
BASE_URL = '''https://o3.prota.space/i/v1/'''


# https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.tauhkpflgrmp


# {{{ User


def get_user(email_addr):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.o0rze6j27nlq
  url = BASE_URL + 'users'
  headers = {}
  data = {}
  params = {"email": email_addr}
  try:
    resp = requests.get(url, headers=headers, data=json.dumps(data), params=params)
    if resp.ok:
      value = resp.json()
      return value['v']
    else:
      logging.warn("Get User Response Text : %s", resp.text)
      return None
  except:
    logging.exception("Raise error.")
    return None


def get_gadget_list_by_tester(product_id):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.am4og2rdbcu7
  url = BASE_URL + 'products/' + product_id + "/testers"
  headers = {}
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
                   'kind': 'testgadget_kind'
               }
           ]}
      ]
      return _test_data
    else:
      resp = requests.get(url, headers=headers)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Register android key Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def get_gadget_list(product_id):
  url = BASE_URL + 'products/' + product_id + "/gadgets"
  headers = {}
  try:
    if IS_DEV:
      _test_data = [
          {"id": "b405b03cc357d3cc18076a4d3735b292", "mac": "f2d63434da93",
           "name": "mibs(f2d6)", "kind": "mibs", "firmware_version": "1.1.9",
           "model_number": 512, "model_name": 512, "sdk_version": "0.1",
           "hub_id": "f1bac4169156cd1f29da073c51de33d5",
           "account_id": "dbb0cf4a18a37f79f13126e4407f1d75",
           "user_id": "d3e4022166cf428218f87aa8a1759aee", "status": 1,
           "rssi": 0, "battery": 0},
          {"id": "b405b03cc357d3cc18076a4d3735b2e2", "mac": "f2d63434da93",
           "name": "mibs(ddd6)", "kind": "mibs", "firmware_version": "1.0.9",
           "model_number": None, "model_name": None, "sdk_version": "0.1",
           "hub_id": "f1bac4169156cd1f29da073c51de33e5",
           "account_id": "dbb0cf4a18a37f79f13126e440ef1d75",
           "user_id": "d3e4022166cf428218f87aa8a1759eee", "status": 0,
           "rssi": 0, "battery": 0}
      ]
      return _test_data
    else:
      resp = requests.get(url, headers=headers)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Register android key Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


# }}}


def update_android_key(organization_id, kind, secret):
  # kind : package name
  # secret : key
  url = BASE_URL + 'developers/' + organization_id + '/keys/' + kind + "/android"
  headers = {}
  data = {
      "secret": secret
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.ok:
      value = resp.json()
      return value['v']
    else:
      logging.warn("Register android key Response Text : %s", resp.text)
      return None
  except:
    logging.exception("Raise error.")
    return None


def update_ios_key(organization_id, kind, cert, secret, is_dev):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.2q2o6bhvcg6
  # kind : bundle_id
  url = BASE_URL + 'developers/' + organization_id + '/keys/' + kind + "/ios"
  headers = {}
  data = {
      "cert": cert,
      "secret": secret,
      "stage": is_dev
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.ok:
      value = resp.json()
      return value['v']
    else:
      logging.warn("Register android key Response Text : %s", resp.text)
      return None
  except:
    logging.exception("Raise error")
    return None


# {{{ Endpoints


def register_specifications(product_id, version, specification):
  url = BASE_URL + 'products/' + product_id + "/" + version + "/endpoints"
  # TODO: headers
  # TODO: stage
  headers = {}
  data = {
      "specification": specification
  }
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.post(url, headers=headers, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Register specification Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def call_endpoint(gadget_id, endpoint_name, data):
  url = BASE_URL + "gadgets/" + gadget_id + "/endpoints/" + endpoint_name
  headers = {}
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.ok:
      value = resp.json()
      return value['v']
    else:
      logging.warn("Call endpoint Response. gadget : %s, endpoint : %s, Text : %s",
                   gadget_id, endpoint_name, resp.text)
      return None
  except:
    logging.exception("Raise error.")
    return None


def get_endpoint_result(gadget_id, task_id):
  url = BASE_URL + "gadgets/" + gadget_id + "/results/" + task_id
  headers = {}
  data = {}
  try:
    resp = requests.get(url, headers=headers, data=json.dumps(data))
    if resp.ok:
      value = resp.json()
      return value['v']
    else:
      logging.warn("Get endpoint result Response Text : %s", resp.text)
  except:
    logging.exception("Raise error.")
    return None


# }}}


##### new

# {{{  product


def create_product(product_name, developer_id):
  url = BASE_URL + 'product'
  # TODO: headers
  headers = {}
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
      resp = requests.post(url, headers=headers, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Create product Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def update_about_hook(product_id, stage, hook_url=None, hook_client_key=None):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.9y2x4jt3mifj
  url = BASE_URL + 'products/' + product_id + "/stages/" + str(stage) + "/hook"
  # TODO: headers
  headers = {}
  data = {
      "hook_url": hook_url,
      "hook_client_key": hook_client_key
  }

  if data:
    try:
      resp = requests.post(url, headers=headers, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Update about hook Response Text : %s", resp.text)
        return None
    except:
      logging.exception("Raise error.")
      return None
  else:
    return None


def update_product_stage(product_id, product_stage, model_number_dict, stage):
  url = BASE_URL + 'products/' + product_id + "/stages/" + str(stage)
  # TODO: headers
  headers = {}
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
      resp = requests.post(url, headers=headers, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Update product stage Response Text : %s", resp.text)
        return None
    except:
      logging.exception("Raise error.")
      return None


# }}}


# {{{ Model


def create_model(product_id, model_number, model_name):
   # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.fs7h307c0m2e
  url = BASE_URL + 'products/' + product_id + '/models/' + str(model_number)
  # TODO: headers
  headers = {}
  data = {
      "display": model_name
  }
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.post(url, headers=headers, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Create model Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


# }}}


# {{{ developer


def create_org(email):
  url = BASE_URL + 'developer'
  # TODO: headers
  headers = {}
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
      resp = requests.post(url, headers=headers, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Create Organization Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def get_org(organization_id):
  url = BASE_URL + 'developers/' + organization_id
  # TODO: headers
  headers = {}
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
      resp = requests.get(url, headers=headers)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Create Organization Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


# }}}


# {{{ firmware


def register_firmware(product_id, model_number, firmware_version, firmware_binary):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.x8fr9nhc0l1f
  url = BASE_URL + 'products/' + product_id + '/models/' + str(model_number) + "/firmwares/" + firmware_version
  # TODO: headers
  headers = {
      "Content-Type": "application/octet-stream"
  }
  try:
    if IS_DEV:
      _test_data = "https://test.firmware"
      return _test_data
    else:
      resp = requests.post(url, headers=headers, data=firmware_binary)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Register firmware Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None

# }}}


# {{{  Tester


def register_tester(organization_id, product_id, tester_email, stage):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.pd0151kuq7uk
  url = BASE_URL + 'developers/' + organization_id + "/users/" + tester_email
  headers = {}
  data = {
    product_id: stage
  }
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.post(url, headers=headers, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Regsiter tester Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


def delete_tester(organization_id, product_id, tester_email):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.ij1rw8ajky3e
  url = BASE_URL + 'developers/' + organization_id + "/users/" + tester_email
  headers = {}
  params = {"products": [product_id]}
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.delete(url, headers=headers, params=params)
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Regsiter tester Response Text : %s", resp.text)
        return None
  except:
    logging.exception("Raise error.")
    return None


# }}}
