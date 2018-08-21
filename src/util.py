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
        with open(path, 'r') as f:
          try:
            config = json.load(f)
            self._update_value(config)
          except:
            logging.exception("Occured error while loading a config.")
            with open(path, 'r') as rf:
              logging.warn("path: %s\ncontents:\n%s", path, rf.read())
            pass
    self._generate_symbol()

  def _merge_dict(self, a, b):
    if isinstance(b, dict) and isinstance(a, dict):
      a_and_b = a.viewkeys() & b.viewkeys()
      every_key = a.viewkeys() | b.viewkeys()
      return {k: self._merge_dict(a[k], b[k]) if k in a_and_b else deepcopy(
          a[k] if k in a else b[k]) for k in every_key}
    return deepcopy(b)

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
        for k, v in value.items():
          values.append((key, k, v))
      self._config_symbol[key] = value

  def _parse_key(self, key):
    """ Parsing a string key to a list sorted by hirerchy.
    """
    return key.split('.')

  def to_string(self):
    """
    """
    return json.dumps(self._config)

  def to_dict(self):
    """
    """
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
        v = config[k] if k in config else None
        if not isinstance(v, dict):
          break
        config = v
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
    for k, v in items.items():
      self.set(k, v)

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
    d = os.path.dirname(path)
    os.path.exists(d) or os.makedirs(d)
    with open(path, 'w') as f:
      json.dump(self._config, f)

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
