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
import logging

from flask import current_app, redirect, render_template, url_for
from flask_login import current_user

import apis
from base import db
from login import blueprint
from models import User


@blueprint.route('/login', methods={'GET', 'POST'})
def login():
  if not current_user.is_authenticated:
    return current_app.extensions['firebase_auth'].login()
  elif not current_user.authorized:
    user_info = apis.get_user(current_user.email)
    logging.info("## user info : %s", user_info)
    if user_info['user'] and user_info['user']['authorized']:
      user = User.query.filter_by(id=current_user.id).one_or_none()
      user.language = user_info['user']['language']
      user.authorized = user_info['user']['authorized']
      user.account_ids = json.dumps(user_info['user']['account_ids'])
      db.session.commit()
      return redirect(url_for('home_blueprint.index'))
    else:
      # TODO: not ftl handle
      return redirect(url_for('base_blueprint.route_welcome'))
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
