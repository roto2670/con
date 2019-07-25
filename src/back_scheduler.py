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

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from third import suprema_apis
import dash_apis
import in_config_apis
import constants

SCHED = BackgroundScheduler()


def init():
  # worker_config_list = get_all_woreker_config()
  # worker_count_init(worker_config_list)
  # SCHED.start()
  pass


def worker_count_init(worker_config_list):
  for config_data in worker_config_list:
    ret = suprema_apis.login_sup_server(config_data.suprema_id,
                                        config_data.suprema_pw,
                                        config_data.base_url,
                                        config_data.organization_id)
    if ret:
      logging.info("Start Scheduler of url : %s, org : %s",
                   config_data.base_url, config_data.organization_id)
      suprema_apis.set_last_id_cache(config_data.organization_id,
                                     config_data.last_data_id)
      suprema_apis.set_info(config_data.suprema_id,
                            config_data.suprema_pw,
                            config_data.base_url,
                            config_data.organization_id)
      scheduler_main_worker(config_data.organization_id,
                            config_data.server_interval)


def scheduler_main_worker(org_id, server_interval, update=None):
  scheduler_id = '{}_worker_count'.format(org_id)
  if update:
    SCHED.reschedule_job(scheduler_id, None, 'interval',
                         seconds=server_interval)
  else:
    SCHED.add_job(lambda: suprema_apis.set_event(org_id), 'interval',
                  seconds=server_interval, id=scheduler_id)


def get_all_woreker_config():
  config_data_list = in_config_apis.get_all_suprema_config()
  if not config_data_list:
    logging.warning('config data is not exist in DB')
  return config_data_list
