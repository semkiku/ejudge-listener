from unittest.mock import patch

from sqlalchemy.orm.exc import NoResultFound

from ejudge_listener.tasks import load_run_data, send
from tests.unit.base import TestCase, REQUEST_ARGS, RUN


class TestLoadRunDataTask(TestCase):
    @patch('ejudge_listener.flow.load_run_data', return_value=RUN)
    def test_run_exists(self, mock_flow_load):
        self.assertEqual(load_run_data(REQUEST_ARGS), RUN)
        mock_flow_load.assert_called_once_with(REQUEST_ARGS)

    @patch('ejudge_listener.flow.load_run_data', side_effect=NoResultFound)
    def test_run_not_exist_stops_chain(self, mock_flow_load):
        """Если посылки нет в БД ejudge — цепочка прерывается без ретраев."""
        result = load_run_data(REQUEST_ARGS)
        self.assertIsNone(result)
        self.assertIsNone(load_run_data.request.chain)


class TestSendTask(TestCase):
    @patch('ejudge_listener.flow.send')
    def test_delegates_to_flow(self, mock_flow_send):
        send(RUN)
        mock_flow_send.assert_called_once_with(RUN)
