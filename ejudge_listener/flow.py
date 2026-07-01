from typing import NamedTuple, Tuple

import requests
from flask import current_app
from marshmallow import fields, Schema, post_load
from requests import RequestException
from sqlalchemy.orm import joinedload

from ejudge_listener.models import EjudgeRun
from ejudge_listener.extensions import db

REQUEST_TIMEOUT = 10  # seconds


class EjudgeRequest(NamedTuple):
    contest_id: int
    run_id: int
    status: int


class EjudgeRequestSchema(Schema):
    run_id = fields.Integer(required=True)
    contest_id = fields.Integer(required=True)
    status = fields.Integer(required=True, load_from="new_status")

    @post_load
    def make_request(self, data):
        return EjudgeRequest(**data)


class EjudgeRunSchema(Schema):
    run_id = fields.Integer()
    contest_id = fields.Integer()
    run_uuid = fields.String()
    score = fields.Integer()
    status = fields.Integer()
    lang_id = fields.Integer()
    test_num = fields.Integer()
    create_time = fields.DateTime()
    last_change_time = fields.DateTime()


ej_request_schema = EjudgeRequestSchema()
ej_run_schema = EjudgeRunSchema()


def send_non_terminal(request_args: dict) -> None:
    """Send non terminal status run."""

    request_args['judge_id'] = current_app.config['RMATICS_JUDGE_ID']
    r = requests.post(
        current_app.config['RMATICS_ALIVE_URL'],
        json=request_args,
        timeout=REQUEST_TIMEOUT,
    )

def load_run_data(request_args: dict) -> dict:
    r, _ = ej_request_schema.load(request_args)
    run = (
        db.session.query(EjudgeRun)
        .filter_by(contest_id=r.contest_id, run_id=r.run_id)
        .options(joinedload(EjudgeRun.problem))
        .one()
    )
    run_data = ej_run_schema.dump(run).data
    return run_data


def send_terminal(run_data: dict):
    run_data['judge_id'] = current_app.config['RMATICS_JUDGE_ID']
    r = requests.post(
        current_app.config['RMATICS_ALIVE_URL'], json=run_data, timeout=REQUEST_TIMEOUT
    )
    r.raise_for_status()
