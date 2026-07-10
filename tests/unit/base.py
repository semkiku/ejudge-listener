import copy
import os
import sys
import tempfile

import flask_testing
from unittest.mock import patch

# Локальный запуск без mysql: TEST_INFRA=local переводит тесты на sqlite
# (схема ejudge цепляется через ATTACH). По умолчанию, как и раньше,
# используется SQLALCHEMY_DATABASE_URI.
if os.getenv('TEST_INFRA') == 'local':
    try:
        import sqlite3
    except ImportError:
        import pysqlite3 as sqlite3
        sys.modules['sqlite3'] = sqlite3
        sys.modules['sqlite3.dbapi2'] = sqlite3.dbapi2

    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    _tmpdir = tempfile.mkdtemp(prefix='ejudge-listener-test-db-')

    @event.listens_for(Engine, 'connect')
    def _attach_schemas(dbapi_conn, connection_record):
        if not isinstance(dbapi_conn, sqlite3.Connection):
            return
        cursor = dbapi_conn.cursor()
        cursor.execute('ATTACH DATABASE ? AS ejudge',
                       (os.path.join(_tmpdir, 'ejudge.db'),))
        cursor.close()

    from ejudge_listener.config import TestConfig
    TestConfig.SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(_tmpdir, 'main.db')
    TestConfig.SQLALCHEMY_POOL_SIZE = None
    TestConfig.SQLALCHEMY_POOL_RECYCLE = None

from ejudge_listener import create_app
from ejudge_listener.extensions import db
from ejudge_listener.models import EjudgeRun

REQUEST_ARGS = {'contest_id': 1, 'run_id': 10, 'status': 0}

RUN = {
    'run_id': 10,
    'contest_id': 1,
    'status': None,
    'lang_id': None,
    'score': None,
    'last_change_time': None,
    'create_time': None,
    'run_uuid': None,
    'test_num': None,
}


class TestCase(flask_testing.TestCase):
    def create_app(self):
        app = create_app('ejudge_listener.config.TestConfig')
        return app

    def create_runs(self):
        """
        contest_id | run_id
            1      |   10
            2      |   20
            3      |   30
            4      |   40
            5      |   50
        """
        for i in range(1, 6):
            run = EjudgeRun(contest_id=i, run_id=i * 10)
            db.session.add(run)
        db.session.commit()

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.run_data = copy.deepcopy(RUN)
        self.addCleanup(patch.stopall)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
