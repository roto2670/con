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

import datetime

from flask import session  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import in_apis
import common

ONBOARDING_NOTI_DAYS = 30

# Session
# {"model": "", "download_file": "", "ep": , "header": "",
#  "firmware": "", "tester": "", "test": "", "release" : "",
#  "next": ""}
#

def clear_session():
  if 'model' in session:
    del session['model']
  if 'download_file' in session:
    del session['download_file']
  if 'ep' in session:
    del session['ep']
  if 'header' in session:
    del session['header']
  if 'firmware' in session:
    del session['firmware']
  if 'tester' in session:
    del session['tester']
  if 'test' in session:
    del session['test']
  if 'release' in session:
    del session['release']
  if 'next' in session:
    del session['next']


def _check_time():
  _cal_time = datetime.datetime.utcnow() - current_user.created_time
  return True if _cal_time.days <= ONBOARDING_NOTI_DAYS else False


def check_onboarding(organization_id=None, product_id=None):
  if _check_time():
    check_release(product_id)
    check_test()
    check_tester(product_id, organization_id)
    check_firmware(product_id)
    check_header_file()
    check_ep(product_id)
    check_download_file()
    check_model(product_id)


def check_model(product_id):
  if session.get('model'):
    return True
  _prd = in_apis.get_product(product_id)
  if _prd.model_list:
    session['model'] = True
    session['next'] = True
    return True
  if session.get('next'):
    title = common.get_msg("onboarding.model.title")
    msg = common.get_msg("onboarding.model.msg")
    common.set_onboarding_message(title, msg)


def set_download_file():
  session['download_file'] = True
  session['next'] = True


def check_download_file():
  if session.get('next') and not session.get('download_file'):
    title = common.get_msg("onboarding.download_file.title")
    msg = common.get_msg("onboarding.download_file.msg")
    common.set_onboarding_message(title, msg)


def check_ep(product_id):
  if session.get('ep'):
    return True
  _prd = in_apis.get_product(product_id)
  if _prd.endpoint_list:
    session['ep'] = True
    session['next'] = True
    return True
  if session.get('next'):
    title = common.get_msg("onboarding.ep.title")
    msg = common.get_msg("onboarding.ep.msg")
    common.set_onboarding_message(title, msg)


def set_header_file():
  session['header'] = True
  session['next'] = True


def check_header_file():
  if session.get('next') and not session.get('header'):
    title = common.get_msg("onboarding.header.title")
    msg = common.get_msg("onboarding.header.msg")
    common.set_onboarding_message(title, msg)


def check_firmware(product_id):
  if True:
    return True
  if session.get('firmware'):
    return True
  _model_list = in_apis.get_model_list(product_id)
  for _model in _model_list:
    if _model.firmware_list:
      session['firmware'] = True
      session['next'] = True
      return True
  if session.get('next'):
    title = common.get_msg("onboarding.firmware.title")
    msg = common.get_msg("onboarding.firmware.msg")
    common.set_onboarding_message(title, msg)


def check_tester(product_id, organization_id):
  if True:
    return True
  if session.get('tester'):
    return True
  _tester_list = in_apis.get_tester_list(product_id, organization_id)
  if _tester_list:
    session['tester'] = True
    session['next'] = True
    return True
  if session.get('next'):
    title = common.get_msg("onboarding.tester.title")
    msg = common.get_msg("onboarding.tester.msg")
    common.set_onboarding_message(title, msg)


def set_test():
  session['test'] = True
  session['next'] = True


def check_test():
  if session.get('next') and not session.get('test'):
    title = common.get_msg("onboarding.test.title")
    msg = common.get_msg("onboarding.test.msg")
    common.set_onboarding_message(title, msg)


def check_release(product_id):
  if session.get('release'):
    return True
  if session.get('next'):
    _stage = in_apis.get_product_stage_by_pre_release(product_id)
    if _stage.stage_info_list:
      session['release'] = True
      session['next'] = False
      return True
    title = common.get_msg("onboarding.release.title")
    msg = common.get_msg("onboarding.release.msg")
    common.set_onboarding_message(title, msg)
