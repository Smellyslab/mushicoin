import sys

import os
import yaml
from simplekv.db.sql import SQLAlchemyStore
from sqlalchemy.exc import OperationalError

from halocoin import tools, custom
from halocoin.service import Service, sync


class DatabaseService(Service):
    """
    Database bindings for leveldb
    """

    def __init__(self, engine):
        Service.__init__(self, name='database')
        self.engine = engine
        self.DB = None
        self.salt = None
        self.req_count = 0
        self.set_state(Service.INIT)
        self.simulations = {}

    def on_register(self):
        try:
            from sqlalchemy import create_engine, MetaData
            db_location = os.path.join(self.engine.working_dir, self.engine.config['database']['location'])
            self.dbengine = create_engine('sqlite:///' + db_location)
            self.metadata = MetaData(bind=self.dbengine)
            self.DB = SQLAlchemyStore(self.dbengine, self.metadata, 'kvstore')
            self.DB.table.create()
        except OperationalError as e:
            pass
        except Exception as e:
            tools.log(e)
            sys.stderr.write('Redis connection cannot be established!\nFalling to SQLAlchemy')
            return False

        self.salt = custom.version
        return True

    @sync
    def get(self, key, sid=None):
        """gets the key in args[0] using the salt"""
        if sid is None:
            db = self.DB
        else:
            db = self.simulations[sid]
        try:
            return yaml.load(db.get(self.salt + str(key)).decode())
        except Exception as e:
            return None

    @sync
    def put(self, key, value, sid=None):
        """
        Puts the val in args[1] under the key in args[0] with the salt
        prepended to the key.
        """
        if sid is None:
            db = self.DB
        else:
            db = self.simulations[sid]
        try:
            db.put(self.salt + str(key), yaml.dump(value).encode())
            return True
        except Exception as e:
            return False

    @sync
    def exists(self, key, sid=None):
        """
        Checks if the key in args[0] with the salt prepended is
        in the database.
        """
        if sid is None:
            db = self.DB
        else:
            db = self.simulations[sid]
        try:
            return (self.salt + str(key)) in db
        except KeyError:
            return False

    @sync
    def delete(self, key, sid=None):
        """
        Removes the entry in the database under the the key in args[0]
        with the salt prepended.
        """
        if sid is None:
            db = self.DB
        else:
            db = self.simulations[sid]
        try:
            db.delete(self.salt + str(key))
            return True
        except:
            return False

    @sync
    def simulate(self):
        import uuid
        try:
            sid = str(uuid.uuid4())
            self.simulations[sid] = SQLSimulationStore(self.dbengine, self.metadata, 'kvstore')
            return sid
        except:
            return None

    @sync
    def commit(self, sid):
        self.simulations[sid].commit()
        del self.simulations[sid]

    @sync
    def rollback(self, sid):
        self.simulations[sid].rollback()
        del self.simulations[sid]


#!/usr/bin/env python
# coding=utf8

from io import BytesIO

from simplekv._compat import imap, text_type
from simplekv import KeyValueStore, CopyMixin

from sqlalchemy import Table, Column, String, LargeBinary, select, exists


class SQLSimulationStore(KeyValueStore, CopyMixin):
    """
    This is a copy of SQLAlchemyStore with transaction no commit support(simulation).
    """
    def __init__(self, bind, metadata, tablename):
        from sqlalchemy.orm import sessionmaker
        self.bind = bind

        self.table = Table(tablename, metadata,
            # 250 characters is the maximum key length that we guarantee can be
            # handled by any kind of backend
            Column('key', String(250), primary_key=True),
            Column('value', LargeBinary, nullable=False),
            extend_existing=True
        )
        Session = sessionmaker()
        Session.configure(bind=bind)
        self.session = Session()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def _has_key(self, key):
        return self.bind.execute(
            select([exists().where(self.table.c.key == key)])
        ).scalar()

    def _delete(self, key):
        self.bind.execute(
            self.table.delete(self.table.c.key == key)
        )

    def _get(self, key):
        rv = self.session.execute(
                select([self.table.c.value], self.table.c.key == key).limit(1)
             ).scalar()

        if not rv:
            raise KeyError(key)

        return rv

    def _open(self, key):
        return BytesIO(self._get(key))

    def _copy(self, source, dest):
        data = self.session.execute(
            select([self.table.c.value], self.table.c.key == source).limit(1)
        ).scalar()
        if not data:
            raise KeyError(source)

        # delete the potential existing previous key
        self.session.execute(self.table.delete(self.table.c.key == dest))
        self.session.execute(self.table.insert({
            'key': dest,
            'value': data,
        }))
        return dest

    def _put(self, key, data):
            # delete the old
        self.session.execute(self.table.delete(self.table.c.key == key))

        # insert new
        self.session.execute(self.table.insert({
            'key': key,
            'value': data
        }))

        return key

    def _put_file(self, key, file):
        return self._put(key, file.read())

    def iter_keys(self, prefix=u""):
        query = select([self.table.c.key])
        if prefix != "":
            query = query.where(self.table.c.key.like(prefix + '%'))
        return imap(lambda v: text_type(v[0]),
                    self.session.execute(query))
