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

import os, stat
import json
import uuid
import logging
import tempfile

from bcrypt import checkpw
from flask import abort, render_template, request, redirect, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import apis
import common
import worker
import in_apis
import in_config_apis
import models
import util
import base.routes
from base import db


LOGO_URL_FORMAT = '''/static/images/{}/{}'''
FOOTER_URL_FORMAT = '''/static/footer/{}/'''


USER_LEVEL = {
    models.SK_ADMIN: "Admin",
    models.SK_NORMAL: "SKEC",
    models.SK_HQ: "SK HQ",
    models.ADNOC_SITE: "ADNOC SITE",
    models.ADNOC_HQ: "ADNOC HQ",
    models.MOI: "MOI",
    models.COVID19_ADMIN: "Covid Admin",
    models.COVID19_TEAMDOCTOR: "Team Doctor"
}


def general():
  if current_user.organization_id:
    org = in_apis.get_organization(current_user.organization_id)
    product_list = in_apis.get_product_list(current_user.organization_id)
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
    #TODO: remove logo allow when support payment
    logo_allow = request.args.get("logo")
    return render_template("general_organization.html", org=org,
                           release_list=release_list,
                           msg=msg, logo_allow=logo_allow)
  else:
    return redirect("/management/organization/create")


def register_logo_image():
  try:
    upload_file = request.files['file']
    content = upload_file.read()
    base_path = util.get_static_path()
    org_path = os.path.join(base_path, 'images', current_user.organization_id)
    if not os.path.exists(org_path):
      os.makedirs(org_path)
    file_path = os.path.join(org_path, upload_file.filename)
    if os.path.exists(file_path):
      os.remove(file_path)
    with open(file_path, 'wb') as _f:
      _f.write(content)
    os.chmod(file_path, stat.S_IREAD)
    logo_url = LOGO_URL_FORMAT.format(current_user.organization_id,
                                      upload_file.filename)
    in_apis.update_organization_by_logo(current_user.organization_id, logo_url)
    return redirect("/management/organization/general")
  except:
    logging.exception("Raise error while register logo image")
    abort(500)


def notification_key():
  if current_user.organization_id:
    noti_key_list = in_apis.get_noti_key_list(current_user.organization_id)
    return render_template("notification_organization.html",
                           noti_key_list=noti_key_list)
  else:
    return redirect("/management/organization/create")


def member():
  if current_user.organization_id:
    user_list = in_apis.get_user_list(current_user.organization_id)
    invite_list = in_apis.get_invite_list(current_user.organization_id)
    return render_template("member_organization.html",
                           user_list=user_list,
                           invite_list=invite_list, user_level=USER_LEVEL)
  else:
    return redirect("/management/organization/create")


def member_level(user_id, level):
  in_apis.update_user_by_level(user_id, level)
  return redirect("/management/organization/member")


def member_accept(user_id):
  in_apis.update_user_by_accept(user_id)
  return redirect("/management/organization/member")


def member_delete(user_id):
  in_apis.delete_user_by_id(user_id)
  return redirect("/management/organization/member")


def member_create():
  if request.method == "GET":
    return render_template('member_create.html', user_level=USER_LEVEL)
  else:
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    department = request.form['department']
    level = request.form['level']
    emirates_id = request.form.get('emiratesId', '')
    in_apis.create_user(email, username, password, department, level,
                        emirates_id)
    return redirect("/management/organization/member")


def member_password(user_id):
  if request.method == "GET":
    return render_template('password.html', user_id=user_id)
  else:
    cur_password = request.form['cur_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    _user = in_apis.get_user(user_id)
    if _user and cur_password and _user.password and \
        checkpw(cur_password.encode('utf8'), _user.password):
      if new_password and confirm_password and new_password == confirm_password:
        in_apis.update_user_password(user_id, new_password)
        return redirect('/management/organization/member')
    #TODO: update then remove below
    elif _user and not _user.password and new_password and \
        confirm_password and new_password == confirm_password:
      in_apis.update_user_password(user_id, new_password)
      return redirect('/management/organization/member')
    return render_template('password.html')


def member_update(user_id):
  if request.method == "GET":
    user = in_apis.get_user(user_id)
    return render_template('member_update.html', user=user)
  else:
    username = request.form['username']
    department = request.form['department']
    in_apis.update_user_information(user_id, username, department)
    return redirect('/management/organization/member')


def product():
  if current_user.organization_id:
    product_list = in_apis.get_product_list(current_user.organization_id)
    return render_template("product_organization.html",
                           product_list=product_list)
  else:
    return redirect("/management/organization/create")


def create():
  if request.method == "GET":
    if current_user.organization_id:
      return redirect('/management/organization')
    else:
      modal = {
          "title": common.get_msg("organization.create.organization.modal_title"),
          "sub_title": common.get_msg("organization.create.organization.modal_sub_title"),
          "message": common.get_msg("organization.create.organization.modal_message"),
          "ok": common.get_msg("organization.create.organization.modal_ok")
      }
      return render_template("create_organization.html", modal=modal)
  else:
    name = request.form['name']
    owner_email = current_user.email
    is_org = in_apis.get_organization_by_name(name.lower())
    if is_org:
      title = common.get_msg("organization.create.organization.fail_exists_organization_title")
      msg = common.get_msg("organization.create.organization.fail_exists_organization_message")
      common.set_error_message(title, msg)
      return redirect('/management/organization/create')
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


def register_noti_key(platform):
  referrer = "/management/organization/notification"
  if request.method == "GET":
    product_list = in_apis.get_product_list(current_user.organization_id)
    if platform == "ios":
      return render_template("register_ios.html", referrer=referrer,
                             product_list=product_list)
    else:
      return render_template("register_android.html", referrer=referrer,
                             product_list=product_list)
  else:
    allow_dict = json.loads(request.form['allowDict'])
    allow_model_id_list = json.loads(request.form['allowModelIdList'])
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
                                cert, secret_key, state, allow_dict)
      if ret:
        noti_key = in_apis.get_ios_noti_key(current_user.organization_id,
                                            models.IOS, bundle_id, password,
                                            state)
        if noti_key:
          in_apis.update_noti_key(noti_key)
          for model_id in allow_model_id_list:
            in_apis.create_noti_model_permission(current_user.email,
                                                 noti_key.id,
                                                 model_id)
        else:
          noti_key = in_apis.create_ios_noti_key(bundle_id, password, state)
          for model_id in allow_model_id_list:
            in_apis.create_noti_model_permission(current_user.email,
                                                 noti_key.id,
                                                 model_id)
        if os.path.exists(temp_file):
          os.remove(temp_file)
        return redirect('/management/organization/notification')
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
                                    key, allow_dict)
      if ret:
        noti_key = in_apis.get_android_noti_key(current_user.organization_id,
                                                models.ANDROID, package_name, key)
        if noti_key:
          in_apis.update_noti_key(noti_key)
          for model_id in allow_model_id_list:
            in_apis.create_noti_model_permission(current_user.email,
                                                 noti_key.id,
                                                 model_id)
        else:
          noti_key = in_apis.create_android_noti_key(package_name, key)
          for model_id in allow_model_id_list:
            in_apis.create_noti_model_permission(current_user.email,
                                                 noti_key.id,
                                                 model_id)
        return redirect('/management/organization/notification')
      else:
        logging.warning(
            "Fail to register android noti key. org : %s, name : %s, key : %s, user : %s",
            current_user.organization_id, package_name, key, current_user.email)
        abort(500)


def update_noti_key(noti_key_id):
  referrer = "/management/organization/notification"
  if request.method == "GET":
    noti_key = in_apis.get_noti_key(noti_key_id)
    product_list = in_apis.get_product_list(current_user.organization_id)
    allow_model_id_list = []
    allow_dict = {}
    for permit in noti_key.permission_list:
      allow_model_id_list.append(permit.model_id)
    for product in product_list:
      for model in product.model_list:
        if model.id in allow_model_id_list:
          if product.code in allow_dict:
            allow_dict[product.code].append(model.id)
          else:
            allow_dict[product.code] = [model.id]
    return render_template("update_notification.html", referrer=referrer,
                            noti_key=noti_key, product_list=product_list,
                            allow_model_id_list=allow_model_id_list,
                            allow_dict=allow_dict)
  else:
    allow_dict = json.loads(request.form['allowDict'])
    allow_model_id_list = json.loads(request.form['allowModelIdList'])
    if allow_dict and allow_model_id_list:
      noti_key = in_apis.get_noti_key(noti_key_id)
      ret = apis.update_allow_noti_key(current_user.organization_id, noti_key.name,
                                       allow_dict)
      if ret:
        permit_list = in_apis.get_noti_model_permission_list_by_noti_id(noti_key.id)
        if permit_list:
          for permit in permit_list:
            if permit.model_id in allow_model_id_list:
              in_apis.update_noti_model_permission(permit.id, current_user.email,
                                                  noti_key.id, permit.model_id)
              allow_model_id_list.remove(permit.model_id)
            else:
              in_apis.delete_noti_model_permission(permit.id)
        for model_id in allow_model_id_list:
          in_apis.create_noti_model_permission(current_user.email, noti_key.id,
                                              model_id)
        return redirect('/management/organization/notification')
      else:
        logging.warning("Failed to update noti key. id : %s, user : %s, message : %s",
                        noti_key_id, current_user.email, ret)
        abort(500)
    else:
      return redirect('/management/organization/notification')


def delete_noti_key(noti_key_id):
  logging.info("Try to delete noti key. User : %s, noti id : %s",
               current_user.email, noti_key_id)
  ret = in_apis.delete_noti_key(current_user.organization_id, noti_key_id)
  if ret:
    return redirect('/management/organization/notification')
  else:
    logging.warning("Failed to delete noti key.")
    return redirect('/management/organization/notification')


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


def get_domain_list():
  domain_list = in_apis.get_domain_list(current_user.organization_id)
  return render_template("domain_organization.html", domain_list=domain_list)


def register_domain():
  if request.method == "GET":
    referrer = "/management/organization/domain"
    return render_template("register_domain.html", referrer=referrer)
  else:
    domain = request.form['domain']
    if in_apis.has_domain_by_domain(domain):
      title = common.get_msg("organization.domain.duplicated_title")
      msg = common.get_msg("organization.domain.duplicated_message")
      common.set_error_message(title, msg)
      return redirect('/management/organization/domain/register')
    files_path = []
    # TODO: file save
    ip_addr = util.get_ip_addr()
    try:
      in_apis.create_domain(domain, ip_addr, current_user.email,
                            json.dumps(files_path),
                            current_user.organization_id)
      return redirect('/management/organization/domain')
    except:
      logging.exception("Failed to register domain")
      return redirect('/management/organization/domain')


def accepted_domain():
  # TODO: accepted domain
  # TODO: Send cert files and register domain to reverse proxy server
  # TODO: in_apis.update_domain(domain_id)
  pass
