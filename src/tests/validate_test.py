import json
import os.path
import pytest

try:
  import validate
except:
  import sys
  base_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
  sys.path.insert(0, base_path)
  import validate


FILES_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files')


def test_check_key():
  path = os.path.join(FILES_PATH, 'example.json')
  with open(path, 'r') as _fp:
    specification = _fp.read()
    specification = json.loads(specification)
  assert validate._check_key(specification.keys())


def test_check_require_value():
  path = os.path.join(FILES_PATH, 'example.json')
  with open(path, 'r') as _fp:
    specification = _fp.read()
    specification = json.loads(specification)
  assert validate._check_require_value(specification)


def test_check_version_format():
  path = os.path.join(FILES_PATH, 'example.json')
  with open(path, 'r') as _fp:
    specification = _fp.read()
    specification = json.loads(specification)
  assert validate._check_version_format(specification['version'])
