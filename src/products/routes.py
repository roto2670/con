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
from products import blueprint
from products.models import Product


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    return render_template("product_create.html")
  else:
    prd = Product(prdname=request.form['name'],
                  description=request.form['desc'],
                  user_id=current_user.id)
    db.session.add(prd)
    db.session.commit()
    return redirect('products/management')


@blueprint.route('/remove', methods=['GET'])
@login_required
def remove():
  prd_id = request.args.get('id')
  prd = Product.query.get(prd_id)
  db.session.delete(prd)
  db.session.commit()
  return redirect('products/management')


@blueprint.route('/product', methods=['GET', 'POST'])
@login_required
def product():
  if request.method == "GET":
    return render_template('product.html')
  else:
    pass


@blueprint.route('/management', methods=['GET'])
@login_required
def get_list():
  user_id = current_user.id
  prds = Product.query.filter_by(user_id=user_id).all()
  return render_template("management.html", prds=prds)


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
