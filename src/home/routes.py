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
import time
import json
import logging
import collections

from flask import render_template, request, redirect  # noqa : pylint: disable=import-error
from flask_login import login_required, current_user  # noqa : pylint: disable=import-error

import apis
import util
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
"""  # noqa : pylint: disable=pointless-string-statement
DASHBOARD_CACHE = {}
DATA_CACHE = {}  # {'time': '', 'data': ''}
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
    _tmp_od_firmware = collections.OrderedDict(sorted(_tmp_firmware.items(),
                                                      reverse=True))
    _info['firmware'] = _tmp_od_firmware
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
    if int(r_time) >= REFRESH_TIME:
      logging.debug("# Refresh product info. : %s", product_id)
      ret = _build_product_info(product_id)
      DASHBOARD_CACHE[product_id] = ret
      return ret
    else:
      logging.debug("# Already product info. : %s", product_id)
      return DASHBOARD_CACHE[product_id]
  else:
    logging.debug("# New product info. : %s", product_id)
    ret = _build_product_info(product_id)
    DASHBOARD_CACHE[product_id] = ret
    return ret


def _get_data():
  path = os.path.join(util.get_res_path(), 'data', 'result.json')
  with open(path, 'r') as _f:
    ret = _f.read()
  return json.loads(ret)


def _get_endpoint_info(product_id):
  # {ep : [press, push], r1 : [1, 2], r2 : [3, 4]}
  if DATA_CACHE:
    st_time = DATA_CACHE['time']
    rt_time = time.time() - st_time
    if int(rt_time) >= 3600:
      ret = _get_data()
      DATA_CACHE['time'] = time.time()
      DATA_CACHE['data'] = ret
  else:
    ret = _get_data()
    DATA_CACHE['time'] = time.time()
    DATA_CACHE['data'] = ret

  if product_id in DATA_CACHE['data']:
    ret = DATA_CACHE['data'][product_id]
    if product_id == 'mibp':
      allow_key = ['press', 'release', 'push']
      _r = {'ep': [], 'r1': [], 'r2': []}
      for key, value in ret.items():
        if key in allow_key:
          _r['ep'].append(key)
          _r['r1'].append(value['r_1'])
          _r['r2'].append(value['r_2'])
    elif product_id == 'mibs':
      allow_key = ['get_measure', 'get_history', 'chemical_setting', 'noise_setting']
      _r = {'ep': [], 'r1': [], 'r2': []}
      for key, value in ret.items():
        if key in allow_key:
          _r['ep'].append(key)
          _r['r1'].append(value['r_1'])
          _r['r2'].append(value['r_2'])
    else:
      allow_key = ['clear_pin', 'set_pin']
      _r = {'ep': [], 'r1': [], 'r2': []}
      for key, value in ret.items():
        if key in allow_key:
          _r['ep'].append(key)
          _r['r1'].append(value['r_1'])
          _r['r2'].append(value['r_2'])
    return json.dumps(_r)
  else:
    return json.dumps({})


@blueprint.route('/index')
@login_required
def index():
  current_product = base.routes.about_product()['current_product']
  if not current_product:
    product_list = base.routes.about_product()['product_list']
    if product_list:
      current_product = product_list[-1]
      base.routes.set_current_product(current_product)
    else:
      return redirect("/products/create")
  return redirect("/home/" + current_product.id)


@blueprint.route('/<product_id>')
@login_required
def product_index(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
  infos = _get_product_info(product_id)
  ep_infos = _get_endpoint_info(product_id)
  in_apis.update_user_by_ip(current_user.id, util.get_ip_addr(request))
  return render_template('index.html', infos=infos, ep_infos=ep_infos)


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
