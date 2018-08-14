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
import datetime
import logging

from flask import abort, render_template, request, redirect, url_for
from flask_login import login_required
from flask_login import current_user

import apis
import cmds
import in_apis
import models
import mail
from base import db
from models import Organization
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
    return render_template("organization.html", org=org,
                           noti_key_list=noti_key_list, user_list=user_list,
                           product_list=product_list,
                           invite_list=invite_list)
  else:
    return redirect("/organization/create")


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    if current_user.organization_id:
      return redirect('/organization')
    else:
      return render_template("create.html")
  else:
    name = request.form['name']
    owner_email = current_user.email
    is_org = in_apis.get_organization_by_name(name.lower())
    if is_org:
      # TODO: change message
      error_msg = {"title": "Exists Name", "msg": "Exists name"}
      return render_template("create.html", error_msg=error_msg)
    else:
      ret = apis.create_org(owner_email)
      if ret:
        org = Organization(id=ret['id'],
                           users=json.dumps([owner_email]),
                           products=json.dumps(ret['products']),
                           tokens=json.dumps(ret['tokens']),
                           kinds=json.dumps(ret['kinds']),
                           name=name.lower(),
                           original_name=name,
                           created_time=datetime.datetime.utcnow(),
                           last_update=datetime.datetime.utcnow())
        db.session.add(org)
        db.session.commit()
        user = in_apis.get_user_by_email(owner_email)
        if user:
          user.organization_id = ret['id']
          user.level = models.OWNER
          db.session.commit()
        return redirect('/products/create')
      else:
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
      cmds.send_noti_key(current_user.organization_id, bundle_id, password,
                         content, state)
      in_apis.create_ios_noti_key(bundle_id, password, state)
      return redirect('organization')
    else:
      package_name = request.form['packageName']
      key = request.form['key']
      in_apis.create_android_noti_key(package_name, key)
      return redirect('organization')


@blueprint.route('/invite', methods=['POST'])
@login_required
def send_invite():
  email_addr = request.form['email']
  with open(os.path.join(cmds.get_res_path(), 'invite.html'), 'r') as f:
    content = f.read()
  key = uuid.uuid4().hex
  auth_url = request.host_url + 'organization/confirm?key=' + key + \
      '&o=' + current_user.organization_id
  content = content.format(auth_url=auth_url)
  try:
    mail.send(email_addr, 'Invite', content)
    in_apis.create_invite(email_addr, key, current_user.email,
                          current_user.organization_id)
  except:
    logging.exception("Raise error")
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
      return redirect(url_for('home_blueprint.index'))
  else:
    abort(400)


@blueprint.route('/invite/<invite_id>')
@login_required
def delete_invite(invite_id):
  in_apis.delete_invite(invite_id)
  return redirect('organization')
