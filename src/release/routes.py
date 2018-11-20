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

from flask import render_template, redirect  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import base
import util
import in_apis
from release import blueprint


def _is_allow_release(stage):
  # noti
  noti_key = in_apis.get_noti_key_list(current_user.organization_id)
  if not noti_key:
    logging.warning("Can not find noti key.")
    return False
  if not stage.stage_info_list:
    logging.warning("Can not find stage info.")
    return False
  for stage_info in stage.stage_info_list:
    #endpoint
    if not stage_info.endpoint_id:
      logging.warning("Can not find endpoint")
      return False
    # model
    if not stage_info.model_id:
      logging.warning("Can not find model")
      return False
    # firmware
    if not stage_info.firmware_id:
      logging.warning("Can not find firmware")
      return False
  return True


def _build_release_info(stage_info):
  _product = in_apis.get_product(stage_info.product_id)
  stage_info.product = _product
  for _info in stage_info.stage_info_list:
    _endpoint = in_apis.get_specifications(_info.endpoint_id)
    _model = in_apis.get_model(_info.model_id)
    _firmware = in_apis.get_firmware(_info.firmware_id)
    _info.endpoint = _endpoint
    _info.model = _model
    _info.firmware = _firmware
  return stage_info


def _build_history_info(product_id, history_list):
  _product = in_apis.get_product(product_id)
  for _info in history_list:
    _info.product = _product
    _endpoint = in_apis.get_specifications(_info.endpoint_id)
    _model = in_apis.get_model(_info.model_id)
    _firmware = in_apis.get_firmware(_info.firmware_id)
    _info.endpoint = _endpoint
    _info.model = _model
    _info.firmware = _firmware
  return history_list


@blueprint.route('/<product_id>/list', methods=['GET'])
@util.require_login
def get_list(product_id):
  _set_product(product_id)
  dev_stage = None
  pre_stage = None
  release_stage = None
  _dev = in_apis.get_product_stage_by_dev(product_id)
  allow_pre_release = False
  if _dev:
    allow_pre_release = _is_allow_release(_dev)
    dev_stage = _build_release_info(_dev)
  _release = in_apis.get_product_stage_by_release(product_id)
  if _release:
    release_stage = _build_release_info(_release)
  _pre_release = in_apis.get_product_stage_by_pre_release(product_id)
  allow_release = False
  if _pre_release:
    allow_release = _is_allow_release(_pre_release)
    pre_stage = _build_release_info(_pre_release)
  _history_list = in_apis.get_history_list(product_id)
  history_list = _build_history_info(product_id, _history_list)
  return render_template('release_list.html', release_stage=release_stage,
                         dev_stage=dev_stage, pre_stage=pre_stage,
                         history_list=history_list, allow_pre_release=allow_pre_release,
                         allow_release=allow_release)


@blueprint.route('/<product_id>/pre_release', methods=['POST'])
@util.require_login
def pre_release(product_id):
  ret = in_apis.pre_release(product_id)
  logging.info("%s Pre Release ret : %s", product_id, ret)
  return redirect("/release/" + product_id + "/list")


@blueprint.route('/<product_id>/release', methods=['POST'])
@util.require_login
def release(product_id):
  ret = in_apis.release(product_id)
  logging.info("%s Release ret : %s", product_id, ret)
  return redirect("/release/" + product_id + "/list")


def _set_product(product_id):
  product = in_apis.get_product(product_id)
  base.routes.set_current_product(product)
