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

import os
import logging
import tempfile
import subprocess

from OpenSSL import crypto
from flask_login import current_user

import apis


def _generate_private_key(p12, key_path):
  private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
  with open(key_path, 'wb') as f:
    f.write(private_key)


def _get_certificate(p12):
  return crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())


def _get_secret_key(private_key_path, secret_key_path):
  cmd = "openssl rsa -in {} -out {}".format(private_key_path, secret_key_path)
  try:
    ret = subprocess.check_call(cmd, shell=True)
    with open(secret_key_path, 'rb') as f:
      secret_key = f.read()
    return secret_key
  except:
    logging.exception("Raise error while generate secret key.")


def _generate_noti_key(product_id, content, password):
  product = apis.get_product(product_id, current_user.organization_id)
  p12 = crypto.load_pkcs12(content, password)
  tmp_private_key_path = tempfile.mkstemp()[1]
  tmp_secret_key_path = tempfile.mkstemp()[1]
  _generate_private_key(p12, tmp_private_key_path)
  cert = _get_certificate(p12)
  secret_key = _get_secret_key(tmp_private_key_path, tmp_secret_key_path)
  os.remove(tmp_private_key_path)
  os.remove(tmp_secret_key_path)
  return cert.decode(), secret_key.decode()


def _allow_send_noti_key(noti_key, is_dev=False):
  if is_dev:
    bundle_id = noti_key.ios_dev_bundle_id
    password = noti_key.ios_dev_password
  else:
    bundle_id = noti_key.ios_production_bundle_id
    password = noti_key.ios_production_password
  return bundle_id and password


def send_noti_key(product_id, noti_key, content, is_dev=False):
  product = apis.get_product(product_id, current_user.organization_id)
  if _allow_send_noti_key(noti_key, is_dev):
    bundle_id = noti_key.ios_dev_bundle_id \
        if is_dev else product.ios_production_bundle_id
    password = noti_key.ios_dev_password \
        if is_dev else product.ios_production_password
    cert, secret_key = _generate_noti_key(product_id, content, password)
    ret = apis.update_ios_key(product.developer_id, bundle_id, cert, secret_key,
                              is_dev=is_dev)
    return ret
  else:
    # TODO: error handle
    return False
