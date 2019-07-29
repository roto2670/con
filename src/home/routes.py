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


from flask import render_template  # noqa : pylint: disable=import-error

import util
from home import blueprint


@blueprint.route('/<product_id>')
@util.require_login
def product_index(product_id):
  return render_template('index.html')


@blueprint.route('/<template>')
@util.require_login
def route_template(template):
  return render_template(template + '.html')
