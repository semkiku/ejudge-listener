import random
from unittest.mock import patch, MagicMock

from flask import url_for

from tests.unit.base import TestCase

MIN_ID = 1
MAX_ID = 1_000_000


def random_id():
    return random.randint(MIN_ID, MAX_ID)


class TestView(TestCase):
    valid_int_request = {
        'contest_id': random_id(),
        'run_id': random_id(),
        'new_status': 0,
    }

    valid_str_request = {
        'contest_id': str(random_id()),
        'run_id': str(random_id()),
        'new_status': 0,
    }

    def send_request(self, params):
        return self.client.get(url_for('update_run', **params))

    @patch('ejudge_listener.views.make_chain')
    def test_any_status_triggers_chain(self, mock_make_chain):
        """Теперь все статусы (и терминальные, и нет) идут одной цепочкой."""
        chain = MagicMock()
        mock_make_chain.return_value = chain

        self.assert200(self.send_request(self.valid_int_request))
        self.assert200(self.send_request(self.valid_str_request))
        self.assert200(self.send_request({**self.valid_int_request,
                                          'new_status': 98}))

        self.assertEqual(chain.delay.call_count, 3)

    @patch('ejudge_listener.views.make_chain')
    def test_chain_receives_dumped_args(self, mock_make_chain):
        chain = MagicMock()
        mock_make_chain.return_value = chain

        self.assert200(self.send_request(self.valid_str_request))

        (args, ), _ = chain.delay.call_args
        self.assertEqual(args['contest_id'],
                         int(self.valid_str_request['contest_id']))
        self.assertEqual(args['run_id'],
                         int(self.valid_str_request['run_id']))
        self.assertEqual(args['status'],
                         self.valid_str_request['new_status'])
