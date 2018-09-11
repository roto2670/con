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

import sendgrid  # noqa : pylint: disable=import-error
from OpenSSL import crypto  # noqa : pylint: disable=import-error
from intelhex import IntelHex  # noqa : pylint: disable=import-error
from celery import Celery  # noqa : pylint: disable=import-error


def init():
  _worker = Celery('worker', backend='amqp',
                   broker='pyamqp://console:skfksxpzm1@localhost:5672/')
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
def _get_about_noti_key(password, content):
  cert, secret_key = _generate_noti_key(content, password)
  return (cert, secret_key)


def get_about_noti_key(password, content):
  ret = _get_about_noti_key.delay(password, content)
  cert, secret_key = ret.get()
  return (cert, secret_key)


@worker.task()
def _get_hex_to_json(file_path):
  _ih = IntelHex(file_path)
  bin_array = _ih.tobinarray()
  bin_list = bin_array.tolist()
  ret_json = json.dumps(bin_list)
  return ret_json


def get_hex_to_json(file_path):
  try:
    ret = _get_hex_to_json.delay(file_path)
    ret_json = ret.get()
    return ret_json
  except Exception:
    logging.exception("Raise error while convert firmware.")


SG_API_KEY = 'SG.Iit8M_G8R9GBiRBknKi7fw.'\
          '-qGUCtHKXjZplV89FHYScAVG9u5crHlsCIopTQxg5aM'


@worker.task()
def _send_mail(request_body):
  sendgrid_client = sendgrid.SendGridAPIClient(apikey=SG_API_KEY)
  _resp = sendgrid_client.client.mail.send.post(request_body=request_body)
  logging.debug("code : %s, header : %s, body : %s", _resp.status_code,
                _resp.headers, _resp.body)
  logging.debug("resp : %s", _resp)
  logging.debug("resp : %s", dir(_resp))
  resp = {}
  return json.dumps(resp)


def send_mail(request_body):
  ret = _send_mail.delay(request_body)
  resp = ret.get()
  return json.loads(resp)
