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

import flask_login
from flask import render_template, request, redirect
from flask_login import login_required
from flask_login import current_user

from settings import blueprint


@blueprint.route('/', methods=['GET'])
@login_required
def default_route():
  return render_template("settings.html")


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
