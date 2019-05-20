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

import random

MOCK_HUB_CACHE = {
  "4740d95c92355d968946db07d1671afd": {
    "id": "4740d95c92355d968946db07d1671afd",
    "uuid": "4510d10f41e07759",
    "status": 1,
    "name": "mibh(what)",
    "kind": "com.thenaran.rtos.m",
    "app_version": "0.1.21",
    "platform": "rtos",
    "model": "hubm",
    "locale": "locale",
    "system_version": "v3.2",
    "gadget_ids": [],
    "latest_version": "0.1.21",
    "issuer": "com.thenaran.skec",
    "beacons": [],
    "custom": {},
    "tags": []
  },
  "64598ab247e597fcb3cc44839d9ad63c": {
    "id": "64598ab247e597fcb3cc44839d9ad63c",
    "uuid": "ad078ca3e4bdcfa9",
    "status": 1,
    "name": "mibh(mock)",
    "kind": "com.thenaran.rtos.m",
    "app_version": "0.1.21",
    "platform": "rtos",
    "model": "hubm",
    "locale": "locale",
    "system_version": "v3.2",
    "gadget_ids": [],
    "latest_version": "0.1.21",
    "issuer": "com.thenaran.skec",
    "beacons": [
      {
        "uuid": "d3224588-8d09-a53b-268f-09977a9e418f",
        "major": -1,
        "minor": -1,
        "interval": 2
      },
      {
        "uuid": "f2d464da-2384-72a9-ac8a-5592e4d90835",
        "major": -1,
        "minor": -1,
        "interval": 2
      }
    ],
    "custom": {},
    "tags": []
  },
  "799b9f874bc1c50775233d2a0c00e388": {
    "id": "799b9f874bc1c50775233d2a0c00e388",
    "uuid": "240ac4a64c9e",
    "status": 1,
    "name": "mibh(4c9c)",
    "kind": "com.thenaran.rtos.m",
    "app_version": "0.1.21",
    "platform": "rtos",
    "model": "hubm",
    "locale": "locale",
    "system_version": "v3.2",
    "gadget_ids": [],
    "latest_version": "0.1.21",
    "issuer": "com.thenaran.skec",
    "beacons": [
      {
        "uuid": "897d4536-ad17-eb35-7c12-6cfeef2b6c4b",
        "major": -1,
        "minor": -1,
        "interval": 2
      },
      {
        "uuid": "f2d464da-2384-72a9-ac8a-5592e4d90835",
        "major": -1,
        "minor": -1,
        "interval": 2
      }
    ],
    "custom": {},
    "tags": []
  },
  "ada945f96840831219fe721fbcf9a7b8": {
    "id": "ada945f96840831219fe721fbcf9a7b8",
    "uuid": "b2398356a0d0f040",
    "status": 1,
    "name": "mibh(when)",
    "kind": "com.thenaran.rtos.m",
    "app_version": "0.1.21",
    "platform": "rtos",
    "model": "hubm",
    "locale": "locale",
    "system_version": "v3.2",
    "gadget_ids": [],
    "latest_version": "0.1.21",
    "issuer": "com.thenaran.skec",
    "beacons": [],
    "custom": {},
    "tags": []
  },
  "f68d061d27b49ae91523401b816a9ceb": {
    "id": "f68d061d27b49ae91523401b816a9ceb",
    "uuid": "f971d3d730fe5018",
    "status": 1,
    "name": "mibh(who)",
    "kind": "com.thenaran.rtos.m",
    "app_version": "0.1.21",
    "platform": "rtos",
    "model": "hubm",
    "locale": "locale",
    "system_version": "v3.2",
    "gadget_ids": [],
    "latest_version": "0.1.21",
    "issuer": "com.thenaran.skec",
    "beacons": [],
    "custom": {},
    "tags": []
  },
  "d8e6869fb17fd6d561a4f7c9f2393cda": {
    "id": "d8e6869fb17fd6d561a4f7c9f2393cda",
    "uuid": "18054b3aa99998d8",
    "status": 1,
    "name": "mibh(why)",
    "kind": "com.thenaran.rtos.m",
    "app_version": "0.1.21",
    "platform": "rtos",
    "model": "hubm",
    "locale": "locale",
    "system_version": "v3.2",
    "gadget_ids": [],
    "latest_version": "0.1.21",
    "issuer": "com.thenaran.skec",
    "beacons": [],
    "custom": {},
    "tags": []
  },
  "c05babe4c40386090db95ac2e544deee": {
    "id": "c05babe4c40386090db95ac2e544deee",
    "uuid": "1bb73079110526e8",
    "status": 1,
    "name": "mibh(how)",
    "kind": "com.thenaran.rtos.m",
    "app_version": "0.1.21",
    "platform": "rtos",
    "model": "hubm",
    "locale": "locale",
    "system_version": "v3.2",
    "gadget_ids": [],
    "latest_version": "0.1.21",
    "issuer": "com.thenaran.skec",
    "beacons": [],
    "custom": {},
    "tags": []
  }
}  # hub test data

MOCK_BEACON_CACHE = {
  "23083dde817b2fd416112733d6985baf": {
    "id": "23083dde817b2fd416112733d6985baf",
    "mac": "d5a25468161e",
    "name": "Testhafget",
    "kind": "mibs",
    "firmware_version": "1.3.9",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.3",
    "hub_id": "4740d95c92355d968946db07d1671afd",
    "account_id": "897d4536ad17eb357c126cfeef2b6c4b",
    "user_id": "0e3a549b05a5c5eadfed522a61b8a3df",
    "status": 0,
    "locale": "KR",
    "rssi": 0,
    "battery": 97,
    "custom": {},
    "tags": ["1"],
    "beacon_spec": {
      "uuid": "897d4536-ad17-eb35-7c12-6cfeef2b6c4b",
      "major": 1,
      "minor": 5234,
      "interval": 700,
      "during_second": 0
    }
  },
  "822c5303bcb71f54e891e5c493537aae": {
    "id": "822c5303bcb71f54e891e5c493537aae",
    "mac": "d70b402efafe",
    "name": "Beacon test",
    "kind": "mibs",
    "firmware_version": "1.3.8",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.2",
    "hub_id": "c05babe4c40386090db95ac2e544deee",
    "account_id": "897d4536ad17eb357c126cfeef2b6c4b",
    "user_id": "0b2023c3a692415c9bd6314cdbf8a0a8",
    "status": 1,
    "locale": "KR",
    "rssi": 0,
    "battery": 100,
    "custom": {},
    "tags": ["2"],
    "beacon_spec": {
      "uuid": "897d4536-ad17-eb35-7c12-6cfeef2b6c4b",
      "major": 2,
      "minor": 3814,
      "interval": 700,
      "during_second": 0
    }
  },
  "0cd28df214ddcc23a44abe080dc463a7": {
    "id": "0cd28df214ddcc23a44abe080dc463a7",
    "mac": "f9c38f6aa512",
    "name": "Beacon mock",
    "kind": "mibs",
    "firmware_version": "1.3.8",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.2",
    "hub_id": "c05babe4c40386090db95ac2e544deee",
    "account_id": "897d4536ad17eb357c126cfeef2b6c4b",
    "user_id": "0b2023c3a692415c9bd6314cdbf8a0a8",
    "status": 1,
    "locale": "KR",
    "rssi": 0,
    "battery": 100,
    "custom": {},
    "tags": ["3"],
    "beacon_spec": {
      "uuid": "897d4536-ad17-eb35-7c12-6cfeef2b6c4b",
      "major": 2,
      "minor": 381,
      "interval": 700,
      "during_second": 0
    }
  },
  "0010d38c17bb4ec66e5043fc5d75f0e8": {
    "id": "0010d38c17bb4ec66e5043fc5d75f0e8",
    "mac": "c79373039061",
    "name": "Beacon what",
    "kind": "mibs",
    "firmware_version": "1.3.8",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.2",
    "hub_id": "c05babe4c40386090db95ac2e544deee",
    "account_id": "f2d464da238472a9ac8a5592e4d90835",
    "user_id": "0b2023c3a692415c9bd6314cdbf8a0a8",
    "status": 1,
    "locale": "KR",
    "rssi": 0,
    "battery": 100,
    "custom": {},
    "tags": ["4"],
    "beacon_spec": {
      "uuid": "f2d464da-2384-72a9-ac8a-5592e4d90835",
      "major": 2,
      "minor": 33,
      "interval": 700,
      "during_second": 0
    }
  },
  "00163daabe25a08ea8f80e21ee476249": {
    "id": "00163daabe25a08ea8f80e21ee476249",
    "mac": "f14e18e672a5",
    "name": "Beacon when",
    "kind": "mibs",
    "firmware_version": "1.3.8",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.2",
    "hub_id": "c05babe4c40386090db95ac2e544deee",
    "account_id": "f2d464da238472a9ac8a5592e4d90835",
    "user_id": "0b2023c3a692415c9bd6314cdbf8a0a8",
    "status": 1,
    "locale": "KR",
    "rssi": 0,
    "battery": 100,
    "custom": {},
    "tags": ["5"],
    "beacon_spec": {
      "uuid": "f2d464da-2384-72a9-ac8a-5592e4d90835",
      "major": 1,
      "minor": 993,
      "interval": 700,
      "during_second": 0
    }
  },
  "003ac8dfa487a958b50b4eb734eede29": {
    "id": "003ac8dfa487a958b50b4eb734eede29",
    "mac": "e6c4f0e68f88",
    "name": "Beacon who",
    "kind": "mibs",
    "firmware_version": "1.3.8",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.2",
    "hub_id": "c05babe4c40386090db95ac2e544deee",
    "account_id": "f2d464da238472a9ac8a5592e4d90835",
    "user_id": "0b2023c3a692415c9bd6314cdbf8a0a8",
    "status": 1,
    "locale": "KR",
    "rssi": 0,
    "battery": 100,
    "custom": {},
    "tags": ["6"],
    "beacon_spec": {
      "uuid": "f2d464da-2384-72a9-ac8a-5592e4d90835",
      "major": 1,
      "minor": 1212,
      "interval": 700,
      "during_second": 0
    }
  },
  "003adf032a4727e89453a13347b3d9f2": {
    "id": "003adf032a4727e89453a13347b3d9f2",
    "mac": "e838140a4c69",
    "name": "Beacon how",
    "kind": "mibs",
    "firmware_version": "1.3.8",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.2",
    "hub_id": "c05babe4c40386090db95ac2e544deee",
    "account_id": "d32245888d09a53b268f09977a9e418f",
    "user_id": "0b2023c3a692415c9bd6314cdbf8a0a8",
    "status": 1,
    "locale": "KR",
    "rssi": 0,
    "battery": 100,
    "custom": {},
    "tags": ["7"],
    "beacon_spec": {
      "uuid": "d3224588-8d09-a53b-268f-09977a9e418f",
      "major": 2,
      "minor": 445,
      "interval": 700,
      "during_second": 0
    }
  },
  "00982357be27a0782ee9938e74d6f7f9": {
    "id": "00982357be27a0782ee9938e74d6f7f9",
    "mac": "ca589f7e9be1",
    "name": "Beacon where",
    "kind": "mibs",
    "firmware_version": "1.3.8",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.2",
    "hub_id": "c05babe4c40386090db95ac2e544deee",
    "account_id": "d32245888d09a53b268f09977a9e418f",
    "user_id": "0b2023c3a692415c9bd6314cdbf8a0a8",
    "status": 1,
    "locale": "KR",
    "rssi": 0,
    "battery": 100,
    "custom": {},
    "tags": ["8"],
    "beacon_spec": {
      "uuid": "d3224588-8d09-a53b-268f-09977a9e418f",
      "major": 2,
      "minor": 5,
      "interval": 700,
      "during_second": 0
    }
  },
  "009ec27cfd2a80c9aa72640f7cc13119": {
    "id": "009ec27cfd2a80c9aa72640f7cc13119",
    "mac": "cae18ee8fd7f",
    "name": "Beacon which",
    "kind": "mibs",
    "firmware_version": "1.3.8",
    "model_number": 0,
    "model_name": "v4",
    "sdk_version": "0.2",
    "hub_id": "c05babe4c40386090db95ac2e544deee",
    "account_id": "d32245888d09a53b268f09977a9e418f",
    "user_id": "0b2023c3a692415c9bd6314cdbf8a0a8",
    "status": 1,
    "locale": "KR",
    "rssi": 0,
    "battery": 100,
    "custom": {},
    "tags": ["9"],
    "beacon_spec": {
      "uuid": "d3224588-8d09-a53b-268f-09977a9e418f",
      "major": 1,
      "minor": 530,
      "interval": 700,
      "during_second": 0
    }
  }
}

HID_LIST = list(MOCK_HUB_CACHE.keys())

GID_LIST = list(MOCK_BEACON_CACHE.keys())

TIME_LIST = [1558074462.1417236, 1558074482.108364,
             1558074530.9247077, 1558074572.3208876,
             1558074907.1522868, 1558075002.1417236,
             1558075006.108364, 1558075009.9247077,
             1558075016.3208876, 1558075022.1522868]

QID_START = 111111111111111
QID_END = 999999999999999


def make_get_detected_beacons(hid):
  dist_data_list = []
  main_form = {}
  if hid in MOCK_HUB_CACHE:
    if MOCK_HUB_CACHE[hid]['custom']:
      for count in range(0, random.randrange(10)):
        dist_data = {}
        dist_data['_t'] = TIME_LIST[count]
        dist_data['gid'] = random.choice(GID_LIST)
        dist_data['hid'] = hid
        dist_data['dist'] = round(random.uniform(0, 30), 1)
        dist_data_list.append(dist_data)
  dist_data_list = sorted(dist_data_list, key=lambda k: k["_t"])
  main_form['query_id'] = random.randrange(QID_START, QID_END)
  main_form['data'] = dist_data_list
  return main_form


def make_get_detected_hubs(gid):
  dist_data_list = []
  main_form = {}
  if gid in MOCK_BEACON_CACHE:
    for count in range(0, random.randrange(10)):
      dist_data = {}
      dist_data['_t'] = TIME_LIST[count]
      dist_data['gid'] = gid
      dist_data['hid'] = random.choice(HID_LIST)
      dist_data['dist'] = round(random.uniform(0, 30), 1)
      dist_data_list.append(dist_data)
  dist_data_list = sorted(dist_data_list, key=lambda k: k["_t"])
  main_form['query_id'] = random.randrange(QID_START, QID_END)
  main_form['data'] = dist_data_list
  return main_form


def update_hub_location_mock(hub_obj):
  hid = hub_obj['id']
  if hid in MOCK_HUB_CACHE:
    MOCK_HUB_CACHE[hid]['custom'] = hub_obj['custom']
    return True
  return False


def beacon_info(beacon_id):
  if beacon_id in MOCK_BEACON_CACHE:
    return MOCK_BEACON_CACHE[beacon_id]
  return None


def scanner_list():
  return list(MOCK_HUB_CACHE.values())


def beacon_list():
  return list(MOCK_BEACON_CACHE.values())

