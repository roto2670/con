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

from models import Product, Endpoint


BASE_URL = '''https://o3.prota.space/i/v1/'''


# https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.tauhkpflgrmp


# {{{ User

# TODO: request response -> r.json()[0] ?


def get_user(email_addr):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.o0rze6j27nlq
  url = BASE_URL + 'users'
  headers = {}
  data = {}
  params = {"email": email_addr}
  try:
    resp = requests.get(url, headers=headers, data=json.dumps(data), params=params)
    value = resp.json()
    return value['v']
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



def create_product(product_name, developer_id):
  url = BASE_URL + 'product'
  # TODO: headers
  headers = {}
  data = {
      "name": product_name,
      "developer_id": developer_id
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    value = resp.json()
    return value['v']
  except:
    logging.exception("Raise error.")
    return None


def update_product(product_name, product, hook_url=None, hook_client_key=None):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.khxm4rwdkhy2
  url = BASE_URL + 'product/' + product_name
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
      value = resp.json()
      return value['v']
    except:
      logging.exception("Raise error.")
      return None
  else:
    return None


def update_android_key(organization_id):
  #TODO:
  url = BASE_URL + 'developers/' + organization_id + '/key'
  headers = {}
  data = {
      "kind": "",
      "platform": "android",
      "cert": "",
      "secret": "",
      "stage": ""
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    value = resp.json()
    return value['v']
  except:
    logging.exception("Raise error.")
    return None


def update_ios_key(organization_id, kind, cert, secret, is_dev=False):
  # https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.2q2o6bhvcg6
  url = BASE_URL + 'developers/' + organization_id + '/key/' + kind + "/ios"
  headers = {}
  data = {
      "kind": kind,
      "platform": "ios",
      "cert": cert,
      "secret": secret,
      "stage": 1 if is_dev else 0  # 1 -> dev, 0 -> production
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    value = resp.json()
    return value['v']
  except:
    logging.exception("Raise error")
    return None


def remove_product():
  #TODO:
  pass


def get_product(product_id, developer_id):
  product = Product.query.filter_by(id=product_id, developer_id=developer_id).one_or_none()
  return product


def get_product_list(developer_id):
  product_list = Product.query.filter_by(developer_id=developer_id).all()
  return product_list


# {{{ Endpoints


def register_specifications(product_id, version, specification):
  url = BASE_URL + 'products/' + product_id + "/" + version + "/endpoints"
  # TODO: headers
  # TODO: stage
  headers = {}
  data = {
      "stage": 1,  # 0 -> release, 1 -> dev
      "specification": specification
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    value = resp.json()
    return value['v']
  except:
    logging.exception("Raise error.")
    return None


def get_specifications(product_id, version):
  specifications = Endpoint.query.filter_by(product_id=product_id, version=version).one_or_none()
  return specifications


def get_specifications_list(product_id):
  specifications_list = Endpoint.query.filter_by(product_id=product_id).all()
  return specifications_list


def call_endpoint(gadget_id, endpoint_name, data):
  url = BASE_URL + "gadgets/" + gadget_id + "/endpoints/" + endpoint_name
  headers = {}
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.ok:
      value = resp.json()
      return value['v']
    else:
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
    value = resp.json()
    return value['v']
  except:
    logging.exception("Raise error.")
    return None


# }}}


# {{{ admin page


def create_org(email):
  url = BASE_URL + 'developer'
  # TODO: headers
  headers = {}
  data = {
      "email": email,
  }
  try:
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    value = resp.json()
    return value['v']
  except:
    logging.exception("Raise error.")
    return None


# }}}
