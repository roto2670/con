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

from OpenSSL import crypto  # noqa : pylint: disable=import-error
from intelhex import IntelHex  # noqa : pylint: disable=import-error

from celery import Celery  # noqa : pylint: disable=import-error


BACKEND = '''rpc://'''
BROKER = '''pyamqp://console:skfksrltnf1@localhost:5672/'''


def init():
  backend = BACKEND
  broker = BROKER
  _worker = Celery('worker', backend=backend, broker=broker)
  return _worker


worker = init()


def _generate_private_key(p12, key_path):
  private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
  with open(key_path, 'wb') as _f:
    _f.write(private_key)


def _get_certificate(p12):
  return crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())


def _get_secret_key(private_key_path, secret_key_path):
  cmd = "openssl rsa -in {} -out {}".format(private_key_path, secret_key_path)
  try:
    subprocess.check_call(cmd, shell=True)
    with open(secret_key_path, 'rb') as _f:
      secret_key = _f.read()
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


@worker.task()
def get_about_noti_key(password, content):
  cert, secret_key = _generate_noti_key(content, password)
  return (cert, secret_key)


@worker.task()
def get_hex_to_json(hex_content):
  tmp_file = tempfile.mkstemp()[1]
  with open(tmp_file, 'wb') as _f:
    _f.write(hex_content)
  _ih = IntelHex(tmp_file)
  bin_array = _ih.tobinarray()
  bin_list = bin_array.tolist()
  ret_json = json.dumps(bin_list)
  os.remove(tmp_file)
  return ret_json
