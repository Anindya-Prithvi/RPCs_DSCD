# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: community_server.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import registry_server_pb2 as registry__server__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16\x63ommunity_server.proto\x1a\x15registry_server.proto\"1\n\tClientele\x12$\n\x07\x63lients\x18\x01 \x03(\x0b\x32\x13.Client_information\"\xc6\x01\n\x07\x41rticle\x12%\n\x0c\x61rticle_type\x18\x01 \x01(\x0e\x32\r.Article.typeH\x00\x12\x13\n\x06\x61uthor\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x11\n\x04time\x18\x03 \x01(\x03H\x02\x88\x01\x01\x12\x14\n\x07\x63ontent\x18\x04 \x01(\tH\x03\x88\x01\x01\"-\n\x04type\x12\n\n\x06SPORTS\x10\x00\x12\x0b\n\x07\x46\x41SHION\x10\x01\x12\x0c\n\x08POLITICS\x10\x02\x42\x07\n\x05_typeB\t\n\x07_authorB\x07\n\x05_timeB\n\n\x08_content\"n\n\rArticleFormat\x12\x1a\n\x06SPORTS\x18\x01 \x01(\x0b\x32\x08.ArticleH\x00\x12\x1b\n\x07\x46\x41SHION\x18\x02 \x01(\x0b\x32\x08.ArticleH\x00\x12\x1c\n\x08POLITICS\x18\x03 \x01(\x0b\x32\x08.ArticleH\x00\x42\x06\n\x04Type\")\n\x0b\x41rticleList\x12\x1a\n\x08\x61rticles\x18\x01 \x03(\x0b\x32\x08.Article\"\x93\x01\n\x14\x41rticleRequestFormat\x12(\n\x06\x63lient\x18\x01 \x01(\x0b\x32\x13.Client_informationH\x00\x88\x01\x01\x12\x1e\n\x07\x61rticle\x18\x02 \x01(\x0b\x32\x08.ArticleH\x01\x88\x01\x01\x12\x11\n\x04type\x18\x03 \x01(\tH\x02\x88\x01\x01\x42\t\n\x07_clientB\n\n\x08_articleB\x07\n\x05_type2m\n\x10\x43lientManagement\x12+\n\nJoinServer\x12\x13.Client_information\x1a\x08.Success\x12,\n\x0bLeaveServer\x12\x13.Client_information\x1a\x08.Successb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'community_server_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _CLIENTELE._serialized_start=49
  _CLIENTELE._serialized_end=98
  _ARTICLE._serialized_start=101
  _ARTICLE._serialized_end=299
  _ARTICLE_TYPE._serialized_start=213
  _ARTICLE_TYPE._serialized_end=258
  _ARTICLEFORMAT._serialized_start=301
  _ARTICLEFORMAT._serialized_end=411
  _ARTICLELIST._serialized_start=413
  _ARTICLELIST._serialized_end=454
  _ARTICLEREQUESTFORMAT._serialized_start=457
  _ARTICLEREQUESTFORMAT._serialized_end=604
  _CLIENTMANAGEMENT._serialized_start=606
  _CLIENTMANAGEMENT._serialized_end=715
# @@protoc_insertion_point(module_scope)
