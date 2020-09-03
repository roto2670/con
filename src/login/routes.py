# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|

import logging

from bcrypt import checkpw
from flask import current_app, redirect, render_template, request, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user, login_user, logout_user  # noqa : pylint: disable=import-error

import util
import models
import in_apis
import constants
from base import db
from login import blueprint


SK_LOGO_URI = '''/static/images/logo-login_page.png'''


@blueprint.route('/login', methods={'GET'})
def login():
  if not current_user.is_authenticated:
    _is_error = request.args.get('error')
    is_error = True if _is_error == "true" else False
    return render_template('new_login.html', logo_uri=SK_LOGO_URI,
                           is_error=is_error)
  else:
    user = in_apis.get_user(current_user.id)
    user.last_access_time = in_apis.get_servertime()
    user.ip_address = util.get_ip_addr()
    db.session.commit()
    if current_user.email_verified:
      if not current_user.organization_id:
        return redirect(url_for('management_blueprint.create'))
      else:
        if current_user.level == models.MOI:
          return redirect(url_for('moi_blueprint.route_default'))
        elif current_user.level == models.COVID19_ADMIN or \
            current_user.level == models.COVID19_TEAMDOCTOR:
          return redirect(url_for('covid19_blueprint.route_default'))
        else:
          return redirect(url_for('dashboard_blueprint.default_route'))
    else:
      return redirect(url_for('base_blueprint.route_verified'))


@blueprint.route('/login/signin', methods=['POST'])
def sign_in_progress():
  email = request.form.get('email')
  password = request.form.get('password')
  user = in_apis.get_user_by_email(email, constants.ORG_ID)
  if user and user.password and checkpw(password.encode('utf-8'), user.password):
    in_apis.update_user_by_ip(user.id, util.get_ip_addr())
    login_user(user, remember=False)
    if user.level == models.MOI:
      logging.info("MOI User login. User : %s", user)
      # TODO:
      #return redirect(url_for('moi_blueprint.route_default'))
      return "<script>window.location.href = '/moi/'; </script>"
    elif user.level == models.COVID19_ADMIN or \
        user.level == models.COVID19_TEAMDOCTOR:
      # return redirect(url_for('covid19_blueprint.route_default'))
      return "<script>window.location.href = '/covid19/'; </script>"
    else:
      logging.info("SmartSystem User login. User : %s", user)
      # TODO:
      # return redirect(url_for('dashboard_blueprint.default_route'))
      return "<script>window.location.href = '/dashboard/'; </script>"
  # TODO:
  # elif user:
  #   login_user(user)
  #   return redirect(url_for('base_blueprint.route_default'))
  else:
    return redirect("/auth/login?error=true")


@blueprint.route('/sign-out')
def sign_out():
  logout_user()
  return redirect(url_for('login_blueprint.login'))


@blueprint.route('/<template>')
def route_template(template):
  return render_template('login/' + template + '.html')
