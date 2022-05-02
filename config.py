import logging
import hashlib

# таймаут токина позьзователя АПИ
token_timeout = 60
# таймаут опроса Менеджментовых нодов
mng_nodes_timeout = 5
# таймаут опроса нодов на статистику
nodes_timeout = 10
# Порт подключения для клинта АПИ
api_port = '3033'
# Порт подключени для узлов МНГ
mng_port = '3030'

cluster_config = {}
api_access_tokens = {}
cluster_tasks = {}

quorum_status = {
    "status": '',
    "errors": [],
    'master': '',
    'nodes': []
}

cluster_status = {
    "status": '',
    "errors": [],
    'nodes': {}
}



# DEBUG,INFO,WARNING,ERROR,CRITICAL
LogLevel = 'DEBUG'
LogFile = 'docluster.log'

VERSION = '1.0'

default_config = {
    "version": 0,
    "systems": {
        "users": {"admin": {"password": hashlib.md5("admin".encode("utf-8")).hexdigest()}}
    }
}

logger = logging.getLogger('SYSTEM')

if LogLevel == "DEBUG":
    logger.setLevel(logging.DEBUG)
if LogLevel == "INFO":
    logger.setLevel(logging.INFO)
if LogLevel == "WARNING":
    logger.setLevel(logging.WARNING)
if LogLevel == "ERROR":
    logger.setLevel(logging.ERROR)
if LogLevel == "CRITICAL":
    logger.setLevel(logging.CRITICAL)
fh = logging.FileHandler(LogFile)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
