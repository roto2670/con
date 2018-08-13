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


def get_gadget_list(email_addr):
  ret = get_user(email_addr)
  if 'gadgets' in ret:
    return ret['gadgets']
  else:
    return []


# }}}


def update_android_key(organization_id, kind, secret):
  # kind : package name
  # secret : key
  url = BASE_URL + 'developers/' + organization_id + '/key'
  headers = {}
  data = {
      "kind": kind,
      "platform": "android",
      "secret": secret,
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
  url = BASE_URL + 'developers/' + organization_id + '/key'
  headers = {}
  data = {
      "kind": kind,
      "platform": "ios",
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


def register_specifications(product_id, version, specification, stage):
  url = BASE_URL + 'products/' + product_id + "/" + version + "/endpoints"
  # TODO: headers
  # TODO: stage
  headers = {}
  data = {
      "stage": stage,  # 0 -> release, 1 -> dev, 2 -> pre-release, 3 -> release
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
          "id": "test_product",
          "developer_id": "test_dev",
          "key": "test_product_key",
          "hook_url": "",
          "hook_client_key": ""
      }
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


def update_product(product_id, product, hook_url=None, hook_client_key=None):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.khxm4rwdkhy2
  url = BASE_URL + 'products/' + product_id
  # TODO: headers
  headers = {}
  data = {}
  if hook_url is not None and hook_url != product.hook_url:
    data['hook_url'] = hook_url
  if hook_client_key is not None and hook_client_key != product.hook_client_key:
    data['hook_client_key'] = hook_client_key

  if data:
    try:
      resp = requests.post(url, headers=headers, data=json.dumps(data))
      if resp.ok:
        value = resp.json()
        return value['v']
      else:
        logging.warn("Update product Response Text : %s", resp.text)
        return None
    except:
      logging.exception("Raise error.")
      return None
  else:
    return None


def update_product_stage(product_id, version, stage):
  url = BASE_URL + 'products/' + product_id + "/" + version + "/stages/" + str(stage)
  # TODO: headers
  headers = {}
  data = {}

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
  url = BASE_URL + 'products/' + product_id + '/models/' + model_number
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
          "id" : "test_dev",
          "users" : [],
          "products": [],
          "tokens": {"access": "test_dev_access_token"},
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


# }}}


# {{{ firmware


def register_firmware(product_id, version, model_number, firmware_binary):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.x8fr9nhc0l1f
  url = BASE_URL + 'products/' + product_id + '/' + version + '/firmware/' + model_number
  # TODO: headers
  headers = {
      "Content-Type:": "application/octet-stream"
  }
  try:
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
