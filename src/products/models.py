from base import db, login_manager
from sqlalchemy import Column, Integer, String


class Product(db.Model):

  __tablename__ = 'Products'

  id = Column(Integer, primary_key=True)
  prdname = Column(String(120))
  description = Column(String(200))
  user_id = Column(String(120))

  def __init__(self, **kwargs):
    for property, value in kwargs.items():
      # depending on whether value is an iterable or not, we must
      # unpack it's value (when **kwargs is request.form, some values
      # will be a 1-element list)
      if hasattr(value, '__iter__') and not isinstance(value, str):
        # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
        value = value[0]
      setattr(self, property, value)

  def __repr__(self):
      return self.prd
