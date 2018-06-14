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

import flask_login
from flask import render_template, request, redirect
from flask_login import login_required
from flask_login import current_user

from base import db
from organization import blueprint
from organization.models import Organization


@blueprint.route('/', methods=['GET'])
@login_required
def default_route():
  user_id = current_user.id
  orgs = Organization.query.filter_by(user_id=user_id).all()
  return render_template("organization.html", orgs=orgs)


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    return render_template("create.html")
  else:
    org = Organization(orgname=request.form['name'],
                       description=request.form['desc'],
                       user_id=current_user.id)
    db.session.add(org)
    db.session.commit()
    return redirect('profile/organization')


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
