import os
from typing import Optional

# avialable cofig modules
DEV_CONFIG_MODULE = 'ejudge_listener.config.DevConfig'
TEST_CONFIG_MODULE = 'ejudge_listener.config.TestConfig'
PROD_CONFIG_MODULE = 'ejudge_listener.config.ProdConfig'

# env-config mapping
CONFIG_ENV_MODULES = {
    'development': DEV_CONFIG_MODULE,
    'testing': TEST_CONFIG_MODULE,
    'production': PROD_CONFIG_MODULE,
}


def get_config_from_env() -> str:
    """Determine appropriate config class based on provided env var

    :return: path to config module
    """
    ENV = os.getenv('FLASK_ENV', 'development')
    # failback to dev, if `FLASK_ENV` has invalid value
    return CONFIG_ENV_MODULES.get(ENV, DEV_CONFIG_MODULE)

def int_(v: str = None) -> Optional[int]:
    try:
        return int(v)
    except:
        return None

def bool_(v: str = None) -> bool:
    """Cast bool string representation into actual Bool type

    :param v: String, representing bool, e.g. 'True', 'yes'
    :return: Boolean cast result
    """
    if type(v) is bool:
        return v
    if isinstance(v, str) is False:
        return False
    return v.lower() in ('yes', 'true', 't', '1')


class BaseConfig:
    # global
    DEBUG = False
    TESTING = False
    FLASK_ENV = 'developemnt'

    # secrets
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_key')

    # databases
    URL_ENCODER_ALPHABET = os.getenv('URL_ENCODER_ALPHABET', 'abcdefg')

    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
                                        'mysql+pymysql://root:@localhost:3306/')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    
    # Services
    RMATICS_ALIVE_URL = os.getenv('RMATICS_ALIVE_URL')
    RMATICS_JUDGE_ID = int_(os.getenv('RMATICS_JUDGE_ID'))

    # Celery requires lowercased config
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    task_ignore_result = bool_(os.getenv('CELERY_TASK_IGNORE_RESULT', True))
    imports = (
        'ejudge_listener.tasks'
    )
    worker_max_memory_per_child = 250_000  # 250MB
    broker_transport_options = {
        'fanout_prefix': True,
        'fanout_patterns': True,
        'visibility_timeout': 24 * 60 * 60,  # 24 hours
    }
    worker_hijack_root_logger = False

    # Debug settings
    DEBUG_PROTOCOL_DUMP_DIR = os.getenv('DEBUG_PROTOCOL_DUMP_DIR', '/tmp/protocols_dump')
    RESERVE_LISTENER_SERVICE_URL = os.getenv('RESERVE_LISTENER_SERVICE_URL', 'http://127.0.0.1:5001/notification/update_run')

class DevConfig(BaseConfig):
    ...
    SQLALCHEMY_ECHO = False


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    FLASK_ENV = 'testing'
    SQLALCHEMY_ECHO = False


class ProdConfig(BaseConfig):
    FLASK_ENV = 'production'
    SQLALCHEMY_ECHO = False


CONFIG_MODULE = get_config_from_env()
