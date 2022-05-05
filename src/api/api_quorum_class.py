from src.api.api_class import api
from src.functions import *

import config

import os
import requests
import json
import random
import string
from src.functions import *


class quorum(api):

    def status(self):
        self.answer_status = 'success'
        self.answer_msg = config.quorum_status
        self.answer_error = ''

    def nodes(self):
        if len(self.url) != 3:
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'wrong api path'
            return 0

        if self.url[2] not in ['add', 'delete']:
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'wrong api path'
            return 0

        if len(self.args) == 0:
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'data not submitted'
            return 0

        if 'node' not in self.args:
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'data not submitted'
            return 0

        if self.args['node'] not in config.cluster_config['cluster']['nodes']:
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'node is not in cluster'
            return 0

        if self.url[2] == 'delete':
            if self.args['node'] not in config.cluster_config['quorum']['nodes']:
                self.answer_status = 'error'
                self.answer_msg = {}
                self.answer_error = 'node is not in quorum'
                return 0

            if len(config.cluster_config['quorum']['nodes']) == 1:
                self.answer_status = 'error'
                self.answer_msg = {}
                self.answer_error = 'can not delete last node'
                return 0

            if self.args['node'] == config.quorum_status['master']:
                self.answer_status = 'error'
                self.answer_msg = {}
                self.answer_error = 'Can not delete master node'
                return 0



            config.cluster_config['quorum']['nodes'].remove(self.args['node'])
            config.logger.name = 'QUORUM'
            config.logger.info('Removed node from quorum: ' + self.args['node'])
            SaveConfiguration()
            self.answer_status = 'success'
            self.answer_msg = {}
            self.answer_error = ''

        if self.url[2] == 'add':
            if self.args['node'] in config.cluster_config['quorum']['nodes']:
                self.answer_status = 'error'
                self.answer_msg = {}
                self.answer_error = 'node already in quorum'
                return 0

            config.cluster_config['quorum']['nodes'].append(self.args['node'])
            config.logger.name = 'QUORUM'
            config.logger.info('Node added to quorum: ' + self.args['node'])
            SaveConfiguration()
            self.answer_status = 'success'
            self.answer_msg = {}
            self.answer_error = ''
