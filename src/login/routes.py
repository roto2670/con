
from login import blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required

import logging


@blueprint.route('/<template>')
def route_template(template):
  return render_template('login/' + template + '.html')
