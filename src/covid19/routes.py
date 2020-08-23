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
import logging

from flask import render_template, redirect, request  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error
import firebase_admin as fbase
from firebase_admin import firestore
from firebase_admin import credentials

import base
import util
import models
import in_apis
from covid19 import blueprint


# Initialize firebase
cred = credentials.Certificate("../res/fbase_key/service.json")
fbase_app = fbase.initialize_app(cred)

stats = {} # today's stats

@blueprint.route('/')
@util.require_login
def route_default():
  # Gets today stats from firebase store.
  # TODO: update daily
  fbase_store = firestore.client()
  global stats
  # if not stats:
    # query to firebase.
    # stat_ref = fbase_store.collection(u'covid19_stats')
    # query = stat_ref.order_by(u'ts', direction=firestore.Query.DESCENDING).limit(1)
    # results = query.stream()
    # try:
    #   doc = next(results)
    #   stats = doc.to_dict()
    # except StopIteration:
    #   pass

  return render_template("dashboard.html", stats=stats)

@blueprint.route('/stats', methods=['GET'])
@util.require_login
def default_today_stats():
  fbase_store = firestore.client()
  stat_ref = fbase_store.collection(u'covid19_stats')
  query = stat_ref.order_by(u'ts', direction=firestore.Query.DESCENDING).limit(1)
  results = query.stream()
  stats = {}
  try:
    doc = next(results)
    stats = doc.to_dict()
  except StopIteration:
    pass

  return json.dumps(stats, indent=4, sort_keys=True, default=str)

@blueprint.route('/users')
@util.require_login
def route_users():
  return render_template("users.html")

@blueprint.route('/users', methods=['GET'])
@util.require_login
def default_users():
  # Get users from firebase firestore
  docs = fbase_store.collection('users').stream()
  users = []
  for doc in docs:
    users.append(doc.to_dict())

  return json.dumps(users, indent=4, sort_keys=True, default=str)

@blueprint.route('/notifications')
@util.require_login
def route_notifications():
  return render_template("notifications.html")

@blueprint.route('/managedata')
@util.require_login
def route_manage_data():
  return render_template("manage_data.html")