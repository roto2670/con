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
import in_apis
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
      'firmware': {}
  }
  if gadget_list:
    _tmp_user = []
    _tmp_firmware = {}
    _info['total_gadgets'] = len(gadget_list)
    for gadget in gadget_list:
      if gadget['status']:
        _info['online'] += 1
      else:
        _info['offline'] += 1
      if gadget['firmware_version']:
        if gadget['firmware_version'] in _tmp_firmware:
          _tmp_firmware[gadget['firmware_version']] += 1
        else:
          _tmp_firmware[gadget['firmware_version']] = 1
      if gadget['user_id'] and gadget['user_id'] not in _tmp_user:
        _tmp_user.append(gadget['user_id'])
    _info['total_users'] = len(_tmp_user)
    _info['firmware'] = _tmp_firmware
    _info['created_time'] = time.time()
    return _info
  else:
    return _info


def _get_product_info(product_id):
  if product_id in DASHBOARD_CACHE:
    old_time = DASHBOARD_CACHE[product_id]['created_time']
    r_time = time.time() - old_time
    if r_time >= REFRESH_TIME:
      ret = _build_product_info(product_id)
      DASHBOARD_CACHE['product_id'] = ret
      return ret
    else:
      return DASHBOARD_CACHE['product_id']
  else:
    ret = _build_product_info(product_id)
    DASHBOARD_CACHE['product_id'] = ret
    return ret


@blueprint.route('/index')
@login_required
def index():
  current_product = base.routes.about_product()['current_product']
  if not current_product:
    product_list = base.routes.about_product()['product_list']
    logging.info("## product_list : %s", product_list)
    if product_list:
      current_product = product_list[-1]
      base.routes.set_current_product(current_product)
  infos = _get_product_info(current_product.id)
  org = in_apis.get_organization(current_user.organization_id)
  return render_template('index.html', users=json.loads(org.users),
                         products=json.loads(org.products),
                         infos=infos)


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
