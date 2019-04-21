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

import util
import dash_apis
from dash import blueprint



@blueprint.route('/scanner/list', methods=["GET"])
# @util.require_login
def get_scanner_list():
  ret = dash_apis.get_scanner_list()
  return json.dumps(ret)


@blueprint.route('/beacons/detected/<hub_id>', methods=["GET"])
#@util.require_login
def get_detected_beacons(hub_id):
  ret = dash_apis.get_detected_beacons(hub_id)
  return json.dumps(ret)


@blueprint.route('/beacons/list', methods=["GET"])
#@util.require_login
def get_beacon_list():
  ret = dash_apis.get_beacon_list()
  return json.dumps(ret)


@blueprint.route('/hubs/location', methods=["POST"])
#@util.require_login
def add_scanner_location():
  json_data = request.get_json()
  hub_data = json_data['hub']
  ret = dash_apis.add_scanner_location(hub_data)
  return json.dumps(ret)