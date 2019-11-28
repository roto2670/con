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
  SUPREMA_ADDR = '''http://127.0.0.1:5556'''
  REG_HUB_ID = '''463d638edc74a0b5feaf7507f0ecb7ca'''
  REG_ACCOUNT_ID = '''9cba31e20237eb4445f27b288dbe1c44'''
  BEACON_SPEC = '''9cba31e2-0237-eb44-45f2-7b288dbe1c44'''
else:
  THIRD_BASE_URL = '''http://172.16.5.4/v1/'''
  BASE_URL = '''http://172.16.5.4/i/v1/'''
  SUPREMA_ADDR = '''http://127.0.0.1:5556'''
  REG_HUB_ID = '''bc298b66bd67a950a49bdd64b09d37a0'''  # Galaxy A30
  REG_ACCOUNT_ID = '''d526b46a854d018d355b90ee2527fd4e'''
  BEACON_SPEC = '''d526b46a-854d-018d-355b-90ee2527fd4e'''

ORG_ID = '''ac983bfaa401d89475a45952e0a642cf'''
KIND_IPCAM = '''ipcam'''
KIND_SPEAKER = '''speaker'''
KIND_ROUTER = '''router'''
