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

import base.routes
from base import db
from products import blueprint
from products.models import Product


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    parse_ret = urllib.parse.urlparse(request.referrer)
    referrer = parse_ret.path if parse_ret else "/"
    return render_template("prd_create.html", referrer=referrer)
  else:
    prd = Product(prdname=request.form['name'],
                  description=request.form['desc'],
                  user_id=current_user.id)
    db.session.add(prd)
    db.session.commit()
    return redirect('products/' + str(prd.id) + '/general')


@blueprint.route('/<product_id>/remove', methods=['GET'])
@login_required
def remove(product_id):
  prd = Product.query.get(product_id)
  db.session.delete(prd)
  db.session.commit()
  return redirect('products/management')


@blueprint.route('/<product_id>/general', methods=['GET', 'POST'])
@login_required
def general(product_id):
  if request.method == "GET":
    prd = Product.query.get(product_id)
    base.routes.set_current_product(prd)
    return render_template('prd_general.html')
  else:
    prd_name = request.form['prdName']
    prd_desc = request.form['prdDesc']
    prd_key = request.form['prdKey']
    hook_url = request.form['hookUrl']
    logging.info("%s, %s, %s, %s", prd_name, prd_desc, prd_key, hook_url)
    return render_template('prd_general.html')


@blueprint.route('/<product_id>/branding', methods=['GET'])
@login_required
def branding(product_id):
  return render_template('prd_branding.html')


@blueprint.route('/<product_id>/authentication', methods=['GET', 'POST'])
@login_required
def authentication(product_id):
  if request.method == "GET":
    prd = Product.query.get(product_id)
    base.routes.set_current_product(prd)
    return render_template('prd_authentication.html')
  else:
    access_token = request.form['accessToken']
    ios_noti_key = request.form['iosNotiKey']
    android_noti_key = request.form['androidNotiKey']
    logging.info("%s, %s, %s", access_token, ios_noti_key, android_noti_key)
    return render_template('prd_authentication.html')


@blueprint.route('/<product_id>/admins', methods=['GET', 'POST'])
@login_required
def admins(product_id):
  if request.method == "GET":
    return render_template('prd_admins.html')
  else:
    new_member_email = request.form['newMemberEmail']
    #TODO: Send email
    logging.info("%s", new_member_email)
    return render_template('prd_admins.html')


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
