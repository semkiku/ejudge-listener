import functools

from flask import request

from ejudge_listener.api import jsonify
from ejudge_listener.flow import EjudgeRequestSchema

ej_request_schema = EjudgeRequestSchema()

TERMINAL_STATUSES = {0, 99, 8, 14, 9, 1, 10, 7, 11, 2, 3, 4, 5, 6, 12, 13}

do_once = functools.lru_cache(1)


@do_once
def make_non_terminal_chain():
    """
    Returns chain for sending celery task for non terminal statuses,
    e.g. Compiling.
    Cache for only once module importing
    """
    from ejudge_listener.tasks import (
        send_non_terminal,
    )

    send_non_terminal_chain = send_non_terminal.s()
    return send_non_terminal_chain


@do_once
def make_terminal_chain():
    """
    Returns chain for sending celery task for terminal statuses,
    e.g. CE, OK.
    Cache for only once module importing
    """
    from ejudge_listener.tasks import (
        load_run_data,
        send_terminal,
    )

    send_terminal_chain = load_run_data.s() | send_terminal.s()
    return send_terminal_chain


def update_run():
    request_args, _ = ej_request_schema.load(request.args)
    json_args, _ = ej_request_schema.dump(request_args)
    isterminal = request_args.status in TERMINAL_STATUSES

    send_non_terminal_chain = make_non_terminal_chain()
    send_terminal_chain = make_terminal_chain()

    if isterminal:
        send_terminal_chain.delay(json_args)
    else:
        send_non_terminal_chain.delay(json_args)
    return jsonify({})
