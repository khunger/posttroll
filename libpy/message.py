# -*-python-*- 
#
"""A Message, goes like: 
<subject> <type> <timestamp> <sender> [data]

fx: pytroll:/DC/address info 2010-12-01T12:21:11 juhu@prodsat prodsat:22010
"""
import re
from datetime import datetime

class MessageError(Exception):
    pass

def is_valid_subject(s):
    """Currently we only check for empty stings
    """
    return isinstance(s, str) and bool(s)

def is_valid_type(s):
    """Currently we only check for empty stings
    """
    return isinstance(s, str) and bool(s)

def is_valid_sender(s):
    """Currently we only check for empty stings
    """
    return isinstance(s, str) and bool(s)

def _strptime(str):
    _isoformat = "%Y-%m-%dT%H:%M:%S.%f"
    return datetime.strptime(str, _isoformat)

def _getsender():
    import getpass
    import socket
    host = socket.gethostname()
    user = getpass.getuser()
    return "%s@%s"%(user, host)

class Message:

  """Wrap a smsg dictonary into a Message class.

  - Has to be initialized with a 'subject', 'type' and optionally 'data'.
  - It will forbid rebinding of message specific attributes.
  - It will add a few extra attributes.
  - It will make a Message pickleable."""

  def __init__(self, subject='', atype='', data='', empty=False):
      """A Message needs at least a subject, type and a sender ... if not specified as empty.
      """
      if empty:
          self.subject, self.type, self.time, self.sender, self.data = \
              ('', '', '', '', '')
      else:
          self.subject = subject
          self.type = atype
          self.time = datetime.utcnow()
          self.sender = _getsender()
          self.data = data
          self._validate()

  @property
  def user(self):
      try:
          return self.sender[:self.sender.index('@')]
      except ValueError:
          return ''
      
  @property
  def host(self):
      try:
          return self.sender[self.sender.index('@')+1:]
      except ValueError:
          return ''

  @staticmethod
  def decode(rawstr):
      m = Message(empty=True)
      a = re.split(r"\s+", rawstr, maxsplit=4)
      if len(a) < 4:
          raise MessageError, "Could node decode raw string: '%s ...'"%str(rawstr[:36])
      m.subject = a[0].strip()
      m.type = a[1].strip()
      m.time = _strptime(a[2].strip())
      m.sender = a[3].strip()
      try:
          m.data = a[4]
      except IndexError:
          m.data = ''
      m._validate()
      return m

  def encode(self):
      self._validate()
      text = "%s %s %s %s"%(self.subject, self.type, self.time.isoformat(), self.sender)
      return text + ' ' + self.data

  def __repr__(self):
      return self.encode()

  def __str__(self):
      return self.encode()

  def _validate(self):
      if not is_valid_subject(self.subject):
          raise MessageError, "Invalid subject: '%s'"%self.subject
      if not is_valid_subject(self.type):
          raise MessageError, "Invalid type: '%s'"%self.type
      if not is_valid_subject(self.sender):
          raise MessageError, "Invalid sender: '%s'"%self.sender
      
  #
  # Make it pickleable.
  #
  def __getstate__(self):
      return self.encode()

  def __setstate__(self, state):
      self.__dict__.clear()
      self.__dict__ = Message.decode(state).__dict__

if __name__ == '__main__':
    import pickle
    import os

    m1 = Message('/test/whatup/doc', 'info', data='not much to say')
    uh = '%s@%s'%(m1.user, m1.host)
    print uh
    if uh != m1.sender:
        print 'OOPS ... deconding sender failed'
    m2 = Message.decode(m1.encode())
    print m2
    if uh != m1.sender:
        print 'OOPS ... decoding/encoding message failed'  
    rawstr = "/test/what/todo info 2008-04-11T22:13:22.123000 ras@hawaii what's up doc"
    m = Message.decode(rawstr)
    print m
    if str(m) != rawstr:
        print 'OOPS ... decoding/encoding message failed'  
