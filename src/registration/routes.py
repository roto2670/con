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
import uuid
import hashlib
import logging

from flask import render_template, redirect, request  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import apis
import base
import util
import in_apis
import local_apis
import in_config_apis
from dashboard import count
from registration import blueprint
from constants import REG_HUB_ID, REG_ACCOUNT_ID, BEACON_SPEC
from constants import KIND_IPCAM, KIND_SPEAKER, KIND_ROUTER, KIND_NEW_BEACON
from constants import WHITE_LIST
from config_models import SCANNER_TYPE


IPCAM_KIND = {
    "0": "Fixed",
    "1": "Wireless",
    "2": "Equipment"
}


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


@blueprint.route('/beacon/create', methods=['GET', 'POST'])
@util.require_login
def reg_beacon():
  if request.method == "GET":
    beacon_info = apis.get_new_beacon_info(REG_ACCOUNT_ID)
    # KIND_NEW_BEACON = mibs00001 -> KIND_NEW_BEACON[:4] = mibs
    logging.info("## Beacon spec info : %s", beacon_info)
    return render_template("register_beacon.html", beacon_info=beacon_info,
                           category=count.GADGET_INFO, new_name=KIND_NEW_BEACON[:4])
  else:
    device_id = request.form.get('deviceId')
    tag = request.form.get('tag')
    name = request.form.get('name')
    _uuid = request.form.get('uuid')
    _major = request.form.get('major')
    _minor = request.form.get('minor')

    mac_hash = hashlib.md5()
    mac_hash.update(device_id.encode('utf-8'))
    mac_addr = mac_hash.hexdigest()[:12]
    new_id_hash = hashlib.md5()
    new_id_hash.update(mac_addr.encode('utf-8'))
    new_id = new_id_hash.hexdigest()
    security = uuid.uuid4().hex[:24]
    logging.info("## Register New Beacon name : %s, uuid : %s, major : %s, minor : %s",
                 name, _uuid, _major, _minor)
    value = {
      "id": new_id,
      "mac": mac_addr,
      "name": name,
      "kind": KIND_NEW_BEACON,
      "protocol": 0,
      "firmware_version": "1.0.0",
      "model_number": 0,
      "model_name": "SKEC New Beacon",
      "sdk_version": "0.1",
      "beacon": REG_ACCOUNT_ID,
      "security": security,
      "hub_id": REG_HUB_ID,
      "account_id": REG_ACCOUNT_ID,
      "status": 0,
      "locale": "US",
      "rssi": 0,
      "battery": 0,
      "progress": 0,
      "latest_version": "0.0.0",
      "is_depr": 0,
      "custom": {},
      "tags": [tag],
      "beacon_spec": {
          "uuid": _uuid,
          "major": int(_major),
          "minor": int(_minor),
          "interval": 700,
          "during_second": 0
      },
      "img_url": ""
    }
    ret = local_apis.register_new_beacon(value)
    logging.info("Register new beacon resp : %s", ret)
    local_apis.update_new_beacon_info(value, WHITE_LIST)
    return redirect("/registration/beacon")


@blueprint.route('/beacon/<gid>/delete', methods=['GET'])
@util.require_login
def beacon_delete_route(gid):
  local_apis.remove_new_beacon(gid)
  return redirect("/registration/beacon")


@blueprint.route('/beacon/<gid>/update', methods=['GET', 'POST'])
@util.require_login
def beacon_update_route(gid):
  if request.method == "GET":
    beacon = count.get_beacon(gid)
    ipcam_list = count.ipcam_list()
    return render_template("update_beacon.html", beacon=beacon,
                           category=count.GADGET_INFO, ipcam_list=ipcam_list)
  else:
    name = request.form.get('name')
    kind = request.form.get('kind')
    moi = request.form.get('moi')
    ipcam_id = request.form.get('ipcam')
    hid = request.form.get('hid')
    local_apis.update_beacon_information(gid, hid, name, kind, moi, ipcam_id)
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
    selected_location = request.form['location']
    new_list = []
    if selected_onoff != 100:
      for scanner in scanner_list:
        if scanner['status'] == selected_onoff:
          if selected_location != "100":
            if scanner['tags'] and scanner['tags'][0] == selected_location:
              new_list.append(scanner)
          else:
            new_list.append(scanner)
      return render_template("scanner_list.html", scanner_list=new_list,
                            selected_onoff=selected_onoff,
                            selected_location=selected_location,
                            location=count.SCANNER_LOCATION)
    elif selected_location != "100":
      for scanner in scanner_list:
        if scanner['tags'] and scanner['tags'][0] == selected_location:
          if selected_onoff != 100:
            if scanner['status'] == selected_onoff:
              new_list.append(scanner)
          else:
            new_list.append(scanner)
      return render_template("scanner_list.html", scanner_list=new_list,
                            selected_onoff=selected_onoff,
                            selected_location=selected_location,
                            location=count.SCANNER_LOCATION)
    else:
      return render_template("scanner_list.html", scanner_list=scanner_list,
                            selected_onoff=selected_onoff,
                            selected_location=selected_location,
                            location=count.SCANNER_LOCATION)


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
    ret = local_apis.update_scanner_information(hid, name, location, is_count)
    if ret:
      # Same internal/routes.py
      hub_data = count.get_scanner(hid)
      if int(is_count) == 1:
        # 0, 0 is none -> default
        device_setting = in_config_apis.get_count_device(hub_data['id'])
        access_point = device_setting.access_point if device_setting else 0
        in_config_apis.create_or_update_count_device_setting(hub_data['id'],
                                                             SCANNER_TYPE,
                                                             0, access_point,
                                                             name=hub_data['name'])
      else:
        # TODO: delete count setting and delete redis ...
        count.delete_device(hub_data['id'], SCANNER_TYPE)
    return redirect("/registration/scanner")


@blueprint.route('/ipcam', methods=['GET', 'POST'])
@util.require_login
def ipcam_list_route():
  ipcam_list = count.ipcam_list()
  if request.method == "GET":
    return render_template("ipcam_list.html", ipcam_list=ipcam_list,
                           category=IPCAM_KIND, selected_category="100",
                           selected_onoff=100)
  else:
    selected_onoff = int(request.form['onoff'])
    selected_category = request.form['category']
    new_list = []
    if selected_onoff != 100:
      for ipcam in ipcam_list:
        if ipcam['status'] == selected_onoff:
          if selected_category != "100":
            if ipcam['tags'] and ipcam['tags'][0] == selected_category:
              new_list.append(ipcam)
          else:
            new_list.append(ipcam)
    elif selected_category != "100":
      for ipcam in ipcam_list:
        if ipcam['tags'] and ipcam['tags'][0] == selected_category:
          if selected_onoff != 100:
            if ipcam['status'] == selected_onoff:
              new_list.append(ipcam)
          else:
            new_list.append(ipcam)
    else:
      new_list = ipcam_list
    return render_template("ipcam_list.html", ipcam_list=new_list,
                           category=IPCAM_KIND,
                           selected_category=selected_category,
                           selected_onoff=selected_onoff)



@blueprint.route('/ipcam/create', methods=['GET', 'POST'])
@util.require_login
def reg_ipcam():
  if request.method == "GET":
    return render_template("register_ipcam.html", category=IPCAM_KIND)
  else:
    ip = request.form.get('ip')
    _id = request.form.get('id')
    password = request.form.get('password')
    kind = request.form.get('kind')
    name = request.form.get('name')
    mac_hash = hashlib.md5()
    mac_hash.update(ip.encode('utf-8'))
    mac_addr = mac_hash.hexdigest()[:12]

    new_id_hash = hashlib.md5()
    new_id_hash.update(mac_addr.encode('utf-8'))
    new_id = new_id_hash.hexdigest()

    security = uuid.uuid4().hex[:24]

    value = {
      "id": new_id,
      "mac": mac_addr,
      "name": name,
      "kind": KIND_IPCAM,
      "protocol": 0,
      "firmware_version": "0.0.0",
      "model_number": 0,
      "model_name": KIND_IPCAM,
      "sdk_version": "0.3",
      "beacon": REG_ACCOUNT_ID,
      "security": security,
      "hub_id": REG_HUB_ID,
      "account_id": REG_ACCOUNT_ID,
      "status": 0,
      "locale": "US",
      "rssi": 0,
      "battery": 0,
      "progress": 0,
      "latest_version": "0.0.0",
      "is_depr": 0,
      "custom": {
          "ip": ip,
          "password": password,
          "id": _id,
          "is_visible_moi": 0,
      },
      "tags": [kind],
      "beacon_spec": {
          "uuid": BEACON_SPEC,
          "major": 36805,
          "minor": 36533,
          "interval": 700,
          "during_second": 0
      },
      "img_url": ""
    }
    ret = local_apis.register_ipcam(value)
    logging.info("Register ipcam resp : %s", ret)
    local_apis.update_ipcam_information(new_id, name, 0, kind, value)
    return redirect("/registration/ipcam")


@blueprint.route('/ipcam/<ipcam_id>/update', methods=['GET', 'POST'])
@util.require_login
def ipcam_update_route(ipcam_id):
  if request.method == "GET":
    ipcam = count.get_ipcam(ipcam_id)
    return render_template("update_ipcam.html", ipcam=ipcam,
                           category=IPCAM_KIND)
  else:
    name = request.form.get('name')
    kind = request.form.get('kind')
    moi = request.form.get('moi')
    local_apis.update_ipcam_information(ipcam_id, name, moi, kind)
    return redirect("/registration/ipcam")


@blueprint.route('/ipcam/<ipcam_id>/delete', methods=['GET'])
@util.require_login
def ipcam_delete_route(ipcam_id):
  local_apis.remove_ipcam(ipcam_id)
  return redirect("/registration/ipcam")


@blueprint.route('/pa', methods=['GET', 'POST'])
@util.require_login
def pa_list_route():
  pa_list = count.pa_list()
  if request.method == "GET":
    return render_template("pa_list.html", pa_list=pa_list,
                           selected_onoff=100)
  else:
    selected_onoff = int(request.form['onoff'])
    new_list = []
    if selected_onoff != 100:
      for pa_speaker in pa_list:
        if pa_speaker['status'] == selected_onoff:
          new_list.append(pa_speaker)
    else:
      new_list = pa_list
    return render_template("pa_list.html", pa_list=new_list,
                           selected_onoff=selected_onoff)


@blueprint.route('/pa/create', methods=['GET', 'POST'])
@util.require_login
def reg_pa():
  if request.method == "GET":
    return render_template("register_pa.html")
  else:
    ip = request.form.get('ip')
    name = request.form.get('name')
    mac_hash = hashlib.md5()
    mac_hash.update(ip.encode('utf-8'))
    mac_addr = mac_hash.hexdigest()[:12]

    new_id_hash = hashlib.md5()
    new_id_hash.update(mac_addr.encode('utf-8'))
    new_id = new_id_hash.hexdigest()

    security = uuid.uuid4().hex[:24]

    value = {
      "id": new_id,
      "mac": mac_addr,
      "name": name,
      "kind": KIND_SPEAKER,
      "protocol": 0,
      "firmware_version": "0.0.0",
      "model_number": 0,
      "model_name": KIND_SPEAKER,
      "sdk_version": "0.3",
      "beacon": REG_ACCOUNT_ID,
      "security": security,
      "hub_id": REG_HUB_ID,
      "account_id": REG_ACCOUNT_ID,
      "status": 0,
      "locale": "US",
      "rssi": 0,
      "battery": 0,
      "progress": 0,
      "latest_version": "0.0.0",
      "is_depr": 0,
      "custom": {
          "ip": ip
      },
      "tags": [],
      "beacon_spec": {
          "uuid": BEACON_SPEC,
          "major": 36805,
          "minor": 36533,
          "interval": 700,
          "during_second": 0
      },
      "img_url": ""
    }
    ret = local_apis.register_pa(value)
    logging.info("Register PA Speaker resp : %s", ret)
    local_apis.update_pa_information(new_id, name, data=value)
    return redirect("/registration/pa")


@blueprint.route('/pa/<pa_id>/update', methods=['GET', 'POST'])
@util.require_login
def pa_update_route(pa_id):
  if request.method == "GET":
    pa = count.get_pa(pa_id)
    return render_template("update_pa.html", pa=pa)
  else:
    name = request.form.get('name')
    local_apis.update_pa_information(pa_id, name)
    return redirect("/registration/pa")


@blueprint.route('/pa/<pa_id>/delete', methods=['GET'])
@util.require_login
def pa_delete_route(pa_id):
  local_apis.remove_pa(pa_id)
  return redirect("/registration/pa")


@blueprint.route('/router', methods=['GET', 'POST'])
@util.require_login
def router_list_route():
  router_list = count.router_list()
  if request.method == "GET":
    return render_template("router_list.html", router_list=router_list,
                           selected_onoff=100)
  else:
    selected_onoff = int(request.form['onoff'])
    new_list = []
    if selected_onoff != 100:
      for _router in router_list:
        if _router['status'] == selected_onoff:
          new_list.append(_router)
    else:
      new_list = router_list
    return render_template("router_list.html", router_list=new_list,
                           selected_onoff=selected_onoff)


@blueprint.route('/router/create', methods=['GET', 'POST'])
@util.require_login
def reg_router():
  if request.method == "GET":
    return render_template("register_router.html")
  else:
    ip = request.form.get('ip')
    name = request.form.get('name')
    mac_hash = hashlib.md5()
    mac_hash.update(ip.encode('utf-8'))
    mac_addr = mac_hash.hexdigest()[:12]

    new_id_hash = hashlib.md5()
    new_id_hash.update(mac_addr.encode('utf-8'))
    new_id = new_id_hash.hexdigest()

    security = uuid.uuid4().hex[:24]

    value = {
      "id": new_id,
      "mac": mac_addr,
      "name": name,
      "kind": KIND_ROUTER,
      "protocol": 0,
      "firmware_version": "0.0.0",
      "model_number": 0,
      "model_name": KIND_ROUTER,
      "sdk_version": "0.3",
      "beacon": REG_ACCOUNT_ID,
      "security": security,
      "hub_id": REG_HUB_ID,
      "account_id": REG_ACCOUNT_ID,
      "status": 0,
      "locale": "US",
      "rssi": 0,
      "battery": 0,
      "progress": 0,
      "latest_version": "0.0.0",
      "is_depr": 0,
      "custom": {
          "ip": ip
      },
      "tags": [],
      "beacon_spec": {
          "uuid": BEACON_SPEC,
          "major": 36805,
          "minor": 36533,
          "interval": 700,
          "during_second": 0
      },
      "img_url": ""
    }
    ret = local_apis.register_router(value)
    logging.info("Register Router resp : %s", ret)
    local_apis.update_router_information(new_id, name, data=value)
    return redirect("/registration/router")


@blueprint.route('/router/<router_id>/update', methods=['GET', 'POST'])
@util.require_login
def router_update_route(router_id):
  if request.method == "GET":
    _router = count.get_router(router_id)
    return render_template("update_router.html", router=_router)
  else:
    name = request.form.get('name')
    local_apis.update_router_information(router_id, name)
    return redirect("/registration/router")


@blueprint.route('/router/<router_id>/delete', methods=['GET'])
@util.require_login
def router_delete_route(router_id):
  local_apis.remove_router(router_id)
  return redirect("/registration/router")
