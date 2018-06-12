
from products import blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required
import flask_login

import logging


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == "GET":
    return render_template("product_create.html")
  else:
    logging.info("name : %s", str(request.form['name']))
    logging.info("desc : %s", str(request.form['desc']))
    return redirect('management')


@blueprint.route('/remove', methods=['GET'])
@login_required
def remove():
  return redirect('management')


@blueprint.route('/product', methods=['GET', 'POST'])
def product():
  logging.info("query string : %s", str(request.query_string))
  if request.method == "GET":
    return render_template('product.html')
  else:
    pass


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')
