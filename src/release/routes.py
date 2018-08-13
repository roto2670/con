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

from flask import render_template, redirect
from flask_login import login_required, current_user

import in_apis
import base
from release import blueprint


@blueprint.route('/<product_id>/list', methods=['GET'])
@login_required
def get_list(product_id):
  _set_product(product_id)
  release_list = []
  dev_list = []
  pre_release_list = []
  _dev = in_apis.get_product_stage_by_dev(product_id)
  if _dev:
    dev_list.append(_dev)
  _release = in_apis.get_product_stage_by_release(product_id)
  if _release:
    release_list.append(_release)
  _pre_release = in_apis.get_product_stage_by_pre_release(product_id)
  if _pre_release:
    pre_release_list.append(_pre_release)
  archive_list = in_apis.get_product_stage_by_archive(product_id)
  return render_template('release_list.html', release_list=release_list,
                         dev_list=dev_list, pre_release_list=pre_release_list,
                         archive_list=archive_list)


@blueprint.route('/<product_id>/pre_release', methods=['POST'])
@login_required
def pre_release(product_id):
  ret = in_apis.pre_release(product_id)
  logging.info("%s Pre Release ret : %s", product_id, ret)
  return redirect("/release/" + product_id + "/list")


@blueprint.route('/<product_id>/release', methods=['POST'])
@login_required
def release(product_id):
  ret = in_apis.release(product_id)
  logging.info("%s Release ret : %s", product_id, ret)
  return redirect("/release/" + product_id + "/list")


def _set_product(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
