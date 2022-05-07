import logging
import hashlib

# таймаут токина позьзователя АПИ
token_timeout = 300
# таймаут опроса Менеджментовых нодов
mng_nodes_timeout = 3
# таймаут опроса нодов на статистику
nodes_timeout = 5
# Порт подключения для клинта АПИ
api_port = '3033'
# Порт подключени для узлов МНГ
mng_port = '3030'

cluster_config = {}
api_access_tokens = {}

cluster_tasks = []
local_tasks = []

modules_data = {}
modules_stat = {}

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

schedulers = {}

# DEBUG,INFO,WARNING,ERROR,CRITICAL
LogLevel = 'DEBUG'
LogFile = 'docluster.log'

VERSION = '1.0'

default_config = {
    "version": 0,
    "system": {
        "users": {"admin": {"password": hashlib.md5("admin".encode("utf-8")).hexdigest()}}
    }
}

default_modules_data = {"version": 0}





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
