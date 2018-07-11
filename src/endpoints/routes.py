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

from flask import abort, render_template, redirect, request, Response
from flask_login import login_required
from markupsafe import Markup

from endpoints import blueprint

MOCK_LIST = ['v1.0.1', 'v0.4.1', 'v0.2.1', 'v0.0.1']
MOCK_GADGET_LIST = ['iPhone', 'Nexus']


def _get_content():
  content = {
      "product": "mibp",
      "requests": [
          {"type": "request",
           "name": "push",
           "id": 1,
           "params": [{"name": "req_id",
                       "type": "uint8_t",
                       "length": 1,
                       "default": 0}],
           "return": [{"name": "result",
                       "type": "uint8_t",
                       "length": 1,
                       "default": 0}],
           "timeout": 3
          },
          {"type": "request",
           "name": "release",
           "id": 2,
           "params": [],
           "return": [{"name": "result",
                       "type": "uint8_t",
                       "length": 1,
                       "default": 0}
                     ],
           "timeout": 3
          }
      ],
      "events": [
          {"type": "event",
           "name": "press",
           "id": 1,
           "values": [{"name": "major",
                       "type": "uint8_t",
                       "length": 1,
                       "default": 0},
                      {"name": "minor",
                       "type": "uint8_t",
                       "length": 1,
                       "default": 0},
                      {"name": "build",
                       "type": "uint8_t",
                       "length": 1,
                       "default": 0}]
          }
      ]
  }
  return content


@blueprint.route('/<product_id>/specifications', methods=['GET', 'POST'])
@login_required
def specifications(product_id):
  # TODO: Upload
  content = _get_content()
  if request.method == "GET":
    selected = MOCK_LIST[0] if MOCK_LIST else None
    return render_template('ep_specifications.html', version_list=MOCK_LIST,
                           selected=selected, content=content)
  else:
    version = request.form['version']
    logging.info("%s", version)
    return render_template('ep_specifications.html', version_list=MOCK_LIST,
                           selected=version, content=content)


@blueprint.route('/<product_id>/tests', methods=['GET', 'POST'])
@login_required
def tests(product_id):
  # TODO: Test
  content = _get_content()
  if request.method == "GET":
    selected = MOCK_LIST[0] if MOCK_LIST else None
    gadget = MOCK_GADGET_LIST[0] if MOCK_GADGET_LIST else None
    return render_template('ep_tests.html', version_list=MOCK_LIST,
                           gadget_list=MOCK_GADGET_LIST, gadget=gadget,
                           selected=selected, content=content)
  else:
    version = request.form['version']
    gadget = request.form['gadget']
    logging.info("%s, %s", version, gadget)
    return render_template('ep_tests.html', version_list=MOCK_LIST,
                           gadget_list=MOCK_GADGET_LIST, gadget=gadget,
                           selected=version, content=content)


@blueprint.route('/<product_id>/upload', methods=['POST'])
@login_required
def upload_header_file(product_id):
  #TODO: Handle upload content
  upload_file = request.files['file']
  content = upload_file.read()
  # TODO: Check format?? Or send to cloud server
  logging.info("Upload file content : %s", content)
  return redirect('endpoints/' + product_id + '/specifications')


@blueprint.route('/<product_id>/download', methods=['GET'])
@login_required
def download_header_file(product_id):
  #TODO: Handle download content
  content = '{"name": "micorobot"}'
  return Response(content, mimetype='text/x-c',
                  headers={'Content-Disposition':'attachment;filename=mib.h'})