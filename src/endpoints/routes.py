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

import json
import logging

from flask import abort, render_template, redirect, request, Response
from flask_login import login_required, current_user

import apis
import builder
from base import db
from models import Endpoint
from endpoints import blueprint

MOCK_GADGET_LIST = ['iPhone', 'Nexus']


@blueprint.route('/<product_id>/specifications', methods=['GET', 'POST'])
@login_required
def specifications(product_id):
  if request.method == "GET":
    version_list = apis.get_specifications_list(product_id)
    v_list = []
    for version in version_list:
      v_list.append(version.version)
    if version_list:
      selected = version_list[-1].version
      content = json.loads(version_list[-1].specifications)
    else:
      selected = None
      content = {}
    return render_template('ep_specifications.html', version_list=v_list,
                           selected=selected, content=content)
  else:
    ver = request.form['version']
    version_list = apis.get_specifications_list(product_id)
    logging.info("#### version list : %s", version_list)
    v_list = []
    for version in version_list:
      v_list.append(version.version)
    selected = apis.get_specifications(product_id, ver)
    logging.info("## selected : %s", selected)
    content = json.loads(selected.specifications)
    logging.info("## selected : %s", content)
    logging.info("%s", ver)
    return render_template('ep_specifications.html', version_list=v_list,
                           selected=ver, content=content)


@blueprint.route('/<product_id>/tests', methods=['GET', 'POST'])
@login_required
def tests(product_id):
  # TODO: Test
  if request.method == "GET":
    version_list = apis.get_specifications_list(product_id)
    v_list = []
    for version in version_list:
      v_list.append(version.version)
    if version_list:
      selected = version_list[-1].version
      content = json.loads(version_list[-1].specifications)
    else:
      selected = None
      content = {}
    user_info = apis.get_user(current_user.email)
    logging.info("## user info : %s", user_info)
    gadgets = apis.get_gadget_list(current_user.email)
    gadget = gadgets[-1] if gadgets else None
    return render_template('ep_tests.html', version_list=v_list,
                           gadget_list=gadgets, gadget=gadget,
                           selected=selected, content=content)
  else:
    ver = request.form['version']
    version_list = apis.get_specifications_list(product_id)
    v_list = []
    for version in version_list:
      v_list.append(version.version)
    selected = apis.get_specifications(product_id, ver)
    content = json.loads(selected.specifications)

    gadget = request.form['gadget']
    logging.info("%s, %s", ver, gadget)
    gadgets = apis.get_gadget_list(current_user.email)
    return render_template('ep_tests.html', version_list=v_list,
                           gadget_list=gadgets, gadget=gadget,
                           selected=ver, content=content)


@blueprint.route('/<product_id>/upload', methods=['POST'])
@login_required
def upload_header_file(product_id):
  #TODO: Handle upload content
  upload_file = request.files['file']
  content = upload_file.read()
  # TODO: Check format?? Or send to cloud server
  logging.info("Upload file content : %s", content)
  try:
    decode_content = content.decode()
    json_content = json.loads(decode_content)
    if json_content['product'] != product_id:
      return redirect('endpoints/' + product_id + '/specifications')
    ret = apis.register_specifications(product_id, json_content['version'], decode_content)
    old_specifications = apis.get_specifications(product_id, json_content['version'])
    if old_specifications:
      old_specifications.specifications = decode_content
    else:
      endpoint = Endpoint(version=json_content['version'],
                          specifications=decode_content,
                          organization_id=current_user.organization_id,
                          product_id=product_id)
      db.session.add(endpoint)
    db.session.commit()
    logging.info("ret : %s", ret)
    return redirect('endpoints/' + product_id + '/specifications')
  except:
    logging.exception("### riase error")
    return redirect('endpoints/' + product_id + '/specifications')


@blueprint.route('/<product_id>/<version>/download', methods=['GET'])
@login_required
def download_header_file(product_id, version):
  #TODO: Handle download content
  content = apis.get_specifications(product_id, version)
  h_builder = builder.MibEndpoints.build(json.loads(content.specifications))
  _header = h_builder.to_lib_body()
  return Response(_header, mimetype='text/x-c',
                  headers={'Content-Disposition':'attachment;filename=gadget.h'})


@blueprint.route('/<product_id>/testcall/<gadget>/<endpoint_name>', methods=['POST'])
@login_required
def test_call(product_id, gadget, endpoint_name):
  logging.info("### test call. %s", endpoint_name)
  product =  apis.get_product(product_id, current_user.organization_id)
  # TODO: data
  args = [14]
  kwargs = {}
  data = {
      "key": product.key,
      "args": args,
      "kwargs": kwargs
  }
  task_id = apis.call_endpoint(gadget, endpoint_name, data)
  logging.info("### task id : %s", task_id)
  if task_id:
    ret = apis.get_endpoint_result(gadget, task_id)
    logging.info("### ret : %s", ret)
    return json.dumps(ret)
  else:
    return "Fail"
