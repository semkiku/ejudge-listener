from werkzeug.utils import import_string

from ejudge_listener.config import CONFIG_MODULE

config = import_string(CONFIG_MODULE)

from ejudge_listener.extensions import db

from .rmatics.utils.json_type import JsonType


class Problem(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_problems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255))
    content = db.Column(db.Text)
    review = db.Column(db.Text)
    hidden = db.Column(db.Boolean)
    timelimit = db.Column(db.Float)
    memorylimit = db.Column(db.Integer)
    description = db.Column(db.Text)
    analysis = db.Column(db.Text)
    sample_tests = db.Column(db.Unicode(255))
    sample_tests_html = db.Column(db.Text)
    sample_tests_json = db.Column(JsonType)
    show_limits = db.Column(db.Boolean)
    output_only = db.Column(db.Boolean)
    pr_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_ejudge_problem.id'))

    def __init__(self, *args, **kwargs):
        super(Problem, self).__init__(*args, **kwargs)
        self.hidden = 1
        self.show_limits = True


class EjudgeProblem(Problem):
    """
    Модель задачи из ejudge

    ejudge_prid -- primary key, на который ссылается Problem.pr_id.
        После инициализации, соответствтующему объекту Problem проставляется корректный pr_id

    contest_id --

    ejudge_contest_id -- соответствует contest_id из ejudge

    secondary_ejudge_contest_id --

    problem_id -- соответствует problem_id из ejudge

    short_id -- короткий id (обычно буква)
    """

    __table_args__ = (
        db.Index('ejudge_contest_id_problem_id', 'ejudge_contest_id', 'problem_id'),
        {'schema': 'moodle', 'extend_existing': True}
    )
    __tablename__ = 'mdl_ejudge_problem'
    __mapper_args__ = {'polymorphic_identity': 'ejudgeproblem'}

    ejudge_prid = db.Column('id', db.Integer, primary_key=True)  # global id in ejudge
    contest_id = db.Column(db.Integer, primary_key=True, nullable=False,
                           autoincrement=False)
    ejudge_contest_id = db.Column(db.Integer, primary_key=True, nullable=False,
                                  autoincrement=False)
    secondary_ejudge_contest_id = db.Column(db.Integer, nullable=True)
    problem_id = db.Column(db.Integer, primary_key=True, nullable=False,
                           autoincrement=False)  # id in contest
    short_id = db.Column(db.Unicode(50))
    ejudge_name = db.Column('name', db.Unicode(255))
    judges_settings = db.Column(JsonType, nullable=True)

    @staticmethod
    def create(**kwargs):
        """
        При создании EjudgeProblem сначала в базу пишет Problem потом EjudgeProblem,
        из-за чего pr_id не проставляется
        """
        instance = EjudgeProblem(**kwargs)
        db.session.add(instance)
        db.session.flush([instance])

        problem_id = instance.id
        ejudge_problem_id = instance.pr_id
        db.session.commit()

        problem_instance = db.session.query(Problem).filter_by(id=problem_id).one()
        problem_instance.pr_id = ejudge_problem_id
        db.session.commit()

        return db.session.query(EjudgeProblem).filter_by(id=problem_id).one()

class EjudgeRun(db.Model):
    __table_args__ = (db.ForeignKeyConstraint(
        ['contest_id', 'prob_id'],
        ['moodle.mdl_ejudge_problem.ejudge_contest_id',
         'moodle.mdl_ejudge_problem.problem_id']
    ), {'schema': 'ejudge'})
    __tablename__ = 'runs'

    run_id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    create_nsec = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    prob_id = db.Column(db.Integer)  # TODO: rename to problem_id
    lang_id = db.Column(db.Integer)
    status = db.Column(db.Integer)
    ssl_flag = db.Column(db.Integer)
    ip_version = db.Column(db.Integer)
    ip = db.Column(db.String(64))
    hash = db.Column(db.String(128))
    run_uuid = db.Column(db.String(40))
    score = db.Column(db.Integer)
    test_num = db.Column(db.Integer)
    score_adj = db.Column(db.Integer)
    locale_id = db.Column(db.Integer)
    judge_id = db.Column(db.Integer)
    variant = db.Column(db.Integer)
    pages = db.Column(db.Integer)
    is_imported = db.Column(db.Integer)
    is_hidden = db.Column(db.Integer)
    is_readonly = db.Column(db.Integer)
    is_examinable = db.Column(db.Integer)
    mime_type = db.Column(db.String(64))
    examiners0 = db.Column(db.Integer)
    examiners1 = db.Column(db.Integer)
    examiners2 = db.Column(db.Integer)
    exam_score0 = db.Column(db.Integer)
    exam_score1 = db.Column(db.Integer)
    exam_score2 = db.Column(db.Integer)
    last_change_time = db.Column(db.DateTime)
    last_change_nsec = db.Column(db.Integer)
    is_marked = db.Column(db.Integer)
    is_saved = db.Column(db.Integer)
    saved_status = db.Column(db.Integer)
    saved_score = db.Column(db.Integer)
    saved_test = db.Column(db.Integer)
    passed_mode = db.Column(db.Integer)
    eoln_type = db.Column(db.Integer)
    store_flags = db.Column(db.Integer)
    token_flags = db.Column(db.Integer)
    token_count = db.Column(db.Integer)

    problem = db.relationship(
        'EjudgeProblem',
        backref=db.backref('ejudge_runs', lazy='dynamic'),
        uselist=False,
    )
