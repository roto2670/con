# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


IS_DEV = True

if IS_DEV:
  THIRD_BASE_URL = '''http://192.168.0.14/v1/'''
  BASE_URL = '''http://192.168.0.14/i/v1/'''
  LOCAL_HUB_CLI_ADDR = '''https://192.168.1.224:443'''
  SUPREMA_ADDR = '''http://127.0.0.1:5556'''
else:
  THIRD_BASE_URL = '''http://172.16.5.4/v1/'''
  BASE_URL = '''http://172.16.5.4/i/v1/'''
  LOCAL_HUB_CLI_ADDR = '''https://172.16.5.10:443'''
  SUPREMA_ADDR = '''http://127.0.0.1:5556'''

ORG_ID = '''ac983bfaa401d89475a45952e0a642cf'''

