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
import uuid
import datetime
import logging

from flask import render_template, redirect, request, url_for
from flask import send_from_directory
from flask_login import current_user, login_required, login_user, logout_user

import in_apis
from base import blueprint
from base import db, login_manager, auth
from models import User, Permission


BASE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'doc')


@blueprint.route('/')
def route_default():
  return redirect(url_for('login_blueprint.login'))


@blueprint.route('/doc')
def route_doc():
  return render_template('doc.html')


@blueprint.route('/file/<file_name>')
def route_file(file_name):
  return send_from_directory(directory=BASE, filename=file_name)


@blueprint.route('/welcome')
def welcome():
  # TODO : Tester
  return render_template('welcome.html')


@blueprint.route('/nowelcome')
def welcome_no_ftl():
  # TODO : Tester
  return render_template('welcome_noftl.html')


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')


@blueprint.route('/fixed_<template>')
@login_required
def route_fixed_template(template):
  return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
  return render_template('errors/page_{}.html'.format(error))


## Login & Registration


"""
email auth token
{'iss': 'https://securetoken.google.com/console-4196c', 'name': 'jslee',
 'aud': 'console-4196c', 'auth_time': 1528782910,
 'user_id': 'HObbPOyiSchoV6uOtVOIiCphD883',
 'sub': 'HObbPOyiSchoV6uOtVOIiCphD883', 'iat': 1528782910, 'exp': 1528786510,
 'email': 'jslee@thenaran.com', 'email_verified': False,
 'firebase': {'identities': {'email': ['jslee@thenaran.com']},
              'sign_in_provider': 'password'}
}

google
{'iss': 'https://securetoken.google.com/console-4196c', 'name': 'Jaeseung Lee',
 'picture': 'https://lh6.googleusercontent.com/-PSY5qMeC5vk/AAAAAAAAAAI/AAAAAAAAAAA/AB6qoq1vsG8shcIE6VuINH_SEVmU0eJTrg/mo/photo.jpg',
 'aud': 'console-4196c', 'auth_time': 1528792232,
 'user_id': 'XtxGnNysQXSg0zzDgJJpD1BRR172', 'sub': 'XtxGnNysQXSg0zzDgJJpD1BRR172',
 'iat': 1528792232, 'exp': 1528795832, 'email': 'jslee@narantech.com',
 'email_verified': True,
 'firebase': {'identities': {'google.com': ['107405048989999876505'],
                             'email': ['jslee@narantech.com']},
              'sign_in_provider': 'google.com'}
}
"""

DEFAULT_PHOTO_URL = '''/static/images/user.png'''


@auth.production_loader
def production_sign_in(token):
  # https://firebase.google.com/docs/auth/admin/verify-id-tokens?hl=ko
  user = User.query.filter_by(id=token['sub']).one_or_none()
  if not user:
    user = User(id=token['sub'],
                firebase_user_id=token['sub'])
    db.session.add(user)
  user.name = token.get('name')
  user.email = token['email']
  user.email_verified = token['email_verified']
  user.sign_in_provider = token['firebase']['sign_in_provider']
  user.photo_url = token.get('picture', DEFAULT_PHOTO_URL)
  user.created_time = datetime.datetime.utcnow()
  user.last_access_time = datetime.datetime.utcnow()
  user.ip_address = request.remote_addr
  invite = in_apis.get_invite_by_email(token['email'])
  if invite:
    user.organization_id = invite.organization_id
  db.session.commit()
  permission = Permission(id=uuid.uuid4().hex,
                          permission='777',
                          user_id=user.id)
  db.session.add(permission)
  db.session.commit()
  login_user(user)
  return redirect(url_for('base_blueprint.route_default'))


@auth.unloader
def logout():
  logout_user()
  return redirect(url_for('login_blueprint.login'))


@blueprint.route('/shutdown')
def shutdown():
  func = request.environ.get('werkzeug.server.shutdown')
  if func is None:
    raise RuntimeError('Not running with the Werkzeug Server')
  func()
  return 'Server shutting down...'


## Errors


@login_manager.unauthorized_handler
def unauthorized_handler():
  return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
  return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
  return render_template('errors/page_404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
  return render_template('errors/page_500.html'), 500


## context processor


CUR_PRODUCT = {}  # {user_id : CUR_PRODUCT}


def _get_product_list():
  if current_user and current_user.is_authenticated:
    product_list = in_apis.get_product_list(current_user.organization_id)
    if current_user.id not in CUR_PRODUCT and product_list:
      set_current_product(product_list[-1])
    return product_list
  else:
    return []


def set_current_product(cur_product):
  if current_user and current_user.is_authenticated:
    CUR_PRODUCT[current_user.id] = cur_product


def _get_current_product():
  if current_user and current_user.is_authenticated:
    if current_user.id in CUR_PRODUCT:
      return CUR_PRODUCT[current_user.id]
    else:
      return None
  else:
    return None


def about_product():
  return dict(current_product=_get_current_product(),
              product_list=_get_product_list())
