from src.functions import *

import time
import config
import requests
import json
import hashlib
import random
import string


class mng:
    url = []
    args = {}
    client_ip = ''
    mng_port = 3030
    answer_msg = {}
    answer_error = ''
    answer_status = ''

    def __init__(self, mng_port, url, args, client_ip):
        self.url = url
        self.args = args
        self.client_ip = client_ip
        self.mng_port = mng_port
        self.answer_msg = {}
        self.answer_error = ''
        self.answer_status = ''

    def SendToNode(self, node, url, data):
        to_hash = config.cluster_config['cluster']['nodes'][os.uname()[1]]['MNG_IP'] + \
                            config.cluster_config['cluster']['nodes'][node]['MNG_IP'] + \
                            config.cluster_config['cluster']['nodes'][node]['API_key']
        data['hash'] = hashlib.md5(to_hash.encode("utf-8")).hexdigest()

        answer = {'status': '', 'error': '', 'msg':  {}}
        try:
            send = requests.post(url='http://' + node + ':' + str(self.mng_port) + '/mng/' + url, data=data, timeout=5)
            try:
                send_answer = json.loads(send.text)
            except ValueError as e:
                answer['status'] = 'critical'
                answer['error'] = 'answer problem: ' + str(e)
                answer['msg'] = {}
            else:
                answer = send_answer
        except requests.Timeout:
            answer['status'] = 'offline'
            answer['error'] = 'network problem: Timeout'
            answer['msg'] = {}
        except requests.ConnectionError:
            answer['status'] = 'offline'
            answer['error'] = 'network problem: ConnectionError'
            answer['msg'] = {}

        return answer


