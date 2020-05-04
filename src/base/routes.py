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
import in_apis
import constants
import in_config_apis
from base import blueprint
from base import db, login_manager
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


def _get_server_time():
  return datetime.datetime.now().replace(microsecond=0)


def about_product():
  return dict(current_product=_get_current_product(),
              product_list=_get_product_list(),
              server_time=_get_server_time())


## Jinja template


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


def datetime_check(value):
  cur_date = datetime.datetime.now()
  new_check_date = value - datetime.timedelta(days=-3)
  return new_check_date > cur_date


def change_us_format(value):
  return value.strftime("%m/%d/%Y  %H:%M:%S")


def change_us_format_for_date(value):
  return value.strftime("%m/%d/%Y")


def during_time(value):
  form = "%Y-%m-%d %H:%M:%S"
  value_time = datetime.datetime.strptime(value, form)
  cur_time = in_config_apis.get_servertime()
  ret = cur_time - value_time
  return ret


def is_dict(value):
  return isinstance(value, dict)


def second_to_time_format(value):
  return str(datetime.timedelta(seconds=value))
