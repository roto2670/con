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
from flask_login import current_user  # noqa : pylint: disable=import-error

import apis
import util
import common
import builder
import in_apis
import models
import validate
import onboarding
import base.routes
from endpoints import blueprint


@blueprint.route('/<product_id>/specifications', methods=['GET'])
@util.require_login
def specifications(product_id):
  _set_product(product_id)
  _product = in_apis.get_product(product_id)
  model_list = _product.model_list
  specification_list = _product.endpoint_list
  spec_dict = {}

  for _spec in specification_list:
    spec_dict[_spec.id] = json.loads(_spec.specifications)
  return render_template('ep_specifications.html',
                         specification_list=specification_list,
                         model_list=model_list, spec_dict=spec_dict)


@blueprint.route('/<product_id>/specifications/<specification_id>/download', methods=['GET'])
@util.require_login
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


def _check_version(ep_version, firmware_version):
  return ep_version.split(".") == firmware_version.split(".")[:2]


def _build_gadget_dict(gadgets, endpoint):
  gadget_dict = {}
  ep_version = endpoint.version if endpoint else None
  if ep_version:
    for _gadget in gadgets:
      if _gadget['stage'] == models.STAGE_DEV:
        for __gadget in _gadget['gadgets']:
          if __gadget['status'] == 1 and \
              _check_version(ep_version, __gadget['firmware_version']):
            display = "{} (Version : {}, {})".format(__gadget['name'],
                                                    __gadget['firmware_version'],
                                                    _gadget['email'])
            gadget_dict[__gadget['id']] = display
  return gadget_dict


@blueprint.route('/<product_id>/tests', methods=['GET', 'POST'])
@util.require_login
def tests(product_id):
  _set_product(product_id)
  gadget_dict = {}
  gadgets = apis.get_gadget_list_by_tester(product_id)
  _product = in_apis.get_product(product_id)
  specification_list = _product.endpoint_list
  if request.method == "GET":
    if specification_list:
      selected = specification_list[0]
      content = json.loads(selected.specifications)
    else:
      selected = None
      content = {}
    if gadgets:
      gadget_dict = _build_gadget_dict(gadgets, selected)
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
    if gadgets:
      gadget_dict = _build_gadget_dict(gadgets, selected)
    gadget = None
    gadget_id = None
    if 'gadget' in request.form and request.form['gadget'] in gadget_dict:
      gadget = {request.form['gadget'] : gadget_dict[request.form['gadget']]}
      gadget_id = request.form['gadget']
    return render_template('ep_tests.html', specification_list=specification_list,
                           gadget_dict=gadget_dict, gadget=gadget, gadget_id=gadget_id,
                           selected=selected, content=content)


@blueprint.route('/<product_id>/upload', methods=['POST'])
@util.require_login
def upload_header_file(product_id):
  _product = in_apis.get_product(product_id)
  upload_file = request.files['file']
  content = upload_file.read()
  # TODO: Check format?? Or send to cloud server
  logging.info("Upload file content : %s", len(content))
  try:
    decode_content = content.decode()
    json_content = json.loads(decode_content)
    if not validate.check_validate_specification(product_id, _product.typ,
                                                 json_content):
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
      in_apis.update_dev(product_id)
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
@util.require_login
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
    onboarding.set_header_file()
    return Response(_header, mimetype='text/x-c',
                    headers={'Content-Disposition':'attachment;filename=gadget.h'})
  except:
    logging.exception("Raise error while download header file., Prd : %s, sp : %s, model : %s, user : %s",
                      product_id, specification_id, model.name, current_user.email)
    abort(500)


@blueprint.route('/<product_id>/testcall/<gadget>/<endpoint_name>/<version>', methods=['POST'])
@util.require_login
def test_call(product_id, gadget, endpoint_name, version):
  logging.info("Test call. %s", endpoint_name)
  onboarding.set_test()
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


DEFAULT_LIMIT = '''20'''


@blueprint.route('/<product_id>/next_logs', methods=['GET'])
@util.require_login
def get_next_logs(product_id):
  _set_product(product_id)
  _limit = request.args.get("limit", DEFAULT_LIMIT)
  _keyword = request.args.get('keyword', "")
  _token = request.args.get('token')
  rets = apis.get_logs(product_id, keyword=_keyword, token=_token,
                        limit=_limit)
  token = rets.get('token', None)
  logs = rets.get('logs', [])
  data = {"logs": logs, "token": token, "keyword": _keyword, "limit": _limit}
  return json.dumps(data)


@blueprint.route('/<product_id>/logs', methods=['GET', 'POST'])
@util.require_login
def get_logs(product_id):
  _set_product(product_id)
  _limit = request.args.get("limit", DEFAULT_LIMIT)
  _keyword = request.args.get('keyword', "")
  if request.method == "GET":
    _token = request.args.get('token')
    return render_template('logs.html', keyword=_keyword, limit=_limit)
  else:
    _keyword = request.form['keyword']
    return render_template('logs.html',
                           keyword=_keyword, limit=_limit)


@blueprint.route('/<product_id>/logs/gadget/<gadget_id>', methods=['GET', 'POST'])
@util.require_login
def get_logs_with_gadget(product_id, gadget_id):
  _set_product(product_id)
  _limit = request.args.get("limit", DEFAULT_LIMIT)
  _keyword = request.args.get('keyword', "")
  if request.method == "GET":
    _token = request.args.get('token')
    rets = apis.get_logs_with_gadget(product_id, gadget_id, keyword=_keyword,
                                     token=_token, limit=_limit)
    token = rets.get('token', None)
    logs = rets.get('logs', [])
    return render_template('logs.html', logs=logs, token=token)
  else:
    _keyword = request.form['keyword']
    rets = apis.get_logs(product_id, keyword=_keyword, limit=_limit)
    token = rets.get('token', None)
    logs = rets.get('logs', [])
    return render_template('logs.html', logs=logs, token=token,
                           keyword=_keyword, limit=_limit)


def _set_product(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
