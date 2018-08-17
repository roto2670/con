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
import in_apis
import models
import base.routes
from endpoints import blueprint


@blueprint.route('/<product_id>/specifications', methods=['GET', 'POST'])
@login_required
def specifications(product_id):
  _set_product(product_id)
  product_dev_stage = in_apis.get_product_stage_by_dev(product_id)
  model_list = product_dev_stage.model_list
  specification_list = []
  if product_dev_stage.endpoint:
    specification_list.append(in_apis.get_specifications(product_dev_stage.endpoint.id))
  if request.method == "GET":
    if specification_list:
      specification = specification_list[-1]
      content = json.loads(specification.specifications)
    else:
      specification = None
      content = {}
    product_dev_stage = in_apis.get_product_stage_by_dev(product_id)
    model_list = product_dev_stage.model_list
    return render_template('ep_specifications.html',
                           specification_list=specification_list,
                           selected=specification, content=content,
                           model_list=model_list)
  else:
    specification_id = request.form['specifications']
    specification = in_apis.get_specifications(specification_id)
    content = json.loads(specification.specifications)
    return render_template('ep_specifications.html',
                           specification_list=specification_list,
                           selected=specification, content=content,
                           model_list=model_list)


def _build_gadget_dict(gadgets):
  gadget_dict = {}
  for _gadget in gadgets:
    if _gadget['stage'] == 2:  # only dev level
      for __gadget in _gadget['gadgets']:
        display = "{} ({})".format(__gadget['name'], _gadget['email'])
        gadget_dict[__gadget['id']] = display
  return gadget_dict


@blueprint.route('/<product_id>/tests', methods=['GET', 'POST'])
@login_required
def tests(product_id):
  _set_product(product_id)
  gadget_dict = {}
  gadgets = apis.get_gadget_list(product_id)
  if gadgets:
    gadget_dict = _build_gadget_dict(gadgets)
  product_dev_stage = in_apis.get_product_stage_by_dev(product_id)
  specification_list = []
  if product_dev_stage.endpoint:
    specification_list.append(in_apis.get_specifications(product_dev_stage.endpoint.id))
  if request.method == "GET":
    if specification_list:
      selected = specification_list[-1]
      content = json.loads(selected.specifications)
    else:
      selected = None
      content = {}
    gadget = None
    if gadget_dict:
      _key = list(gadget_dict.keys())[0]
      gadget = {_key : gadget_dict[_key]}
    return render_template('ep_tests.html', specification_list=specification_list,
                           gadget_dict=gadget_dict, gadget=gadget,
                           selected=selected, content=content)
  else:
    specification_id = request.form['specification']
    selected = in_apis.get_specifications(specification_id)
    content = json.loads(selected.specifications)

    gadget = None
    if request.form['gadget'] in gadget_dict:
      gadget = {request.form['gadget'] : gadget_dict[request.form['gadget']]}
    return render_template('ep_tests.html', specification_list=specification_list,
                           gadget_dict=gadget_dict, gadget=gadget,
                           selected=selected, content=content)


@blueprint.route('/<product_id>/upload', methods=['POST'])
@login_required
def upload_header_file(product_id):
  product_dev_stage = in_apis.get_product_stage_by_dev(product_id)
  upload_file = request.files['file']
  content = upload_file.read()
  # TODO: Check format?? Or send to cloud server
  logging.info("Upload file content : %s", content)
  try:
    decode_content = content.decode()
    json_content = json.loads(decode_content)
    if json_content['product'] != product_id:
      return redirect('endpoints/' + product_id + '/specifications')
    ret = apis.register_specifications(product_id, json_content['version'],
                                       decode_content)
    if ret:
      if product_dev_stage.endpoint:
        in_apis.update_specifications(product_dev_stage.endpoint.id,
                                      current_user.email,
                                      decode_content)
      else:
        in_apis.create_specifications(json_content['version'], decode_content,
                                      current_user.email,
                                      current_user.organization_id,
                                      product_dev_stage.id)
      return redirect('endpoints/' + product_id + '/specifications')
    else:
      abort(500)
  except:
    logging.exception("Raise error while upload header file.")
    return redirect('endpoints/' + product_id + '/specifications')


@blueprint.route('/<product_id>/<specification_id>/<model_id>/download', methods=['GET'])
@login_required
def download_header_file(product_id, specification_id, model_id):
  content = in_apis.get_specifications(specification_id)
  model = in_apis.get_model(model_id)
  build_number = 0
  if model.firmware_list:
    build_number = len(model.firmware_list) + 1

  try:
    # TODO: Handle build number when upper 255
    h_builder = builder.MibEndpoints.build(json.loads(content.specifications))
    _header = h_builder.to_lib_body(model.code, build_number)
    return Response(_header, mimetype='text/x-c',
                    headers={'Content-Disposition':'attachment;filename=gadget.h'})
  except:
    logging.exception("Raise error while download header file.")
    abort(500)


@blueprint.route('/<product_id>/testcall/<gadget>/<endpoint_name>', methods=['POST'])
@login_required
def test_call(product_id, gadget, endpoint_name):
  logging.info("Test call. %s", endpoint_name)
  product =  in_apis.get_product(product_id)
  dev_stage = in_apis.get_product_stage_by_dev(product_id)
  specification = json.loads(dev_stage.endpoint.specifications)

  args = []
  kwargs = {}

  request_list = specification['requests']
  for req in request_list:
    if endpoint_name == req['name']:
      for param in req['params']:
        args.append(param['default'])

  data = {
      "key": product.key,
      "args": args,
      "kwargs": kwargs
  }
  task_id = apis.call_endpoint(gadget, endpoint_name, data)
  logging.info("%s endpoint task id : %s", endpoint_name, task_id)
  if task_id:
    ret = apis.get_endpoint_result(gadget, task_id)
    logging.info("%s endpoint result : %s", endpoint_name, ret)
    return json.dumps(ret)
  else:
    return "Fail"


def _set_product(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
