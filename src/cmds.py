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
import json
import logging
import tempfile
import subprocess

from OpenSSL import crypto
from intelhex import IntelHex

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


def _generate_noti_key(content, password):
  p12 = crypto.load_pkcs12(content, password)
  tmp_private_key_path = tempfile.mkstemp()[1]
  tmp_secret_key_path = tempfile.mkstemp()[1]
  _generate_private_key(p12, tmp_private_key_path)
  cert = _get_certificate(p12)
  secret_key = _get_secret_key(tmp_private_key_path, tmp_secret_key_path)
  os.remove(tmp_private_key_path)
  os.remove(tmp_secret_key_path)
  return cert.decode(), secret_key.decode()


def send_noti_key(organization_id, bundle_id, password , content, is_dev):
  cert, secret_key = _generate_noti_key(content, password)
  ret = apis.update_ios_key(organization_id, bundle_id, cert, secret_key,
                            is_dev)
  return ret


def get_res_path():
  path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')
  return  path


def get_hex_to_json(hex_content):
  tmp_file = tempfile.mkstemp()[1]
  json_tempfile = tempfile.mkstemp()[1]
  with open(tmp_file, 'wb') as f:
    f.write(hex_content)
  ih = IntelHex(tmp_file)
  bin_array = ih.tobinarray()
  bin_list = bin_array.tolist()
  ret_json = json.dump(bin_list)
  os.remove(tmp_file)
  logging.debug("hex to json : %s", ret_json)
  return ret_json
