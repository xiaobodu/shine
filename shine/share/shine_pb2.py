# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: shine.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='shine.proto',
  package='shine.gw_proto',
  serialized_pb='\n\x0bshine.proto\x12\x0eshine.gw_proto\"\x8c\x01\n\x04Task\x12\x0f\n\x07proc_id\x18\x01 \x01(\x0c\x12\x11\n\tclient_id\x18\x02 \x01(\x0c\x12\x11\n\tclient_ip\x18\x03 \x01(\t\x12\r\n\x05inner\x18\x04 \x01(\t\x12\x0b\n\x03\x63md\x18\x05 \x01(\x05\x12\x0c\n\x04\x64\x61ta\x18\x06 \x01(\x0c\x12\x0e\n\x03uid\x18\x07 \x01(\x03:\x01\x30\x12\x13\n\x08userdata\x18\x08 \x01(\x03:\x01\x30\"n\n\nRspToUsers\x12,\n\x04rows\x18\x01 \x03(\x0b\x32\x1e.shine.gw_proto.RspToUsers.Row\x1a\x32\n\x03Row\x12\x0c\n\x04uids\x18\x01 \x03(\x03\x12\x0b\n\x03\x62uf\x18\x02 \x01(\x0c\x12\x10\n\x08userdata\x18\x03 \x01(\x03\",\n\nCloseUsers\x12\x0c\n\x04uids\x18\x01 \x03(\x03\x12\x10\n\x08userdata\x18\x02 \x01(\x03\x42\"\n\x17\x63n.vimer.shine.gw_protoB\x07GWProto')




_TASK = _descriptor.Descriptor(
  name='Task',
  full_name='shine.gw_proto.Task',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='proc_id', full_name='shine.gw_proto.Task.proc_id', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='client_id', full_name='shine.gw_proto.Task.client_id', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='client_ip', full_name='shine.gw_proto.Task.client_ip', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='inner', full_name='shine.gw_proto.Task.inner', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cmd', full_name='shine.gw_proto.Task.cmd', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data', full_name='shine.gw_proto.Task.data', index=5,
      number=6, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='uid', full_name='shine.gw_proto.Task.uid', index=6,
      number=7, type=3, cpp_type=2, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='userdata', full_name='shine.gw_proto.Task.userdata', index=7,
      number=8, type=3, cpp_type=2, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=32,
  serialized_end=172,
)


_RSPTOUSERS_ROW = _descriptor.Descriptor(
  name='Row',
  full_name='shine.gw_proto.RspToUsers.Row',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uids', full_name='shine.gw_proto.RspToUsers.Row.uids', index=0,
      number=1, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='buf', full_name='shine.gw_proto.RspToUsers.Row.buf', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='userdata', full_name='shine.gw_proto.RspToUsers.Row.userdata', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=234,
  serialized_end=284,
)

_RSPTOUSERS = _descriptor.Descriptor(
  name='RspToUsers',
  full_name='shine.gw_proto.RspToUsers',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='rows', full_name='shine.gw_proto.RspToUsers.rows', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_RSPTOUSERS_ROW, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=174,
  serialized_end=284,
)


_CLOSEUSERS = _descriptor.Descriptor(
  name='CloseUsers',
  full_name='shine.gw_proto.CloseUsers',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uids', full_name='shine.gw_proto.CloseUsers.uids', index=0,
      number=1, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='userdata', full_name='shine.gw_proto.CloseUsers.userdata', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=286,
  serialized_end=330,
)

_RSPTOUSERS_ROW.containing_type = _RSPTOUSERS;
_RSPTOUSERS.fields_by_name['rows'].message_type = _RSPTOUSERS_ROW
DESCRIPTOR.message_types_by_name['Task'] = _TASK
DESCRIPTOR.message_types_by_name['RspToUsers'] = _RSPTOUSERS
DESCRIPTOR.message_types_by_name['CloseUsers'] = _CLOSEUSERS

class Task(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TASK

  # @@protoc_insertion_point(class_scope:shine.gw_proto.Task)

class RspToUsers(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class Row(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _RSPTOUSERS_ROW

    # @@protoc_insertion_point(class_scope:shine.gw_proto.RspToUsers.Row)
  DESCRIPTOR = _RSPTOUSERS

  # @@protoc_insertion_point(class_scope:shine.gw_proto.RspToUsers)

class CloseUsers(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CLOSEUSERS

  # @@protoc_insertion_point(class_scope:shine.gw_proto.CloseUsers)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), '\n\027cn.vimer.shine.gw_protoB\007GWProto')
# @@protoc_insertion_point(module_scope)
