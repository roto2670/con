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
import util
from flask import session  # noqa : pylint: disable=import-error
from util import Settings


def _get_error_message():
  error_message = session.get('error_message', {})
  if error_message:
    del session['error_message']
  return error_message


def set_error_message(title, message):
  session['error_message'] = {"title": title, "msg": message}


def _get_info_message():
  info_message = session.get('info_message', {})
  if info_message:
    del session['info_message']
  return info_message


def set_info_message(title, message):
  session['info_message'] = {"title": title, "msg": message}


def get_message():
  return dict(error_msg=_get_error_message(), info_msg=_get_info_message())


FILE_NAME = "message.{}"
I18N_PATH = os.path.join(util.get_res_path(), "i18n")
LOCALES_DICT = {}

EN_US = '''en-us'''


def _init_en_us():
  return Settings([os.path.join(I18N_PATH, FILE_NAME.format(EN_US))])


def get_msg(key, locale=None):
  locale = locale or ""
  locales = LOCALES_DICT.get(locale.lower(), {})
  if not locales:
    locales = LOCALES_DICT.get(EN_US)
  settings = locales()
  ret = settings.get(key)
  return ret


def start():
  LOCALES_DICT[EN_US] = _init_en_us
