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

import logging
import urllib.parse

import flask_login
from flask import render_template, request, redirect
from flask_login import login_required
from flask_login import current_user

import products
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
    product = products.api.create_product(request.form['name'],
                                          current_user.developer_id)
    return redirect('products/' + str(product['product_id']) + '/general')


@blueprint.route('/<product_id>/remove', methods=['GET'])
@login_required
def remove(product_id):
  # TODO:
  return redirect('products/management')


@blueprint.route('/<product_id>/general', methods=['GET', 'POST'])
@login_required
def general(product_id):
  if request.method == "GET":
    product = products.api.get_product(product_id, current_user.developer_id)
    base.routes.set_current_product(product)
    return render_template('prd_general.html')
  else:
    prd_name = request.form['prdName']
    prd_key = request.form['prdKey']
    hook_url = request.form['hookUrl']
    logging.info("%s, %s, %s", prd_name, prd_key, hook_url)
    return redirect('products/' + product_id + '/general')


@blueprint.route('/<product_id>/branding', methods=['GET'])
@login_required
def branding(product_id):
  #TODO:
  return render_template('prd_branding.html')


@blueprint.route('/<product_id>/authentication', methods=['GET', 'POST'])
@login_required
def authentication(product_id):
  if request.method == "GET":
    product = products.api.get_product(product_id, current_user.developer_id)
    base.routes.set_current_product(product)
    return render_template('prd_authentication.html')
  else:
    access_token = request.form['accessToken']
    ios_noti_key = request.form['iosNotiKey']
    android_noti_key = request.form['androidNotiKey']
    hook_client_key = request.form['hookClientKey']
    logging.info("%s, %s, %s, %s", access_token, ios_noti_key,
                 android_noti_key, hook_client_key)
    return redirect('products/' + product_id + '/authentication')


@blueprint.route('/<product_id>/admins', methods=['GET', 'POST'])
@login_required
def admins(product_id):
  if request.method == "GET":
    return render_template('prd_admins.html')
  else:
    new_member_email = request.form['newMemberEmail']
    #TODO: Send email
    logging.info("%s", new_member_email)
    return redirect('products/' + product_id + '/admins')


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
