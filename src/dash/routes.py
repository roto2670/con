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

import util
import dash_apis
from dash import blueprint


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


@blueprint.route('/hubs/detected/<product_id>/<uuid>', methods=["GET"])
@util.require_login
def get_detected_hubs_by_beacon(product_id, uuid):
  query_id = request.args.get("qid", None)
  ret = dash_apis.get_detected_hubs(uuid, product_id, query_id=query_id)
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
