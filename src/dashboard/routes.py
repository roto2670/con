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

import os, stat
import json
import uuid
import datetime
import logging

from flask import render_template, request, redirect  # noqa : pylint: disable=import-error
from flask_login import current_user  # noqa : pylint: disable=import-error
from flask import make_response

import util
import base.routes
import in_config_apis
from dashboard import count
from dashboard import blueprint
from constants import ORG_ID


NOTICE_COMMON_FILE_NAME = '''notice'''
SCHEDULE_COMMON_FILE_NAME = '''schedule'''
LOCATION_MAP_COMMON_FILE_NAME = '''location.png'''
LOCATION_MAP_URI = "/dashboard/static/location/{org_id}/{file_name}"


def _get_download_csv_response(csv_str, filename):
  resp = make_response(csv_str, 200)
  resp.headers['Cache-Control'] = 'no-cache'
  resp.headers['Content-Type'] = 'text/csv'
  resp.headers['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
  resp.headers['Content-Length'] = len(csv_str)
  return resp


@blueprint.route('/testcheck/bus', methods=['GET'])
@util.require_login
def default_test_bus():
  return json.dumps(count.test())


@blueprint.route('/testcheck', methods=['GET'])
@util.require_login
def default_test():
  return json.dumps(count.test_count())


@blueprint.route('/', methods=['GET'])
@util.require_login
def default_route():
  emergency_cache = count.get_emergency_info()
  notice_list = _get_notice_list_summary()
  schedule_list = _get_schedule_list_summary()
  return render_template("dashboard_home.html",
                         emergency=emergency_cache[count.IS_EMERGENCY_KEY],
                         time_msg=emergency_cache[count.TIME_MSG_KEY],
                         date_msg=emergency_cache[count.DATE_MSG_KEY],
                         notice_list=notice_list,
                         schedule_list=schedule_list)


@blueprint.route('/emergency', methods=['POST'])
@util.require_login
def default_emergency():
  cur_time = request.form.get('cur_time')
  cur_date = request.form.get('cur_date')
  is_emergency = json.loads(request.form.get('emergency'))
  return count.set_emergency(is_emergency, cur_time, cur_date)


@blueprint.route('/count', methods=['GET'])
@util.require_login
def default_count():
  return count.default_count()


@blueprint.route('/count/detail', methods=['GET'])
@util.require_login
def detail_count():
  return count.detail_count()


@blueprint.route('/count/reset', methods=['GET'])
@util.require_login
def reset_count():
  return count.clear_all()


@blueprint.route('/count/settings/entrance', methods=['GET'])
@util.require_login
def default_count_setting_page():
  return count.device_list()


@blueprint.route('/count/settings/<device_id>', methods=['POST'])
@util.require_login
def default_count_setting(device_id):
  return count.set_device(device_id)


@blueprint.route('/device/refresh', methods=['GET'])
@util.require_login
def default_refresh_device():
  org_id = current_user.organization_id
  # TODO: Refresh beacon list to apiserver?
  return redirect("/dashboard/count/settings")


@blueprint.route('/bus/settings', methods=['POST'])
@util.require_login
def set_bus_settting():
  # bus_user_id from facestation, bus_beacon_id from mib
  bus_user_id = request.form.get('bus_user_id')
  bus_user_name = request.form.get('bus_user_name')
  bus_beacon_id = request.form.get('bus_beacon_id')
  return count.set_bus_setting(bus_user_id, bus_user_name, bus_beacon_id)


@blueprint.route('/bus/delete/<_id>/beacon/<bus_beacon_id>', methods=['GET'])
@util.require_login
def delete_bus_settting(_id, bus_beacon_id):
  return count.delete_bus_setting(_id, bus_beacon_id)


@blueprint.route('/count/settings/delete/<device_id>/typ/<typ>', methods=['GET'])
@util.require_login
def default_count_delete(device_id, typ):
  return count.delete_device(device_id, int(typ))


@blueprint.route('/count/settings/equip/kind/<equip_key>', methods=['POST'])
@util.require_login
def default_equip_operator_count_setting(equip_key):
  value = request.form.get('equip_worker_count')
  logging.info("Set euqipment operator count. User : %s", current_user.email)
  return count.set_equip_operator_count(equip_key, value)


@blueprint.route('/count/worker/counting/<key>', methods=['GET'])
@util.require_login
def get_worker_count(key):
  worker_count = count.get_worker_count(int(key))
  return json.dumps(worker_count)


@blueprint.route('/count/worker/counting/total', methods=['GET'])
@util.require_login
def get_total_worker_count():
  total_worker_count = count.get_total_worker()
  return json.dumps(total_worker_count)


@blueprint.route('/count/covid/counting/each', methods=['GET'])
@util.require_login
def get_covid_count():
  """
  Request
    ex) /count/covid/counting/each?count=1,2,30,31,32
  Response
    ex) {"1": 10, "2": 5, "30": 20, "31": 50, "32": 20}
  """
  req_args = request.args
  count_key = req_args.get("count", "")
  _count = {}
  if count_key:
    for key in count_key.split(","):
      _count[key] = count.get_worker_count(key)
  return json.dumps(_count)


@blueprint.route('/count/covid/counting/total', methods=['GET'])
@util.require_login
def get_total_covid_count():
  """
  Request
    ex) /count/covid/counting/total?count=1,2,3,4
  Response
    ex) 85
  """
  req_args = request.args
  count_key = req_args.get("count", "")
  _total_count = 0
  if count_key:
    _total_count = count.get_total_worker_count(count_key.split(","))
  return json.dumps(_total_count)


@blueprint.route('/count/counting/total', methods=['GET'])
def get_total_count():
  """
  Request
    ex) /count/counting/total
  Response
    ex) {
          "worker": {"at1": 0, "at2": 0},
          "equipment" : {"at1": 0, "at2": 0},
          "total": {"at1": 0, "at2": 0, "worker": 0, "equipment": 0, "total": 0}
        }
  """
  data = count.get_total_count()
  return json.dumps(data)


@blueprint.route('/count/equip/counting/<key>', methods=['GET'])
@util.require_login
def get_equip_count(key):
  equip_count = count.get_equip_count(int(key))
  return json.dumps(equip_count)


@blueprint.route('/count/equip/counting/total', methods=['GET'])
@util.require_login
def get_total_equip_count():
  total_equip_count = count.get_total_equip()
  return json.dumps(total_equip_count)


@blueprint.route('/count/worker/list/<key>', methods=['GET'])
@util.require_login
def get_worker_list(key):
  worker_list = count.get_all_workers(key)
  operator_list = count.get_all_equip_operators(key)
  return render_template("worker_list.html", workers=worker_list, ap=key,
                         operators=operator_list, kind=count.GADGET_INFO)


@blueprint.route('/count/equip/list/<key>', methods=['GET'])
@util.require_login
def get_equip_list(key):
  equip_list = count.get_all_equips(key)
  count_equip_list = count.get_equip_operator_count_settings()
  return render_template("equip_list.html", equips=equip_list,
                         kind=count.GADGET_INFO, ap=key,
                         equip_setting_list = count_equip_list)


@blueprint.route('/count/worker/list/download/<key>', methods=["GET"])
@util.require_login
def download_current_worker_list(key):
  worker_list = count.get_all_workers(key)
  operator_list = count.get_all_equip_operators(key)
  filename = "AT{} Worker List_{}".format(key,
                                          str(in_config_apis.get_servertime()))
  csv_str = "\uFEFF"
  csv_str += "ID,Name,Group,EntranceTime,WorkingTime\n"
  for k, v in worker_list.items():
    if v and v['event_time']:
      working_time = base.routes.during_time(v['event_time'])
      r_str = "{},{},{},{},{}\n".format(v['user_id']['user_id'],
                                        v['user_id']['name'],
                                        v['user_group_id']['name'],
                                        v['event_time'],
                                        str(working_time).replace(",", " "))
    csv_str += r_str
  for k, v in operator_list.items():
    if v and v['event_time']:
      working_time = base.routes.during_time(v['event_time'])
      r_str = "{},{},{},{},{}\n".format(v['device_name'],
                                        v['device_name'],
                                        count.GADGET_INFO[v['tag']],
                                        v['event_time'],
                                        str(working_time).replace(",", " "))
    csv_str += r_str
  return _get_download_csv_response(csv_str, filename)


@blueprint.route('/count/equip/list/download/<key>', methods=["GET"])
@util.require_login
def download_current_equip_list(key):
  equip_list = count.get_all_equips(key)
  count_equip_list = count.get_equip_operator_count_settings()
  filename = "AT{} Equip List_{}".format(key,
                                         str(in_config_apis.get_servertime()))
  csv_str = "\uFEFF"
  csv_str += "Name,Kind,Count,EntranceTiem,WorkingTime\n"
  for k, v in equip_list.items():
    if v and v['event_time']:
      working_time = base.routes.during_time(v['event_time'])
      count_kind = "Yes" if v['tag'] in count_equip_list else ""
      r_str = "{},{},{},{},{}\n".format(v['device_name'],
                                        count.GADGET_INFO[v['tag']],
                                        count_kind,
                                        v['event_time'],
                                        str(working_time).replace(",", " "))
    csv_str += r_str
  return _get_download_csv_response(csv_str, filename)


@blueprint.route('/count/worker/list/<key>/<worker_id>', methods=['GET'])
@util.require_login
def remove_woker_in_list(key, worker_id):
  count.delete_in_worker(ORG_ID, key, worker_id)
  return redirect("/dashboard/count/worker/list/{}".format(key))


@blueprint.route('/count/equip/list/<key>/<equip_id>/<tag>', methods=['GET'])
@util.require_login
def remove_equip_in_list(key, equip_id, tag):
  count.delete_in_equip(ORG_ID, key, equip_id, tag)
  return redirect("/dashboard/count/equip/list/{}".format(key))


@blueprint.route('/location', methods=['GET'])
@util.require_login
def default_location():
  return render_template("location.html")


@blueprint.route('/location/view', methods=['GET'])
@util.require_login
def get_location_map():
  map_data = in_config_apis.get_latest_location_map()
  uri = ""
  if map_data:
    uri = map_data.file_path
  return uri


@blueprint.route('/location/upload', methods=['POST'])
@util.require_login
def upload_location_map():
  upload_file = request.files['file']
  content = upload_file.read()
  base_path = util.get_static_path("dashboard")
  org_path = os.path.join(base_path, 'location',
                          current_user.organization_id)
  if not os.path.exists(org_path):
    os.makedirs(org_path)
  file_name = "{}.png".format(uuid.uuid4().hex)
  file_path = os.path.join(org_path, file_name)
  if os.path.exists(file_path):
    os.remove(file_path)
  with open(file_path, 'wb') as f:
    f.write(content)
  os.chmod(file_path, stat.S_IREAD)
  uri = LOCATION_MAP_URI.format(org_id=current_user.organization_id,
                                file_name=file_name)
  in_config_apis.create_map_data(uri)
  return uri


@blueprint.route('/worker_logs', methods=["GET"])
@util.require_login
def get_enterence_worker_log():
  return render_template("worker_logs.html")


@blueprint.route('/equip_logs', methods=["GET"])
@util.require_login
def get_enterence_equip_log():
  return render_template("equip_logs.html")


def _convert_data(data_dict):
  ret_data = {
    "total": data_dict.total,
    "next_page": data_dict.next_num if data_dict.next_num is not None else 0,
    "pages": data_dict.pages
  }
  ret_list = []
  for data in data_dict.items:
    _data = {
        "worker_id": data.worker_id,
        "worker_name": data.worker_name,
        "worker_group": data.worker_group,  # department
        "event_time": str(data.event_time),
        "inout": data.inout,
        "access_point": data.access_point,
        "typ": data.typ,  # violation
        "device_name": data.device_name
    }
    ret_list.append(_data)
  ret_data['data_list'] = ret_list
  return ret_data


@blueprint.route('/search/covid/worker', methods=["GET"])
@util.require_login
def get_covid_worker_search_page():
  if request.method == "GET":
    req_args = request.args
    page_number = req_args.get("num", None)
    worker_id = req_args.get("wid", None)
    worker_name = req_args.get("wname", None)
    department = req_args.get("depart", None)
    inout = req_args.get("inout", None)
    location = req_args.get("locate", None)
    violation = req_args.get("violation", None)
    raw_datetime_list = req_args.get("datetime", "")
    datetime_list = json.loads(raw_datetime_list)
    worker_log_list = in_config_apis.search_worker_log(worker_id, worker_name,
                                                       datetime_list,
                                                       int(location), int(inout),
                                                       str(violation),
                                                       department,
                                                       int(page_number))
    ret_list = _convert_data(worker_log_list)
    return json.dumps(ret_list)


@blueprint.route('/search/worker', methods=["GET", "POST"])
@util.require_login
def get_worker_search_page():
  if request.method == "GET":
    return render_template("search_worker_prepare.html")
  else:
    _id = request.form.get('userid')
    name = request.form.get('username')
    group = request.form.get('group')
    ap = request.form.get('ap')
    inout = request.form.get('inout')
    violation = request.form.get('violation')
    raw_datetime_list = request.form.get('datetime')
    datetime_list = json.loads(raw_datetime_list)
    page = request.form.get('page')
    next_num = request.form.get('next_num')
    prev_num = request.form.get('prev_num')
    page_num = None
    if page == "1":
      page_num = prev_num
    elif page == "2":
      page_num = next_num

    worker_log_list = in_config_apis.search_worker_log(_id, name, datetime_list,
                                                       int(ap), int(inout),
                                                       violation, group, page_num)
    data = {
      "id": _id, "name": name, "ap": ap, "inout": inout, "group": group,
      "violation": violation, "datetime": raw_datetime_list
    }
    start_date = "-".join(datetime_list[0].split(",")[:3])
    start_time = ":".join(datetime_list[0].split(",")[3:])
    end_date = "-".join(datetime_list[1].split(",")[:3])
    end_time = ":".join(datetime_list[1].split(",")[3:])
    start = "{} {}".format(start_date, start_time)
    end = "{} {}".format(end_date, end_time)
    return render_template("search_worker.html", log_list=worker_log_list,
                           data=data, start_date=start, end_date=end)


@blueprint.route('/search/worker/download', methods=["GET"])
@util.require_login
def download_worker_log():
  _id = request.args.get('userid')
  name = request.args.get('username')
  group = request.args.get('group')
  ap = request.args.get('ap')
  inout = request.args.get('inout')
  violation = request.args.get('violation')
  datetime_list = request.args.get('datetime')
  datetime_list = json.loads(datetime_list)
  csv_log_list = in_config_apis.csv_worker_log(_id, name, datetime_list,
                                               int(ap), int(inout),
                                               violation, group)
  filename = "Worker Search_{}".format(str(in_config_apis.get_servertime()))
  csv_str = "\uFEFF"
  csv_str += "ID,Name,Department,Time,In/Out,Access,Violation,DeviceName\n"
  for r in csv_log_list:
    row_string = str(r)
    csv_str += row_string + "\n"
  return _get_download_csv_response(csv_str, filename)


@blueprint.route('/search/equip', methods=["GET", "POST"])
@util.require_login
def get_equip_search_page():
  if request.method == "GET":
    return render_template("search_equip_prepare.html",
                           kind_dict=count.GADGET_INFO)
  else:
    kind = request.form.get('kind')
    name = request.form.get('equipname')
    ap = request.form.get('ap')
    inout = request.form.get('inout')
    raw_datetime_list = request.form.get('datetime')
    datetime_list = json.loads(raw_datetime_list)
    page = request.form.get('page')
    next_num = request.form.get('next_num')
    prev_num = request.form.get('prev_num')
    page_num = None
    if page == "1":
      page_num = prev_num
    elif page == "2":
      page_num = next_num

    equip_log_list = in_config_apis.search_equip_log(name, kind, datetime_list,
                                                     int(ap), int(inout),
                                                     page_num)
    data = {
      "name": name, "ap": ap, "inout": inout, "kind": kind,
      "datetime": raw_datetime_list
    }
    start_date = "-".join(datetime_list[0].split(",")[:3])
    start_time = ":".join(datetime_list[0].split(",")[3:])
    end_date = "-".join(datetime_list[1].split(",")[:3])
    end_time = ":".join(datetime_list[1].split(",")[3:])
    start = "{} {}".format(start_date, start_time)
    end = "{} {}".format(end_date, end_time)
    return render_template("search_equip.html", log_list=equip_log_list,
                           kind_dict=count.GADGET_INFO, data=data,
                           start_date=start, end_date=end)


@blueprint.route('/search/equip/download', methods=["GET"])
@util.require_login
def download_equip_log():
  kind = request.args.get('kind')
  name = request.args.get('equipname')
  ap = request.args.get('ap')
  inout = request.args.get('inout')
  raw_datetime_list = request.args.get('datetime')
  datetime_list = json.loads(raw_datetime_list)
  csv_log_list = in_config_apis.csv_equip_log(name, kind, datetime_list,
                                              int(ap), int(inout))
  filename = "Equipments Search_{}".format(str(in_config_apis.get_servertime()))
  csv_str = "\uFEFF"
  csv_str += "Name,TypeName,TypeCode,Time,In/Out,Access,DeviceName\n"
  for r in csv_log_list:
    row_string = str(r)
    csv_str += row_string + "\n"
  return _get_download_csv_response(csv_str, filename)


def _get_notice_list_summary():
  notice_list = in_config_apis.get_notice_list()
  if len(notice_list.items) > 7:
    notice_list = notice_list.items[:7]
  else:
    notice_list = notice_list.items
  return notice_list


@blueprint.route('/board/notice/<notice_id>/show', methods=["GET"])
@util.require_login
def get_notice_content(notice_id):
  notice = in_config_apis.get_notice(int(notice_id))
  return render_template("show_notice.html", notice=notice)


@blueprint.route('/board/notice', methods=["GET", "POST"])
@util.require_login
def get_notice_list():
  if request.method == "GET":
    notice_list = in_config_apis.get_notice_list()
    return render_template("notice_list.html", notice_list=notice_list)
  else:
    page = request.form.get('page')
    next_num = request.form.get('next_num')
    prev_num = request.form.get('prev_num')
    page_num = None
    if page == "1":
      page_num = prev_num
    elif page == "2":
      page_num = next_num
    notice_list = in_config_apis.get_notice_list(int(page_num))
    return render_template("notice_list.html", notice_list=notice_list)


@blueprint.route('/board/notice/register', methods=["GET", "POST"])
@util.require_login
def register_notice():
  if request.method == "GET":
    return render_template("register_notice.html")
  else:
    title = request.form.get('title')
    category = request.form.get('category')
    writer = request.form.get('writer')
    department = request.form.get('department')
    upload_file = request.files['file']
    content = upload_file.read()

    if content:
      name = upload_file.filename
      base_path = util.get_static_path()
      org_path = os.path.join(base_path, 'dashboard', 'notice',
                              current_user.organization_id)
      if not os.path.exists(org_path):
        os.makedirs(org_path)
      file_path = os.path.join(org_path, NOTICE_COMMON_FILE_NAME + "_" + name)
      if os.path.exists(file_path):
        os.remove(file_path)
      with open(file_path, 'wb') as f:
        f.write(content)
      os.chmod(file_path, stat.S_IREAD)
      url = '/static/dashboard/notice/' + current_user.organization_id + \
          "/" + NOTICE_COMMON_FILE_NAME + "_" + name
    else:
      url = ""
    in_config_apis.create_notice_content(title, category, writer, department,
                                         url)
    return redirect("/dashboard/board/notice")


@blueprint.route('/board/notice/<notice_id>/delete', methods=["GET"])
@util.require_login
def delete_notice(notice_id):
  _notice = in_config_apis.get_notice(int(notice_id))
  if _notice.file_path:
    base_path = util.get_static_path()
    file_path = os.path.join(base_path, _notice.file_path)
    if os.path.exists(file_path):
      os.remove(file_path)
  in_config_apis.delete_notice(notice_id)
  return redirect("/dashboard/board/notice")


def _get_schedule_list_summary():
  schedule_list = in_config_apis.get_schedule_list()
  if len(schedule_list.items) > 7:
    schedule_list = schedule_list.items[:7]
  else:
    schedule_list = schedule_list.items
  return schedule_list


@blueprint.route('/board/schedule/<schedule_id>/show', methods=["GET"])
@util.require_login
def get_schedule_content(schedule_id):
  schedule = in_config_apis.get_schedule(int(schedule_id))
  return render_template("show_schedule.html", schedule=schedule)


@blueprint.route('/board/schedule', methods=["GET", "POST"])
@util.require_login
def get_schedule_list():
  if request.method == "GET":
    schedule_list = in_config_apis.get_schedule_list()
    return render_template("schedule_list.html", schedule_list=schedule_list)
  else:
    page = request.form.get('page')
    next_num = request.form.get('next_num')
    prev_num = request.form.get('prev_num')
    page_num = None
    if page == "1":
      page_num = prev_num
    elif page == "2":
      page_num = next_num
    schedule_list = in_config_apis.get_schedule_list(int(page_num))
  return render_template("schedule_list.html", schedule_list=schedule_list)


@blueprint.route('/board/schedule/register', methods=["GET", "POST"])
@util.require_login
def register_schedule():
  if request.method == "GET":
    return render_template("register_schedule.html")
  else:
    title = request.form.get('title')
    category = request.form.get('category')
    writer = request.form.get('writer')
    department = request.form.get('department')
    upload_file = request.files['file']
    content = upload_file.read()
    if content:
      name = upload_file.filename
      base_path = util.get_static_path()
      org_path = os.path.join(base_path, 'dashboard', 'schedule',
                              current_user.organization_id)
      if not os.path.exists(org_path):
        os.makedirs(org_path)
      file_path = os.path.join(org_path, SCHEDULE_COMMON_FILE_NAME + "_" + name)
      if os.path.exists(file_path):
        os.remove(file_path)
      with open(file_path, 'wb') as f:
        f.write(content)
      os.chmod(file_path, stat.S_IREAD)
      url = '/static/dashboard/schedule/' + current_user.organization_id + \
          "/" + SCHEDULE_COMMON_FILE_NAME + "_" + name
    else:
      url = ""
    in_config_apis.create_schedule_content(title, category, writer, department,
                                           url)
    return redirect("/dashboard/board/schedule")


@blueprint.route('/board/schedule/<schedule_id>/delete', methods=["GET"])
@util.require_login
def delete_schedule(schedule_id):
  _schedule = in_config_apis.get_schedule(int(schedule_id))
  if _schedule.file_path:
    base_path = util.get_static_path()
    file_path = os.path.join(base_path, _schedule.file_path)
    if os.path.exists(file_path):
      os.remove(file_path)
  in_config_apis.delete_schedule(schedule_id)
  return redirect("/dashboard/board/schedule")
