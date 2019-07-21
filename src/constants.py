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
else:
  THIRD_BASE_URL = '''http://api.mib.io/v1/'''
  BASE_URL = '''http://api.mib.io/i/v1/'''
