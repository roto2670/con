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

import pytz
from flask_login import current_user  # noqa : pylint: disable=import-error
from sqlalchemy.orm.session import make_transient  # noqa : pylint: disable=import-error
from sqlalchemy import desc

import apis
import mail
import models
from base import db
from models import _Product as Product
from models import _ProductStage as ProductStage
from models import _StageInfo as StageInfo
from models import _Model as Model
from models import _Endpoint as Endpoint
from models import _NotiKey as NotiKey
from models import _Organization as Organization
from models import _User as User
from models import _Invite as Invite
from models import _Tester as Tester
from models import _Firmware as Firmware
from models import _History as History
from models import _EmailAuth as EmailAuth
from models import _ReferrerInfo as ReferrerInfo


def get_datetime():
  return datetime.datetime.now(pytz.timezone('UTC'))


# {{{ Product


def create_product(product_name, product_obj, product_type):
  # product_obj : response from microbot cloud
  product = Product(id=product_obj['id'],
                    code=product_obj['id'],
                    developer_id=product_obj['developer_id'],
                    key=product_obj['key'],
                    name=product_name,
                    typ=product_type,
                    created_time=get_datetime(),
                    last_updated_time=get_datetime(),
                    organization_id=product_obj['developer_id'])
  db.session.add(product)
  db.session.commit()
  product_stage = ProductStage(id=uuid.uuid4().hex,
                               hook_url="",
                               hook_client_key="",
                               stage=models.STAGE_DEV,
                               created_time=get_datetime(),
                               last_updated_time=get_datetime(),
                               last_updated_user=current_user.email,
                               product_id=product.id)
  db.session.add(product_stage)
  db.session.commit()
  create_product_stage_by_dev(product.id)
  return product


def get_product(product_id):
  product = Product.query.filter_by(id=product_id).one_or_none()
  return product


def create_product_stage_by_dev(product_id):
  product_stage = ProductStage(id=uuid.uuid4().hex,
                               hook_url="",
                               hook_client_key="",
                               stage=models.DEV_STATE,
                               created_time=get_datetime(),
                               last_updated_time=get_datetime(),
                               last_updated_user=current_user.email,
                               product_id=product_id)
  db.session.add(product_stage)
  db.session.commit()


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


def remove_product_stage(product_stage_id):
  product_stage = ProductStage.query.filter_by(id=product_stage_id).one_or_none()
  if product_stage:
    db.session.delete(product_stage)
    db.session.commit()


def create_stage_info(product_stage_id, model_id):
  stage_info = StageInfo(id=uuid.uuid4().hex,
                         model_id=model_id,
                         endpoint_id="",
                         firmware_id="",
                         created_time=get_datetime(),
                         last_updated_time=get_datetime(),
                         last_updated_user=current_user.email,
                         product_stage_id=product_stage_id)
  db.session.add(stage_info)
  db.session.commit()


def get_dev_stage_info_by_model(model_id, product_stage_id):
  stage_info = StageInfo.query.\
      filter_by(model_id=model_id, product_stage_id=product_stage_id).one_or_none()
  return stage_info


def update_stage_info_by_dev_about_firmware(product_id, model_id, firmware_id):
  dev_stage = get_product_stage_by_dev(product_id)
  stage_info = get_dev_stage_info_by_model(model_id, dev_stage.id)
  if stage_info:
    stage_info.firmware_id = firmware_id
    stage_info.last_updated_time = get_datetime()
    stage_info.last_updated_user = current_user.email
    db.session.commit()


def update_stage_info_by_dev_about_endpoint(product_id, endpoint_id):
  dev_stage = get_product_stage_by_dev(product_id)
  for stage_info in dev_stage.stage_info_list:
    stage_info.endpoint_id = endpoint_id
    stage_info.last_updated_time = get_datetime()
    stage_info.last_updated_user = current_user.email
    db.session.commit()


def get_history_list(product_id):
  history_list = History.query.filter_by(product_id=product_id).\
      order_by(desc(History.created_time)).all()
  return history_list


def delete_product(_id):
  product = get_product(_id)
  if product:
    db.session.delete(product)
    db.session.commit()


def create_model(model_name, model_code, model_type, product_id, user_email):
  model = Model(id=uuid.uuid4().hex,
                code=model_code,
                name=model_name,
                typ=model_type,
                created_time=get_datetime(),
                last_updated_time=get_datetime(),
                last_updated_user=user_email,
                product_id=product_id)
  db.session.add(model)
  db.session.commit()
  dev_stage = get_product_stage_by_dev(product_id)
  create_stage_info(dev_stage.id, model.id)


def get_model(_id):
  model = Model.query.filter_by(id=_id).one_or_none()
  return model


def get_model_by_code(code, product_id):
  model = Model.query.filter_by(code=code, product_id=product_id).one_or_none()
  return model


def get_model_list(product_id):
  model = Model.query.filter_by(product_id=product_id).all()
  return model


def delete_model(_id):
  model = get_model(_id)
  if model:
    db.session.delete(model)
    db.session.commit()


# }}}


# {{{  Organization


def create_organization(owner_email, organization_name, ret):
  # ret -> developer object from cloud server
  org = Organization(id=ret['id'],
                     users=json.dumps([owner_email]),
                     products=json.dumps(ret['products']),
                     tokens=json.dumps(ret['tokens']),
                     kinds=json.dumps(ret['kinds']),
                     name=organization_name.lower(),
                     original_name=organization_name,
                     created_time=get_datetime(),
                     last_updated_time=get_datetime())
  db.session.add(org)
  db.session.commit()
  return org


def get_organization(organization_id):
  org = Organization.query.filter_by(id=organization_id).one_or_none()
  return org


def get_organization_by_name(name):
  org = Organization.query.filter_by(name=name.lower()).one_or_none()
  return org


def delete_organization(organization_id):
  org = Organization.query.filter_by(id=organization_id).one_or_none()
  if org:
    db.session.delete(org)
    db.session.commit()


# }}}


# {{{ User


def get_user(user_id):
  user = User.query.filter_by(id=user_id).one_or_none()
  return user


def get_user_by_email(email, organization_id):
  user = User.query.filter_by(email=email, organization_id=organization_id).one_or_none()
  return user


def get_user_list(organization_id):
  user_list = User.query.filter_by(organization_id=organization_id).all()
  return user_list


def update_user_by_ip(user_id, ip_addr):
  user = User.query.filter_by(id=user_id).one_or_none()
  user.ip_address = ip_addr
  user.last_access_time = get_datetime()
  db.session.commit()


def update_user_by_confirm(user_id):
  user = User.query.filter_by(id=user_id).one_or_none()
  user.email_verified = True
  user.last_access_time = get_datetime()
  db.session.commit()


# }}}


# {{{ NotiKey


def _create_noti_key(noti_key):
  db.session.add(noti_key)
  db.session.commit()


def get_ios_noti_key(organization_id, typ, name, key, is_dev):
  noti_key = NotiKey.query.filter_by(organization_id=organization_id,
                                     typ=typ, name=name, key=key,
                                     is_dev=is_dev).one_or_none()
  return noti_key


def get_android_noti_key(organization_id, typ, name, key):
  noti_key = NotiKey.query.filter_by(organization_id=organization_id,
                                     typ=typ, name=name, key=key).one_or_none()
  return noti_key


def create_ios_noti_key(name, key, state):
  # name = bundle_id, key = password
  noti_key = NotiKey(id=uuid.uuid4().hex,
                     typ=models.IOS,
                     name=name,
                     key=key,
                     is_dev=state,
                     created_time=get_datetime(),
                     last_updated_time=get_datetime(),
                     last_updated_user=current_user.email,
                     organization_id=current_user.organization_id)
  _create_noti_key(noti_key)


def create_android_noti_key(name, key):
  # name = package_name, key = key
  noti_key = NotiKey(id=uuid.uuid4().hex,
                     typ=models.ANDROID,
                     name=name,
                     key=key,
                     created_time=get_datetime(),
                     last_updated_time=get_datetime(),
                     last_updated_user=current_user.email,
                     organization_id=current_user.organization_id)
  _create_noti_key(noti_key)


def update_noti_key(noti_key):
  noti_key.last_updated_time = get_datetime()
  noti_key.last_updated_user = current_user.email
  db.session.commit()


def get_noti_key_list(organization_id):
  noti_key = NotiKey.query.filter_by(organization_id=organization_id).all()
  return noti_key


# {{{ specifications


def create_specifications(version, specifications, user_email, organization_id,
                          product_id):
  specification = Endpoint(id=uuid.uuid4().hex,
                           version=version,
                           specifications=specifications,
                           created_time=get_datetime(),
                           last_updated_time=get_datetime(),
                           last_updated_user=user_email,
                           organization_id=organization_id,
                           product_id=product_id)
  db.session.add(specification)
  db.session.commit()
  update_stage_info_by_dev_about_endpoint(product_id, specification.id)


def update_specifications(_id, user_email, version, specifications):
  specification = get_specifications(_id)
  specification.version = version
  specification.last_updated_time = get_datetime()
  specification.last_updated_user = user_email
  specification.specifications = specifications
  db.session.commit()
  update_stage_info_by_dev_about_endpoint(specification.product_id,
                                          specification.id)


def get_specifications(_id):
  specifications = Endpoint.query.filter_by(id=_id).one_or_none()
  return specifications


def get_specifications_list(product_id):
  specifications_list = Endpoint.query.filter_by(product_id=product_id).all()
  return specifications_list


def get_specifications_by_version(product_id, version):
  specifications = Endpoint.query.filter_by(product_id=product_id,
                                            version=version).one_or_none()
  return specifications


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
                  invited_time=get_datetime(),
                  invited_user=user_email,
                  accepted=0)
  db.session.add(invite)
  db.session.commit()


def get_invite(key, organization_id):
  invite = Invite.query.filter_by(key=key, organization_id=organization_id).\
      one_or_none()
  return invite


def get_invite_by_email(email):
  invite = Invite.query.filter_by(level=models.MEMBER, email=email).one_or_none()
  return invite


def get_invite_by_member(email, organization_id):
  invite = Invite.query.filter_by(level=models.MEMBER, email=email, accepted=0,
                                  organization_id=organization_id).one_or_none()
  return invite


def get_invite_list(organization_id):
  invite_list = Invite.query.filter_by(organization_id=organization_id,
                                       accepted=0).all()
  return invite_list


def get_invite_by_product_id(product_id, email, organization_id):
  invite = Invite.query.filter_by(level=models.TESTER, email=email,
                                  product_id=product_id, accepted=0,
                                  organization_id=organization_id).one_or_none()
  return invite


def get_invite_list_by_tester(product_id, organization_id):
  invite_list = Invite.query.filter_by(level=models.TESTER, accepted=0,
                                       product_id=product_id,
                                       organization_id=organization_id).all()
  return invite_list


def update_invite(key, organization_id):
  invite = get_invite(key, organization_id)
  if invite:
    invite.accepted = 1
    invite.accepted_time = get_datetime()
    db.session.commit()


def update_invite_by_key(key, invite):
  invite.key = key
  db.invited_time = get_datetime()
  db.session.commit()


def delete_invite(invite_id):
  invite = Invite.query.filter_by(id=invite_id).one_or_none()
  if invite:
    db.session.delete(invite)
    db.session.commit()


def delete_invite_by_product(product_id):
  Invite.query.filter_by(product_id=product_id).delete()
  db.session.commit()


def delete_invite_by_organization(organization_id):
  Invite.query.filter_by(organization_id=organization_id).delete()
  db.session.commit()


# }}}


# {{{ Tester


def create_tester(email, organization_id, product_id, authorized, stage):
  tester = Tester(id=uuid.uuid4().hex,
                  email=email,
                  authorized=authorized,
                  level=stage,
                  organization_id=organization_id,
                  product_id=product_id)
  db.session.add(tester)
  db.session.commit()


def update_tester_to_authorized(_id):
  tester = Tester.query.filter_by(id=_id).one_or_none()
  if tester:
    tester.authorized = True
    db.session.commit()


def get_tester(_id, product_id):
  tester = Tester.query.filter_by(id=_id, product_id=product_id).one_or_none()
  return tester


def get_tester_by_email(email_addr, product_id):
  tester = Tester.query.filter_by(email=email_addr, product_id=product_id).one_or_none()
  return tester


def get_tester_list(product_id, organization_id):
  tester_list = Tester.query.\
      filter_by(product_id=product_id, organization_id=organization_id).\
      order_by('level').all()
  return tester_list


def get_tester_list_by_dev(product_id, organization_id):
  tester_list = Tester.query.\
      filter_by(product_id=product_id, organization_id=organization_id,
                level=2).all()
  return tester_list


def get_tester_list_by_pre_release(product_id, organization_id):
  tester_list = Tester.query.\
      filter_by(product_id=product_id, organization_id=organization_id,
                level=1).all()
  return tester_list


def get_send_tester_list(product_id, organization_id, level):
  tester_list = Tester.query.filter_by(product_id=product_id, level=level,
                                       organization_id=organization_id,
                                       authorized=True).all()
  return tester_list


def delete_tester(_id):
  tester = Tester.query.filter_by(id=_id).one_or_none()
  if tester:
    db.session.delete(tester)
    db.session.commit()


# }}}


# {{{ Firmware


def create_firmware(version, ep_version, model_code, user_email, json_path,
                    model_id):
  firmware = Firmware(id=uuid.uuid4().hex,
                      version=version,
                      ep_version=ep_version,
                      model_code=model_code,
                      hex_path="",
                      json_path=json_path,
                      created_time=get_datetime(),
                      last_updated_time=get_datetime(),
                      last_updated_user=user_email,
                      is_removed=False,
                      model_id=model_id)
  db.session.add(firmware)
  db.session.commit()
  return firmware


def get_firmware(_id):
  firmware = Firmware.query.filter_by(id=_id).one_or_none()
  return firmware


def get_firmware_list_order_by_version(ep_version, model_code):
  firmware_list = Firmware.query.filter_by(ep_version=ep_version, model_code=model_code).\
      order_by(desc(Firmware.last_updated_time)).all()
  return firmware_list


def delete_firmware(firmware_id):
  firmware = get_firmware(firmware_id)
  if firmware:
    firmware.is_removed = True
    db.session.commit()


# }}}


#{{{  Handle release


def _delete_before_pre_release(product_id):
  _pre_release = get_product_stage_by_pre_release(product_id)
  if _pre_release:
    db.session.delete(_pre_release)
    db.session.commit()


def update_dev(product_id):
  _dev = get_product_stage_by_dev(product_id)
  if _dev:
    _dev.last_updated_time = get_datetime()
    _dev.last_updated_user = current_user.email
    db.session.commit()


def pre_release(product_id):
  dev = get_product_stage_by_dev(product_id)
  models_dict = {}  # {model_code : firmware_version}
  send_mail_info_dict = {}  # {model_name : firmware_version}
  try:
    for _info in dev.stage_info_list:
      _model = get_model(_info.model_id)
      _firmware = get_firmware(_info.firmware_id)
      models_dict[_model.code] = _firmware.version
      send_mail_info_dict[_model.name] = _firmware.version
  except:
    logging.exception("Fail to Release.")
    raise Exception("Fail to Release.")
  prd_ret = apis.update_product_stage(product_id, dev, models_dict,
                                      models.STAGE_PRE_RELEASE)
  if prd_ret:
    _pre_release = get_product_stage_by_pre_release(product_id)
    # TODO: Is there a need?
    # if _pre_release:
    #   for _stage_info in _pre_release.stage_info_list:
    #     history = History(id=uuid.uuid4().hex,
    #                       model_id=_stage_info.model_id,
    #                       firmware_id=_stage_info.firmware_id,
    #                       endpoint_id=_stage_info.endpoint_id,
    #                       hook_url=_pre_release.hook_url,
    #                       hook_client_key=_pre_release.hook_client_key,
    #                       stage=_pre_release.stage,
    #                       created_time=get_datetime(),
    #                       last_updated_time=get_datetime(),
    #                       last_updated_user=current_user.email,
    #                       product_id=product_id)
    #     db.session.add(history)
    #   db.session.commit()
    remove_product_stage(_pre_release.id)

    new_pre_release_id = uuid.uuid4().hex
    new_pre_release = ProductStage(id=new_pre_release_id,
                                   hook_url=dev.hook_url,
                                   hook_client_key=dev.hook_client_key,
                                   stage=models.STAGE_PRE_RELEASE,
                                   created_time=get_datetime(),
                                   last_updated_time=get_datetime(),
                                   last_updated_user=current_user.email,
                                   product_id=product_id)
    db.session.add(new_pre_release)
    for _info in dev.stage_info_list:
      stage_info = StageInfo(id=uuid.uuid4().hex,
                             model_id=_info.model_id,
                             endpoint_id=_info.endpoint_id,
                             firmware_id=_info.firmware_id,
                             created_time=get_datetime(),
                             last_updated_time=get_datetime(),
                             last_updated_user=current_user.email,
                             product_stage_id=new_pre_release_id)
      db.session.add(stage_info)
    db.session.commit()
    for model_name, firmware_version in send_mail_info_dict.items():
      mail.send_about_test_user(product_id, model_name, firmware_version,
                                models.TESTER_PRE_RELEASE)
    return True
  else:
    return False


def release(product_id):
  _pre_release = get_product_stage_by_pre_release(product_id)
  models_dict = {}
  try:
    for _info in _pre_release.stage_info_list:
      _model = get_model(_info.model_id)
      _firmware = get_firmware(_info.firmware_id)
      models_dict[_model.code] = _firmware.version
  except:
    logging.exception("Fail to Release.")
    raise Exception("Fail to Release.")
  prd_ret = apis.update_product_stage(product_id, _pre_release, models_dict,
                                      models.STAGE_RELEASE)
  if prd_ret:
    _release = get_product_stage_by_release(product_id)
    if _release:
      for _stage_info in _release.stage_info_list:
        history = History(id=uuid.uuid4().hex,
                          model_id=_stage_info.model_id,
                          firmware_id=_stage_info.firmware_id,
                          endpoint_id=_stage_info.endpoint_id,
                          hook_url=_release.hook_url,
                          hook_client_key=_release.hook_client_key,
                          stage=_release.stage,
                          created_time=get_datetime(),
                          last_updated_time=get_datetime(),
                          last_updated_user=current_user.email,
                          product_id=product_id)
        db.session.add(history)
      db.session.commit()

    remove_product_stage(_release.id)
    new_release_id = uuid.uuid4().hex
    new_release = ProductStage(id=new_release_id,
                               hook_url=_pre_release.hook_url,
                               hook_client_key=_pre_release.hook_client_key,
                               stage=models.STAGE_RELEASE,
                               created_time=get_datetime(),
                               last_updated_time=get_datetime(),
                               last_updated_user=current_user.email,
                               product_id=product_id)
    db.session.add(new_release)
    for _info in _pre_release.stage_info_list:
      stage_info = StageInfo(id=uuid.uuid4().hex,
                             model_id=_info.model_id,
                             endpoint_id=_info.endpoint_id,
                             firmware_id=_info.firmware_id,
                             created_time=get_datetime(),
                             last_updated_time=get_datetime(),
                             last_updated_user=current_user.email,
                             product_stage_id=new_release_id)
      db.session.add(stage_info)
    db.session.commit()
    return True
  else:
    return False


# }}}


# {{{ EmailAuth


def create_email_auth(email, key, user_id):
  email_auth = EmailAuth(id=uuid.uuid4().hex,
                         email=email,
                         key=key,
                         user_id=user_id,
                         is_confirm=False,
                         sent_time=get_datetime(),
                         accepted_time=get_datetime())
  db.session.add(email_auth)
  db.session.commit()


def get_email_auth(email, key):
  email_auth = EmailAuth.query.filter_by(email=email, key=key,
                                         is_confirm=False).one_or_none()
  return email_auth


def has_email(email):
  email_auth = EmailAuth.query.filter_by(email=email, is_confirm=False).one_or_none()
  return email_auth


def update_email_auth(_id):
  email_auth = EmailAuth.query.filter_by(id=_id).one_or_none()
  email_auth.is_confirm = True
  email_auth.accepted_time = get_datetime()
  db.session.commit()


def remove_email_auth(_id):
  email_auth = EmailAuth.query.filter_by(id=_id).one_or_none()
  if email_auth:
    db.session.delete(email_auth)
    db.session.commit()


# }}}


# {{{ ReferrerInfo


def create_referrer_info(user, ip_addr, referrer, user_agent, accept_language):
  referrer_info = ReferrerInfo(id=uuid.uuid4().hex,
                               user=user,
                               ip_address=ip_addr,
                               referrer=referrer,
                               user_agent=user_agent,
                               accept_language=accept_language,
                               accepted_time=get_datetime())
  db.session.add(referrer_info)
  db.session.commit()


# }}}
