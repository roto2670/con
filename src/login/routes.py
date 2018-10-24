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

import datetime

from flask import current_app, redirect, render_template, request, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import util
import in_apis
from base import db
from login import blueprint


@blueprint.route('/login', methods={'GET', 'POST'})
def login():
  if not current_user.is_authenticated:
    return current_app.extensions['firebase_auth'].login()
  else:
    user = in_apis.get_user(current_user.id)
    user.last_access_time = in_apis.get_datetime()
    user.ip_address = request.headers.get('X-Real-IP', util.get_ip_addr(request))
    db.session.commit()
    if not current_user.organization_id:
      return redirect(url_for('organization_blueprint.create'))
    else:
      return redirect(url_for('home_blueprint.index'))


@blueprint.route('/sign-in', methods={'POST'})
def sign_in():
  return current_app.extensions['firebase_auth'].sign_in()


@blueprint.route('/sign-out')
def sign_out():
  return current_app.extensions['firebase_auth'].sign_out()


@blueprint.route('/<template>')
def route_template(template):
  return render_template('login/' + template + '.html')
