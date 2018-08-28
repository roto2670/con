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


from flask import session


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
