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
  LOCAL_HUB_CLI_ADDR = '''http://192.168.0.14/v1/'''
  LOCAL_HUB_CLI_GID = '''74e6788846294397c9616c502daad659'''
else:
  THIRD_BASE_URL = '''http://api.mib.io/v1/'''
  BASE_URL = '''http://api.mib.io/i/v1/'''
  #TODO:
  LOCAL_HUB_CLI_ADDR = '''http://123.123.123.123/v1/'''
  LOCAL_HUB_CLI_GID = ''''''

ORG_ID = '''ac983bfaa401d89475a45952e0a642cf'''
