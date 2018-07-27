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
from tornado import gen
from hashlib import md5

# clique
import engine.eventlog
from engine.adt.collections import Lazy

# thirdparty
import sendgrid
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import Attachment
from mailchimp3 import MailChimp


__DATA__ = Lazy()
__DATA__.add_initializer('sendgrid', lambda: _init_sendgrid())
__DATA__.add_initializer('mailchimp', lambda: _init_mailchimp())
SG_API_KEY = 'SG.Iit8M_G8R9GBiRBknKi7fw.'\
          '-qGUCtHKXjZplV89FHYScAVG9u5crHlsCIopTQxg5aM'
MC_API_KEY = 'd265df789694603990ec195d36bf52fa-us8'
MC_LIST_ID = 'a8c763654e'


def _init_sendgrid():
  return sendgrid.SendGridAPIClient(apikey=SG_API_KEY)


def _init_mailchimp():
  return MailChimp(MC_API_KEY)


async def subscribe_to(email, opt_in=False):
  try:
    logging.info("Subscribe %s, opt_in:%s", email, opt_in)
    data = {
      'email_address': email,
      'status_if_new': 'subscribed',
      'merge_fields': {
        'CONSENT': 'Opt-in' if opt_in else 'Opt-out'
      }}
    return __DATA__.mailchimp.lists.members.create_or_update(
        MC_LIST_ID, md5(email.encode('utf-8')).hexdigest(), data)
  except Exception:
    logging.warn("Failed subscribe", exc_info=True)


async def _send_mail(request_body):
  return __DATA__.sendgrid.client.mail.send.post(request_body=request_body)


@gen.coroutine
def send(to_addr, subject, data, content_type=None, attachment=None):
  try:
    content_type = content_type or 'text/html'
    from_addr = 'noreply@microbot.is'
    from_name = 'MicroBot Cloud'
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
    res = yield _send_mail(_mail.get())
    yield engine.eventlog.write(to_addr, 'send_signin',
                                {'email': to_addr, 'code': res.status_code})
    logging.debug("send mail status : %s", res.status_code)
    return True
  except Exception:
    logging.warn("Failed to send mail. to: %s, subject: %s",
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