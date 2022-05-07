#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

import signal
import ctypes
import time
import threading
import config
from src.DoCluster_class import DoClusterMng
from src.functions import *

def terminate(signalNumber, frame):
    config.logger.name = 'SYSTEM'
    config.logger.info('Stopped DoCluster. Signal: ' + str(signalNumber))

    SaveConfiguration()
    SaveModulesData()

    for thread in threading.enumerate():
        if thread.is_alive():
            exc = ctypes.py_object(SystemExit)
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)



parser = argparse.ArgumentParser(description="Example daemon in Python")
parser.add_argument('-l', '--log-file', default='/home/user/test_daemon.log')
args = parser.parse_args()
signal.signal(signal.SIGTERM, terminate)


Cluster = DoClusterMng()
time.sleep(1)
Cluster.MngStartWeb()
time.sleep(1)
Cluster.ApiStartWeb()
time.sleep(1)
Cluster.MngLoopsStart()



