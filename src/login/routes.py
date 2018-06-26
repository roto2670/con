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

from flask import current_app, redirect, render_template, url_for
from flask_login import current_user

from login import blueprint


@blueprint.route('/login', methods={'GET', 'POST'})
def login():
  if not current_user.is_authenticated:
    return current_app.extensions['firebase_auth'].login()
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
