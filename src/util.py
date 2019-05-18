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


"""The utility module.
"""

import os
import json
import logging
from copy import deepcopy
from functools import wraps

from flask import redirect, request, session, url_for
from flask_login import current_user


class Settings(object):
  """Abstraction for managing configurations.
  """
  def __init__(self, paths):
    """
    :param list paths: an iterator of config file paths
    """
    self._paths = paths
    self._read(self._paths)

  def _read(self, paths):
    self._config = {}
    self._config_symbol = {}

    for path in paths:
      if os.path.exists(path):
        with open(path, 'r') as _f:
          try:
            config = json.load(_f)
            self._update_value(config)
          except:
            logging.exception("Occured error while loading a config.")
            with open(path, 'r') as _rf:
              logging.warning("path: %s\ncontents:\n%s", path, _rf.read())
    self._generate_symbol()

  def _merge_dict(self, _a, _b):
    if isinstance(_b, dict) and isinstance(_a, dict):
      a_and_b = _a.viewkeys() & _b.viewkeys()
      every_key = _a.viewkeys() | _b.viewkeys()
      return {k: self._merge_dict(_a[k], _b[k]) if k in a_and_b else deepcopy(
          _a[k] if k in _a else _b[k]) for k in every_key}
    return deepcopy(_b)

  def _update_value(self, config):
    if not self._config:
      self._config = config
    else:
      self._config = self._merge_dict(self._config, config)

  def _generate_symbol(self):
    self._config_symbol = {}
    values = [('', k, v) for k, v in self._config.items()]
    while values:
      parent_key, sub_key, value = values.pop()
      key = '.'.join([parent_key, sub_key])
      key = key[1:] if key.startswith('.') else key
      if isinstance(value, dict):
        for _k, _v in value.items():
          values.append((key, _k, _v))
      self._config_symbol[key] = value

  def _parse_key(self, key):
    """ Parsing a string key to a list sorted by hirerchy.
    """
    return key.split('.')

  def to_string(self):
    return json.dumps(self._config)

  def to_dict(self):
    return self._config

  def get(self, key, default=None):
    """Gets the string value associated with the key.

    :param string key:
    :param string, boolean, int, float default:
    """
    value = self._config_symbol.get(key)
    if value is None and default is not None:
      value = default
      self.set(key, value)
    return value

  def get_int(self, key, default=0):
    """Gets the integer value associated with the key.

    :param string key:
    :param int default:
    """
    return int(self.get(key, default))

  def get_float(self, key, default=0.0):
    """Gets the float value accociated with the key.

    :param string key:
    :param float default:
    """
    return float(self.get(key, default))

  def get_bool(self, key, default=False):
    """Gets the boolean value accociated with the key.

    :param string key:
    :param float default:
    """
    return bool(self.get(key, default))

  def update(self, config):
    """Update to given config.

    :param dictionary config:
    """
    self._update_value(config)
    self._generate_symbol()

  def set(self, key, value):
    """Sets the given value to the key.

    :param string key:
    :param string, boolean, int, float value:
    """
    if not key:
      raise Exception("Key is not '{v}'".format(v=key))
    keys = self._parse_key(key)
    if len(keys) < 2:
      self._config_symbol[key] = value
      self._config[key] = value
      return
    parent_keys = keys[:-1]
    parent_key = '.'.join(parent_keys)
    if parent_key in self._config_symbol:
      self._config_symbol[key] = value
      sub_key = keys[len(parent_keys)]
      self._config_symbol[parent_key][sub_key] = value
    else:
      level = 0
      config = self._config
      for k in keys:
        _v = config[k] if k in config else None
        if not isinstance(_v, dict):
          break
        config = _v
        level += 1
      parent_key = '.'.join(keys[:level])
      p_k = keys[level]
      for k in keys[level + 1:]:
        parent_key = '{parent}.{child}'.format(parent=parent_key, child=k)
        if parent_key == key:
          config[p_k] = value
          self._config_symbol[parent_key] = config[p_k]
        else:
          value_set = {k: value}
          config[p_k] = value_set
          self._config_symbol[p_k] = value_set
          p_k = k

  def set_bulk(self, items):
    """Sets key and value with dictionary.

    :param dictionary items:
    """
    for _k, _v in items.items():
      self.set(_k, _v)

  def __iter__(self):
    for key in self._config_symbol.keys():
      yield key

  def remove(self, key):
    """Removes the specified key.

    :param string key:
    """
    if key in self._config_symbol:
      del self._config_symbol[key]

  def keys(self, key):
    """Returns a list of child keys available in the specified key

    :param string key:
    """
    keys = self._parse_key(key)
    config = self._config
    for k in keys:
      config = config[k]
    return config.keys()

  def get_dict(self, key=None):
    """Gets items by dictionary set

    :param string key:
    """
    config = self._config
    if key:
      keys = self._parse_key(key)
      for k in keys:
        config = config[k]
    return config

  def reload(self):
    """Reloads the settings from the file system.
    """
    self._read(self._paths)

  def _write(self, path):
    _d = os.path.dirname(path)
    os.path.exists(_d) or os.makedirs(_d)
    with open(path, 'w') as _f:
      json.dump(self._config, _f)

  def flush(self, path=None):
    """Flushes the current settings value to the given path.

    :param string path:
    """
    if path:
      self._write(path)
    else:
      for path in reversed(self._paths):
        try:
          self._write(path)
          break
        except:
          logging.exception("Failed to flush the settings.")


def get_res_path():
  path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')
  return  path


def get_static_path(name=None):
  dir_name = name if name else "base"
  path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_name,
                      'static')
  return  path


def get_mail_form_path(file_name):
  path = os.path.join(get_res_path(), 'mailform', file_name)
  return path


def get_ip_addr():
  if 'X-Real-Ip' in request.headers:
    return request.headers['X-Real-Ip']
  elif 'X-Forwarded-For' in request.headers:
    return request.headers['X-Forwarded-For']
  else:
    return request.remote_addr


def require_login(f):
  @wraps(f)
  def check_email_auth(*args, **kwargs):
    if current_user is None:
      return redirect(url_for('login_blueprint.login', next=request.url))
    elif current_user.is_anonymous:
      return redirect(url_for('login_blueprint.login', next=request.url))
    elif not current_user.is_authenticated:
      return redirect(url_for('login_blueprint.login', next=request.url))
    elif not current_user.email_verified:
      return redirect(url_for('base_blueprint.route_verified'))
    # TODO: check session _fresh
    #elif not session.get('_fresh', False):
    #  return redirect(url_for('login_blueprint.login', next=request.url))
    return f(*args, **kwargs)
  return check_email_auth
