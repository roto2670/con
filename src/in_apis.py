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

import json
import uuid
import logging
import datetime

import pytz
from bcrypt import gensalt, hashpw
from flask_login import current_user  # noqa : pylint: disable=import-error
from flask import abort, render_template  # noqa : pylint: disable=import-error
from sqlalchemy.orm.session import make_transient  # noqa : pylint: disable=import-error
from sqlalchemy import desc

import apis
import util
import models
import constants
from base import db
from models import _Product as Product
from models import _ProductStage as ProductStage
from models import _StageInfo as StageInfo
from models import _Model as Model
from models import _Endpoint as Endpoint
from models import _NotiKey as NotiKey
from models import _NkModelPermission as NkModelPermission
from models import _Organization as Organization
from models import _User as User
from models import _Invite as Invite
from models import _Tester as Tester
from models import _Firmware as Firmware
from models import _History as History
from models import _SubDomain as SubDomain
from models import _Domain as Domain
from models import _ForkProduct as ForkProduct
from models import _Permission as Permission


def get_datetime():
  return datetime.datetime.now(pytz.timezone('UTC'))


def get_servertime():
  return datetime.datetime.now().replace(microsecond=0)


# {{{ Product


def create_product(product_name, product_obj, product_type):
  # product_obj : response from microbot cloud
  product = Product(id=product_obj['id'],
                    code=product_obj['keyword'],  # When BLE Scan
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
  return product


def create_product_to_import(product_name, product_obj, product_type,
                             parent_product_id):
  product = Product(id=product_obj['id'],
                    code=product_obj['keyword'],
                    developer_id=product_obj['developer_id'],
                    key=product_obj['key'],
                    name=product_name,
                    typ=product_type,
                    parent_product_id=parent_product_id,
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
  return product


def create_fork_product(product_obj, email_addr, model_id, sent_user, key,
                        target_organization):
  fork_product = ForkProduct(id=uuid.uuid4().hex,
                             model_id=model_id,
                             target_email=email_addr,
                             target_organization=target_organization,
                             key=key,
                             sent_user=sent_user,
                             created_time=get_datetime(),
                             product_id=product_obj.id)
  db.session.add(fork_product)
  db.session.commit()
  return fork_product


def delete_fork_product(fork_product_id):
  fork_product = get_fork_product_by_id(fork_product_id)
  if fork_product:
    db.session.delete(fork_product)
    db.session.commit()


def get_fork_product_list(product_id):
  fork_product_list = ForkProduct.query.filter_by(product_id=product_id).all()
  return fork_product_list


def get_fork_product_by_key(key):
  fork_product = ForkProduct.query.filter_by(key=key,
                                             target_email=current_user.email).\
      one_or_none()
  return fork_product


def get_fork_product_by_id(fork_product_id):
  fork_product = ForkProduct.query.filter_by(id=fork_product_id).one_or_none()
  return fork_product


def update_fork_product(key):
  fork_product = get_fork_product_by_key(key)
  if fork_product:
    fork_product.accepted_time = get_datetime()
    fork_product.accepted_user = current_user.email
    db.session.commit()
    return True
  return False


def has_fork_product(model_id, product_id, organization_id):
  fork_product = ForkProduct.query.filter_by(model_id=model_id,
                                             product_id=product_id,
                                             target_organization=organization_id).\
      one_or_none()
  return fork_product


def get_product(product_id):
  try:
    product = Product.query.filter_by(id=product_id,
                                      organization_id=current_user.organization_id).\
        one_or_none()
    if product:
      return product
    else:
      raise Exception("This product(%s) does not belong to %s. user : %s",
                      product_id, current_user.organization_id,
                      current_user.email)
  except:
    abort(403)


def has_product(product_id):
  product = Product.query.filter_by(id=product_id).one_or_none()
  return True if product else False


def get_product_by_key(product_key):
  product = Product.query.filter_by(key=product_key).one_or_none()
  return product


def get_product_by_keyword(product_keyword):
  product = Product.query.filter_by(code=product_keyword).one_or_none()
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


def create_model_import(model_name, model_code, model_type, product_id,
                        user_email, parent_model_id):
  model = Model(id=uuid.uuid4().hex,
                code=model_code,
                name=model_name,
                typ=model_type,
                parent_model_id=parent_model_id,
                created_time=get_datetime(),
                last_updated_time=get_datetime(),
                last_updated_user=user_email,
                product_id=product_id)
  db.session.add(model)
  db.session.commit()
  dev_stage = get_product_stage_by_dev(product_id)
  create_stage_info(dev_stage.id, model.id)
  return model


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

DEFAULT_LOGO_PATH = '''/static/images/naran-logo-white.svg'''


def create_organization(owner_email, organization_name, ret):
  # ret -> developer object from cloud server
  org = Organization(id=ret['id'],
                     users=json.dumps([owner_email]),
                     products=json.dumps(ret['products']),
                     tokens=json.dumps(ret['tokens']),
                     kinds=json.dumps(ret['kinds']),
                     name=organization_name.lower(),
                     topside_logo_path=DEFAULT_LOGO_PATH,
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


def update_organization_by_logo(organization_id, logo_path):
  org = Organization.query.filter_by(id=organization_id).one_or_none()
  if org:
    org.topside_logo_path = logo_path
    org.last_updated_time = get_datetime()
    db.session.commit()


# }}}


# {{{ User


def create_user(email, username, password, department, level):
  cur_time = get_datetime()
  org_id = constants.ORG_ID
  user_id = uuid.uuid4().hex
  user = User(id=user_id,
              email=email,
              name=username,
              firebase_user_id=user_id,
              email_verified=True,
              sign_in_provider=department,  # Using department
              photo_url='/static/images/user.png',
              created_time=cur_time,
              ip_address=util.get_ip_addr(),
              level=int(level),
              password=password,
              organization_id=org_id)
  db.session.add(user)
  db.session.commit()
  permission = Permission(id=uuid.uuid4().hex,
                          permission='777',
                          user_id=user.id)
  db.session.add(permission)
  db.session.commit()


def get_user(user_id):
  user = User.query.filter_by(id=user_id).one_or_none()
  return user


def get_user_by_email(email, organization_id):
  user = User.query.filter_by(email=email, organization_id=organization_id).one_or_none()
  return user


def get_user_by_email_only(email):
  user = User.query.filter_by(email=email).one_or_none()
  return user


def get_user_list(organization_id):
  user_list = User.query.filter_by(organization_id=organization_id).all()
  return user_list


def get_user_list_by_moi(organization_id):
  user_list = User.query.filter_by(level=6,
                                   organization_id=organization_id).all()
  return user_list


def update_user_by_ip(user_id, ip_addr):
  user = User.query.filter_by(id=user_id).one_or_none()
  user.ip_address = ip_addr
  user.last_access_time = get_servertime()
  db.session.commit()


def update_user_by_confirm(user_id):
  user = User.query.filter_by(id=user_id).one_or_none()
  user.email_verified = True
  user.last_access_time = get_datetime()
  db.session.commit()


def update_user_by_accept(user_id):
  user = User.query.filter_by(id=user_id).one_or_none()
  user.email_verified = True
  db.session.commit()


def update_user_by_level(user_id, level):
  user = User.query.filter_by(id=user_id).one_or_none()
  user.level = int(level)
  db.session.commit()


def delete_user_by_id(user_id):
  user = User.query.filter_by(id=user_id).one_or_none()
  if user:
    db.session.delete(user)
    db.session.commit()
    return True
  return False


def update_user_password(user_id, password):
  user = User.query.filter_by(id=user_id).one_or_none()
  if user:
    _password = hashpw(password.encode('utf-8'), gensalt())
    user.password = _password
    db.session.commit()


def update_user_information(user_id, name, department):
  user = User.query.filter_by(id=user_id).one_or_none()
  if user:
    user.name = name
    user.sign_in_provider = department
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
  return noti_key


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
  return noti_key


def update_noti_key(noti_key):
  noti_key.last_updated_time = get_datetime()
  noti_key.last_updated_user = current_user.email
  db.session.commit()


def get_noti_key(_id):
  noti_key = NotiKey.query.filter_by(id=_id).one_or_none()
  return noti_key


def get_noti_key_list(organization_id):
  noti_key = NotiKey.query.filter_by(organization_id=organization_id).all()
  return noti_key


def delete_noti_key(organization_id, noti_key_id):
  noti_key = NotiKey.query.filter_by(organization_id=organization_id,
                                     id=noti_key_id).one_or_none()
  if noti_key:
    if noti_key.typ == models.IOS:
      ret = apis.delete_ios_key(organization_id, noti_key.name)
    else:
      ret = apis.delete_android_key(organization_id, noti_key.name)

    if ret:
      db.session.delete(noti_key)
      db.session.commit()
      return True
    else:
      logging.warning("Failed to delete noti key. org_id : %s, noti_id : %s, ret : %s",
                      organization_id, noti_key_id, ret)
      return False
  else:
    logging.warning("Can not find noti key. org_id : %s, noti_id : %s",
                    organization_id, noti_key_id)
    return False


# {{{ Noti Model Permission


def create_noti_model_permission(user_email, noti_key_id, model_id,
                                 has_code=None):
  nk_model_permit = NkModelPermission(id=uuid.uuid4().hex,
                                      permission=0,
                                      has_code=True if has_code else False,
                                      created_time=get_datetime(),
                                      last_updated_time=get_datetime(),
                                      last_updated_user=user_email,
                                      noti_key_id=noti_key_id,
                                      model_id=model_id)
  db.session.add(nk_model_permit)
  db.session.commit()


def update_noti_model_permission(_id, user_email, noti_key_id, model_id):
  nk_model_permit = get_noti_model_permission(_id)
  nk_model_permit.noti_key_id = noti_key_id
  nk_model_permit.model_id = model_id
  nk_model_permit.last_update_time = get_datetime()
  nk_model_permit.last_update_user = user_email
  db.session.commit()


def delete_noti_model_permission(_id):
  nk_model_permit = get_noti_model_permission(_id)
  db.session.delete(nk_model_permit)
  db.session.commit()


def get_noti_model_permission(_id):
  nk_model_permit = NkModelPermission.query.filter_by(id=_id).one_or_none()
  return nk_model_permit


def get_noti_model_permission_list_by_noti_id(noti_key_id):
  nk_model_permit_list = NkModelPermission.query.\
      filter_by(noti_key_id=noti_key_id).all()
  return nk_model_permit_list


def get_noti_model_permission_list_by_model_id(model_id):
  nk_model_permit_list = NkModelPermission.query.\
      filter_by(model_id=model_id).all()
  return nk_model_permit_list


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


# {{{ invite  # TODO: remove this


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


def get_firmware_list_order_by_version(model_id, ep_version, model_code):
  firmware_list = Firmware.query.filter_by(model_id=model_id,
                                           ep_version=ep_version,
                                           model_code=model_code).\
      order_by(desc(Firmware.last_updated_time)).all()
  return firmware_list


def delete_firmware(firmware_id):
  firmware = get_firmware(firmware_id)
  if firmware:
    firmware.last_updated_time = get_datetime()
    firmware.last_updated_user = current_user.email
    firmware.is_removed = True
    db.session.commit()


# }}}


# {{{  Handle release


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


def pre_release(product_id, model_id_list):
  dev = get_product_stage_by_dev(product_id)
  models_dict = {}  # {model_code : firmware_version}
  send_mail_info_dict = {}  # {model_name : firmware_version}
  release_stage_info_list = []
  try:
    for _info in dev.stage_info_list:
      if _info.model_id in model_id_list:
        _model = get_model(_info.model_id)
        _firmware = get_firmware(_info.firmware_id)
        models_dict[_model.code] = _firmware.version
        send_mail_info_dict[_model.name] = _firmware.version
        release_stage_info_list.append(_info)
  except:
    logging.exception("Fail to Release.")
    raise Exception("Fail to Release.")
  prd_ret = apis.update_product_stage(product_id, dev, models_dict,
                                      models.STAGE_PRE_RELEASE)
  if prd_ret:
    _pre_release = get_product_stage_by_pre_release(product_id)
    no_update_info_list = []
    # TODO: Is there a need?
    if _pre_release:
      for _stage_info in _pre_release.stage_info_list:
        if _stage_info.model_id not in model_id_list:
          no_update_info_list.append(_stage_info)
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
    for _info in release_stage_info_list:
      stage_info = StageInfo(id=uuid.uuid4().hex,
                             model_id=_info.model_id,
                             endpoint_id=_info.endpoint_id,
                             firmware_id=_info.firmware_id,
                             created_time=get_datetime(),
                             last_updated_time=get_datetime(),
                             last_updated_user=current_user.email,
                             product_stage_id=new_pre_release_id)
      db.session.add(stage_info)
    for _info in no_update_info_list:
      _info.product_stage_id = new_pre_release_id
    db.session.commit()
    remove_product_stage(_pre_release.id)
    return True
  else:
    return False


def release(product_id, model_id_list):
  _pre_release = get_product_stage_by_pre_release(product_id)
  models_dict = {}
  release_stage_info_list = []
  try:
    for _info in _pre_release.stage_info_list:
      if _info.model_id in model_id_list:
        _model = get_model(_info.model_id)
        _firmware = get_firmware(_info.firmware_id)
        models_dict[_model.code] = _firmware.version
        release_stage_info_list.append(_info)
  except:
    logging.exception("Fail to Release.")
    raise Exception("Fail to Release.")
  prd_ret = apis.update_product_stage(product_id, _pre_release, models_dict,
                                      models.STAGE_RELEASE)
  if prd_ret:
    _release = get_product_stage_by_release(product_id)
    no_update_info_list = []
    if _release:
      for _stage_info in _release.stage_info_list:
        if _stage_info.model_id in model_id_list:
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
        else:
          no_update_info_list.append(_stage_info)
      db.session.commit()

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
    for _info in release_stage_info_list:
      stage_info = StageInfo(id=uuid.uuid4().hex,
                             model_id=_info.model_id,
                             endpoint_id=_info.endpoint_id,
                             firmware_id=_info.firmware_id,
                             created_time=get_datetime(),
                             last_updated_time=get_datetime(),
                             last_updated_user=current_user.email,
                             product_stage_id=new_release_id)
      db.session.add(stage_info)
    for _info in no_update_info_list:
      _info.product_stage_id = new_release_id
    db.session.commit()
    if _release:
      remove_product_stage(_release.id)
    return True
  else:
    return False


# }}}


# {{{ SubDomain


def create_sub_domain(gadget_id, subname, domain_name, request_ip_address,
                      domain_id, organization_id, product_id):
  sub_domain = SubDomain(id=uuid.uuid4().hex,
                         gadget_id=gadget_id,
                         subname=subname,
                         domain_name=domain_name,
                         request_ip_address=request_ip_address,
                         accepted=False,
                         created_time=get_datetime(),
                         organization_id=organization_id,
                         domain_id=domain_id,
                         product_id=product_id)
  db.session.add(sub_domain)
  db.session.commit()


def update_sub_domain(sub_domain_id):
  sub_domain = get_sub_domain(sub_domain_id)
  sub_domain.accepted = True
  sub_domain.accepted_time = get_datetime()
  sub_domain.accepted_user = current_user.email
  db.session.commit()


def delete_sub_domain(sub_domain_id):
  sub_domain = get_sub_domain(sub_domain_id)
  db.session.delete(sub_domain)
  db.session.commit()


def get_sub_domain(_id):
  sub_domain = SubDomain.query.filter_by(id=_id).one_or_none()
  return sub_domain


def get_sub_domain_list(product_id):
  sub_domain_list = SubDomain.query.filter_by(product_id=product_id).all()
  return sub_domain_list


def get_sub_domain_by_sub_domain(subname, domain_name):
  sub_domain = SubDomain.query.filter_by(subname=subname,
                                         domain_name=domain_name).\
      one_or_none()
  return sub_domain


# }}}


# {{{


def create_domain(domain, request_ip_address, request_user, file_paths,
                  organization_id):
  domain = Domain(id=uuid.uuid4().hex,
                  domain=domain,
                  request_ip_address=request_ip_address,
                  accepted=False,
                  request_user=request_user,
                  file_paths=file_paths,
                  created_time=get_datetime(),
                  organization_id=organization_id)
  db.session.add(domain)
  db.session.commit()


def update_domain(domain_id):
  domain = get_domain(domain_id)
  domain.accepted = True
  domain.files_path = "[]"
  domain.accepted_time = get_datetime()
  domain.accepted_user = current_user.email
  db.session.commit()


def get_domain(_id):
  domain = Domain.query.filter_by(id=_id).one_or_none()
  return domain


def get_domain_list(organization_id):
  domain_list = Domain.query.filter_by(organization_id=organization_id).all()
  return domain_list


def get_domain_by_domain_name(domain_name, organization_id):
  domain = Domain.query.filter_by(domain=domain_name,
                                  organization_id=organization_id).\
      one_or_none()
  return domain


def has_domain_by_domain(domain_name):
  domain = Domain.query.filter_by(domain=domain_name).one_or_none()
  return True if domain else False


#}}}
