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


def get_gadget_list(product_id):
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


def update_product_stage(product_id, product_stage, model_number_list,
                         version, stage):
  url = BASE_URL + 'products/' + product_id + "/" + version + "/stages/" + str(stage)
  # TODO: headers
  headers = {}
  data = {
      "model_numbers": model_number_list,
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


def register_firmware(product_id, version, model_number, firmware_binary):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.x8fr9nhc0l1f
  url = BASE_URL + 'products/' + product_id + '/' + version + '/firmware/' + str(model_number)
  # TODO: headers
  headers = {
      "Content-Type:": "application/octet-stream"
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
  url = BASE_URL + '/developers/' + organization_id + "/users/" + tester_email
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


def delete_tester(organization_id, tester_email):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.ij1rw8ajky3e
  url = BASE_URL + '/developers/' + organization_id + "/users/" + tester_email
  headers = {}
  try:
    if IS_DEV:
      _test_data = True
      return _test_data
    else:
      resp = requests.delete(url, headers=headers)
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
