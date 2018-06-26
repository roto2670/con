
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

import logging


#  {{{ Mock api


import uuid

MOCK_PRD_CACHE = {}  # {developer_id : {product_id : {}}}


def _create_product(product_name, developer_id, hook_client_key=None):
  _product = {
      "product_id": uuid.uuid4().hex,
      "name": product_name,
      "developer_id": developer_id,
      "api_key": uuid.uuid4().hex,
      "vendor_id": "",
      "stage": 0,
      "hook_url": "",
      "hook_client_key": hook_client_key if hook_client_key else ""
  }
  if developer_id not in MOCK_PRD_CACHE:
    MOCK_PRD_CACHE[developer_id] = {}
  MOCK_PRD_CACHE[developer_id][_product['product_id']] = _product
  return _product


def _get_product(product_id, developer_id):
  if developer_id in MOCK_PRD_CACHE and \
      product_id in MOCK_PRD_CACHE[developer_id]:
    return MOCK_PRD_CACHE[developer_id][product_id]
  else:
    return {}


# }}}


# https://docs.google.com/document/d/1KZxebs5gkNqnUiD3ooKMfVcry5UD2USFaPaNyFQ2XCE/edit#heading=h.tauhkpflgrmp


def create_product(product_name, developer_id, hook_client_key=None):
  # TODO: handle develop or release mode
  return _create_product(product_name, developer_id, hook_client_key)


def remove_product():
  pass


def update_product():
  pass


def get_product(product_id, developer_id):
  # TODO: handle develop or release mode
  return _get_product(product_id, developer_id)


def get_product_list(developer_id):
  # TODO: handle develop or release mode
  logging.info("## developer id : %s, cache : %s", developer_id, MOCK_PRD_CACHE)
  if developer_id in MOCK_PRD_CACHE:
    return MOCK_PRD_CACHE[developer_id].values()
  else:
    return []
