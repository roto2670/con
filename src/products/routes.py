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
import re
import json
import uuid
import logging
import datetime
import urllib.parse

from flask import abort, render_template, request, redirect, url_for
from flask_login import login_required, current_user

import apis
import cmds
import mail
import common
import models
import in_apis
import base.routes
from base import db
from products import blueprint


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    return render_template("prd_create.html", referrer=referrer)
  else:
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    if referrer == "/products/create":
      # TODO:  change referrer url
      referrer = "/home/index"

    code = request.form['code']
    if re.compile(r'\W|\d').findall(code):
      title = common.get_msg("products.create.product.invalid_code_title")
      msg = common.get_msg("products.create.product.invalid_code_message")
      common.set_error_message(title, msg)
      return render_template("prd_create.html", referrer=referrer)
    has_product = in_apis.get_product(code)
    if has_product:
      title = common.get_msg("products.create.product.exists_product_title")
      msg = common.get_msg("products.create.product.exists_product_message")
      common.set_error_message(title, msg)
      return render_template("prd_create.html", referrer=referrer)
    else:
      ret = apis.create_product(code, current_user.organization_id)
      if ret:
        # TODO: Product type
        product = in_apis.create_product(request.form['name'], ret,
                                         models.PRD_TYPE_BLE)
        org = in_apis.get_organization(current_user.organization_id)
        if org:
          product_list = json.loads(org.products)
          product_list.append(ret['id'])
          org.products = json.dumps(product_list)
          org.last_updated_time = datetime.datetime.utcnow()
          db.session.commit()
        _set_product(product.id)
        return redirect('products/' + ret['id'] + '/model/create')
      else:
        abort(500)


def _get_type_dict(product):
  if product.typ == models.PRD_TYPE_BLE:
    typ_dict = {
        models.MODEL_TYPE_NRF_51 : "NRF51",
        models.MODEL_TYPE_NRF_52 : "NRF52"
    }
    return typ_dict
  else:
    return {}


@blueprint.route('/<product_id>/model/create', methods=['GET', 'POST'])
@login_required
def create_model(product_id):
  if request.method == "GET":
    _set_product(product_id)
    product = in_apis.get_product(product_id)
    typ_dict = _get_type_dict(product)
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    return render_template("model_create.html", referrer=referrer, typ_dict=typ_dict)
  else:
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    if referrer == "/products/" + product_id + "/model/create":
      # TODO:  change referrer url
      referrer = "/products/" + product_id + "/model"

    name = request.form['name']
    model_type = request.form['type']
    code = 0
    _model_list = in_apis.get_model_list(product_id)
    if _model_list:
      code = len(_model_list) + 1

    if code < 0 or code > 65535:
      title = common.get_msg("products.create.model.usage_full_title")
      msg = common.get_msg("products.create.model.usage_full_message")
      common.set_error_message(title, msg)
      return render_template("prd_create.html", referrer=referrer)
    has_model = in_apis.get_model_by_code(code, product_id)
    if has_model:
      title = common.get_msg("products.create.model.exists_model_title")
      msg = common.get_msg("products.create.model.exists_model_message")
      common.set_error_message(title, msg)
      return render_template("prd_create.html", referrer=referrer)
    else:
      ret = apis.create_model(product_id, code, name)
      if ret:
        product_stage = in_apis.get_product_stage_by_dev(product_id)
        in_apis.create_model(name, code, model_type, product_stage.id, current_user.email)
        return redirect('products/' + product_id + '/general')
      else:
        abort(500)


@blueprint.route('/<product_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_product(product_id):
  in_apis.delete_product(product_id)
  return redirect("/organization")


@blueprint.route('/<product_id>/model/<model_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_model(product_id, model_id):
  in_apis.delete_model(model_id)
  return redirect("/products/" + product_id + "/model")


@blueprint.route('/<product_id>/general', methods=['GET'])
@login_required
def general(product_id):
  _set_product(product_id)
  return render_template('prd_general.html')


@blueprint.route('/<product_id>/authentication', methods=['GET'])
@login_required
def authentication(product_id):
  _set_product(product_id)
  tokens = json.loads(current_user.organization.tokens)
  token = tokens['access'] if 'access' in tokens else None
  return render_template('prd_authentication.html', token=token)


@blueprint.route('/<product_id>/hook', methods=['POST'])
@login_required
def hook(product_id):
  hook_url = request.form['hookUrl']
  hook_client_key = request.form['hookClientKey']
  ret = apis.update_about_hook(product_id, models.STAGE_DEV, hook_url, hook_client_key)

  if ret:
    dev = in_apis.get_product_stage_by_dev(product_id)
    dev.hook_url = hook_url
    dev.hook_client_key = hook_client_key
    db.session.commit()
    return redirect('products/' + product_id + '/authentication')
  else:
    abort(500)


@blueprint.route('/<product_id>/tester', methods=['GET', 'POST'])
@login_required
def tester(product_id):
  _set_product(product_id)
  if request.method == "GET":
    #TODO: tester
    tester_list = in_apis.get_tester_list(product_id, current_user.organization_id)
    invite_list = in_apis.get_invite_list_by_tester(product_id,
                                                    current_user.organization_id)
    return render_template('prd_tester.html', tester_list=tester_list,
                           invite_list=invite_list)
  else:
    #TODO: Send email
    tester_email = request.form['newTesterEmail']
    _tester = in_apis.get_tester_by_email(tester_email, product_id)
    if not _tester:
      _send_invite(tester_email, product_id)
    return redirect('products/' + product_id + '/tester')


def _send_invite(email_addr, product_id):
  with open(os.path.join(cmds.get_res_path(), 'tester_invite.html'), 'r') as f:
    content = f.read()
  key = uuid.uuid4().hex
  auth_url = request.host_url + 'products/confirm?key=' + key + '&o=' + \
      current_user.organization_id
  _product = in_apis.get_product(product_id)
  title = common.get_msg("products.tester.mail_title")
  title = title.format(_product.name)
  msg =  common.get_msg("products.tester.mail_message")
  msg =  msg.format(_product.name)
  content = content.format(auth_url=auth_url, title=title, msg=msg)
  try:
    mail.send(email_addr, title, content)
    in_apis.create_invite(email_addr, key, current_user.email,
                          current_user.organization_id, level=models.TESTER,
                          product_id=product_id)
  except:
    logging.exception("Raise error")


@blueprint.route('/<product_id>/tester/<tester_id>/change/<level>')
@login_required
def change_tester_level(product_id, tester_id, level):
  tester = in_apis.get_tester(tester_id, product_id)
  if tester:
    ret = apis.register_tester(tester.organization_id, product_id, tester.email,
                               int(level))
    if ret:
      tester.level = level
      db.session.commit()
      return redirect('products/' + product_id + '/tester')
    else:
      logging.warn("Failed to change tester level. Id : %s, ret : %s",
                   tester_id, ret)
      return redirect('products/' + product_id + '/tester')
  else:
    logging.warn("Can not find tester. Id : %s", tester_id)
    return redirect('products/' + product_id + '/tester')



@blueprint.route('/<product_id>/tester/<tester_id>/delete')
@login_required
def remove_tester(product_id, tester_id):
  tester = in_apis.get_tester(tester_id, product_id)
  if tester:
    ret = apis.delete_tester(tester.organization_id, product_id, tester.email)
    if ret:
      in_apis.delete_tester(tester_id)
    else:
      logging.warn("Failed to delete tester. Tester : %s", tester.email)
  return redirect('products/' + product_id + '/tester')


@blueprint.route('/<product_id>/tester/<tester_id>/refresh')
@login_required
def check_authorized(product_id, tester_id):
  tester = in_apis.get_tester(tester_id, product_id)
  if tester:
    tester_info = apis.get_user(tester.email)
    tester_authorized = tester_info['user']['authorized']
    if tester_authorized:
      in_apis.update_tester_to_authorized(tester.id)
  return redirect('products/' + product_id + '/tester')


@blueprint.route('/<product_id>/invite/tester/<invite_id>/delete')
@login_required
def remove_invite_tester(product_id, invite_id):
  in_apis.delete_invite(invite_id)
  return redirect('products/' + product_id + '/tester')


@blueprint.route('/confirm', methods=['GET'])
def confirm_mail():
  key = request.args['key']
  organization_id = request.args['o']
  invite = in_apis.get_invite(key, organization_id)
  if invite:
    in_apis.update_invite(key, organization_id)
    tester_info = apis.get_user(invite.email)
    tester_authorized = tester_info['user']['authorized'] if tester_info else False
    logging.debug("Tester info : %s", tester_info)
    # TODO:
    ret = apis.register_tester(organization_id, invite.product_id, invite.email,
                                models.STAGE_PRE_RELEASE)
    if ret:
      in_apis.create_tester(invite.email, invite.organization_id,
                            invite.product_id, tester_authorized,
                            models.STAGE_PRE_RELEASE)
      if tester_authorized:
        return redirect(url_for('base_blueprint.welcome'))
      else:
        return redirect(url_for('base_blueprint.welcome_no_ftl'))
    else:
      abort(500)
  else:
    abort(400)


@blueprint.route('/<product_id>/model', methods=['GET'])
@login_required
def model_list(product_id):
  _set_product(product_id)
  dev_product = in_apis.get_product_stage_by_dev(product_id)
  release_product = in_apis.get_product_stage_by_release(product_id)
  release_list = []
  if release_product:
    release_list = release_product.model_list
  product = in_apis.get_product(product_id)
  typ_dict = _get_type_dict(product)
  return render_template('model_list.html', model_list=dev_product.model_list,
                         release_list=release_list, typ_dict=typ_dict)


@blueprint.route('/<product_id>/model/<model_id>', methods=['GET'])
@login_required
def model_info(product_id, model_id):
  _set_product(product_id)
  model = in_apis.get_model(model_id)
  return render_template('model.html', model=model, firmware_list=model.firmware_list)


def _get_build_number(version):
  _, _, build_number = version.split(".")
  return int(build_number) + 1


@blueprint.route('/<product_id>/model/<model_id>/firmware', methods=['GET', 'POST'])
@login_required
def upload_firmware(product_id, model_id):
  referrer = "/products/" + product_id + "/model/" + model_id
  if request.method == "GET":
    _set_product(product_id)
    model = in_apis.get_model(model_id)
    allow_stage_list = [models.STAGE_DEV]
    pre_release = in_apis.get_product_stage_by_pre_release(product_id)
    release = in_apis.get_product_stage_by_release(product_id)
    if pre_release:
      for pre_release_model in pre_release.model_list:
        if model.code == pre_release_model.code:
          allow_stage_list.append(models.STAGE_PRE_RELEASE)
          break
    if release:
      for release_model in release.model_list:
        if model.code == release_model.code:
          allow_stage_list.append(models.STAGE_RELEASE)
          break
    return render_template('register_firmware.html', referrer=referrer,
                           allow_stage_list=allow_stage_list, model=model)
  else:
    state = int(request.form['state'])
    upload_file = request.files['file']
    content = upload_file.read()
    model = in_apis.get_model(model_id)
    firmware_list = \
        in_apis.get_firmware_list_order_by_version(model.product_stage.endpoint.version,
                                                   model.code)
    if firmware_list:
      build_number = _get_build_number(firmware_list[0].version)
    else:
      build_number = 0
    firmware_version = model.product_stage.endpoint.version + "." + \
        str(build_number)
    ret_json = cmds.get_hex_to_json(content)
    ret = apis.register_firmware(product_id, model.code, firmware_version, ret_json)
    if ret:
      if state == models.STAGE_RELEASE:
        stage_info = in_apis.get_product_stage_by_release(product_id)
      elif state == models.STAGE_PRE_RELEASE:
        stage_info = in_apis.get_product_stage_by_pre_release(product_id)
      elif state == models.STAGE_DEV:
        stage_info = in_apis.get_product_stage_by_dev(product_id)
      else:
        stage_info = in_apis.get_product_stage_by_archive(product_id)
      ret_stage = apis.update_product_stage(product_id, stage_info,
                                            {model.code: firmware_version},
                                            state)
      if ret_stage:
        firmware = in_apis.create_firmware(firmware_version,
                                           model.product_stage.endpoint.version,
                                           model.code, current_user.email,
                                           ret, model.id)
        return redirect('products/' + product_id + '/model/' + model_id)
      else:
        logging.warn("Raise update stage error. model : %s", model_id)
        abort(500)
    else:
      logging.warn("Raise upload firmware error. model : %s", model_id)
      abort(500)


def _set_product(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
