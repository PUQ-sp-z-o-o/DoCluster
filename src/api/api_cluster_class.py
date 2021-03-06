from src.api.api_class import api
from src.functions import *
import config
import os
import requests
import json
import random
import string
from src.functions import *


class cluster(api):

    def status(self):
        self.answer_status = 'success'
        self.answer_msg = config.cluster_status
        self.answer_error = ''

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
                                    'MNG_IP': self.server_ip
                                    }
                }
            }
            config.cluster_config['quorum'] = {'nodes': [os.uname()[1]]}
            SaveConfiguration()
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
            'hash': '',
            'cluster_username': self.args['cluster_username'],
            'cluster_password': self.args['cluster_password'],
            'cluster_ip': self.args['cluster_ip'],
            'node': os.uname()[1],
            'machine': os.uname()[4]
        }

        answer = self.SendToNode(self.args['cluster_ip'], 'cluster/join', node)

        self.answer_msg = answer['msg']
        self.answer_status = answer['status']
        self.answer_error = answer['error']

        if answer['status'] == 'success':
            config.cluster_config = self.answer_msg
            SaveConfiguration()
            config.api_access_tokens.clear()

