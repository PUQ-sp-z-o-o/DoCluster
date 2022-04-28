import logging
import hashlib


token_timeout = 60
access_tokens = {}
cluster_config = {}
cluster_tasks = {}
cluster_quorum ={
    "status": 'OK',
    "error": '',
    'master': ''
}
cluster_nodes_status = {}

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
