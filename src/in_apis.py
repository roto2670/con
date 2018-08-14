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
import uuid
import logging
import datetime

from flask_login import current_user
from sqlalchemy.orm.session import make_transient

import apis
import models
from base import db
from models import Product, ProductStage, Model
from models import Endpoint, NotiKey, Organization, User
from models import Invite, Tester, Firmware, FirmwareStage


# {{{ Product


def create_product(product_name, product_obj):
  # product_obj : response from microbot cloud
  product = Product(id=product_obj['id'],
                    code=product_obj['id'],
                    developer_id=product_obj['developer_id'],
                    key=product_obj['key'],
                    name=product_name,
                    created_time=datetime.datetime.utcnow(),
                    last_updated_time=datetime.datetime.utcnow(),
                    organization_id=product_obj['developer_id'])
  db.session.add(product)
  db.session.commit()
  product_stage = ProductStage(id=uuid.uuid4().hex,
                               hook_url=product_obj['hook_url'],
                               hook_client_key=product_obj['hook_client_key'],
                               stage=models.STAGE_DEV,
                               created_time=datetime.datetime.utcnow(),
                               last_updated_time=datetime.datetime.utcnow(),
                               product_id=product.id)
  db.session.add(product_stage)
  db.session.commit()
  return product


def get_product(product_id):
  product = Product.query.filter_by(id=product_id).one_or_none()
  return product


def get_product_list(developer_id):
  product_list = Product.query.filter_by(developer_id=developer_id).all()
  return product_list


def get_product_stage_by_dev(product_id):
  product_stage = ProductStage.query.filter_by(product_id=product_id,
                                               stage=models.STAGE_DEV).\
      one_or_none()
  return product_stage


def get_product_stage_by_release(product_id):
  product_stage = ProductStage.query.filter_by(product_id=product_id,
                                               stage=models.STAGE_RELEASE).\
      one_or_none()
  return product_stage


def get_product_stage_by_pre_release(product_id):
  product_stage = ProductStage.query.filter_by(product_id=product_id,
                                               stage=models.STAGE_PRE_RELEASE).\
      one_or_none()
  return product_stage


def get_product_stage_by_archive(product_id):
  product_stage = ProductStage.query.filter_by(product_id=product_id,
                                               stage=models.STAGE_ARCHIVE).\
      all()
  return product_stage


def create_model(model_name, model_code, product_stage_id, user_email):
  model = Model(id=uuid.uuid4().hex,
                code=model_code,
                name=model_name,
                created_time=datetime.datetime.utcnow(),
                last_updated_time=datetime.datetime.utcnow(),
                last_updated_user=user_email,
                product_stage_id=product_stage_id)
  db.session.add(model)
  db.session.commit()


def get_model(id):
  model = Model.query.filter_by(id=id).one_or_none()
  return model


def get_model_by_code(code, product_id):
  dev_stage = get_product_stage_by_dev(product_id)
  model = Model.query.filter_by(code=code, product_stage_id=dev_stage.id).one_or_none()
  return model


def get_model_list(product_id):
  dev_stage = get_product_stage_by_dev(product_id)
  model = Model.query.filter_by(product_stage_id=dev_stage.id).all()
  return model


# }}}


# {{{  Organization


def get_organization(organization_id):
  org = Organization.query.filter_by(id=organization_id).one_or_none()
  return org


def get_organization_by_name(name):
  org = Organization.query.filter_by(name=name.lower()).one_or_none()
  return org


# }}}


# {{{ User


def get_user(user_id):
  user = User.query.filter_by(id=user_id).one_or_none()
  return user


def get_user_by_email(email):
  user = User.query.filter_by(email=email).one_or_none()
  return user


def get_user_list(organization_id):
  user_list = User.query.filter_by(organization_id=organization_id).all()
  return user_list


# }}}


# {{{ NotiKey


def _create_noti_key(noti_key):
  db.session.add(noti_key)
  db.session.commit()


def create_ios_noti_key(name, key, state):
  # name = bundle_id, key = password
  noti_key = NotiKey(typ=models.IOS,
                     name=name,
                     key=key,
                     is_dev=state,
                     created_time=datetime.datetime.utcnow(),
                     last_updated_time=datetime.datetime.utcnow(),
                     last_updated_user=current_user.email,
                     organization_id=current_user.organization_id)
  _create_noti_key(noti_key)


def create_android_noti_key(name, key):
  # name = package_name, key = key
  noti_key = NotiKey(typ=models.ANDROID,
                     name=name,
                     key=key,
                     created_time=datetime.datetime.utcnow(),
                     last_updated_time=datetime.datetime.utcnow(),
                     last_updated_user=current_user.email,
                     organization_id=current_user.organization_id)
  _create_noti_key(noti_key)


def get_noti_key_list(organization_id):
  noti_key = NotiKey.query.filter_by(organization_id=organization_id).all()
  return noti_key


# {{{ specifications


def create_specifications(version, specifications, user_email, organization_id,
                          product_stage_id):
  specification = Endpoint(id=uuid.uuid4().hex,
                           version=version,
                           specifications=specifications,
                           created_time=datetime.datetime.utcnow(),
                           last_updated_time=datetime.datetime.utcnow(),
                           last_updated_user=user_email,
                           organization_id=organization_id,
                           product_stage_id=product_stage_id)
  db.session.add(specification)
  db.session.commit()


def update_specifications(id, user_email, specifications):
  specification = get_specifications(id)
  specification.last_updated_time = datetime.datetime.utcnow()
  specification.last_updated_user = user_email
  specification.specifications = specifications
  db.session.commit()


def get_specifications(id):
  specifications = Endpoint.query.filter_by(id=id).one_or_none()
  return specifications


def get_specifications_list(product_id):
  specifications_list = Endpoint.query.filter_by(product_id=product_id).all()
  return specifications_list


# }}}


# {{{ invite


def create_invite(email_addr, key, user_email, organization_id, level=None,
                  product_id=None):
  invite = Invite(id=uuid.uuid4().hex,
                  email=email_addr,
                  organization_id=organization_id,
                  product_id=product_id if product_id else "",
                  key=key,
                  level=level if level else models.MEMBER,
                  invited_time=datetime.datetime.utcnow(),
                  invited_user=user_email,
                  accepted=0)
  db.session.add(invite)
  db.session.commit()


def get_invite(key, organization_id):
  invite = Invite.query.filter_by(key=key, organization_id=organization_id).\
      one_or_none()
  return invite


def get_invite_by_email(email):
  invite = Invite.query.filter_by(email=email).one_or_none()
  return invite


def get_invite_list(organization_id):
  invite_list = Invite.query.filter_by(organization_id=organization_id).all()
  return invite_list


def get_invite_list_by_tester(product_id, organization_id):
  invite_list = Invite.query.filter_by(level=models.TESTER, product_id=product_id,
                                       organization_id=organization_id).all()
  return invite_list


def update_invite(key, organization_id):
  invite = get_invite(key, organization_id)
  if invite:
    invite.accepted = 1
    invite.accepted_time = datetime.datetime.utcnow()
    db.session.commit()


def delete_invite(invite_id):
  invite = Invite.query.filter_by(id=invite_id).one_or_none()
  #TODO:
  if invite:
    db.session.delete(invite)
    db.session.commit()


# }}}


# {{{ Tester


def create_tester(email, organization_id, product_id, authorized):
  tester = Tester(id=uuid.uuid4().hex,
                  email=email,
                  authorized=authorized,
                  level=models.TESTER,
                  organization_id=organization_id,
                  product_id=product_id)
  db.session.add(tester)
  db.session.commit()


def update_tester_to_authorized(id):
  tester = Tester.query.filter_by(id=id).one_or_none()
  if tester:
    tester.authorized = True
    db.session.commit()


def get_tester(id, product_id):
  tester = Tester.query.filter_by(id=id, product_id=product_id).one_or_none()
  return tester


def get_tester_by_email(email_addr, product_id):
  tester = Tester.query.filter_by(email=email_addr, product_id=product_id).one_or_none()
  return tester


def get_tester_list(product_id, organization_id):
  tester_list = Tester.query.filter_by(product_id=product_id,
                                       organization_id=organization_id).all()
  return tester_list


def delete_tester(id):
  tester = Tester.query.filter_by(id=id).one_or_none()
  if tester:
    db.session.delete(tester)
    db.session.commit()


# }}}


# {{{ Firmware


def create_firmware(version, user_email, url_path, model_id):
  firmware = Firmware(id=uuid.uuid4().hex,
                      version=version,
                      path=url_path,
                      created_time=datetime.datetime.utcnow(),
                      last_updated_time=datetime.datetime.utcnow(),
                      last_updated_user=user_email,
                      model_id=model_id)
  db.session.add(firmware)
  db.session.commit()
  return firmware


def create_firmware_stage(firmware_id, version, stage):
  firmware_stage = FirmwareStage(id=uuid.uuid4().hex,
                                 version=version,
                                 stage=stage,
                                 last_updated_time=datetime.datetime.utcnow(),
                                 firmware_id=firmware_id)
  db.session.add(firmware_stage)
  db.session.commit()
  return firmware_stage


def get_firmware_stage(id):
  firmware_stage = FirmwareStage.query.filter_by(id=id).one_or_none()
  return firmware_stage


# }}}


#{{{  Handle release


def _delete_before_pre_release(product_id):
  _pre_release = get_product_stage_by_pre_release(product_id)
  if pre_release:
    db.session.delete(_pre_release)
    db.session.commit()


def pre_release(product_id):
  dev = get_product_stage_by_dev(product_id)
  model_number_list = []
  for model in dev.model_list:
    model_number_list.append(model.code)
  prd_ret = apis.update_product_stage(product_id, dev, model_number_list,
                                      dev.endpoint.version,
                                      models.STAGE_PRE_RELEASE)
  if prd_ret:
    _delete_before_pre_release(product_id)
    ep = get_specifications(dev.endpoint.id)
    model_list = dev.model_list

    make_transient(dev)
    dev.id = uuid.uuid4().hex
    dev.stage = models.STAGE_PRE_RELEASE
    dev.created_time = datetime.datetime.utcnow()
    dev.last_updated_time = datetime.datetime.utcnow()

    make_transient(ep)
    ep.id = uuid.uuid4().hex
    ep.created_time = datetime.datetime.utcnow()
    ep.last_updated_time = datetime.datetime.utcnow()
    ep.last_updated_user = current_user.email
    ep.product_stage_id = dev.id

    for model in model_list:
      firmware_list = model.firmware_list
      make_transient(model)
      model.id = uuid.uuid4().hex
      model.created_time = datetime.datetime.utcnow()
      model.last_updated_time = datetime.datetime.utcnow()
      model.last_updated_user = current_user.email
      model.product_stage_id = dev.id
      for firmware in firmware_list:
        make_transient(firmware)
        firmware.id = uuid.uuid4().hex
        firmware.created_time = datetime.datetime.utcnow()
        firmware.last_updated_time = datetime.datetime.utcnow()
        firmware.last_updated_user = current_user.email
        firmware.model_id = model.id

        firmware_stage = get_firmware_stage(firmware.firmware_stage.id)
        make_transient(firmware_stage)
        firmware_stage.id = uuid.uuid4().hex
        firmware_stage.last_updated_time = datetime.datetime.utcnow()
        firmware_stage.firmware_id = firmware.id
        db.session.add(firmware_stage)
        db.session.add(firmware)
      db.session.add(model)

    db.session.add(ep)
    db.session.add(dev)
    db.session.commit()
    return True
  else:
    return False


def release(product_id):
  _pre_release = get_product_stage_by_pre_release(product_id)
  model_number_list = []
  for model in _pre_release.model_list:
    model_number_list.append(model.code)
  prd_ret = apis.update_product_stage(product_id, _pre_release,
                                      model_number_list,
                                      _pre_release.endpoint.version,
                                      models.STAGE_RELEASE)
  if prd_ret:
    _release = get_product_stage_by_release(product_id)
    if _release:
      _release.stage = models.STAGE_ARCHIVE
      _release.last_updated_time = datetime.datetime.utcnow()
      db.session.commit()

    _pre_release.stage = models.STAGE_RELEASE
    _pre_release.last_updated_time = datetime.datetime.utcnow()
    db.session.commit()
    return True
  else:
    return False


# }}}
