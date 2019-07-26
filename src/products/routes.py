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
import tempfile
import urllib.parse

from flask import send_from_directory  # noqa : pylint: disable=import-error
from flask import abort, render_template, request, redirect, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import apis
import util
import mail
import common
import models
import worker
import in_apis
import base.routes
from base import db
from products import blueprint


def _get_prd_type_dict():
  typ_dict = {
      models.PRD_TYPE_BLE: "BLE",
      models.PRD_TYPE_WEB: "HTTP"
  }
  return typ_dict


@blueprint.route('/create', methods=['GET', 'POST'])
@util.require_login
def create():
  typ_dict = _get_prd_type_dict()
  if request.method == "GET":
    modal = {}
    product_list = in_apis.get_product_list(current_user.organization_id)
    if not product_list:
      modal['title'] = common.get_msg("products.create.product.first.title")
      modal['sub_title'] = common.get_msg("products.create.product.first.sub_title")
      modal['message'] = common.get_msg("products.create.product.first.message")
      modal['ok'] = common.get_msg("products.create.product.first.ok")
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    return render_template("prd_create.html", referrer=referrer, modal=modal,
                           typ_dict=typ_dict)
  else:
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    if referrer == "/products/create":
      # TODO:  change referrer url
      referrer = "/home/index"

    code = request.form['code']
    name = request.form['name']
    keyword = request.form['keyword']
    prd_type = request.form['type']
    if re.compile(r'\W|\d').findall(code):
      title = common.get_msg("products.create.product.invalid_code_title")
      msg = common.get_msg("products.create.product.invalid_code_message")
      common.set_error_message(title, msg)
      return render_template("prd_create.html", referrer=referrer,
                             typ_dict=typ_dict)
    has_product = in_apis.has_product(code)
    if has_product:
      title = common.get_msg("products.create.product.exists_product_title")
      msg = common.get_msg("products.create.product.exists_product_message")
      common.set_error_message(title, msg)
      return render_template("prd_create.html", referrer=referrer,
                             typ_dict=typ_dict)
    if re.compile(r'\W').findall(keyword):
      title = common.get_msg("products.create.product.invalid_keyword_title")
      msg = common.get_msg("products.create.product.invalid_keyword_message")
      common.set_error_message(title, msg)
      return render_template("prd_create.html", referrer=referrer,
                             typ_dict=typ_dict)
    has_product_keyword = in_apis.get_product_by_keyword(keyword)
    if has_product_keyword:
      title = common.get_msg("products.create.product.exists_keyword_title")
      msg = common.get_msg("products.create.product.exists_keyword_message")
      common.set_error_message(title, msg)
      return render_template("prd_create.html", referrer=referrer,
                             typ_dict=typ_dict)
    else:
      ret = apis.create_product(code, keyword, current_user.organization_id)
      if ret:
        # TODO: Product type
        product = in_apis.create_product(name, ret, prd_type)
        org = in_apis.get_organization(current_user.organization_id)
        if org:
          product_list = json.loads(org.products)
          product_list.append(ret['id'])
          org.products = json.dumps(product_list)
          org.last_updated_time = in_apis.get_datetime()
          db.session.commit()
        _set_product(product.id)
        return redirect('/products/' + ret['id'] + '/model/create')
      else:
        logging.warning("Fail to create product. Name : %sCode : %s, User : %s",
                        name, code, current_user.email)
        abort(500)


def _get_type_dict(product):
  if product.typ == models.PRD_TYPE_BLE:
    typ_dict = {
        models.MODEL_TYPE_NRF_51: "NRF51",
        models.MODEL_TYPE_NRF_52: "NRF52"
    }
    return typ_dict
  else:
    return {}


@blueprint.route('/<product_id>/model/create', methods=['GET', 'POST'])
@util.require_login
def create_model(product_id):
  if request.method == "GET":
    _set_product(product_id)
    product = in_apis.get_product(product_id)
    typ_dict = _get_type_dict(product)
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    return render_template("model_create.html", referrer=referrer,
                           typ_dict=typ_dict)
  else:
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    if referrer == "/products/" + product_id + "/model/create":
      # TODO:  change referrer url
      referrer = "/products/" + product_id + "/model"

    name = request.form['name']
    model_type = request.form.get('type')
    code = 0
    _model_list = in_apis.get_model_list(product_id)
    if _model_list:
      code = len(_model_list) + 1
      has_model = in_apis.get_model_by_code(code, product_id)
      if has_model:
        code += 1

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
        in_apis.create_model(name, code, model_type, product_id,
                             current_user.email)
        return redirect('/products/' + product_id + '/general')
      else:
        logging.warning("Fail to create model. Name : %s, Type : %s, user : %s",
                        name, model_type, current_user.email)
        abort(500)


@blueprint.route('/<product_id>/delete', methods=['GET', 'POST'])
@util.require_login
def delete_product(product_id):
  in_apis.delete_product(product_id)
  return redirect("/organization")


@blueprint.route('/<product_id>/model/<model_id>/delete', methods=['GET', 'POST'])
@util.require_login
def delete_model(product_id, model_id):
  in_apis.delete_model(model_id)
  return redirect("/products/" + product_id + "/model")


@blueprint.route('/<product_id>/general', methods=['GET'])
@util.require_login
def general(product_id):
  _set_product(product_id)
  typ_dict = _get_prd_type_dict()
  return render_template('prd_general.html', typ_dict=typ_dict)


@blueprint.route('/<product_id>/authentication', methods=['GET'])
@util.require_login
def authentication(product_id):
  _set_product(product_id)
  tokens = json.loads(current_user.organization.tokens)
  token = tokens['access'] if 'access' in tokens else None
  dev = in_apis.get_product_stage_by_dev(product_id)
  return render_template('prd_authentication.html', token=token,
                         hook_url=dev.hook_url, hook_client_key=dev.hook_client_key)


@blueprint.route('/<product_id>/hook', methods=['POST'])
@util.require_login
def hook(product_id):
  hook_url = request.form['hookUrl']
  hook_client_key = request.form['hookClientKey']
  ret = apis.update_about_hook(product_id, models.STAGE_DEV, hook_url,
                               hook_client_key)
  if ret:
    dev = in_apis.get_product_stage_by_dev(product_id)
    dev.hook_url = hook_url
    dev.hook_client_key = hook_client_key
    db.session.commit()
    return redirect('/products/' + product_id + '/authentication')
  else:
    logging.warning("Fail to update hook. Url : %s, Key : %s, Product : %s, User : %s",
                    hook_url, hook_client_key, product_id, current_user.email)
    abort(500)


@blueprint.route('/<product_id>/tester', methods=['GET', 'POST'])
@util.require_login
def tester(product_id):
  _set_product(product_id)
  if request.method == "GET":
    dev_level_list = in_apis.get_tester_list_by_dev(product_id,
                                                    current_user.organization_id)
    pre_level_list = in_apis.get_tester_list_by_pre_release(product_id,
                                                            current_user.organization_id)
    invite_list = in_apis.get_invite_list_by_tester(product_id,
                                                    current_user.organization_id)
    return render_template('prd_tester.html',
                           dev_level_list=dev_level_list,
                           pre_level_list=pre_level_list,
                           invite_list=invite_list)
  else:
    # TODO: Send email
    tester_email = request.form['newTesterEmail']
    _tester = in_apis.get_tester_by_email(tester_email, product_id)
    if not _tester:
      _send_invite(tester_email, product_id)
    return redirect('/products/' + product_id + '/tester')


def _send_invite(email_addr, product_id):
  with open(util.get_mail_form_path('tester_invite.html'), 'r') as _f:
    content = _f.read()
  key = uuid.uuid4().hex
  auth_url = request.host_url + 'products/confirm?key=' + key + '&o=' +\
      current_user.organization_id
  _product = in_apis.get_product(product_id)
  title = common.get_msg("products.tester.mail_title")
  title = title.format(_product.name)
  msg = common.get_msg("products.tester.mail_message")
  msg = msg.format(_product.name)
  content = content.format(auth_url=auth_url, title=title, msg=msg)
  try:
    mail.send(email_addr, title, content)
    _invite = in_apis.get_invite_by_product_id(product_id, email_addr,
                                               current_user.organization_id)
    if _invite:
      _t = in_apis.get_datetime() - _invite.invited_time
      if _t.seconds >= 86400:
        in_apis.update_invite_by_key(key, _invite)
    else:
      in_apis.create_invite(email_addr, key, current_user.email,
                            current_user.organization_id, level=models.TESTER,
                            product_id=product_id)
  except:
    logging.exception("Raise error")


@blueprint.route('/<product_id>/product_import', methods=['GET', 'POST'])
@util.require_login
def product_import(product_id):
  _set_product(product_id)
  if request.method == "GET":
    product = in_apis.get_product(product_id)
    fork_list = in_apis.get_fork_product_list(product_id)
    org_dict = {}
    for fork_product in fork_list:
      org_id = fork_product.target_organization
      org_name = in_apis.get_organization(org_id)
      org_dict[org_id] = org_name
    return render_template('prd_import.html',
                           model_list=product.model_list,
                           fork_list=fork_list,
                           org_dict=org_dict)
  else:
    _email = request.form['email']
    _model_id = request.form['modelId']
    _user = in_apis.get_user_by_email_only(_email)
    if _user:
      has_fork_product = in_apis.has_fork_product(_model_id, product_id,
                                                  _user.organization_id)
      if has_fork_product:
        title = common.get_msg("products.product_import.duplicate_title")
        msg = common.get_msg("products.product_import.duplicate_message")
        common.set_error_message(title, msg)
        return redirect('/products/{}/product_import'.format(product_id))
      product_send_invite(_email, product_id, _model_id)
    else:
      logging.warning("User doesn't exist : %s", _email)
    return redirect('/products/{}/product_import'.format(product_id))


def product_send_invite(email, product_id, model_id):
  # TODO : change mail form
  with open(util.get_mail_form_path('prd_import_mail.html'), 'r') as _f:
    content = _f.read()
  key = uuid.uuid4().hex
  auth_url = request.host_url + 'products/' + product_id + \
      '/import/confirm?key=' + key + '&mid=' + model_id
  _product = in_apis.get_product(product_id)
  # TODO : title ~ message1
  title = common.get_msg("products.product_import.mail_title")
  title = title.format(_product.name)
  msg = common.get_msg("products.product_import.mail_message")
  msg = msg.format(_product.name)
  content = content.format(auth_url=auth_url, title=title, msg=msg)
  target_organization_id = in_apis.get_user_by_email_only(email).organization_id
  try:
    mail.send(email, title, content)
    in_apis.create_fork_product(_product, email, model_id,
                                current_user.email, key, target_organization_id)
  except:
    logging.exception("Raise error")


@blueprint.route('/<product_id>/product_import/delete/<fork_id>', methods=['POST'])
@util.require_login
def delete_fork_product(product_id, fork_id):
  in_apis.delete_fork_product(fork_id)
  return redirect('/products/' + product_id + '/product_import')


@blueprint.route('/<product_id>/tester/<tester_id>/change/<level>')
@util.require_login
def change_tester_level(product_id, tester_id, level):
  _tester = in_apis.get_tester(tester_id, product_id)
  if _tester:
    ret = apis.register_tester(_tester.organization_id, product_id, _tester.email,
                               int(level))
    if ret:
      _tester.level = level
      db.session.commit()
      return redirect('/products/' + product_id + '/tester')
    else:
      logging.warning("Failed to change tester level. Id : %s, ret : %s",
                      tester_id, ret)
      return redirect('/products/' + product_id + '/tester')
  else:
    logging.warning("Can not find tester. Id : %s", tester_id)
    return redirect('/products/' + product_id + '/tester')


@blueprint.route('/<product_id>/tester/<tester_id>/delete')
@util.require_login
def remove_tester(product_id, tester_id):
  _tester = in_apis.get_tester(tester_id, product_id)
  if _tester:
    if _tester.authorized:
      ret = apis.delete_tester(_tester.organization_id, product_id,
                               _tester.email)
      if ret:
        in_apis.delete_tester(tester_id)
      else:
        logging.warning("Failed to delete tester. Tester : %s", _tester.email)
    else:
      logging.info("%s is not ftl. Delete only from console DB.", _tester.email)
      in_apis.delete_tester(tester_id)
  return redirect('/products/' + product_id + '/tester')


@blueprint.route('/<product_id>/tester/<tester_id>/refresh')
@util.require_login
def check_authorized(product_id, tester_id):
  _tester = in_apis.get_tester(tester_id, product_id)
  if _tester:
    tester_info = apis.get_user(_tester.email)
    tester_authorized = tester_info['user']['authorized']
    if tester_authorized:
      in_apis.update_tester_to_authorized(_tester.id)
  return redirect('/products/' + product_id + '/tester')


@blueprint.route('/<product_id>/invite/tester/<invite_id>/delete')
@util.require_login
def remove_invite_tester(product_id, invite_id):
  in_apis.delete_invite(invite_id)
  return redirect('/products/' + product_id + '/tester')


@blueprint.route('/confirm', methods=['GET'])
def confirm_mail():
  key = request.args['key']
  organization_id = request.args['o']
  invite = in_apis.get_invite(key, organization_id)
  if invite:
    in_apis.update_invite(key, organization_id)
    tester_info = apis.get_user(invite.email)
    tester_authorized = tester_info['user']['authorized'] if tester_info and tester_info['user'] else False
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
      logging.warning("Fail to register test. Org : %s, Product : %s, email : %s",
                      invite.organization_id, invite.product_id, invite.email)
      abort(500)
  else:
    logging.warning("Can not find invite. Key : %s, org : %s",
                    key, organization_id)
    abort(400)


@blueprint.route('<product_id>/import/confirm', methods=['GET'])
@util.require_login
def confirm_product(product_id):
  noti_key_list = current_user.organization.noti_key
  if not noti_key_list:
    title = common.get_msg("products.product_import.notNotiKey_title")
    msg = common.get_msg("products.product_import.notNotiKey_message")
    common.set_error_message(title, msg)
    return redirect('/management/organization/notification')
  key = request.args['key']
  parent_model_id = request.args['mid']
  fork_product = in_apis.get_fork_product_by_key(key)
  if fork_product:
    parent_product = in_apis.get_product(product_id)
    target_org = in_apis.get_organization(fork_product.target_organization)
    new_product_id = product_id + target_org.name
    new_product_type = parent_product.typ
    return render_template('import_prd_create.html', product_id=new_product_id[:10],
                           product_type=new_product_type,
                           noti_key_list=noti_key_list,
                           parent_product_id=product_id,
                           parent_model_id=parent_model_id,
                           fork_prd_key=key)
  else:
    logging.warning("Can not find fork product. product id : %s, target user : %s",
                    product_id, current_user.email)
    abort(400)


@blueprint.route('/import/create', methods=['POST'])
@util.require_login
def create_import_product():
  try:
    prd_id = request.form['code']
    prd_keyword = request.form['keyword']
    prd_name = request.form['name']
    prd_type = request.form['typ']
    model_name = request.form['modelName']
    parent_prd_id = request.form['parentProductId']
    parent_model_id = request.form['parentModelId']
    key = request.form['forkProductKey']
    raw_allow_noti_key_list = request.form['allowNotiIdList']
    allow_noti_key_list = json.loads(raw_allow_noti_key_list)

    in_apis.update_fork_product(key)
    parent_product = in_apis.get_product(parent_prd_id)
    prd_ret = apis.create_product(prd_id, prd_keyword, current_user.organization_id)
    if not prd_ret:
      logging.warning("Failed to create product. Ret : %s, prd id : %s, keyword : %s",
                      prd_ret, prd_id, prd_keyword)
      abort(500)
    in_apis.create_product_to_import(prd_name, prd_ret, prd_type, parent_prd_id)
    parent_model = in_apis.get_model(parent_model_id)

    code = 0
    model_ret = apis.create_model(prd_id, code, model_name)
    if not model_ret:
      logging.warning("Failed to create model. Ret : %s, code : %s, name : %s",
                      model_ret, code, model_name)
      abort(500)
    model = in_apis.create_model_import(model_name, code, parent_model.typ,
                                        prd_id, current_user.email,
                                        parent_model_id)
    for noti_key_id in allow_noti_key_list:
      noti_key = in_apis.get_noti_key(noti_key_id)
      apis.register_or_update_stream_product(prd_id, noti_key.name,
                                             parent_prd_id, code)
      data = {prd_id: []}  # list에 code가 없으면 스캔만 가능해진다.
      apis.update_allow_noti_key(current_user.organization_id, noti_key.name,
                                 data)
      in_apis.create_noti_model_permission(current_user.email, noti_key.id,
                                           model.id)

    return redirect(url_for('home_blueprint.index'))
  except:
    logging.exception("Raise error while create import product")
    abort(500)


@blueprint.route('/<product_id>/model', methods=['GET'])
@util.require_login
def model_list(product_id):
  _set_product(product_id)
  _product = in_apis.get_product(product_id)
  product = in_apis.get_product(product_id)
  typ_dict = _get_type_dict(product)
  return render_template('model_list.html', model_list=product.model_list,
                         typ_dict=typ_dict)


@blueprint.route('/<product_id>/model/<model_id>', methods=['GET'])
@util.require_login
def model_info(product_id, model_id):
  _set_product(product_id)
  model = in_apis.get_model(model_id)
  dev = in_apis.get_product_stage_by_dev(product_id)
  dev_id = ""
  if dev:
    for info in dev.stage_info_list:
      if info.model_id == model_id:
        dev_id = info.firmware_id
  pre = in_apis.get_product_stage_by_pre_release(product_id)
  pre_id = ""
  if pre:
    for info in pre.stage_info_list:
      if info.model_id == model_id:
        pre_id = info.firmware_id
  release = in_apis.get_product_stage_by_release(product_id)
  release_id = ""
  if release:
    for info in release.stage_info_list:
      if info.model_id == model_id:
        release_id = info.firmware_id
  return render_template('model.html', model=model,
                         firmware_list=model.firmware_list,
                         dev_id=dev_id, pre_id=pre_id, release_id=release_id)


def _get_build_number(ep_version, firmware_version):
  major, minor, build_number = firmware_version.split(".")
  _before_ep_version = ".".join([major, minor])
  if ep_version == _before_ep_version:
    return str(int(build_number) + 1)
  else:
    return "0"


def _get_will_use_firmware_version(product_id, model_id):
  dev_stage = in_apis.get_product_stage_by_dev(product_id)
  stage_info = in_apis.get_dev_stage_info_by_model(model_id, dev_stage.id)
  ep = in_apis.get_specifications(stage_info.endpoint_id)
  if stage_info.firmware_id:
    _firmware = in_apis.get_firmware(stage_info.firmware_id)
    version = ep.version + "." + _get_build_number(ep.version, _firmware.version)
  else:
    version = ep.version + ".0"
  return version


@blueprint.route('/<product_id>/model/<model_id>/firmware', methods=['GET', 'POST'])
@util.require_login
def upload_firmware(product_id, model_id):
  referrer = "/products/" + product_id + "/model/" + model_id
  firmware_version = _get_will_use_firmware_version(product_id, model_id)
  if request.method == "GET":
    _set_product(product_id)
    _model = in_apis.get_model(model_id)
    return render_template('register_firmware.html', referrer=referrer,
                           model=_model, firmware_version=firmware_version)
  else:
    upload_file = request.files['file']
    content = upload_file.read()
    tf_path = tempfile.mkstemp()[1]
    with open(tf_path, 'wb') as _f:
      _f.write(content)

    _model = in_apis.get_model(model_id)
    try:
      ret_json = worker.get_hex_to_json(tf_path)
      os.remove(tf_path)
      if not ret_json:
        logging.warning("Result json is None. Json : %s", ret_json)
        abort(500)

      ret = apis.register_firmware(product_id, _model.code, firmware_version,
                                   ret_json)
      if ret:
        _dev_stage = in_apis.get_product_stage_by_dev(product_id)
        _stage_info = in_apis.get_dev_stage_info_by_model(model_id, _dev_stage.id)
        _ep = in_apis.get_specifications(_stage_info.endpoint_id)
        _firmware = in_apis.create_firmware(firmware_version,
                                            _ep.version,
                                            _model.code, current_user.email,
                                            ret, model_id)
        in_apis.update_dev(product_id)
        _dev = in_apis.get_product_stage_by_dev(product_id)
        models_dict = {_model.code: firmware_version}
        _ret = apis.update_product_stage(product_id, _dev, models_dict,
                                         models.STAGE_DEV)
        if _ret:
          in_apis.update_stage_info_by_dev_about_firmware(product_id, model_id,
                                                          _firmware.id)
          mail.send_about_test_user(product_id, _model.name, firmware_version,
                                    models.TESTER_DEV)
          return redirect('/products/' + product_id + '/model/' + model_id)
        else:
          logging.warning("Failed to update stage while upload firmware.")
          abort(500)
      else:
        logging.warning("Raise upload firmware error. Product : %s, model : %s, name : %s, user : %s",
                        product_id, model_id, _model.name, current_user.email)
        abort(500)
    except Exception:
      if os.path.exists(tf_path):
        os.remove(tf_path)
      logging.exception("Raise error while upload firmware. Product : %s, model : %s, user : %s",
                        product_id, _model.name, current_user.email)
      abort(500)


@blueprint.route('/<product_id>/model/<model_id>/firmware/<firmware_id>', methods=['POST'])
@util.require_login
def delete_firmware(product_id, model_id, firmware_id):
  _firmware = in_apis.get_firmware(firmware_id)
  _model = in_apis.get_model(model_id)
  if _firmware:
    ret = apis.delete_firmware(product_id, _model.code, _firmware.version)
    if ret:
      in_apis.delete_firmware(firmware_id)
    else:
      logging.warning("Failed to delete firmware. P: %s, M: %s, F: %s",
                      product_id, _model.name, _firmware.version)
  return redirect('/products/' + product_id + '/model/' + model_id)


@blueprint.route('/<product_id>/model/<model_id>/firmware/<model_type>/download',
                 methods=['GET', 'POST'])
@util.require_login
def download_software(product_id, model_id, model_type):
  if int(model_type) == models.MODEL_TYPE_NRF_51:
    path = os.path.join(util.get_res_path(), 'firmware', 'nrf51')
    file_name = "nrf51.zip"
  else:
    # NRF 52
    path = os.path.join(util.get_res_path(), 'firmware', 'nrf52')
    file_name = "nrf52.zip"
  return send_from_directory(directory=path, filename=file_name, as_attachment=True)


@blueprint.route('/<product_id>/model/<model_id>/http/download',
                 methods=['GET', 'POST'])
@util.require_login
def download_http_software(product_id, model_id):
  path = os.path.join(util.get_res_path(), 'http')
  file_name = "example.json"
  return send_from_directory(directory=path, filename=file_name, as_attachment=True)


@blueprint.route('/<product_id>/subdomain', methods=['GET'])
@util.require_login
def sub_domain(product_id):
  _set_product(product_id)
  sub_domain_list = in_apis.get_sub_domain_list(product_id)
  return render_template('subdomain.html', sub_domain_list=sub_domain_list)


@blueprint.route('/<product_id>/subdomain/accept/<sub_domain_id>',
                 methods=['GET'])
@util.require_login
def accept_sub_domain(product_id, sub_domain_id):
  sub_domain = in_apis.get_sub_domain(sub_domain_id)
  ret = apis.register_sub_domain(sub_domain.gadget_id, sub_domain.subname,
                                 sub_domain.domain_name)
  if ret:
    #TODO: Register to Domain server
    in_apis.update_sub_domain(sub_domain_id)
    logging.info("Accetped Sub domain. Product : %s, Sub Domain : %s, User : %s",
                 product_id, sub_domain_id, current_user.email)
  else:
    logging.warning("Failed to accepted sub domain. Product : %s, Sub Domain : %s, User : %s",
                    product_id, sub_domain_id, current_user.email)
  return redirect('/products/' + product_id + '/subdomain')


def _set_product(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
