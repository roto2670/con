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

from flask import render_template, request
from flask_login import login_required

from endpoints import blueprint

MOCK_LIST = ['v1.0.1', 'v0.4.1', 'v0.2.1', 'v0.0.1']
MOCK_GADGET_LIST = ['iPhone', 'Nexus']


@blueprint.route('/<product_id>/specifications', methods=['GET', 'POST'])
@login_required
def specifications(product_id):
  # TODO: Upload
  if request.method == "GET":
    selected = MOCK_LIST[0] if MOCK_LIST else None
    return render_template('ep_specifications.html', version_list=MOCK_LIST,
                           selected=selected)
  else:
    version = request.form['version']
    logging.info("%s", version)
    return render_template('ep_specifications.html', version_list=MOCK_LIST,
                           selected=version)


@blueprint.route('/<product_id>/tests', methods=['GET', 'POST'])
@login_required
def tests(product_id):
  # TODO: Test
  if request.method == "GET":
    selected = MOCK_LIST[0] if MOCK_LIST else None
    gadget = MOCK_GADGET_LIST[0] if MOCK_GADGET_LIST else None
    return render_template('ep_tests.html', version_list=MOCK_LIST,
                           gadget_list=MOCK_GADGET_LIST, gadget=gadget,
                           selected=selected)
  else:
    version = request.form['version']
    gadget = request.form['gadget']
    logging.info("%s, %s", version, gadget)
    return render_template('ep_tests.html', version_list=MOCK_LIST,
                           gadget_list=MOCK_GADGET_LIST, gadget=gadget,
                           selected=version)
