import functools

from flask import request

from ejudge_listener.api import jsonify
from ejudge_listener.flow import EjudgeRequestSchema

ej_request_schema = EjudgeRequestSchema()

do_once = functools.lru_cache(1)


@do_once
def make_chain():
    """
    Returns chain for sending celery task for terminal statuses,
    e.g. CE, OK.
    Cache for only once module importing
    """
    from ejudge_listener.tasks import (
        load_run_data,
        send,
    )

    send_terminal_chain = load_run_data.s() | send.s()
    return send_terminal_chain


def update_run():
    request_args, _ = ej_request_schema.load(request.args)
    json_args, _ = ej_request_schema.dump(request_args)

    send_chain = make_chain()
    send_chain.delay(json_args)

    return jsonify({})
