
from time import monotonic
from threading import Lock
from urllib.parse import urlparse

import jwt  # noqa : pylint: disable=import-error
import requests  # noqa : pylint: disable=import-error

from cryptography.x509 import load_pem_x509_certificate  # noqa : pylint: disable=import-error
from cryptography.hazmat.backends import default_backend  # noqa : pylint: disable=import-error
from flask import Blueprint, abort, redirect, request, render_template, url_for  # noqa : pylint: disable=import-error
from werkzeug.http import parse_cache_control_header  # noqa : pylint: disable=import-error


blueprint = Blueprint(
    'login_blueprint',
    __name__,
    url_prefix='/auth',
    template_folder='templates',
    static_folder='static'
)


class FirebaseAuth:

  KEYCHAIN_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'  # noqa : pylint: disable=line-too-long
  PROVIDER_CLASSES = {
      'email': 'EmailAuthProvider',
      'facebook': 'FacebookAuthProvider',
      'github': 'GithubAuthProvider',
      'google': 'GoogleAuthProvider',
      'twitter': 'TwitterAuthProvider',
  }

  def __init__(self, app=None):
    self.debug = None
    self.api_key = None
    self.project_id = None
    self.provider_ids = None
    self.production_load_callback = None
    self.development_load_callback = None
    self.unload_callback = None
    self.blueprint = blueprint
    self.keys = {}
    self.max_age = 0
    self.cached_at = 0
    self.lock = Lock()
    if app is not None:
      self.init_app(app)

  def init_app(self, app):
    app.extensions['firebase_auth'] = self
    self.debug = app.debug
    self.api_key = app.config.get('FIREBASE_API_KEY')
    if self.api_key is None:
      return
    self.project_id = app.config['FIREBASE_PROJECT_ID']
    self.auth_domain = app.config.get('FIREBASE_AUTH_DOMAIN')
    if self.auth_domain is None:
      self.auth_domain = '{}.firebaseapp.com'.format(self.project_id)
    provider_ids = []
    for name in app.config['FIREBASE_AUTH_SIGN_IN_OPTIONS'].split(','):
      class_name = self.PROVIDER_CLASSES[name.strip()]
      provider_id = 'firebase.auth.{}.PROVIDER_ID'.format(class_name)
      provider_ids.append(provider_id)
    self.provider_ids = ','.join(provider_ids)

  def production_loader(self, callback):
    self.production_load_callback = callback
    return callback

  def development_loader(self, callback):
    self.development_load_callback = callback
    return callback

  def unloader(self, callback):
    self.unload_callback = callback
    return callback

  def url_for(self, endpoint, **values):
    return url_for(
        'login_blueprint.{}'.format(endpoint), _external=True,
        _scheme='http' if self.debug else 'https', **values
    )

  def login(self):
    return render_template('login.html', firebase_auth=self)

  def sign_in(self):
    header = jwt.get_unverified_header(request.data)
    with self.lock:
      self.refresh_keys()
      key = self.keys[header['kid']]
    token = jwt.decode(
        request.data, key=key, audience=self.project_id, algorithms=['RS256']
    )
    self.production_load_callback(token)
    return 'OK'

  def sign_out(self):
    self.unload_callback()
    return redirect(self.verify_redirection())

  def verify_redirection(self):
    _next = request.args.get('next') or request.url_root
    if not self.debug:
      next_domain = urlparse(_next).hostname.split('.')[-2:]
      this_domain = urlparse(request.url).hostname.split('.')[-2:]
      if next_domain != this_domain:
        abort(400)
    return _next

  def refresh_keys(self):
    now = monotonic()
    age = now - self.cached_at
    if age >= self.max_age:
      response = requests.get(self.KEYCHAIN_URL)
      if response.status_code != 200:
        raise Exception
      hazmat = default_backend()
      for kid, text in response.json().items():
        certificate = load_pem_x509_certificate(bytes(text, 'utf-8'), hazmat)
        self.keys[kid] = certificate.public_key()
      cache_control = response.headers['Cache-Control']
      self.max_age = parse_cache_control_header(cache_control).max_age
      self.cached_at = now
