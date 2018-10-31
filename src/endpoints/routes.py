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
import time
import logging

from flask import abort, render_template, redirect, request, Response  # noqa : pylint: disable=import-error
from flask_login import login_required, current_user  # noqa : pylint: disable=import-error

import apis
import common
import builder
import in_apis
import models
import base.routes
from endpoints import blueprint


@blueprint.route('/<product_id>/specifications', methods=['GET', 'POST'])
@login_required
def specifications(product_id):
  _set_product(product_id)
  _product = in_apis.get_product(product_id)
  model_list = _product.model_list
  specification_list = _product.endpoint_list

  if request.method == "GET":
    if specification_list:
      specification = specification_list[0]
      content = json.loads(specification.specifications)
    else:
      specification = None
      content = {}
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


@blueprint.route('/<product_id>/specifications/<specification_id>', methods=['GET'])
def view_specifications(product_id, specification_id):
  _set_product(product_id)
  specification = in_apis.get_specifications(specification_id)
  content = json.loads(specification.specifications)
  return render_template('ep_view_specification.html',
                         specification=specification,
                         content=content)


@blueprint.route('/<product_id>/specifications/<specification_id>/download', methods=['GET'])
@login_required
def download_specification_file(product_id, specification_id):
  content = in_apis.get_specifications(specification_id)
  try:
    file_name = "{}.json".format(product_id)
    file_content = content.specifications
    return Response(file_content, mimetype='application/json',
                    headers={'Content-Disposition':'attachment;filename={}'.format(file_name)})
  except:
    logging.exception("Raise error while specification file. Prd : %s, sp : %s, user : %s",
                      product_id, specification_id, current_user.email)
    abort(500)


def _build_gadget_dict(gadgets):
  gadget_dict = {}
  for _gadget in gadgets:
    if _gadget['stage'] == models.STAGE_DEV:
      for __gadget in _gadget['gadgets']:
        if __gadget['status'] == 1:
          display = "{} ({})".format(__gadget['name'], _gadget['email'])
          gadget_dict[__gadget['id']] = display
  return gadget_dict


@blueprint.route('/<product_id>/tests', methods=['GET', 'POST'])
@login_required
def tests(product_id):
  _set_product(product_id)
  gadget_dict = {}
  gadgets = apis.get_gadget_list_by_tester(product_id)
  if gadgets:
    gadget_dict = _build_gadget_dict(gadgets)
  _product = in_apis.get_product(product_id)
  specification_list = _product.endpoint_list
  if request.method == "GET":
    if specification_list:
      selected = specification_list[0]
      content = json.loads(selected.specifications)
    else:
      selected = None
      content = {}
    gadget = None
    gadget_id = None
    if gadget_dict:
      _key = list(gadget_dict.keys())[0]
      gadget = {_key : gadget_dict[_key]}
      gadget_id = _key
    return render_template('ep_tests.html', specification_list=specification_list,
                           gadget_dict=gadget_dict, gadget=gadget, gadget_id=gadget_id,
                           selected=selected, content=content)
  else:
    specification_id = request.form['specification']
    selected = in_apis.get_specifications(specification_id)
    content = json.loads(selected.specifications)

    gadget = None
    if request.form['gadget'] in gadget_dict:
      gadget = {request.form['gadget'] : gadget_dict[request.form['gadget']]}
      gadget_id = request.form['gadget']
    return render_template('ep_tests.html', specification_list=specification_list,
                           gadget_dict=gadget_dict, gadget=gadget, gadget_id=gadget_id,
                           selected=selected, content=content)


def _check_validate(product_id, json_content):
  error_title = common.get_msg("endpoints.upload.fail_title")
  if json_content['product'] != product_id:
    msg = common.get_msg("endpoints.upload.fail_message_not_equal_product")
    logging.warning(msg)
    common.set_error_message(error_title, msg)
    return False

  _requests = json_content['requests']
  for req in _requests:
    if req['name'].lower().startswith('mib'):
      msg = common.get_msg("endpoints.upload.fail_message_request_start_mib")
      logging.warning(msg)
      common.set_error_message(error_title, msg)
      return False
  _events = json_content['events']
  for event in _events:
    if event['name'].lower().startswith('mib'):
      msg = common.get_msg("endpoints.upload.fail_message_event_start_mib")
      logging.warning(msg)
      common.set_error_message(error_title, msg)
      return False
  return True


@blueprint.route('/<product_id>/upload', methods=['POST'])
@login_required
def upload_header_file(product_id):
  _product = in_apis.get_product(product_id)
  upload_file = request.files['file']
  content = upload_file.read()
  # TODO: Check format?? Or send to cloud server
  logging.info("Upload file content : %s", len(content))
  try:
    decode_content = content.decode()
    json_content = json.loads(decode_content)
    _validate = _check_validate(product_id, json_content)
    if not _validate:
      return redirect('endpoints/' + product_id + '/specifications')
    ret = apis.register_specifications(product_id, json_content['version'],
                                       decode_content)
    if ret:
      _version = json_content['version']
      _specifications = in_apis.get_specifications_by_version(product_id, _version)
      if _specifications:
        in_apis.update_specifications(_specifications.id, current_user.email,
                                      json_content['version'], decode_content)
      else:
        in_apis.create_specifications(json_content['version'], decode_content,
                                      current_user.email,
                                      current_user.organization_id,
                                      product_id)
      title = common.get_msg("endpoints.upload.success_title")
      msg = common.get_msg("endpoints.upload.success_message")
      msg = msg.format(json_content['product'], json_content['version'])
      common.set_info_message(title, msg)
      return redirect('endpoints/' + product_id + '/specifications')
    else:
      logging.warning("Failed to register specifications. Prd : %s, user : %s",
                      product_id, current_user.email)
      abort(500)
  except:
    logging.exception("Raise error while upload header file.")
    return redirect('endpoints/' + product_id + '/specifications')


def _get_build_number(version):
  _, _, build_number = version.split(".")
  return int(build_number) + 1


@blueprint.route('/<product_id>/specification/<specification_id>/model/<model_id>/download', methods=['GET'])
@login_required
def download_header_file(product_id, specification_id, model_id):
  content = in_apis.get_specifications(specification_id)
  model = in_apis.get_model(model_id)
  firmware_list = in_apis.get_firmware_list_order_by_version(content.version, model.code)
  if firmware_list:
    build_number = _get_build_number(firmware_list[0].version)
  else:
    build_number = 0

  try:
    # TODO: Handle build number when upper 255
    h_builder = builder.MibEndpoints.build(json.loads(content.specifications))
    _header = h_builder.to_lib_body(model.code, build_number)
    return Response(_header, mimetype='text/x-c',
                    headers={'Content-Disposition':'attachment;filename=gadget.h'})
  except:
    logging.exception("Raise error while download header file., Prd : %s, sp : %s, model : %s, user : %s",
                      product_id, specification_id, model.name, current_user.email)
    abort(500)


@blueprint.route('/<product_id>/testcall/<gadget>/<endpoint_name>/<version>', methods=['POST'])
@login_required
def test_call(product_id, gadget, endpoint_name, version):
  logging.info("Test call. %s", endpoint_name)
  _product = in_apis.get_product(product_id)
  _specifications = in_apis.get_specifications_by_version(product_id, version)
  specification = json.loads(_specifications.specifications)

  args = []
  kwargs = {}

  request_list = specification['requests']
  for req in request_list:
    if endpoint_name == req['name']:
      for param in req['params']:
        if 'default' in param:
          args.append(param['default'])

  data = {
      "key": _product.key,
      "args": args,
      "kwargs": kwargs
  }
  st_time = time.time()
  task_id = apis.call_endpoint(gadget, endpoint_name, data)
  logging.info("%s endpoint task id : %s", endpoint_name, task_id)
  if task_id:
    ret = apis.get_endpoint_result(gadget, task_id)
    end_time = time.time()
    logging.info("%s endpoint result : %s", endpoint_name, ret)
    if 'code' in ret:
      _code = ret['code']
      # code
      # 0 : success
      # 1 : fail
      # 124 : timeout
      if _code == 0:
        ret_data = {
            "status": "Success",
            "time": round(end_time - st_time, 3),
            "ret": ret
        }
      else:
        ret_data = {
            "status": "Fail",
            "time": round(end_time - st_time, 3),
            "ret": ret
        }
    else:
      ret_data = {
          "status": "Fail",
          "time": round(end_time - st_time, 3),
          "ret": ret
      }
  else:
    end_time = time.time()
    ret_data = {
        "status": "Fail",
        "time": round(end_time - st_time, 3),
        "ret": {}
    }
  return json.dumps(ret_data)


def _set_product(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
