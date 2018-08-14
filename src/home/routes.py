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

from flask import render_template
from flask_login import login_required, current_user

import in_apis
from home import blueprint


@blueprint.route('/index')
@login_required
def index():
  org = in_apis.get_organization(current_user.organization_id)
  return render_template('index.html', users=json.loads(org.users),
                         products=json.loads(org.products))


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
