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
            'cluster_username': self.args['cluster_username'],
            'cluster_password': self.args['cluster_password'],
            'cluster_ip': self.args['cluster_ip'],
            'node': os.uname()[1],
            'machine': os.uname()[4]
        }

        answer = self.SendToNode(self.args['cluster_ip'], 'cluster/join/', node)

        self.answer_msg = answer['msg']
        self.answer_status = answer['status']
        self.answer_error = answer['error']


        if answer['status'] == 'success':
            config.cluster_config = self.answer_msg
            SaveConfiguration()
            config.access_tokens = {}


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