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
import logging

from flask import render_template, redirect, request  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import base
import util
import in_apis
import local_apis
from dashboard import count
from registration import blueprint


@blueprint.route('/')
@util.require_login
def route_default():
  return render_template("registration_home.html")


@blueprint.route('/beacon', methods=['GET', 'POST'])
@util.require_login
def beacon_list_route():
  beacon_list = count.beacon_list()
  if request.method == "GET":
    return render_template("beacon_list.html", beacon_list=beacon_list,
                          category=count.GADGET_INFO,
                          selected_category="100")
  else:
    selected_category = request.form['category']
    new_list = []
    if selected_category != "100":
      for beacon in beacon_list:
        if beacon['tags'] and beacon['tags'][0] == selected_category:
          new_list.append(beacon)
    else:
      new_list = beacon_list
    return render_template("beacon_list.html", beacon_list=new_list,
                           category=count.GADGET_INFO,
                           selected_category=selected_category)


@blueprint.route('/beacon/<gid>/update', methods=['GET', 'POST'])
@util.require_login
def beacon_update_route(gid):
  if request.method == "GET":
    beacon = count.get_beacon(gid)
    return render_template("update_beacon.html", beacon=beacon,
                           category=count.GADGET_INFO)
  else:
    name = request.form.get('name')
    kind = request.form.get('kind')
    moi = request.form.get('moi')
    hid = request.form.get('hid')
    local_apis.update_beacon_information(gid, hid, name, kind, moi)
    return redirect("/registration/beacon")



@blueprint.route('/scanner', methods=['GET', 'POST'])
@util.require_login
def scanner_list_route():
  scanner_list = count.scanner_list()
  if request.method == "GET":
    return render_template("scanner_list.html", scanner_list=scanner_list,
                           selected_onoff=100, selected_location=100,
                           location=count.SCANNER_LOCATION)
  else:
    selected_onoff = int(request.form['onoff'])
    selected_location = int(request.form['location'])
    new_list = []
    if selected_onoff != 100:
      for scanner in scanner_list:
        if scanner['status'] == selected_onoff:
          new_list.append(scanner)
      return render_template("scanner_list.html", scanner_list=new_list,
                            selected_onoff=selected_onoff,
                            selected_location=selected_location)
    else:
      return render_template("scanner_list.html", scanner_list=scanner_list,
                            selected_onoff=selected_onoff,
                            selected_location=selected_location)


@blueprint.route('/scanner/<hid>/update', methods=['GET', 'POST'])
@util.require_login
def scanner_update_route(hid):
  if request.method == "GET":
    scanner = count.get_scanner(hid)
    return render_template("update_scanner.html", scanner=scanner,
                           location=count.SCANNER_LOCATION)
  else:
    name = request.form.get('name')
    location = request.form.get('location')
    is_count = request.form.get('count')
    local_apis.update_scanner_information(hid, name, location, is_count)
    return redirect("/registration/scanner")
