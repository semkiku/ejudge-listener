from unittest.mock import patch, Mock

from requests import HTTPError
from sqlalchemy.orm.exc import NoResultFound

from ejudge_listener.flow import (
    EjudgeRequest,
    EjudgeRequestSchema,
    load_run_data,
    send,
)
from tests.unit.base import TestCase

ej_request_schema = EjudgeRequestSchema()

RMATICS_URL = 'http://rmatics/problem/run/action/update_from_ejudge'
JUDGE_ID = '2'


class TestLoadRunData(TestCase):
    def setUp(self):
        super().setUp()
        self.create_runs()

    def test_db_doesnt_contain_run(self):
        ej_request = EjudgeRequest(7777, 5555, 0)  # non existing run
        request_args = ej_request_schema.dump(ej_request).data
        with self.assertRaises(NoResultFound):
            load_run_data(request_args)

    def test_db_contains_run(self):
        ej_request = EjudgeRequest(1, 10, 0)  # existing run
        request_args = ej_request_schema.dump(ej_request).data
        run_data = load_run_data(request_args)
        self.assertEqual(run_data, self.run_data)


class TestSend(TestCase):
    def setUp(self):
        super().setUp()
        self.app.config['RMATICS_ALIVE_URL'] = RMATICS_URL
        self.app.config['RMATICS_JUDGE_ID'] = JUDGE_ID

    @patch('ejudge_listener.flow.requests.post')
    def test_sends_run_data_with_judge_id(self, mock_post):
        mock_post.return_value = Mock(status_code=200)

        send(dict(self.run_data))

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], RMATICS_URL)
        # judge_id дописывается к данным нотификации
        self.assertEqual(kwargs['json']['judge_id'], JUDGE_ID)
        self.assertEqual(kwargs['json']['run_id'], self.run_data['run_id'])

    @patch('ejudge_listener.flow.requests.post')
    def test_error_response_raises(self, mock_post):
        response = Mock(status_code=500)
        response.raise_for_status.side_effect = HTTPError(response=response)
        mock_post.return_value = response

        with self.assertRaises(HTTPError):
            send(dict(self.run_data))
