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
import datetime
import logging

from flask import render_template, request, redirect
from flask_login import login_required
from flask_login import current_user

import apis
from base import db
from models import Organization, User
from organization import blueprint


@blueprint.route('/', methods=['GET'])
@login_required
def default_route():
  orgs = Organization.query.filter_by().all()
  return render_template("organization.html", orgs=orgs)


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    return render_template("create.html")
  else:
    name = request.form['name']
    owner = request.form['owner']
    is_org = Organization.query.filter_by(name=name).one_or_none()
    if is_org:
      return redirect('/organization')
    else:
      ret = apis.create_org(owner)
      org = Organization(id=ret['id'],
                         users=json.dumps(ret['users']),
                         products=json.dumps(ret['products']),
                         tokens=json.dumps(ret['tokens']),
                         kinds=json.dumps(ret['kinds']),
                         name=name,
                         owner=json.dumps([owner]),
                         member=json.dumps([]),
                         created_time=datetime.datetime.utcnow(),
                         last_update=datetime.datetime.utcnow())
      db.session.add(org)
      db.session.commit()
      #TODO:
      user = User.query.filter_by(email=owner).one_or_none()
      if user:
        user.organization_id = ret['id']
        db.session.commit()
      return redirect('/organization')


@blueprint.route('/remove', methods=['GET'])
@login_required
def remove():
  org_id = request.args.get('id')
  org = Organization.query.get(org_id)
  db.session.delete(org)
  db.session.commit()
  return redirect('organization')


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
