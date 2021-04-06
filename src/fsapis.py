import json
import work_apis
import logging
import requests
import time

IS_UPDATE_FIRESTORE = True
JSON_HEADERS = {}
JSON_HEADERS['Content-Type'] = 'application/json'

ACTIVITI_ID = {
  "101": "d61d00bf58304ffa9eca871495eb5b6e",
  "102": "4542c53f38f84d98aaebae1d885fb7cc",
  "103": "cc754efc5a6e41d9a36942a8a2d119cb",
  "104": "fb15104964fd4f55aa7c063f237b8378",
  "105": "e73cf80d1e9149a19f0f585b107e1c2e",
  "106": "424043dc2b1842e782838dfca79f6da1",
  "107": "01bffd8fb74c4e90a7f5c2740e61588a",
  "108": "a1a8a5ae4fb743cf9594ca2137532592",
  "109": "fd00a8d2fc6444c4a683b1218c99414a",
  "110": "a29d1fa8cde548949142a8eaf3da188a",
  "111": "40824508fdb54641b023d9109c506379",
  "112": "28f2ee6979a54f8b9ecec463f09b3569",
  "113": "8bbe92b3bdaa4aba8134e8c8aa68c577",
  "114": "72eaf22cb59e4773b6b09a2608075551",
  "200": "fc29fc12cb3d479a8519ca3c673b26fd",
  "201": "63a073da9d8e4dd9b29af574cc016895",
  "202": "8244fca2be8d4f72844ac69f47c127ee",
  "203": "cb0c8baa663f4045aa47286ae08f79e7",
  "204": "020e51aa2778474cafe67f16ebb7c1b0",
  "205": "e90b21d2111f47eeaca32add35fc3f59",
  "206": "02df864e8cc14aca98cf110ec4bda518",
  "207": "3c0dc4a0aa6e45cba0372b14de4da258",
  "208": "b4aa0402de094487859c1ae26fd70862",
  "300": "beb735ed4e1d43669919e5ab8e9de9af",
  "301": "afda495eba0348959ff31fa53f17e2ef",
  "302": "cb2674f5a2044e3a866d028e2db03894",
  "303": "90847dff76ac438a91910fe1ebf3ec9b",
  "304": "b496da8361e94699b99b5df75ab91420",
  "305": "e12ba13c63e24ff38e3d73f6ae557e3a",
  "306": "20b9cbd7911644efbd3877f0fc0c12b3",
  "307": "4e4516afea7c452dbd63b1161310c03b",
  "308": "be2a377a64174e578a31555be645d3b2",
  "309": "ca0491c9137a48eab0df0595e681748f",
  "310": "b409782dd33b4471816f28238b9c43d9",
  "209": "421ab768dc7543c6aee5011a94d49dea",
  "210": "2b8e705e9e4a49a6bbedb253fbedc41d",
  "212": "a20ef5010f28436e8d462490cd6be688",
  "213": "a6c21ef1df6b4462b5e0378bfb84f185",
  "214": "1dde920b207540acb33c233725b55e8f",
  "215": "bc8405c6996644a58c8b0a922414760e",
  "216": "c52ce0d40b034c21aced5f9883febea1",
  "217": "b46cd67f29c74b13a8e5c5e487be200e"}


WORK_ADD = "/fs/work/add"
WORK_UPDATE = "/fs/work/update"
WORK_REMOVE = "/fs/work/remove"
WORK_START = "/fs/work/start"
WORK_FINISH = "/fs/work/finish"
WORK_PAUSE = "/fs/work/pause"
WORK_RESUME = "/fs/work/resume"


def send(data, uri):
  #url = "https://172.16.5.8:5678" + uri
  url = "http://172.16.5.8:5678" + uri
  resp = requests.post(url, headers=JSON_HEADERS, data=json.dumps(data), verify=False)
  if resp.ok:
    value = resp.json()
    logging.info("Update android key resp : %s", value)
    return True
  else:
    logging.warning("Failed to send Response. Code : %s, Text : %s",
                    resp.status_code, resp.text)
    return None

def convert_dt_to_t(dt):
  if not dt:
    return None
  return time.mktime(dt.timetuple())


def add_work_firestore(data, is_finish=False):
  if not IS_UPDATE_FIRESTORE:
    return None

  try:
    activity = work_apis.get_activity_by_activity_id(data['typ'])
    activity_id = ACTIVITI_ID[str(data['typ'])]
    blast_data = work_apis.get_blast(data['blast_id'])
    tunnel_id = blast_data.tunnel_id
    new_data = {
        # "plan": "",  # TODO:
        "id": data['id'],
        "blast_id": data['blast_id'],
        "tunnel_id": tunnel_id,
        "activity_id": activity_id,
        "activity_name": activity.name,
        "start_at": None,
        "end_at": None,
        "resources": [],
        "input_values": [],
        "is_finish": is_finish,
        "ts": convert_dt_to_t(data['last_updated_time'])
    }
    if is_finish:
      new_data['start_at'] = convert_dt_to_t(data['start_time'])
      new_data['end_at'] = convert_dt_to_t(data['finish_time'])
    ret = send(new_data, WORK_ADD)
    logging.info("Success add records to firestore. R : %s, D : %s", ret, data)
  except:
    logging.exception("Raise error while set records to firestore. D : %s", data)


def update_work_firestore(data):
  if not IS_UPDATE_FIRESTORE:
    return None

  try:
    new_data = {
        # "plan": "",  # TODO:
        "id": data['id'],
        "start_at": convert_dt_to_t(data['start_time']),
        "end_at": convert_dt_to_t(data['finish_time']),
        "ts": convert_dt_to_t(data['last_updated_time'])
        # "resources": [],
        # "input_values": []  # TODO: blasting, charging ?
    }
    ret = send(new_data, WORK_UPDATE)
    logging.info("Success update records to firestore. R : %s, D : %s", ret, data)
  except:
    logging.exception("Raise error while update records to firestore. D : %s", data)


def start_work_firestore(data):
  # data is object
  if not IS_UPDATE_FIRESTORE:
    return None

  try:
    new_data = {
        # "plan": "",  # TODO:
        "id": data.id,
        "start_at": convert_dt_to_t(data.start_time),
        "ts": convert_dt_to_t(data.last_updated_time)
        # "resources": [],
        # "input_values": []  # TODO: blasting, charging ?
    }
    ret = send(new_data, WORK_START)
    logging.info("Success start records to firestore. R : %s, D : %s", ret, data)
  except:
    logging.exception("Raise error while start records to firestore. D : %s", data)


def pause_work_firestore(_id, _time, last_updated_time):
  # data is object
  if not IS_UPDATE_FIRESTORE:
    return None

  try:
    new_data = {
        "id": _id,
        "pause_at": convert_dt_to_t(_time),
        "ts": convert_dt_to_t(last_updated_time)
    }
    ret = send(new_data, WORK_PAUSE)
    logging.info("Success pause records to firestore. R: %s, D: %s", ret, [_id, _time])
  except:
    logging.exception("Raise error while pause records to firestore. D: %s", [_id, _time])


def resume_work_firestore(data):
  # data is object
  if not IS_UPDATE_FIRESTORE:
    return None

  try:
    new_data = {
        "id": data.id,
        "pause_at": None,
        "ts": convert_dt_to_t(data.last_updated_time)
    }
    ret = send(new_data, WORK_RESUME)
    logging.info("Success resume records to firestore. R: %s, D: %s", ret, data)
  except:
    logging.exception("Raise error while resume records to firestore. D: %s", data)


def finish_work_firestore(data):
  # data is object
  if not IS_UPDATE_FIRESTORE:
    return None

  try:
    new_data = {
        # "plan": "",  # TODO:
        "id": data.id,
        "end_at": convert_dt_to_t(data.end_time),
        "pause_at": None,
        "ts": convert_dt_to_t(data.last_updated_time)
        # "resources": [],
        # "input_values": []  # TODO: blasting, charging ?
    }
    ret = send(new_data, WORK_FINISH)
    logging.info("Success finish records to firestore. R: %s, D: %s", ret, data)
  except:
    logging.exception("Raise error while finish records to firestore. D: %s", data)


def remove_work_firestore(data):
  # data is work_id
  if not IS_UPDATE_FIRESTORE:
    return None

  try:
    new_data = {
      "id": data
    }
    ret = send(new_data, WORK_REMOVE)
    logging.info("Success remove records to firestore. R: %s, D: %s", ret, data)
  except:
    logging.exception("Raise error while remove records to firestore. D: %s", data)


# TODO:
# def add_blast_firestore(data, is_finish=False):
#   if not IS_UPDATE_FIRESTORE:
#     return None
#   try:
#     doc = fs.collection("plan_cycles").document(data['id'])
#     tunnel_id = data.tunnel_id
#     new_data = {
#         # "cycle": "",  # TODO:
#         "area": fs.collection("areas").document(tunnel_id),
#         "goal": 0,
#         "initial_value": None,
#         "final_value": None,
#         "x1": 0,
#         "x2": 0,
#         "y": 0
#     }
#     doc.set(new_data)
#     logging.info("Success add plan_cycle to firestore. Data : %s", data)
#   except:
#     logging.exception("Raise error while set plan_cycle to firestore. Data : %s", data)
