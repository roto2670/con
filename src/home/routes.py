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

import time
import json
import logging

from flask import render_template
from flask_login import login_required, current_user

import apis
import base.routes
from home import blueprint


"""
{
    'product_id' : {
        'oragnization_id' : '', 'created_time': '',
        'total_users' : '', 'total_gadgets': '',
        'online': '', 'offline': ''
    }
}
"""
DASHBOARD_CACHE = {}
REFRESH_TIME = 3600  # 1H


def _build_product_info(product_id):
  gadget_list = apis.get_gadget_list(product_id)
  _info = {
      'organization_id': current_user.organization_id,
      'created_time': 0,
      'total_users': 0,
      'total_gadgets': 0,
      'offline': 0,
      'online': 0,
      'firmware': {},
      'total_firmware': 0,
      'avg_battery': 0,
      'name_list': [],
      'model': {}
  }
  if gadget_list:
    _tmp_user = []
    _tmp_firmware = {}
    _tmp_total_firmware = 0
    _tmp_battery = 0
    _tmp_name_list = []
    _tmp_model_dict = {}
    _info['total_gadgets'] = len(gadget_list)
    for gadget in gadget_list:
      if gadget['status']:
        _info['online'] += 1
      else:
        _info['offline'] += 1

      if gadget['firmware_version']:
        if gadget['firmware_version'] in _tmp_firmware:
          _tmp_firmware[gadget['firmware_version']] += 1
          _tmp_total_firmware += 1
        else:
          _tmp_firmware[gadget['firmware_version']] = 1
          _tmp_total_firmware += 1

      if gadget['user_id'] and gadget['user_id'] not in _tmp_user:
        _tmp_user.append(gadget['user_id'])

      if gadget['model_name']:
        if gadget['model_name'] in _tmp_model_dict:
          _tmp_model_dict[gadget['model_name']] += 1
        else:
          _tmp_model_dict[gadget['model_name']] = 1
      _tmp_battery += gadget.get('battery', 0)
      # TODO: size check
      _name_value = {'text': gadget['name'], 'size': 2}
      _tmp_name_list.append(_name_value)

    _info['total_users'] = len(_tmp_user)
    _info['firmware'] = _tmp_firmware
    _info['total_firmware'] = _tmp_total_firmware
    _info['created_time'] = time.time()
    _info['avg_battery'] = int((_tmp_battery / len(gadget_list)))
    _info['name_list'] = json.dumps(_tmp_name_list)
    _info['model'] = _tmp_model_dict
    return _info
  else:
    return _info


def _get_product_info(product_id):
  if product_id in DASHBOARD_CACHE:
    old_time = DASHBOARD_CACHE[product_id]['created_time']
    r_time = time.time() - old_time
    if r_time >= REFRESH_TIME:
      logging.debug("# Refresh product info. : %s", product_id)
      ret = _build_product_info(product_id)
      DASHBOARD_CACHE['product_id'] = ret
      return ret
    else:
      logging.debug("# Already product info. : %s", product_id)
      return DASHBOARD_CACHE['product_id']
  else:
    logging.debug("# New product info. : %s", product_id)
    ret = _build_product_info(product_id)
    DASHBOARD_CACHE['product_id'] = ret
    return ret


@blueprint.route('/index')
@login_required
def index():
  current_product = base.routes.about_product()['current_product']
  if not current_product:
    product_list = base.routes.about_product()['product_list']
    if product_list:
      current_product = product_list[-1]
      base.routes.set_current_product(current_product)
  infos = _get_product_info(current_product.id)
  return render_template('index.html', infos=infos)


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
