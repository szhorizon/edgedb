##
# Copyright (c) 2012, 2013 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import re
import uuid

from metamagic.utils import buckets as abstract
from metamagic import caos
from metamagic.utils import config

from . import exceptions


class BucketMeta(abstract.BucketMeta):
    id_registry = {}
    name_registry = {}

    def __new__(mcls, name, bases, dct, *, abstract=False):
        dct['abstract'] = abstract
        cls = super().__new__(mcls, name, bases, dct)

        try:
            id = dct['id']
        except KeyError:
            if not abstract:
                raise exceptions.StorageError('missing a required attribute "id" for a '
                                              'non-abstract bucket class {}.{}'.
                                              format(cls.__module__, cls.__name__))
        else:
            try:
                cls.id = uuid.UUID(id)
            except TypeError:
                raise exceptions.StorageError('invalid bucket UUID')

            mcls.id_registry[id] = cls

        cls.name = cls.__module__ + '.' + cls.__name__
        mcls.name_registry[cls.name] = cls

        return cls

    def __init__(cls, name, bases, dct, *, abstract=False):
        return super().__init__(name, bases, dct)

    @classmethod
    def get_bucket_class(mcls, bucket:str):
        if isinstance(bucket, uuid.UUID) or '-' in str(bucket):
            # 'bucket' is a UUID of a Bucket class
            bucket = str(bucket)
            try:
                return mcls.id_registry[bucket]
            except KeyError:
                raise exceptions.StorageError('unable to find bucket by id {!r}'.format(bucket))
        else:
            # class name?
            try:
                return mcls.name_registry[bucket]
            except KeyError:
                raise exceptions.StorageError('unable to find bucket by name {!r}'.format(bucket))


class Bucket(abstract.Bucket, metaclass=BucketMeta, abstract=True):
    _re_escape = re.compile(r'[^\w\-\._]')

    def __init__(self, *args, **kwargs):
        raise TypeError('storage Buckets are not meant to be instantiated')

    @classmethod
    def _error_if_abstract(cls):
        if cls.abstract:
            raise exceptions.StorageError('unable to perform a file operation on an '
                                          'abstract bucket {}.{}'.
                                          format(cls.__module__, cls.__name__))

    @classmethod
    def store_http_file(cls, id, file):
        cls._error_if_abstract()
        return cls.get_implementation().store_http_file(cls, id, file)

    @classmethod
    def store_file(cls, id, filename, name=None):
        cls._error_if_abstract()
        return cls.get_implementation().store_file(cls, id, filename, name=name)

    @classmethod
    def get_file_pub_url(cls, id, filename):
        cls._error_if_abstract()
        return cls.get_implementation().get_file_pub_url(cls, id, filename)

    @classmethod
    def get_file_path(cls, id, filename):
        cls._error_if_abstract()
        return cls.get_implementation().get_file_path(cls, id, filename)

    @classmethod
    def get_bucket_entity(cls, session):
        schema = session.schema.metamagic.utils.fs.file

        with session.transaction():
            if cls.id:
                try:
                    return schema.Bucket.get(schema.Bucket.id == schema.Bucket.id(cls.id))
                except caos.session.EntityNotFoundError:
                    return schema.Bucket(name=cls.name, id=cls.id)
            else:
                try:
                    return schema.Bucket.get(schema.Bucket.name == cls.name)
                except caos.session.EntityNotFoundError:
                    return schema.Bucket(name=cls.name)

    @classmethod
    def escape_filename(cls, filename):
        return cls._re_escape.sub('_', filename).strip('-')
