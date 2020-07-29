import uuid
import hashlib

COUNT = 3
SALT = '''d4822b475f222b019287238a45ad5428'''
# SALT -> naran, skec, adnoc

def create_key():
  _uuid = uuid.uuid4().hex
  enc = hashlib.md5()
  enc.update(SALT.encode('utf8'))
  enc.update(_uuid.encode('utf8'))
  print("uuid : ", _uuid) 
  print("key : ", enc.hexdigest())


for i in range(COUNT):
  create_key()

