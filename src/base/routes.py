from flask import render_template, redirect, request, url_for, _request_ctx_stack
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from base import blueprint
from base.models import User
from base import db, login_manager, auth

from products.models import Product


@blueprint.route('/')
def route_default():
  return redirect(url_for('login_blueprint.login'))


@blueprint.route('/<template>')
@login_required
def route_template(template):
  return render_template(template + '.html')


@blueprint.route('/fixed_<template>')
@login_required
def route_fixed_template(template):
  return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
  return render_template('errors/page_{}.html'.format(error))


## Login & Registration


"""
email auth token
{'iss': 'https://securetoken.google.com/console-4196c', 'name': 'jslee',
 'aud': 'console-4196c', 'auth_time': 1528782910,
 'user_id': 'HObbPOyiSchoV6uOtVOIiCphD883',
 'sub': 'HObbPOyiSchoV6uOtVOIiCphD883', 'iat': 1528782910, 'exp': 1528786510,
 'email': 'jslee@thenaran.com', 'email_verified': False,
 'firebase': {'identities': {'email': ['jslee@thenaran.com']},
              'sign_in_provider': 'password'}
}

google
{'iss': 'https://securetoken.google.com/console-4196c', 'name': 'Jaeseung Lee',
 'picture': 'https://lh6.googleusercontent.com/-PSY5qMeC5vk/AAAAAAAAAAI/AAAAAAAAAAA/AB6qoq1vsG8shcIE6VuINH_SEVmU0eJTrg/mo/photo.jpg',
 'aud': 'console-4196c', 'auth_time': 1528792232,
 'user_id': 'XtxGnNysQXSg0zzDgJJpD1BRR172', 'sub': 'XtxGnNysQXSg0zzDgJJpD1BRR172',
 'iat': 1528792232, 'exp': 1528795832, 'email': 'jslee@narantech.com',
 'email_verified': True,
 'firebase': {'identities': {'google.com': ['107405048989999876505'],
                             'email': ['jslee@narantech.com']},
              'sign_in_provider': 'google.com'}
}
"""

DEFAULT_PHOTO_URL = '''/static/images/user.png'''


@auth.production_loader
def production_sign_in(token):
  user = User.query.filter_by(firebase_user_id=token['sub']).one_or_none()
  if not user:
    user = User(firebase_user_id=token['sub'])
    db.session.add(user)
  user.email = token['email']
  user.email_verified = token['email_verified']
  user.username = token.get('name')
  user.photo_url = token.get('picture', DEFAULT_PHOTO_URL)
  db.session.commit()
  login_user(user)
  return redirect(url_for('base_blueprint.route_default'))


@auth.unloader
def logout():
  logout_user()
  return redirect(url_for('login_blueprint.login'))


@blueprint.route('/shutdown')
def shutdown():
  func = request.environ.get('werkzeug.server.shutdown')
  if func is None:
    raise RuntimeError('Not running with the Werkzeug Server')
  func()
  return 'Server shutting down...'


## Errors


@login_manager.unauthorized_handler
def unauthorized_handler():
  return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
  return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
  return render_template('errors/page_404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
  return render_template('errors/page_500.html'), 500


## context processor

def _get_product_list():
  product_list = []
  if current_user:
    user_id = current_user.id
    product_list = Product.query.filter_by(user_id=user_id).all()
  return product_list


def get_product_list():
  return dict(product_list=_get_product_list())
