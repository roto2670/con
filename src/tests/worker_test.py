import os.path
import pytest

try:
  import worker
except:
  import sys
  base_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
  sys.path.insert(0, base_path)
  import worker


FILES_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files')


def test_get_about_noti_key():
  pass


def test_hex_to_json():
  hex_file = os.path.join(FILES_PATH, 'example.hex')
  ret_file = os.path.join(FILES_PATH, 'hex_result.txt')
  with open(ret_file, 'r') as _fp:
    ret = _fp.read()

  hex_to_json = worker.get_hex_to_json(hex_file)
  assert hex_to_json == ret


def test_send_mail():
  pass


def test_get_timezone():
  pass