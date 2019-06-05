# -*- coding: utf-8 -*-
#
# Copyright 2017-2018 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from third import suprema_apis
from dash import routes as dash_routes
import dash_apis
import in_config_apis

SCHED = BackgroundScheduler()


def init():
  worker_config_list = get_all_woreker_config()
  equip_config_list = get_all_equip_config()
  worker_count_init(worker_config_list)
  equip_count_init(equip_config_list)
  SCHED.start()


def worker_count_init(worker_config_list):
  for config_data in worker_config_list:
    ret = suprema_apis.login_sup_server(config_data.suprema_id,
                                        config_data.suprema_pw,
                                        config_data.base_url,
                                        config_data.organization_id)
    if ret:
      logging.info("Start Scheduler of url : %s, org : %s",
                   config_data.base_url, config_data.organization_id)
      scheduler_main_worker(config_data.organization_id,
                            config_data.server_interval)


def equip_count_init(equip_config_list):
  for config_data in equip_config_list:
    scheduler_main_equip(config_data.organization_id,
                         config_data.kind,
                         config_data.server_interval)


def scheduler_main_worker(org_id, server_interval, update=None):
  scheduler_id = '{}_worker_count'.format(org_id)
  if update:
    SCHED.reschedule_job(scheduler_id, None, 'interval',
                         seconds=server_interval)
  else:
    SCHED.add_job(lambda: suprema_apis.set_event(org_id), 'interval',
                  seconds=server_interval, id=scheduler_id)


def scheduler_main_equip(org_id, kind, server_interval, update=None):
  scheduler_id = '{}_equip_count'.format(org_id)
  if update:
    SCHED.reschedule_job(scheduler_id, None, 'interval',
                         seconds=server_interval)
  else:
    SCHED.add_job(lambda: beacon_detect_scheduler(kind, org_id), 'interval',
                  seconds=server_interval, id=scheduler_id)


def get_all_woreker_config():
  config_data_list = in_config_apis.get_all_suprema_config()
  if not config_data_list:
    logging.warning('config data is not exist in DB')
  return config_data_list


def get_all_equip_config():
  config_data_list = in_config_apis.get_all_location_config()
  if not config_data_list:
    logging.warning('config data is not exist in DB')
  return config_data_list


def beacon_detect_scheduler(kind, org_id):
  scanner_list = dash_apis.get_scanner_list(kind)
  for scanner in scanner_list:
    get_detcted_data(scanner, org_id, None)


def get_detcted_data(scanner, org_id, query_id=None):
  detect_result = dash_apis.get_detected_beacons(scanner['id'], query_id)
  dash_routes.set_total_equip(org_id, scanner['id'], detect_result)
  if len(detect_result['data']) >= 30:
    get_detcted_data(scanner, org_id, detect_result['query_id'])
  else:
    logging.info("Server has no more Detected data")