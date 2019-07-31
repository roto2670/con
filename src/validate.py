# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|

import logging
import common


# Specification
OLD_REQUIRED_KEY = set(['product', 'version', 'requests', 'events', 'pid'])
NEW_REQUIRED_KEY = set(['product', 'type', 'version', 'requests', 'events', 'pid'])


def _check_key(key_list):
  if 'type' in key_list:
    return NEW_REQUIRED_KEY == set(key_list)
  else:
    return OLD_REQUIRED_KEY == set(key_list)


def _check_require_value(json_content):
  if not json_content['product']:
    return False
  if not json_content['version']:
    return False
  return True


def _check_version_format(version):
  try:
    if len(version.split(".")) != 2:
      return False
    _major, _minor = version.split(".")
    _major = int(_major)
    _minor = int(_minor)
    return True
  except:
    logging.warning("While error when check version format. Version : %s",
                    version, exc_info=True)
    return False


def check_validate_specification(product_id, product_type, product_keyword,
                                 json_content):
  error_title = common.get_msg("endpoints.upload.fail_title")
  if not _check_key(json_content.keys()):
    msg = common.get_msg("endpoints.upload.fail_message_required_key")
    logging.warning(msg)
    common.set_error_message(error_title, msg)
    return False

  if not _check_require_value(json_content):
    msg = common.get_msg("endpoints.upload.fail_message_required_value")
    logging.warning(msg)
    common.set_error_message(error_title, msg)
    return False

  if json_content['pid'] != product_id:
    msg = common.get_msg("endpoints.upload.fail_message_not_equal_product")
    logging.warning(msg)
    common.set_error_message(error_title, msg)
    return False

  if json_content['product'] != product_keyword:
    msg = common.get_msg("endpoints.upload.fail_message_not_equal_product_keyword")
    logging.warning(msg)
    common.set_error_message(error_title, msg)
    return False

  if not _check_version_format(json_content['version']):
    msg = common.get_msg("endpoints.upload.fail_message_version_format")
    logging.warning(msg)
    common.set_error_message(error_title, msg)
    return False

  if 'type' in json_content and int(product_type) != int(json_content['type']):
    msg = common.get_msg("endpoints.upload.fail_message_product_type")
    logging.warning(msg)
    common.set_error_message(error_title, msg)
    return False

  _requests = json_content['requests']
  for req in _requests:
    if req['name'].lower().startswith('mib'):
      msg = common.get_msg("endpoints.upload.fail_message_request_start_mib")
      logging.warning(msg)
      common.set_error_message(error_title, msg)
      return False
  _events = json_content['events']
  for event in _events:
    if event['name'].lower().startswith('mib'):
      msg = common.get_msg("endpoints.upload.fail_message_event_start_mib")
      logging.warning(msg)
      common.set_error_message(error_title, msg)
      return False
  return True
