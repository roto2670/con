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
import sendgrid  # noqa : pylint: disable=import-error
from sendgrid.helpers.mail import Mail  # noqa : pylint: disable=import-error
from sendgrid.helpers.mail import Email  # noqa : pylint: disable=import-error
from sendgrid.helpers.mail import Content  # noqa : pylint: disable=import-error
from sendgrid.helpers.mail import Attachment  # noqa : pylint: disable=import-error


SG_API_KEY = 'SG.Iit8M_G8R9GBiRBknKi7fw.'\
          '-qGUCtHKXjZplV89FHYScAVG9u5crHlsCIopTQxg5aM'


def _send_mail(request_body):
  sendgrid_client = sendgrid.SendGridAPIClient(apikey=SG_API_KEY)
  return sendgrid_client.client.mail.send.post(request_body=request_body)


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
    res = _send_mail(_mail.get())
    logging.debug("send mail status : %s", res.status_code)
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
