from celery import shared_task
from celery.utils.log import get_task_logger
from requests import RequestException
from sqlalchemy.orm.exc import NoResultFound

from ejudge_listener import flow
from ejudge_listener.extensions import db

logger = get_task_logger(__name__)

@shared_task(bind=True, default_retry_delay=30, max_retries=5)
def load_run_data(self, request_args):
    """ Load Ejudge run from database and load protocol from filesystem for this run.
    """
    logger.info("load_run_data t")
    try:
        res = flow.load_run_data(request_args)

        logger.info("load_run_data t+")
        return res

    except NoResultFound:
        logger.error(f'Run not found. Aborting task. Request args={request_args}')
        self.request.chain = None  # Stop chain


@shared_task(ignore_result=True, retry=False)
def send(self, data):
    """Send Ejudge run data.
    """
    flow.send_terminal(data)
