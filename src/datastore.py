#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016-2017 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


# default
import os
import logging
import tempfile

# Have to be set G_ENV_GRPC to true before import google.cloud
G_ENV_GRPC = '''GOOGLE_CLOUD_DISABLE_GRPC'''
G_ENV_VALUE = '''GOOGLE_APPLICATION_CREDENTIALS'''
PROTACLOUD_CREDENTIALS_DATA = '''{"type": "service_account", "project_id": "protacloud", "private_key_id": "e3ea49188ad6d454ac2da425684bf853fd29b64d", "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC9iQ8RtxZT/7Ov\\nid3q+Xf4qFu4btiAVbtkPx/gx0oiwLFn9IPdDiA6tQmK4l31valWJJRDv222Nnom\\n/1a5RQXoFJlqk3O07tMBNA7zWgKlovnBOt0axi+A6GOLF1YQOUCOz3/jhI8MQXGu\\nbd0mxrwziVPOS3PrxqBMKm+EpXwhM3BOeW34fCCMRxjXXSUet7DMWYv3/mQu7V4g\\nsec92B3+vxOikz24hbar/X54kmtyVI3FkPjMerhQsISc3MCdVIvGctrHxVUF57jY\\n/5VkAkQIy5iqaRdi9nx5/wMJZZrxcVSyrlLGx1c8wuWPKg8H32Tw8fF84NXbzdru\\njhirdITTAgMBAAECggEATXwhWXwwmCGSq4Jg46WeSt1FNga24uxpoid+WE4Q/Fkr\\njdS0LeSO/4EwiANYJ1Uky89Df9jcOOBXmubLZQ2XRxRYze2/IWp7f+Pw8sLLDz0r\\n/reaWc5I8FnRDDV7nUFSp6+j2HdCZd/BYm6OuUIJAca0KMPG/c5jjQ/SLHfc4dMo\\nWGP9s8QKFyolO8GPPv3zhPjQD76kChSFmfrKLkaORoEu+F6Xmsh5TbclCqhlfGhG\\ngl8w0TDTna/sWwpWARQl+jadXfX8y5EbSTXTGtqiewMHYW+EwZpPzVg0FYcHbwH3\\nvGZPdR89s1/r7g37GoIwSStGO3g64XrOpsG+8Ld65QKBgQD8vuPET2vQIydK1d3S\\nImXrkoBoaTfbXx9uV19qJVuhvSdIeVWO3W8HfiMbiv99auUWO7PfEAhQx6c6ORKj\\nzFdM82ito0MkS0Xo0ILBR0QVHiHoOqmZR0GBkIEUtVBUq+nZTCicWJAD12cJIxAO\\nenU8BGAymxlF+jM7MJUJ/ijgvQKBgQC/+dAb99ixCZs2UCBwZ5rYpaX41k+sYe/K\\n8osMJEFzKgV4S60fSid3d6ajrIs2fF7ngGg8w/v+A/bzE82x+pqtKAGE0VlIh6D/\\nQVpFLIGXpYrinBVyX6a62YQb4RkjzBA3HN9jB/eTu5rmxARloQ/DRoh0VQpyppnC\\nDZv57Iy8zwKBgHrUoojDOFg83VmnOlhnUzT7S+ByUi0Qu4u6dqp1YWTnMnIsVYJK\\n5yyzBojaMnRXQOJfPXlIp2HqxcCr//0Oz9ab7OGGGJlI477TptgbtGC29i+QYuAV\\nGybGfZT80P91VP6/3nStLcBQLMjp+2Gt7c+vKLkvW0cA42j+oU/r7x3ZAoGBAL4u\\nILhUQ9q+hYC8yCYSvRe6oj1tMei37PHEbXNNx3jrPBf8ADlrIMX9RpwGprMHao00\\nbA8mqFDwZIhSKggTF4BKjZaiPizYD+pPN7onaQpt+LSdo7F2iJm6OmHUES+hTL8M\\nX1Cf5+f2hnHt5d04PYFaMnvsczk5SkEvckGY0aOJAoGBAK+YAJwbalniCLfhsa6q\\n613/mNK1651ZQFd6XAnVSz3O3UKMV85t09aWSjbnd0iR/F3xSzgt52OU4eZVjjMa\\nIhjNmJUj1cdDtKXq7NI05XMjw+lBQ+RvuumykrNVjo1o8fNL+7Y66zun29uSl8zt\\nFafE0Qf+4r8MEjjzL31naXT0\\n-----END PRIVATE KEY-----\\n", "client_email": "protacloud@protacloud.iam.gserviceaccount.com", "client_id": "113858572627345027036", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://accounts.google.com/o/oauth2/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/protacloud%40protacloud.iam.gserviceaccount.com"}'''  # NOQA


def _init_credential():
  if G_ENV_VALUE not in os.environ or G_ENV_GRPC not in os.environ:
    f = tempfile.NamedTemporaryFile(mode='w', delete=False)
    f.write(PROTACLOUD_CREDENTIALS_DATA)
    f.close()
    os.environ[G_ENV_VALUE] = f.name
    os.environ[G_ENV_GRPC] = 'true'


_init_credential()


import google.cloud.datastore  # NOQA


DEFAULT_KIND = '''default'''

__DATA__ = {}


class GoogleCloudService(object):
  KIND_OF_DATASTORE = 'Datastore'

  def __init__(self):
    self._datastore = self._init_datastore()
    self._datastore_batch = self._datastore.batch()
    self._private_key = None

  def _init_datastore(self):
    return google.cloud.datastore.Client()

  def _convert_entity_to_dict(self, data):
    dict_data = {}
    for key, value in data.items():
      if isinstance(value, google.cloud.datastore.Entity):
        dict_data[key] = self._convert_entity_to_dict(value)
      else:
        dict_data[key] = value
    return dict_data

  def key(self, *path_args, **kwargs):
    return self._datastore.key(*path_args, **kwargs)

  def _fetch(self, query, *args, **kwargs):
    return query.fetch(*args, **kwargs)

  def _search(self, kind, parent_key, namespace, filters, orders, limit):
    order_list = []
    logging.info("NNNN\nK:%s\nP:%s\nN:%s", kind, parent_key, namespace)
    print("NNNN\nK:%s\nP:%s\nN:%s", kind, parent_key, namespace)
    query = self._datastore.query(namespace=namespace,
                                  ancestor=parent_key,
                                  kind=kind if filters else None)
    for key, operator, value in filters:
      logging.info("NNN FILTER: %s, %s, %s", key, operator, value)
      print("NNN FILTER: %s, %s, %s", key, operator, value)
      query.add_filter(key, operator, value)
    for order in orders:
      prop, operator = order
      if operator:
        order_list.append(prop)
      else:
        order_list.append('-' + prop)
    query.order = order_list
    ret = self._fetch(query, limit=limit)
    return list(ret)

  def search(self, kind, parent_key, namespace, filters, orders, limit):
    data = self._search(kind, parent_key, namespace,
                        filters, orders, limit)
    data_list = []
    for data_entity in data:
      data_list.append(self._convert_entity_to_dict(data_entity))
    return data_list


__K_CLOUD__ = '''_c'''
__DATA__[__K_CLOUD__] = GoogleCloudService()


def _get_cloud_service():
  return __DATA__[__K_CLOUD__]


# {{{ datastore


TOP_KEY = '_e'


def search(kind, namespace, parent_name=None, filters=None,
           orders=None, limit=None):
  """
  filters : [[property, operator, value] ..]
  orders : [[property, T(ascending) / F(descending)], ..]
  """
  try:
    kind = kind or DEFAULT_KIND
    _sv = _get_cloud_service()
    _grandparent_key = _sv.key(TOP_KEY, kind,
                               namespace=namespace)
    print("G: ", _grandparent_key)
    _parent_key = None
    if parent_name:
      _parent_key = _sv.key(TOP_KEY, parent_name,
                            parent=_grandparent_key,
                            namespace=namespace)
      print("P: ", _parent_key)
    filters = filters or []
    orders = orders or []
    ret_v = _sv.search(kind, _parent_key or _grandparent_key, namespace,
                       filters, orders, limit)
    return ret_v
  except Exception:
    logging.warn(
        "Raise error while search data. Key: %s, Namespace: %s, Filters : %s",
        parent_name, namespace, filters, exc_info=True)
