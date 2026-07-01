from celery import shared_task
from celery.utils.log import get_task_logger
from requests import RequestException
from sqlalchemy.orm.exc import NoResultFound

from ejudge_listener import flow

logger = get_task_logger(__name__)

@shared_task(ignore_result=True, retry=False)
def send_non_terminal(request_args):
    """Send non terminal status to ejudge front.

    We ignore result and not retry, because we get new status
    from ejudge earlier, then requeued task starts execute.
    And we just don't care about non terminal statuses, because
    main logic around terminal statuses and we can afford to not
    send or loose some of non terminal statuses to ejudge front.
    """
    flow.send_non_terminal(request_args)


@shared_task(bind=True, default_retry_delay=30, max_retries=5)
def load_run_data(self, request_args):
    """ Load Ejudge run from database and load protocol from filesystem for this run.
    """
    logger.info("laod_protocol t")
    try:
        res = flow.load_run_data(request_args)

        logger.info("load_run_data t+")
        return res

    except NoResultFound:
        logger.error(f'Run not found. Aborting task. Request args={request_args}')
        self.request.chain = None  # Stop chain


@shared_task(bind=True, max_retries=None, retry_backoff=True)
def send_terminal(self, data):
    """Send Ejudge run data.
    """
    try:
        flow.send_terminal(data)
    except RequestException as exc:
        logger.exception('Got unexpected error while request to rmatics. Retrying task')
        self.retry(exc=exc, countdown=2 * self.request.retries)
