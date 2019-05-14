# -*- coding: utf-8 -*-
#
# Copyright 2017-2019 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|

import json

from flask import request
from flask_login import current_user

import apis
import util
import dash_apis
import base.routes
from dash import blueprint


@blueprint.route('/info', methods=["GET"])
@util.require_login
def get_inforamtion():
  """
  :param : None
  :return : infomation of dict
  """

  if apis.IS_DEV:
    data = {
        "product_id": "mibs"
    }
    return json.dumps(data)
  else:
    prd = base.routes.get_current_product(current_user.id)
    if not prd:
      data = {
          "product_id": prd.id
      }
      return json.dumps(data)
    else:
      return json.dumps({})


@blueprint.route('/scanner/list', methods=["GET"])
@util.require_login
def get_scanner_list():
  ret = dash_apis.get_scanner_list()
  return json.dumps(ret)


@blueprint.route('/beacons/detected/<hub_id>', methods=["GET"])
@util.require_login
def get_detected_beacons_by_hub(hub_id):
  ret = dash_apis.get_detected_beacons(hub_id)
  return json.dumps(ret)


@blueprint.route('/hubs/detected/<gadget_id>', methods=["GET"])
@util.require_login
def get_detected_hubs_by_beacon(gadget_id):
  query_id = request.args.get("qid", None)
  ret = dash_apis.get_detected_hubs(gadget_id, query_id=query_id)
  return json.dumps(ret)


@blueprint.route('/beacons/list/<product_id>', methods=["GET"])
@util.require_login
def get_beacon_list(product_id):
  ret = dash_apis.get_beacon_list(product_id)
  return json.dumps(ret)


@blueprint.route('/hubs/location', methods=["POST"])
@util.require_login
def update_scanner_location():
  json_data = request.get_json()
  hub_data = json_data['hub']
  ret = dash_apis.update_scanner_location(hub_data)
  return json.dumps(ret)


@blueprint.route('/beacons/<beacon_id>', methods=["GET"])
@util.require_login
def get_beacon_info(beacon_id):
  ret = dash_apis.get_beacon_info(beacon_id)
  return json.dumps(ret)
