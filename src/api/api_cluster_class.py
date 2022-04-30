import config
import os
import requests
import json
import random
import string
from src.functions import *


class cluster:

    SaveConfiguration = False
    url = []
    args = {}
    client_ip = ''
    username = ''

    answer_msg = {}
    answer_error = 'wrong api path'
    answer_status = 'error'

    def __init__(self, url, args, client_ip, username):
        self.url = url
        self.args = args
        self.client_ip = client_ip
        self.username = username

    def status(self):
        self.answer_status = 'success'
        self.answer_msg['status'] = 'OK'
        self.answer_msg['config'] = config.cluster_config

    def create(self):
        if 'cluster' in config.cluster_config:
            self.answer_status = 'error'
            self.answer_error = 'cluster already created'
            config.logger.name = 'SYSTEM'
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'cluster already created')
        else:
            config.cluster_config['cluster'] = {
                'name': 'DoCluster',
                'nodes': {
                    os.uname()[1]: {'machine': os.uname()[4],
                                    'API_key': ''.join(random.choice(string.ascii_lowercase) for i in range(30)),
                                    'enabled': 'true'
                                    }
                }
            }
            config.cluster_config['quorum'] = [{'node': os.uname()[1], 'main': True}]
            self.SaveConfiguration = True
            self.answer_status = 'success'
            self.answer_msg = {}
            self.answer_error = ''
            config.logger.name = 'SYSTEM'
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'cluster created successfully')

    def join(self):
        if 'cluster' in config.cluster_config:
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = 'cluster already created'
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'cluster already created')
            return 0

        if 'cluster_ip' not in self.args or\
                'cluster_username' not in self.args or\
                'cluster_password' not in self.args:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0
        node = {
            'cluster_username': self.args['cluster_username'],
            'cluster_password': self.args['cluster_password'],
            'cluster_ip': self.args['cluster_ip'],
            'node': os.uname()[1],
            'machine': os.uname()[4]
        }

        try:
            send = requests.post(url='http://' + self.args['cluster_ip'] + ':3030/mng/cluster/join/', data=node, timeout=2)
        except requests.Timeout:
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = 'network problem: Timeout'
            return 0
        except requests.ConnectionError:
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = 'network problem: ConnectionError'
            return 0

        if json.loads(send.text)['status'] != "success":
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = json.loads(send.text)['error']
            return 0
        config.access_tokens = {}
        config.cluster_config = json.loads(send.text)['msg']
        self.SaveConfiguration = True
        self.answer_status = json.loads(send.text)['error']
        self.answer_status = json.loads(send.text)['status']
        self.answer_msg = {}



    def management(self):
        if len(self.url) != 3:
            return 0

        if self.url[2] not in ['get', 'set', 'add', 'delete']:
            return 0

        if self.url[2] == 'get':
            self.answer_msg = config.cluster_config['cluster']['management']
            self.answer_status = 'success'
            self.answer_error = ''
            return 0

        if self.url[2] == 'set':
            if 'node' not in self.args or 'weight' not in self.args:
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0

            if self.args['node'] not in config.cluster_config['cluster']['nodes']:
                self.answer_status = 'error'
                self.answer_error = 'node not defined in cluster'
                return 0

            if not self.args['weight'].isdigit():
                self.answer_status = 'error'
                self.answer_error = 'wrong weight'
                return 0


            '''
            self.answer_msg = config.cluster_config['cluster']['management']
            self.answer_status = 'success'
            self.answer_error = ''
'''