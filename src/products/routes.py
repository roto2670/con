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
import datetime
import logging
import urllib.parse

from flask import render_template, request, redirect
from flask_login import login_required
from flask_login import current_user

import apis
import cmds
import base.routes
from base import db
from products import blueprint
from models import Product, NotiKey, Organization, User


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    return render_template("prd_create.html", referrer=referrer)
  else:
    has_product = apis.get_product(request.form['name'], current_user.organization_id)
    if has_product:
      parse_ret = urllib.parse.urlparse(request.referrer)
      referrer = parse_ret.path if parse_ret else "/"
      if referrer == "/products/create":
        # TODO:  change referrer url
        referrer = "/home/index"
      return render_template("prd_create.html", referrer=referrer, error="Product is exists.")
    else:
      ret = apis.create_product(request.form['name'].lower(), current_user.organization_id)
      product = Product(id=ret['id'],
                        developer_id=ret['developer_id'],
                        key=ret['key'],
                        hook_url=ret['hook_url'],
                        hook_client_key=ret['hook_client_key'],
                        name=request.form['name'],
                        created_time=datetime.datetime.utcnow(),
                        last_update=datetime.datetime.utcnow(),
                        organization_id=ret['developer_id'])
      db.session.add(product)
      db.session.commit()
      org = Organization.query.filter_by(id=ret['developer_id']).one_or_none()
      if org:
        product_list = json.loads(org.products)
        product_list.append(ret['id'])
        org.products = json.dumps(product_list)
        db.session.commit()
      return redirect('products/' + product.id + '/general')


@blueprint.route('/<product_id>/remove', methods=['GET'])
@login_required
def remove(product_id):
  # TODO:
  return redirect('products/management')


@blueprint.route('/<product_id>/general', methods=['GET', 'POST'])
@login_required
def general(product_id):
  if request.method == "GET":
    product = apis.get_product(product_id, current_user.organization_id)
    base.routes.set_current_product(product)
    return render_template('prd_general.html')
  else:
    prd_name = request.form['prdName']
    prd_key = request.form['prdKey']
    logging.info("%s, %s, %s", prd_name, prd_key)
    return redirect('products/' + product_id + '/general')


@blueprint.route('/<product_id>/branding', methods=['GET'])
@login_required
def branding(product_id):
  #TODO:
  return render_template('prd_branding.html')


@blueprint.route('/<product_id>/authentication', methods=['GET'])
@login_required
def authentication(product_id):
  product = apis.get_product(product_id, current_user.organization_id)
  org = Organization.query.filter_by(id=product.organization_id).one_or_none()
  tokens = json.loads(org.tokens)
  token = tokens['access'] if 'access' in tokens else None
  noti_key = NotiKey.query.filter_by(product_id=product_id).one_or_none()
  base.routes.set_current_product(product)
  return render_template('prd_authentication.html', noti_key=noti_key, token=token)


@blueprint.route('/<product_id>/hook', methods=['POST'])
@login_required
def hook(product_id):
  hook_url = request.form['hookUrl']
  hook_client_key = request.form['hookClientKey']
  product = apis.get_product(product_id, current_user.organization_id)
  ret = apis.update_product(product_id, product, hook_url, hook_client_key)

  if ret:
    product.hook_url = ret['hook_url']
    product.hook_client_key = ret['hook_client_key']
  db.session.commit()
  return redirect('products/' + product_id + '/authentication')


@blueprint.route('/<product_id>/android/notikey', methods=['POST'])
@login_required
def android_noti_key(product_id):
  android_noti_key = request.form['androidNotiKey']
  android_package_name = request.form['androidPackageName']
  noti_key = NotiKey.query.filter_by(product_id=product_id).one_or_none()
  if not noti_key:
    product = apis.get_product(product_id, current_user.organization_id)
    noti_key = NotiKey(android_key=android_noti_key,
                       android_package_name=android_package_name,
                       ios_dev_bundle_id="",
                       ios_dev_password="",
                       ios_production_bundle_id="",
                       ios_production_password="",
                       organization_id=current_user.organization_id,
                       product_id=product.id)
    db.session.add(noti_key)
  else:
    noti_key.android_key = android_noti_key
    noti_key.android_package_name = android_package_name
  db.session.commit()

  logging.info("## and : %s, %s", android_noti_key, android_package_name)
  return redirect('products/' + product_id + '/authentication')


@blueprint.route('/<product_id>/ios/dev/notikey', methods=['POST'])
@login_required
def ios_dev_noti_key(product_id):
  ios_bundle_identifier = request.form['iosDevBundleIdentifier']
  ios_password = request.form['iosDevPassword']
  noti_key = NotiKey.query.filter_by(product_id=product_id).one_or_none()
  if not noti_key:
    product = apis.get_product(product_id, current_user.organization_id)
    noti_key = NotiKey(android_key="",
                       android_package_name="",
                       ios_dev_bundle_id=ios_bundle_identifier,
                       ios_dev_password=ios_password,
                       ios_production_bundle_id="",
                       ios_production_password="",
                       organization_id=current_user.organization_id,
                       product_id=product.id)
    db.session.add(noti_key)
  else:
    noti_key.ios_dev_bundle_id = ios_bundle_identifier
    noti_key.ios_dev_password = ios_password
  db.session.commit()
  logging.info("## ios : %s, %s", ios_bundle_identifier, ios_password)
  return redirect('products/' + product_id + '/authentication')


@blueprint.route('/<product_id>/ios/production/notikey', methods=['POST'])
@login_required
def ios_production_noti_key(product_id):
  ios_bundle_identifier = request.form['iosBundleIdentifier']
  ios_password = request.form['iosPassword']
  noti_key = NotiKey.query.filter_by(product_id=product_id).one_or_none()
  if not noti_key:
    product = apis.get_product(product_id, current_user.organization_id)
    noti_key = NotiKey(developer_id=product.developer_id,
                       android_key="",
                       android_package_name="",
                       ios_dev_bundle_id="",
                       ios_dev_password="",
                       ios_production_bundle_id=ios_bundle_identifier,
                       ios_production_password=ios_password,
                       organization_id=current_user.organization_id,
                       product_id=product.id)
    db.session.add(noti_key)
  else:
    noti_key.ios_production_bundle_id = ios_bundle_identifier
    noti_key.ios_production_password = ios_password
  db.session.commit()
  logging.info("## ios : %s, %s", ios_bundle_identifier, ios_password)
  return redirect('products/' + product_id + '/authentication')


@blueprint.route('/<product_id>/ios/dev/upload', methods=['POST'])
@login_required
def upload_ios_dev_file(product_id):
  #TODO: Handle upload content
  upload_file = request.files['file']
  content = upload_file.read()
  # TODO: Check format?? Or send to cloud server
  logging.info("Upload file content : %s", content)
  noti_key = NotiKey.query.filter_by(product_id=product_id).one_or_none()
  ret = cmds.send_noti_key(product_id, noti_key, content, is_dev=True)
  logging.info("### ret : %s", ret)
  return redirect('products/' + product_id + '/authentication')


@blueprint.route('/<product_id>/ios/production/upload', methods=['POST'])
@login_required
def upload_ios_production_file(product_id):
  #TODO: Handle upload content
  upload_file = request.files['file']
  content = upload_file.read()
  # TODO: Check format?? Or send to cloud server
  noti_key = NotiKey.query.filter_by(product_id=product_id).one_or_none()
  ret = cmds.send_noti_key(product_id, noti_key, content, is_dev=False)
  logging.info("### ret : %s", ret)
  return redirect('products/' + product_id + '/authentication')


@blueprint.route('/<product_id>/admins', methods=['GET', 'POST'])
@login_required
def admins(product_id):
  if request.method == "GET":
    org = Organization.query.filter_by(id=current_user.organization_id).one_or_none()
    owner = json.loads(org.owner)
    member = json.loads(org.member)
    all_users = User.query.filter_by().all()
    return render_template('prd_admins.html', owner=owner, member=member, all_users=all_users)
  else:
    new_member_email = request.form['newMemberEmail']
    #TODO: Send email
    user = User.query.filter_by(email=new_member_email).one_or_none()
    if user:
      org = Organization.query.filter_by(id=current_user.organization_id).one_or_none()
      user.organization_id = org.id
      member = json.loads(org.member)
      member.append(new_member_email)
      org.member = json.dumps(member)
      db.session.commit()
    logging.info("%s", new_member_email)
    return redirect('products/' + product_id + '/admins')


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
