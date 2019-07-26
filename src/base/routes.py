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

import os
import json
import time
import uuid
import logging
import datetime

import pytz
from country_list import countries_for_language
from flask import send_from_directory  # noqa : pylint: disable=import-error
from flask import render_template, redirect, request, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user, login_user, logout_user  # noqa : pylint: disable=import-error

import apis
import util
import common
import models
import worker
import in_apis
import constants
import in_config_apis
from base import blueprint
from base import db, login_manager, auth
from models import _User as User
from models import _Permission as Permission


@blueprint.route('/')
def route_default():
  return redirect(url_for('login_blueprint.login'))


@blueprint.route('/robots.txt')
def route_robots():
  path = util.get_static_path()
  return send_from_directory(path, 'robots.txt')


@blueprint.route('/verified')
def route_verified():
  if current_user.is_anonymous:
    return redirect(url_for('login_blueprint.login'))
  elif current_user.email_verified:
    return redirect(url_for('login_blueprint.login'))
  else:
    return render_template('confirm_wait.html', user_email=current_user.email)


def _is_confirm(email_auth):
  if email_auth.user_id != current_user.id:
    logging.warning("Invalid user id. Cur ID : %s, Email user ID : %s",
                    current_user.id, email_auth.user_id)
    return False
  _time = in_apis.get_datetime().utcnow() - email_auth.sent_time
  if _time.seconds > 300: # 5 minute
    logging.warning("Time is expire. User ID : %s, time : %s",
                    email_auth.user_id, _time)
    return False
  return True


@blueprint.route('/verified/confirm')
def confirm_verified_email():
  key = request.args['key']
  if current_user.is_anonymous:
    return redirect("/auth/login?ref=" + "/verified/confirm?key=" + key)

  email_auth = in_apis.get_auth_by_key(key)
  if not email_auth:
    logging.warning("Can not find email auth. current user : %s, key : %s",
                    current_user.email, key)
    return render_template('wrong_mail_confirm.html')

  if email_auth.email != current_user.email:
    logout_user()
    return redirect("/auth/login?ref=" + "/verified/confirm?key=" + key)

  if _is_confirm(email_auth):
    in_apis.update_user_by_confirm(current_user.id)
    in_apis.update_email_auth(email_auth.id)
    return redirect(url_for('login_blueprint.login'))
  else:
    logging.warning("Email Auth Failed. current user : %s, key : %s",
                    current_user.email, key)
    if email_auth:
      in_apis.remove_email_auth(email_auth.id)
    return redirect(url_for('base_blueprint.route_verified'))


@blueprint.route('/welcome')
def welcome():
  msg = {
      "title": common.get_msg("products.tester.tester_success_title"),
      "message": common.get_msg("products.tester.tester_success_message")
  }
  return render_template('welcome.html', msg=msg)


@blueprint.route('/nowelcome')
def welcome_no_ftl():
  msg = {
      "title": common.get_msg("products.tester.tester_need_to_ftl_title"),
      "message": common.get_msg("products.tester.tester_need_to_ftl_message")
  }
  return render_template('welcome_noftl.html', msg=msg)


@blueprint.route('/fixed_<template>')
@util.require_login
def route_fixed_template(template):
  return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
  return render_template('errors/page_{}.html'.format(error))


## Login & Registration


DEFAULT_PHOTO_URL = '''/static/images/user.png'''

@auth.production_loader
def production_sign_in(token):
  # https://firebase.google.com/docs/auth/admin/verify-id-tokens?hl=ko
  user = User.query.filter_by(id=token['sub']).one_or_none()
  if not user:
    user = User(id=token['sub'],
                firebase_user_id=token['sub'])
    user.name = token['name'] if 'name' in token else token['email']
    user.email = token['email']
    user.email_verified = user.email_verified if user.email_verified else token['email_verified']
    user.sign_in_provider = token['firebase']['sign_in_provider']
    user.photo_url = token.get('picture', DEFAULT_PHOTO_URL)
    user.created_time = in_apis.get_datetime()
    user.level = models.MEMBER
    db.session.add(user)
  user.last_access_time = in_apis.get_datetime()
  user.ip_address = util.get_ip_addr()
  invite = in_apis.get_invite_by_email(token['email'])
  user.organization_id = constants.ORG_ID
  db.session.commit()
  if not user.permission:
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


@blueprint.app_errorhandler(400)
def bad_request(error):
  return render_template('errors/page_400.html'), 400


@blueprint.app_errorhandler(403)
def access_forbidden(error):
  return render_template('errors/page_403.html'), 403


@blueprint.app_errorhandler(404)
def not_found_error(error):
  return render_template('errors/page_404.html'), 404


@blueprint.app_errorhandler(500)
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


def get_current_product(user_id):
  if user_id in CUR_PRODUCT:
    return CUR_PRODUCT[user_id]
  else:
    return None


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


## Jinja template


CUR_TIMEZONE = {}  # {user_id : {'code': code, 'tz': timezone, 'last_access': timestamp}}


def set_timezone(ip_addr):
  if ip_addr != "127.0.0.1":
    ipinfo = worker.get_timezone(ip_addr)
    if 'country' in ipinfo:
      country_code = ipinfo['country']
      _tz = pytz.country_timezones[country_code]
      if _tz:
        CUR_TIMEZONE[current_user.id] = {'tz': _tz[0], 'code': country_code,
                                         'last_access' : time.time()}
        logging.info("%s user set timezone : %s", current_user.email, _tz)


def get_timezone():
  if current_user.id not in CUR_TIMEZONE:
    set_timezone(util.get_ip_addr())
  elif (time.time() - CUR_TIMEZONE[current_user.id]['last_access']) > 7200:
    set_timezone(util.get_ip_addr())
  if current_user.id in CUR_TIMEZONE and 'tz' in CUR_TIMEZONE[current_user.id]:
    return CUR_TIMEZONE[current_user.id]['tz']
  else:
    return 'UTC'


def datetime_filter(value):
  tz_info = get_timezone()
  _value = pytz.timezone(tz_info).localize(value)
  _timestamp = time.mktime(_value.timetuple())
  _timestamp += _value.utcoffset().seconds
  _new_time = datetime.datetime.fromtimestamp(_timestamp)
  return _new_time


def timestamp_filter(value):
  tz_info = get_timezone()
  _value = pytz.timezone(tz_info).localize(datetime.datetime.utcfromtimestamp(value))
  _timestamp = int(value)
  _timestamp += _value.utcoffset().seconds
  _new_time = datetime.datetime.fromtimestamp(_timestamp)
  return _new_time


COUNTRY_CODES = {}  # {"code": "name", ..}

def get_country_name(code):
  if not COUNTRY_CODES:
    for _code, _name in countries_for_language('en'):
      COUNTRY_CODES[_code] = _name
  if code.upper() in COUNTRY_CODES:
    return COUNTRY_CODES[code.upper()] + " ({})".format(code.upper())
  else:
    return code.upper()


def get_log_id(value):
  return str(value).replace(".", "")
