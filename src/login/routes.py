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


from flask import current_app, redirect, render_template, request, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import util
import in_apis
from base import db
from login import blueprint


@blueprint.route('/login', methods={'GET', 'POST'})
def login():
  if not current_user.is_authenticated:
    referrer = request.args['ref'] if 'ref' in request.args else None
    return current_app.extensions['firebase_auth'].login(referrer=referrer)
  else:
    user = in_apis.get_user(current_user.id)
    user.last_access_time = in_apis.get_datetime()
    user.ip_address = util.get_ip_addr()
    db.session.commit()
    if current_user.email_verified:
      if not current_user.organization_id:
        return redirect(url_for('organization_blueprint.create'))
      else:
        return redirect(url_for('home_blueprint.index'))
    else:
      return redirect(url_for('base_blueprint.route_verified'))


@blueprint.route('/sign-in', methods={'POST'})
def sign_in():
  return current_app.extensions['firebase_auth'].sign_in()


@blueprint.route('/sign-out')
def sign_out():
  return current_app.extensions['firebase_auth'].sign_out()


@blueprint.route('/<template>')
def route_template(template):
  return render_template('login/' + template + '.html')
