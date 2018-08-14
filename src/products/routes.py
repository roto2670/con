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
      error_msg = {"title": "Invalid Code",
                   "msg": "Only lowercase letters can be entered. Special characters, spacing can not be entered."}
      return render_template("prd_create.html", referrer=referrer,
                             error_msg=error_msg)
    has_product = in_apis.get_product(code)
    if has_product:
      error_msg = {"title": "Exists Product",
                   "msg": "The product with that code already exists. Please enter a different code."}
      return render_template("prd_create.html", referrer=referrer,
                             error_msg=error_msg)
    else:
      ret = apis.create_product(code, current_user.organization_id)
      if ret:
        product = in_apis.create_product(request.form['name'], ret)
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


@blueprint.route('/<product_id>/model/create', methods=['GET', 'POST'])
@login_required
def create_model(product_id):
  if request.method == "GET":
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    return render_template("model_create.html", referrer=referrer)
  else:
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    if referrer == "/products/" + product_id + "/model/create":
      # TODO:  change referrer url
      referrer = "/products/" + product_id + "/model"

    code = request.form['code']
    name = request.form['name']
    if re.compile(r'\D').findall(code):
      error_msg = {"title": "Invalid Code",
                   "msg": "Only number can be entered. Range 0 ~ 655350."}
      return render_template("prd_create.html", referrer=referrer,
                             error_msg=error_msg)
    elif int(code) < 0 or int(code) > 65535:
      error_msg = {"title": "Invalid Code",
                   "msg": "Code Range 0 ~ 65535."}
      return render_template("prd_create.html", referrer=referrer,
                             error_msg=error_msg)
    has_model = in_apis.get_model_by_code(code)
    if has_model:
      error_msg = {"title": "Exists Model",
                   "msg": "The model with that code already exists. Please enter a different code."}
      return render_template("prd_create.html", referrer=referrer,
                             error_msg=error_msg)
    else:
      ret = apis.create_model(product_id, code, name)
      if ret:
        product_stage = in_apis.get_product_stage_by_dev(product_id)
        in_apis.create_model(name, code, product_stage.id, current_user.email)
        return redirect('products/' + product_id + '/general')
      else:
        abort(500)


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
  content = content.format(auth_url=auth_url)
  try:
    mail.send(email_addr, 'Tester Invite', content)
    in_apis.create_invite(email_addr, key, current_user.email,
                          current_user.organization_id, level=models.TESTER,
                          product_id=product_id)
  except:
    logging.exception("Raise error")


@blueprint.route('/<product_id>/tester/<tester_id>/delete')
@login_required
def remove_tester(product_id, tester_id):
  tester = in_apis.get_tester(tester_id, product_id)
  if tester:
    ret = apis.delete_tester(tester.organization_id, tester.email)
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
    tester_authorized = tester_info['user']['authorized']
    in_apis.create_tester(invite.email, invite.organization_id,
                          invite.product_id, tester_authorized)
    # TODO:
    ret = apis.register_tester(organization_id, invite.product_id, invite.email,
                                models.STAGE_PRE_RELEASE)
    if tester_authorized:
      return redirect(url_for('base_blueprint.welcome'))
    else:
      return redirect(url_for('base_blueprint.welcome_no_ftl'))
  else:
    abort(400)


@blueprint.route('/<product_id>/model', methods=['GET'])
@login_required
def model_list(product_id):
  _set_product(product_id)
  dev_product = in_apis.get_product_stage_by_dev(product_id)
  return render_template('model_list.html', model_list=dev_product.model_list)


@blueprint.route('/<product_id>/model/<model_id>', methods=['GET'])
@login_required
def model_info(product_id, model_id):
  _set_product(product_id)
  model = in_apis.get_model(model_id)
  return render_template('model.html', model=model)


@blueprint.route('/<product_id>/model/<model_id>/firmware', methods=['GET', 'POST'])
@login_required
def upload_firmware(product_id, model_id):
  referrer = "/products/" + product_id + "/model/" + model_id
  if request.method == "GET":
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
                           allow_stage_list=allow_stage_list)
  else:
    state = int(request.form['state'])
    upload_file = request.files['file']
    content = upload_file.read()
    model = in_apis.get_model(model_id)
    version = model.product_stage.endpoint.version
    ret = apis.register_firmware(product_id, version, model.code, content)
    if ret:
      firmware = in_apis.create_firmware(version, current_user.email, ret,
                                         model.id)
      firmware_stage = in_apis.create_firmware_stage(firmware.id, version,
                                                     models.FIRMWARE_DEV)
      return redirect('products/' + product_id + '/model/' + model_id)
    else:
      logging.warn("Raise error. model : %s", model_id)
      abort(500)


def _set_product(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
