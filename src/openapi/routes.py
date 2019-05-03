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

from flask import make_response ,request

import apis
import util
import in_apis
from openapi import blueprint


GADGET_ID_KEY = '''gadget_id'''
SUBNAME_KEY = '''subname'''
DOMAIN_KEY = '''domain'''
PROTOCOL_KEY = '''protocol'''
SUB_DOMAIN_REQUIRED_KEYS = set([GADGET_ID_KEY, SUBNAME_KEY, DOMAIN_KEY,
                                PROTOCOL_KEY])


@blueprint.route('/subdomain/register', methods=["POST"])
def register_subdomain():
  """
  METHOD
    POST
  HEADER
    Authorization : Bearer {product_key}
    Content-Type : application/json

  BODY
    gadget_id : String
    subname :  String
    domain : String
    protocol :  String

  Example
    url : https://console.mib.io/openapi/subdomain/register
    method : POST
    Header
    {
      "Authorization": "Bearer {product_key}",
      "Content-Type": "application/json"
    }
    Body
    {
      "gadget_id": "gadget_id",
      "subname": "test",
      "domain": "naran.com",
      "protocol": "http"
    }
  """
  if 'Authorization' not in request.headers:
    logging.warning("Unauthorized. Header : %s", request.headers)
    return make_response("Unauthorized", 401)
  auth_value = request.headers.get('Authorization')
  if not auth_value.startswith("Bearer"):
    logging.warning("Unauthorized. Header : %s", request.headers)
    return make_response("Unauthorized", 401)

  prd_keys = auth_value.split()
  if len(prd_keys) != 2:
    logging.warning("Unauthorized. Header : %s", request.headers)
    return make_response("Unauthorized", 401)

  prd = in_apis.get_product_by_key(prd_keys[1])
  if not prd:
    logging.warning("Unauthorized. Can not find prd. Header : %s",
                    request.headers)
    return make_response("Unauthorized", 401)

  data = json.loads(request.data)
  if SUB_DOMAIN_REQUIRED_KEYS != set(data.keys()):
    logging.warning("Component missing. Data : %s", data)
    return make_response("Some component is Missing", 400)

  domain = data[DOMAIN_KEY]
  subname = data[SUBNAME_KEY]
  protocol = data[PROTOCOL_KEY].lower()
  gadget_id = data[GADGET_ID_KEY]
  sub_domain = in_apis.get_sub_domain_by_sub_domain(domain, subname)
  if sub_domain:
    if sub_domain.organization_id != prd.organization_id:
      logging.warning("Not available Domain. Domain : %s, subname : %s",
                      domain, subname)
      logging.warning("Prd Org : %s, subdomain org : %s",
                      prd.organization_id, sub_domain.organization_id)
      return make_response("Domain And Subname is not Available.", 400)
    if sub_domain.product_id == prd.id:
      logging.warning("Not available Domain. Domain : %s, subname : %s",
                      domain, subname)
      logging.warning("Prd id : %s", prd.id)
      return make_response("Domain And Subname is not Available", 400)

  ip_addr = util.get_ip_addr()
  if protocol == "https":
    # TODO: Save files of crt, key about secure
    pass
  files_path = []
  in_apis.create_sub_domain(gadget_id, subname, domain, protocol,
                            files_path, ip_addr, prd.organization_id, prd.id)
  return make_response("Success", 200)
