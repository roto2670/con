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
SUB_DOMAIN_REQUIRED_KEYS = set([GADGET_ID_KEY, SUBNAME_KEY, DOMAIN_KEY])


@blueprint.route('/subdomain/register', methods=["POST"])
def register_subdomain():
  """
  @api {post} /openapi/subdomain/register
              Register subdomain
  @apiVersion 0.0.1
  @apiName register_subdomain
  @apiGroup Subdomain
  @apiPermission developer
  @apiHeader {string} Authorization Product key.
  @apiHeader {String} Content-Type=application/json
  @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "Bearer (product_key)"
        "Content-Type": "application/json"
      }

  @apiParamExample {string} Request-Body-Example
        {"gadget_id": "(string) gadget id to use",
         "subname": "(string) top level domain name",
         "domain": "(stirng) domain"
         }

        # testsubdomain2ffd9835f5b99643dca use "push.mib.io"
        {"gadget_id": "testsubdomain2ffd9835f5b99643dca"
         "subname": "push",
         "domain": "mib.io"
        }

  @apiSuccessExample Success-Response:
        HTTP/1.1 200 OK
        {
          "result": True
        }

  @apiErrorExample Error-Response:
        HTTP/1.1 401 OK
        {
          "result": False,
          "message": "Unauthorized"
        }
  """
  if 'Authorization' not in request.headers:
    logging.warning("Unauthorized. Header : %s", request.headers)
    ret = {
      "result": False,
      "message": "Unauthorized"
    }
    return make_response(json.dumps(ret), 401)
  auth_value = request.headers.get('Authorization')
  if not auth_value.startswith("Bearer"):
    logging.warning("Unauthorized. Header : %s", request.headers)
    ret = {
      "result": False,
      "message": "Unauthorized"
    }
    return make_response(json.dumps(ret), 401)

  prd_keys = auth_value.split()
  if len(prd_keys) != 2:
    logging.warning("Unauthorized. Header : %s", request.headers)
    ret = {
      "result": False,
      "message": "Unauthorized"
    }
    return make_response(json.dumps(ret), 401)

  prd = in_apis.get_product_by_key(prd_keys[1])
  if not prd:
    logging.warning("Unauthorized. Can not find prd. Header : %s",
                    request.headers)
    ret = {
      "result": False,
      "message": "Unauthorized"
    }
    return make_response(json.dumps(ret), 401)

  data = json.loads(request.data)
  if SUB_DOMAIN_REQUIRED_KEYS != set(data.keys()):
    logging.warning("Component missing. Data : %s", data)
    ret = {
      "result": False,
      "message": "Some component is Missing"
    }
    return make_response(json.dumps(ret), 400)

  domain_name = data[DOMAIN_KEY]
  subname = data[SUBNAME_KEY]
  gadget_id = data[GADGET_ID_KEY]

  parent_domain = in_apis.get_domain_by_domain_name(domain_name,
                                                    prd.organization_id)
  if not parent_domain:
    logging.warning("Domain is not registered . Domain : %s, org : %s",
                    domain_name, prd.organization_id)
    ret = {
      "result": False,
      "message": "Domain is not registered your organization."
    }
    return make_response(json.dumps(ret), 400)
  elif not parent_domain.accepted:
    logging.warning("Domain is not accepted . Domain : %s, org : %s",
                    domain_name, prd.organization_id)
    ret = {
      "result": False,
      "message": "Domain is not accepted your organization."
    }
    return make_response(json.dumps(ret), 400)

  sub_domain = in_apis.get_sub_domain_by_sub_domain(domain_name, subname)
  if sub_domain:
    if sub_domain.organization_id != prd.organization_id:
      # TODO: Remove this?
      logging.warning("Not available Domain. Domain : %s, subname : %s",
                      domain_name, subname)
      logging.warning("Prd Org : %s, subdomain org : %s",
                      prd.organization_id, sub_domain.organization_id)
      ret = {
        "result": False,
        "message": "Domain And Subname is not Available"
      }
      return make_response(json.dumps(ret), 400)
    if sub_domain.product_id == prd.id:
      logging.warning("Not available Domain. Domain : %s, subname : %s",
                      domain_name, subname)
      logging.warning("Prd id : %s", prd.id)
      ret = {
        "result": False,
        "message": "Domain And Subname is not Available"
      }
      return make_response(json.dumps(ret), 400)

  ip_addr = util.get_ip_addr()
  in_apis.create_sub_domain(gadget_id, subname, domain_name, ip_addr,
                            parent_domain.id, prd.organization_id, prd.id)
  ret = {
    "result": True
  }
  return make_response(json.dumps(ret), 200)
