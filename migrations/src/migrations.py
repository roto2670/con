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


from base import db
import models as old
import models1 as new

DB = {}

def set(app):
  DB['old'] = db.get_engine(app, 'old')
  DB['new'] = db.get_engine(app, 'new')


def migrations():
  _invite()
  _org()
  _noti_key()
  _user()
  _permission()
  _product()
  _tester()
  _endpoint()
  _model()
  _firmware()
  _prd_stage()


def _invite():
  print("=== Invited migration start ===")
  old_invites = old.Invite.query.all()
  for _i in old_invites:
    _d = _i.__dict__
    if '_sa_instance_state' in _d:
      del _d['_sa_instance_state']
    new_inv = new._Invite()
    new_inv.id = _d['id']
    new_inv.email = _d['email']
    new_inv.organization_id = _d['organization_id']
    new_inv.product_id = _d['product_id']
    new_inv.key = _d['key']
    new_inv.level = _d['level']
    new_inv.invited_time = _d['invited_time']
    new_inv.invited_user = _d['invited_user']
    new_inv.accepted = _d['accepted']
    new_inv.accepted_time = _d['accepted_time']
    db.session.add(new_inv)
  db.session.commit()
  print("=== Success migration of Invited ===")


def _org():
  print("=== Organization migration start ===")
  old_orgs = old.Organization.query.all()
  for _o in old_orgs:
    _d = _o.__dict__
    if '_sa_instance_state' in _d:
      del _d['_sa_instance_state']
    new_org = new._Organization()
    new_org.id = _d['id']
    new_org.users = _d['users']
    new_org.products = _d['products']
    new_org.tokens = _d['tokens']
    new_org.kinds = _d['kinds']
    new_org.name = _d['name']
    new_org.original_name = _d['original_name']
    new_org.created_time = _d['created_time']
    new_org.last_updated_time = _d['last_updated_time']
    db.session.add(new_org)
  db.session.commit()
  print("=== Success migration of Organization ===")


def _noti_key():
  print("=== NotiKey migration start ===")
  old_notis = old.NotiKey.query.all()
  for _n in old_notis:
    _d = _n.__dict__
    if '_sa_instance_state' in _d:
      del _d['_sa_instance_state']
    new_noti = new._NotiKey()
    new_noti.id = _d['id']
    new_noti.typ = _d['typ']
    new_noti.name = _d['name']
    new_noti.key = _d['key']
    new_noti.is_dev = _d['is_dev']
    new_noti.created_time = _d['created_time']
    new_noti.last_updated_time = _d['last_updated_time']
    new_noti.last_updated_user = _d['last_updated_user']
    new_noti.organization_id = _d['organization_id']
    db.session.add(new_noti)
  db.session.commit()
  print("=== Success migration of NotiKey ===")


def _user():
  print("=== User migration start ===")
  old_users = old.User.query.all()
  for _u in old_users:
    _d = _u.__dict__
    if '_sa_instance_state' in _d:
      del _d['_sa_instance_state']
    new_user = new._User()
    new_user.id = _d['id']
    new_user.email = _d['email']
    new_user.name = _d['name']
    new_user.firebase_user_id = _d['firebase_user_id']
    new_user.email_verified = _d['email_verified']
    new_user.sign_in_provider = _d['sign_in_provider']
    new_user.photo_url = _d['photo_url']
    new_user.created_time = _d['created_time']
    new_user.last_access_time = _d['last_access_time']
    new_user.ip_address = _d['ip_address']
    new_user.level = _d['level']
    new_user.organization_id = _d['organization_id']
    db.session.add(new_user)
  db.session.commit()
  print("=== Success migration of User ===")


def _permission():
  print("=== Permission migration start ===")
  old_permms = old.Permission.query.all()
  for _p in old_permms:
    _d = _p.__dict__
    if '_sa_instance_state' in _d:
      del _d['_sa_instance_state']
    new_per = new._Permission()
    new_per.id = _d['id']
    new_per.permission = _d['permission']
    new_per.user_id = _d['user_id']
    db.session.add(new_per)
  db.session.commit()
  print("=== Success migration of Permission ===")

def _product():
  print("=== Product migration start ===")
  old_prds = old.Product.query.all()
  for _p in old_prds:
    _d = _p.__dict__
    if '_sa_instance_state' in _d:
      del _d['_sa_instance_state']
    new_prd = new._Product()
    new_prd.id = _d['id']
    new_prd.code = _d['code']
    new_prd.developer_id = _d['developer_id']
    new_prd.key = _d['key']
    new_prd.typ = _d['typ']
    new_prd.name = _d['name']
    new_prd.created_time = _d['created_time']
    new_prd.last_updated_time = _d['last_updated_time']
    new_prd.organization_id = _d['organization_id']
    db.session.add(new_prd)
  db.session.commit()
  print("=== Success migration of Product ===")


def _tester():
  print("=== Tester migration start ===")
  old_t = old.Tester.query.all()
  for _t in old_t:
    _d = _t.__dict__
    if '_sa_instance_state' in _d:
      del _d['_sa_instance_state']
    new_t = new._Tester()
    new_t.id = _d['id']
    new_t.email = _d['email']
    new_t.authorized = _d['authorized']
    new_t.level = _d['level']
    new_t.organization_id = _d['organization_id']
    new_t.product_id = _d['product_id']
    db.session.add(new_t)
  db.session.commit()
  print("=== Success migration of Tester ===")


def _endpoint():
  print("=== Endpoint migration start ===")
  old_eps = old.Endpoint.query.all()
  for _e in old_eps:
    _d = _e.__dict__
    prd_id = _e.product_stage.product_id
    new_ep = new._Endpoint()
    new_ep.id = _d['id']
    new_ep.version = _d['version']
    new_ep.specifications = _d['specifications']
    new_ep.created_time = _d['created_time']
    new_ep.last_updated_time = _d['last_updated_time']
    new_ep.last_updated_user = _d['last_updated_user']
    new_ep.organization_id = _d['organization_id']
    new_ep.product_id = prd_id
    db.session.add(new_ep)
  db.session.commit()
  print("=== Success migration of Endpoint ===")


def _model():
  print("=== Model migration start ===")
  old_models = old.Model.query.all()
  for _m in old_models:
    _d = _m.__dict__
    new_m = new._Model()
    new_m.id = _d['id']
    new_m.code = _d['code']
    new_m.name = _d['name']
    new_m.typ = _d['typ']
    new_m.created_time = _d['created_time']
    new_m.last_updated_time = _d['last_updated_time']
    new_m.last_updated_user = _d['last_updated_user']
    new_m.product_id = _m.product_stage.product_id
    db.session.add(new_m)
  db.session.commit()
  print("=== Success migration of Model ===")


def _firmware():
  print("=== Firmware migration start ===")
  old_fs = old.Firmware.query.all()
  for _f in old_fs:
    _d = _f.__dict__
    new_f = new._Firmware()
    new_f.id = _d['id']
    new_f.version = _d['version']
    new_f.ep_version = _d['ep_version']
    new_f.model_code = _d['model_code']
    new_f.hex_path = ""
    new_f.json_path = _d['path']
    new_f.created_time = _d['created_time']
    new_f.last_updated_time = _d['last_updated_time']
    new_f.last_updated_user = _d['last_updated_user']
    new_f.is_removed = False
    new_f.model_id = _d['model_id']
    db.session.add(new_f)
  db.session.commit()
  print("=== Success migration of Firmware ===")


def _prd_stage():
  print("=== Product Stage migration start ===")
  prd_sg = old.ProductStage.query.order_by('product_id', 'stage').all()
  for _sg in prd_sg:
    if _sg.stage == old.STAGE_ARCHIVE:
      # History
      new_h = new._History()
      new_h.id = _sg.id
      if _sg.model_list:
        new_h.model_id = _sg.model_list[0].id
        if _sg.model_list[0].firmware_list:
          new_h.firmware_id = _sg.model_list[0].firmware_list[0].id
        else:
          new_h.firmware_id = ""
      else:
        new_h.model_id = ""
        new_h.firmware_id = ""
      new_h.endpoint_id = _sg.endpoint.id
      new_h.hook_url = _sg.hook_url
      new_h.hook_client_key = _sg.hook_client_key
      new_h.stage = old.STAGE_ARCHIVE
      new_h.created_time = _sg.created_time
      new_h.last_updated_time = _sg.last_updated_time
      new_h.last_updated_user = _sg.last_updated_user
      new_h.product_id = _sg.product_id
      db.session.add(new_h)
    else:
      # Stage
      new_sg = new._ProductStage()
      new_sg.id = _sg.id
      new_sg.hook_url = _sg.hook_url
      new_sg.hook_client_key = _sg.hook_client_key
      new_sg.stage = _sg.stage
      if _sg.model_list:
        new_sg.model_id = _sg.model_list[0].id
        if _sg.model_list[0].firmware_list:
          new_sg.firmware_id = _sg.model_list[0].firmware_list[0].id
        else:
          new_sg.firmware_id = ""
      else:
        new_sg.model_id = ''
        new_sg.firmware_id = ''
      new_sg.created_time = _sg.created_time
      new_sg.last_updated_time = _sg.last_updated_time
      new_sg.last_updated_user = _sg.last_updated_user
      new_sg.product_id = _sg.product_id
      db.session.add(new_sg)
  db.session.commit()
  print("=== Success migration of Product Stage ===")
