import os
from src.functions import *
from src.mng.mng_class import mng
import config

import time
import requests
import json
import copy


class quorum(mng):

    def Scheduler_QuorumStatus(self):
        while True:
            if os.uname()[1] not in config.cluster_config['quorum']['nodes']:
                time.sleep(10)
                continue
            '''The process polls the quorum nodes.'''
            if 'quorum' in config.cluster_config:
                config.quorum_status['nodes'] = copy.deepcopy(config.cluster_config['quorum']['nodes'])

                url = 'quorum/status'
                data = {}
                i = 0
                while i < len(config.quorum_status['nodes']):
                    answer = self.SendToNodes(config.quorum_status['nodes'][i]['node'], url, data)
                    config.quorum_status['nodes'][i]['status'] = answer['status']
                    config.quorum_status['nodes'][i]['error'] = answer['error']
                    if answer['error'] == '':
                        config.quorum_status['nodes'][i]['config_version'] = answer['msg']['config_version']
                    i = i + 1

                self.QuorumMaster()
                config.logger.name = 'QUORUM'
                config.logger.debug(str(config.quorum_status))
                time.sleep(1)

    def status(self):
        self.answer_status = 'online'
        self.answer_msg = {'config_version': config.cluster_config['version']}
        self.answer_error = ''

    ''' The process that selects the master. '''
    def QuorumMaster(self):
        i = 0
        online = 0
        offline = 0
        while i < len(config.quorum_status['nodes']):
            if config.quorum_status['nodes'][i]['status'] == 'online':
                online = online + 1
            else:
                offline = offline + 1
            i = i + 1

        if offline == 0:
            config.quorum_status['status'] = 'OK'
            config.quorum_status['error'] = ''
        else:
            config.quorum_status['status'] = 'WARNING'
            config.quorum_status['error'] = str(offline) + ' MNG nodes are not online'

        i = 0
        while i < len(config.quorum_status['nodes']):
            if config.quorum_status['nodes'][i]['status'] in ['OK','online']:
                config.quorum_status['master'] = config.cluster_config['quorum'][i]['node']
                break
            else:
                if config.quorum_status['nodes'][i]['status'] == 'online':
                    config.quorum_status['master'] = config.quorum_status['nodes'][i]['node']
                    break
            i = i + 1
