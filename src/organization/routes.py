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
import json
import uuid
import logging
import datetime
import tempfile

from flask import abort, render_template, request, redirect, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user, login_required  # noqa : pylint: disable=import-error

import apis
import common
import worker
import in_apis
import models
import mail
import util
import base.routes
from base import db
from organization import blueprint


@blueprint.route('/', methods=['GET'])
@login_required
def default_route():
  if current_user.organization_id:
    org = in_apis.get_organization(current_user.organization_id)
    noti_key_list = in_apis.get_noti_key_list(current_user.organization_id)
    product_list = in_apis.get_product_list(current_user.organization_id)
    user_list = in_apis.get_user_list(current_user.organization_id)
    invite_list = in_apis.get_invite_list(current_user.organization_id)
    release_list = []
    for product in product_list:
      _release = in_apis.get_product_stage_by_release(product.id)
      if _release:
        release_list.append(_release.id)
    msg = {
        "delete": common.get_msg("organization.delete.organization.delete_message"),
        "delete_ok": common.get_msg("organization.delete.organization.delete_ok"),
        "delete_cancel": common.get_msg("organization.delete.organization.delete_cancel")
    }
    return render_template("organization.html", org=org,
                           noti_key_list=noti_key_list, user_list=user_list,
                           product_list=product_list,
                           invite_list=invite_list,
                           release_list=release_list,
                           msg=msg)
  else:
    return redirect("/organization/create")


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    if current_user.organization_id:
      return redirect('/organization')
    else:
      modal = {
          "title": common.get_msg("organization.create.organization.modal_title"),
          "sub_title": common.get_msg("organization.create.organization.modal_sub_title"),
          "message": common.get_msg("organization.create.organization.modal_message"),
          "ok": common.get_msg("organization.create.organization.modal_ok")
      }
      return render_template("create.html", modal=modal)
  else:
    name = request.form['name']
    owner_email = current_user.email
    is_org = in_apis.get_organization_by_name(name.lower())
    if is_org:
      title = common.get_msg("organization.create.organization.fail_exists_organization_title")
      msg = common.get_msg("organization.create.organization.fail_exists_organization_message")
      common.set_error_message(title, msg)
      return redirect('/organization/create')
    else:
      ret = apis.create_org(owner_email)
      if ret:
        in_apis.create_organization(owner_email, name, ret)
        user = in_apis.get_user(current_user.id)
        if user:
          user.organization_id = ret['id']
          user.level = models.OWNER
          db.session.commit()
        return redirect('/products/create')
      else:
        logging.warning("Fail to create org. Name : %s, user : %s",
                        name, current_user.email)
        abort(500)


@blueprint.route('/register/<platform>', methods=['GET', 'POST'])
@login_required
def register_noti_key(platform):
  referrer = "/organization"
  if request.method == "GET":
    if platform == "ios":
      return render_template("register_ios.html", referrer=referrer)
    else:
      return render_template("register_android.html", referrer=referrer)
  else:
    if platform == "ios":
      bundle_id = request.form['bundleId']
      password = request.form['password']
      state = int(request.form['state'])
      upload_file = request.files['file']
      content = upload_file.read()
      temp_file = tempfile.mkstemp()[1]
      with open(temp_file, 'wb') as _f:
        _f.write(content)
      cert, secret_key = worker.get_about_noti_key(password, temp_file)
      ret = apis.update_ios_key(current_user.organization_id, bundle_id,
                                cert, secret_key, state)
      if ret:
        noti_key = in_apis.get_ios_noti_key(current_user.organization_id,
                                            models.IOS, bundle_id, password,
                                            state)
        if noti_key:
          in_apis.update_noti_key(noti_key)
        else:
          in_apis.create_ios_noti_key(bundle_id, password, state)
        if os.path.exists(temp_file):
          os.remove(temp_file)
        return redirect('organization')
      else:
        logging.warning(
            "Fail to ios register noti key. org : %s, id : %s, pw : %s, state : %s, user : %s",
            current_user.organization_id, bundle_id, password, state,
            current_user.email)
        if os.path.exists(temp_file):
          os.remove(temp_file)
        abort(500)
    else:
      package_name = request.form['packageName']
      key = request.form['key']
      ret = apis.update_android_key(current_user.organization_id, package_name,
                                    key)
      if ret:
        noti_key = in_apis.get_android_noti_key(current_user.organization_id,
                                                models.ANDROID, package_name, key)
        if noti_key:
          in_apis.update_noti_key(noti_key)
        else:
          in_apis.create_android_noti_key(package_name, key)
        return redirect('organization')
      else:
        logging.warning(
            "Fail to register android noti key. org : %s, name : %s, key : %s, user : %s",
            current_user.organization_id, package_name, key, current_user.email)
        abort(500)


@blueprint.route('/invite', methods=['POST'])
@login_required
def send_invite():
  email_addr = request.form['email']
  _user = in_apis.get_user_by_email(email_addr, current_user.organization_id)
  if not _user:
    with open(util.get_mail_form_path('invite.html'), 'r') as _f:
      content = _f.read()
    key = uuid.uuid4().hex
    auth_url = request.host_url + 'organization/confirm?key=' + key + \
        '&o=' + current_user.organization_id
    org = in_apis.get_organization(current_user.organization_id)
    title = common.get_msg("organization.member.mail_title")
    title = title.format(org.original_name)
    msg = common.get_msg("organization.member.mail_message")
    msg = msg.format(org.original_name, org.original_name)
    content = content.format(auth_url=auth_url, title=title, msg=msg)
    try:
      mail.send(email_addr, title, content)
      _invite = in_apis.get_invite_by_member(email_addr,
                                             current_user.organization_id)
      if _invite:
        _t = datetime.datetime.utcnow() - _invite.invited_time
        if _t.seconds >= 86400:
          in_apis.update_invite_by_key(key, _invite)
      else:
        in_apis.create_invite(email_addr, key, current_user.email,
                              current_user.organization_id)
    except:
      logging.exception("Raise error. to : %s, sender : %s, org : %s",
                        email_addr, current_user.email, org.original_name)
      abort(500)
  return redirect('organization')


@blueprint.route('/confirm', methods=['GET'])
def confirm_mail():
  key = request.args['key']
  organization_id = request.args['o']
  invite = in_apis.get_invite(key, organization_id)
  if invite:
    in_apis.update_invite(key, organization_id)
    if current_user.is_anonymous:
      return redirect(url_for('login_blueprint.login'))
    else:
      if invite.email == current_user.email:
        user = in_apis.get_user(current_user.id)
        user.organization_id = organization_id
        org = in_apis.get_organization(organization_id)
        users = json.loads(org.users)
        users.append(user.email)
        org.users = json.dumps(users)
        db.session.commit()
        return redirect(url_for('home_blueprint.index'))
      else:
        base.routes.logout()
        return redirect(url_for('login_blueprint.login'))
  else:
    logging.warning("Fail to confirm to mail. key : %s, org : %s",
                    key, organization_id)
    abort(400)


@blueprint.route('/invite/<invite_id>')
@login_required
def delete_invite(invite_id):
  try:
    in_apis.delete_invite(invite_id)
    return redirect('organization')
  except:
    logging.exception("Raise error while delete invite. Id : %s, user : %s",
                      invite_id, current_user.email)
    abort(500)


@blueprint.route('/delete', methods=['POST'])
@login_required
def delete_organization():
  if current_user.level == models.OWNER:
    try:
      organization_id = current_user.organization_id
      in_apis.delete_invite_by_organization(organization_id)
      in_apis.delete_organization(organization_id)
      return redirect('/')
    except:
      logging.exception("Raise error while delete organization. Id : %s, user : %s",
                        current_user.organization_id, current_user.email)
      abort(500)
  else:
    return redirect('/')
