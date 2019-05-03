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


from flask import abort, render_template, request, redirect, url_for  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

import util
from management import blueprint
from management import organization
from management import settings


@blueprint.route('/', methods=['GET'])
@util.require_login
def default_route():
  return organization.default_route()


# {{{ Organization


@blueprint.route('/organization', methods=['GET'])
@util.require_login
def default_organization():
  return organization.general()


@blueprint.route('/organization/general', methods=['GET'])
@util.require_login
def default_organization_general():
  return organization.general()


@blueprint.route('/organization/notification', methods=['GET'])
@util.require_login
def default_organization_notification():
  return organization.notification_key()


@blueprint.route('/organization/member', methods=['GET'])
@util.require_login
def default_organization_member():
  return organization.member()


@blueprint.route('/organization/product', methods=['GET'])
@util.require_login
def default_organization_product():
  return organization.product()


@blueprint.route('/organization/create', methods=['GET', 'POST'])
@util.require_login
def create():
  return organization.create()


@blueprint.route('/organization/register/<platform>', methods=['GET', 'POST'])
@util.require_login
def register_noti_key(platform):
  return organization.register_noti_key(platform)


@blueprint.route('/organization/notikey/update/<noti_key_id>', methods=['GET', 'POST'])
@util.require_login
def update_noti_key(noti_key_id):
  return organization.update_noti_key(noti_key_id)


@blueprint.route('/organization/notikey/delete/<noti_key_id>', methods=['POST'])
@util.require_login
def delete_noti_key(noti_key_id):
  return organization.delete_noti_key(noti_key_id)


@blueprint.route('/organization/invite', methods=['POST'])
@util.require_login
def send_invite():
  return organization.send_invite()


@blueprint.route('/organization/confirm', methods=['GET'])
def confirm_mail():
  return organization.confirm_mail()


@blueprint.route('/organization/invite/delete/<invite_id>')
@util.require_login
def delete_invite(invite_id):
  return organization.delete_invite(invite_id)


@blueprint.route('/organization/delete', methods=['POST'])
@util.require_login
def delete_organization():
  return organization.delete_organization()


@blueprint.route('/organization/domain', methods=['GET'])
@util.require_login
def get_domain_list():
  return organization.get_domain_list()


@blueprint.route('/organization/domain/register', methods=['GET', 'POST'])
@util.require_login
def register_domain():
  return organization.register_domain()


# }}}


# {{{ Settings


@blueprint.route('/settings', methods=['GET'])
@util.require_login
def default_setting():
  return settings.default_route()


# }}}
