#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


""" mail related
"""

# default
import logging

# thirdparty
from sendgrid.helpers.mail import Mail  # noqa : pylint: disable=import-error
from sendgrid.helpers.mail import Email  # noqa : pylint: disable=import-error
from sendgrid.helpers.mail import Content  # noqa : pylint: disable=import-error
from sendgrid.helpers.mail import Attachment  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error

# self
import util
import common
import worker
import in_apis


def send(to_addr, subject, data, content_type=None, attachment=None):
  try:
    content_type = content_type or 'text/html'
    from_addr = 'noreply@microbot.is'
    from_name = 'MiB Console'
    from_email = Email(from_addr, from_name)
    to_email = Email(to_addr)
    content = Content(content_type, data)
    _mail = Mail(from_email, subject, to_email, content)
    if attachment and isinstance(attachment, list):
      for attach in attachment:
        if isinstance(attach, Attachment):
          _mail.add_attachment(attach)
        else:
          logging.info("Invalid type. Type : %s", type(attach))
    elif not isinstance(attachment, list):
      logging.info("Attachment is not list. Attachment : %r", attachment)
    resp = worker.send_mail(_mail.get())
    logging.debug("send mail status : %s", resp)
    return True
  except Exception:
    logging.warning("Failed to send mail. to: %s, subject: %s",
                    to_addr, subject, exc_info=True)
    raise


def build_attachment(filename, content_id, content,
                     content_type='image/png', disposition='inline'):
  attachment = Attachment()
  attachment.filename = filename
  attachment.content_id = content_id
  attachment.type = content_type
  attachment.content = content
  attachment.disposition = disposition
  return attachment


def send_about_test_user(product_id, model_name, firmware_version, state):
  with open(util.get_mail_form_path('firmware_upload.html'), 'r') as _f:
    content = _f.read()
  _product = in_apis.get_product(product_id)
  title = common.get_msg("products.firmware.mail.upload_title")
  title = title.format(_product.name, model_name, firmware_version)
  msg = common.get_msg("products.firmware.mail.upload_message")
  msg = msg.format(_product.name, model_name, firmware_version)
  content = content.format(title=title, msg=msg)
  tester_list = in_apis.get_send_tester_list(product_id,
                                             current_user.organization_id,
                                             state)
  for _tester in tester_list:
    try:
      send(_tester.email, title, content)
    except:
      logging.warning(
          "Failed to send firemware upload email. Tester : %s, product : %s, model : %s, version : %s, Sender : %s",
          _tester.email, product_id, model_name, firmware_version,
          current_user.email, exc_info=True)