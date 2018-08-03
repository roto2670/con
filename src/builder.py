# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


"""
MIB util
"""


from io import StringIO


# Header builder {{{


MIBIO_JSON = '''
{
"product":"mibio",
"version":"0.0",
"requests":[{
    "name":"set_pin",
    "params":[{
        "name":"pin_number",
        "type":"uint8_t",
        "length":1,
        "default":0
    }],
    "returns":[{
        "name":"result",
        "type":"uint8_t",
        "length":1,
        "default":0
    }],
    "timeout":3
    },
    {
    "name":"clear_pin",
    "params":[{
        "name":"pin_number",
        "type":"uint8_t",
        "length":1,
        "default":0
    }],
    "returns":[{
        "name":"result",
        "type":"uint8_t",
        "length":1,
        "default":0
    }],
    "timeout":3
    },
    {
    "name":"mock",
    "params":[{
        "name":"pin_number",
        "type":"uint8_t",
        "length":1,
        "default":0
    }],
    "returns":[
    ],
    "timeout":3
}]
,
"events":[{
    "name":"pin_interrupt",
    "params":[{
        "name":"pin_number",
        "type":"uint8_t",
        "length":1
        },
        {
        "name":"pin_state",
        "type":"uint8_t",
        "length":1
        }]
    }]
}
'''


HEADER_FRAME = '''
#pragma pack(1)
#ifndef GADGET_H__
#define GADGET_H__
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#define FIRMWARE_VERSION_MAJOR {major_ver}
#define FIRMWARE_VERSION_MINOR {minor_ver}
#define REQUEST_CNT {requests_num}
#define EVENT_CNT {events_num}
typedef void (*ep_hnd) (void* self, void* cb_data);
typedef void (*p_endpoints) (ep_hnd* self, void* data);

static char MIB_PRODUCT_NAME[] = "{product_name}";  // max 12 char
static p_endpoints endpoints[REQUEST_CNT];
static uint32_t return_size[REQUEST_CNT];
{requests_define}

{events_define}

{request_funcs_interface}

#ifndef GADGET_INIT__
#define GADGET_INIT__
static void mib_init(void) {{
  {main_body}
}}
#endif // GADGET_INIT__
#endif // GADGET_H__
'''

NAME_KEY = '''product'''
VER_KEY = '''version'''
REQUESTS_KEY = '''requests'''
EVENTS_KEY = '''events'''

NONE_VALUE_FORM = '''
  uint8_t none;'''
VALUE_FORM = '''
  {value_type} {name};'''
ARRAY_VALUE_FORM = '''
  {value_type} {name}[{size}];'''

REQUESTS_DEFINE_FORM = '''
typedef enum
{{ {requests_enum}
}} request_ids;
{requests_struct}
'''

REQUESTS_STRUCT_FORM = '''
{param_struct}
{return_struct}'''

PARAM_STRUCT_FORM = '''
typedef struct {name}_t {name}_t;
struct {name}_t
{{ {input_values}
}};'''

RETURN_STRUCT_FORM = '''
typedef struct {name}_return_t {name}_return_t;
struct {name}_return_t
{{ {output_values}
}};
static {name}_return_t* {name}_return_size;'''

REQUEST_ENUM_FORM = '''
  MIB_EP_{name} = {e_id},'''

REQUEST_INTERFACE_FORM = '''
void {name}(ep_hnd* _hnd, {name}_t* data_t);'''

EVENTS_DEFINE_FORM = '''
typedef enum
{{ {events_enum}
}} event_ids;
{events_struct}
'''

EVENT_TYPE_FORM = '''
  uint16_t {name};'''

EVENT_STRUCT_FORM = '''
typedef struct {name}_t {name}_t;
struct {name}_t
{{ {event_values}
}};'''

EVENT_ENUM_FORM = '''
  MIB_EVT_{name} = {e_id},'''

MAIN_EP_VALUE = '''
  endpoints[MIB_EP_{name_up}] = {name_low};'''
MAIN_EP_RET_VALUE = '''
  return_size[MIB_EP_{name_up}] = sizeof(*{name_low}_return_size);'''
MAIN_EP_RET_NONE_VALUE = '''
  return_size[MIB_EP_{name_up}] = 0;'''


class MibEndpoints(object):
  NAME_MAX_LEN = 12

  def __init__(self):
    self.name = None
    self._requests = {}
    self._events = {}

  def to_lib_body(self):
    _main_body = StringIO()
    _req_funcs_interface = StringIO()
    _requests_define = StringIO()
    _requests_enum = StringIO()
    _requests_struct = StringIO()
    for req_name, attrs in self._requests.items():
      _main_body.write(MAIN_EP_VALUE.format(
          name_up=req_name.upper(),
          name_low=req_name.lower()))
      _req_funcs_interface.write(REQUEST_INTERFACE_FORM.format(
          name=req_name))
      _requests_enum.write(REQUEST_ENUM_FORM.format(
          name=req_name.upper(), e_id=attrs['id']))
      _inputs = StringIO()
      _outputs = StringIO()
      _params = attrs['params']
      if _params:
        for param_attr in attrs['params']:
          _size = param_attr['length']
          if _size == 1:
            _form = VALUE_FORM
          else:
            _form = ARRAY_VALUE_FORM
          _inputs.write(_form.format(
              value_type=param_attr['type'],
              name=param_attr['name'],
              size=param_attr['length']))
      else:
        _inputs.write(NONE_VALUE_FORM)
      _returns = attrs['returns']
      if _returns:
        _main_body.write(MAIN_EP_RET_VALUE.format(
            name_up=req_name.upper(),
            name_low=req_name.lower()))
      else:
        _main_body.write(
            MAIN_EP_RET_NONE_VALUE.format(name_up=req_name.upper()))
      for ret_attr in _returns:
        _size = ret_attr['length']
        if _size == 1:
          _form = VALUE_FORM
        else:
          _form = ARRAY_VALUE_FORM
        print(ret_attr)
        _outputs.write(_form.format(
            value_type=ret_attr['type'],
            name=ret_attr['name'],
            size=ret_attr['length']))
      _param_struct = PARAM_STRUCT_FORM.format(
          name=req_name,
          input_values=_inputs.getvalue())
      _inputs.close()
      if _returns:
        _return_struct = RETURN_STRUCT_FORM.format(
            name=req_name,
            output_values=_outputs.getvalue()
            )
      else:
        _return_struct = ''
      _outputs.close()
      _requests_struct.write(
          REQUESTS_STRUCT_FORM.format(
              param_struct=_param_struct,
              return_struct=_return_struct))
      _main_body.write('\n')
    _requests_define.write(
        REQUESTS_DEFINE_FORM.format(
            requests_enum=_requests_enum.getvalue(),
            requests_struct=_requests_struct.getvalue()))
    _requests_enum.close()
    _requests_struct.close()

    _events_define = StringIO()
    _events_enum = StringIO()
    _events_struct = StringIO()
    for evt_name, attrs in self._events.items():
      _events_enum.write(EVENT_ENUM_FORM.format(
          name=evt_name.upper(), e_id=attrs['id']))
      _event_values = StringIO()
      _params = attrs['params']
      if _params:
        for param_attr in attrs['params']:
          if _size == 1:
            _form = VALUE_FORM
          else:
            _form = ARRAY_VALUE_FORM
          _event_values.write(
              _form.format(
                  value_type=param_attr['type'],
                  name=param_attr['name'],
                  size=param_attr['length']))
      else:
        _event_values.write(NONE_VALUE_FORM)
      _events_struct.write(EVENT_STRUCT_FORM.format(
          name=evt_name,
          event_values=_event_values.getvalue()))
      _event_values.close()
    _events_define.write(
        EVENTS_DEFINE_FORM.format(
            events_struct=_events_struct.getvalue(),
            events_enum=_events_enum.getvalue()))
    _events_enum.close()
    _events_struct.close()

    _lib_body = HEADER_FRAME.format(
        major_ver=self._major_ver,
        minor_ver=self._minor_ver,
        events_define=_events_define.getvalue(),
        requests_define=_requests_define.getvalue(),
        request_funcs_interface=_req_funcs_interface.getvalue(),
        main_body=_main_body.getvalue(),
        product_name=self.name[:self.NAME_MAX_LEN],
        requests_num=len(self._requests),
        events_num=len(self._events))
    _requests_define.close()
    _req_funcs_interface.close()
    _main_body.close()
    return _lib_body

  @staticmethod
  def build(json_data):
    _ep = MibEndpoints()
    _ep.name = json_data[NAME_KEY]
    _ep.set_version(*json_data[VER_KEY].split('.'))
    _ep_id = -1
    for _req in json_data[REQUESTS_KEY]:
      _ep_name = _req['name']
      _timeout = _req['timeout']
      if 'id' in _req:
        _ep_id = _req['id']
      else:
        _ep_id = _ep_id + 1
      _ep.set_requests(_ep_name,
                       {'params': _req['params'],
                        'id': _ep_id,
                        'returns': _req['returns'],
                        'timeout': _timeout})
    _evt_id = -1
    for _evt in json_data[EVENTS_KEY]:
      if 'id' in _evt:
        _evt_id = _evt['id']
      else:
        _evt_id = _evt_id + 1
      _evt_name = _evt['name']
      _ep.set_events(_evt_name,
                     {'params': _evt['params'],
                      'id': _evt_id})
    return _ep

  def set_version(self, major, minor):
    """
    Set request item
    """
    self._major_ver = major
    self._minor_ver = minor

  def set_requests(self, name, attr):
    """
    Set request item
    """
    self._requests[name] = attr

  def set_events(self, name, attr):
    """
    Set event item
    """
    self._events[name] = attr


# }}}


if __name__ == '__main__':
  import json
  import os
  _file_name = 'sense.json'
  if os.path.exists(_file_name):
    with open(_file_name, 'r') as testf:
      _data = testf.read().strip()
  else:
    _data = MIBIO_JSON
  _json_data = json.loads(_data)
  b = MibEndpoints.build(_json_data)
  _header = b.to_lib_body()
  print(_header)