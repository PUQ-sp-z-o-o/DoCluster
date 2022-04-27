#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import time
import threading
import json
import os
from flask import Flask, request
import config
from src.api.api import ApiStart
from src.mng.mng import *
from src.functions import *

#####
if not os.access('config/docluster.conf', os.F_OK):
    f = open('config/docluster.conf', 'w+')
    json.dump(config.default_config, f, indent=1)
    f.close()
#####
ReadConfiguration()


api = Flask(__name__)
api.debug = True


@api.route('/api/', defaults={'path': ''}, methods=['GET', 'POST'])
@api.route('/api/<path:path>', methods=['GET', 'POST'])
def api_get_dir(path):
    args = {}
    if request.method == 'POST':
        args = request.form.to_dict()
    client_ip = request.remote_addr
    url = list(filter(None, path.split('/')))
    return ApiStart(url, args, client_ip)


def api_web():
    api.run(host='0.0.0.0', port=3033, use_reloader=False)


mng = Flask(__name__)
mng.debug = True


@mng.route('/mng/', methods=['POST', 'GET'])
def mng_get_dir():
    args = {}
    if request.method == 'POST':
        args = request.form.to_dict()
    client_ip = request.remote_addr
    return MngStart(args, client_ip)

@mng.route('/join/', methods=['POST', 'GET'])
def join():
    args = {}
    if request.method == 'POST':
        args = request.form.to_dict()
    client_ip = request.remote_addr
    return MngJoin(args, client_ip)


def mng_web():
    mng.run(host='0.0.0.0', port=3030, use_reloader=False)


if __name__ == '__main__':
    config.logger.info('Start API service')
    api_t = threading.Thread(target=api_web, daemon=False)
    api_t.start()
    time.sleep(1)
    config.logger.info('Start MNG service')
    mng_t = threading.Thread(target=mng_web, daemon=False)
    mng_t.start()





