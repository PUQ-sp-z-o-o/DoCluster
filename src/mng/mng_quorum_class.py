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
            if 'quorum' in config.cluster_config:
                if os.uname()[1] not in config.cluster_config['quorum']['nodes']:
                    time.sleep(10)
                    continue
            '''The process polls the quorum nodes.'''
            if 'quorum' in config.cluster_config:

                quorum_nodes = []
                for node in config.cluster_config['quorum']['nodes']:
                    quorum_nodes.append({'node': node})
                config.quorum_status['nodes'] = copy.deepcopy(quorum_nodes)

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

                config_v_tmp = 0
                node_config_v_tmp = ''
                while i < len(config.quorum_status['nodes']):
                    if config.quorum_status['nodes'][i]['status'] == 'online':
                        if config_v_tmp < config.quorum_status['nodes'][i]['config_version']:
                            config_v_tmp = config.quorum_status['nodes'][i]['config_version']
                            node_config_v_tmp = config.quorum_status['nodes'][i]['node']
                    i = i + 1

                print(str(config_v_tmp))
                print(str(node_config_v_tmp))
                if config_v_tmp > config.cluster_config['version']:
                    url = 'cluster/config/get'
                    data = {}
                    answer = self.SendToNodes(node_config_v_tmp, url, data)
                    print(str(config_v_tmp))
                    print(str(node_config_v_tmp))
                    if answer['status'] == 'success':
                        config.cluster_config = answer['msg']['config']
                        config.quorum_status['master'] = ''
                        SaveConfiguration()

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
                config.quorum_status['master'] = config.quorum_status['nodes'][i]['node']
                break
            i = i + 1
        if config.quorum_status['master'] != config.cluster_config['quorum']['nodes'][0]:
            if config.quorum_status['master'] in config.cluster_config['quorum']['nodes']:
                config.cluster_config['quorum']['nodes'].remove(config.quorum_status['master'])
                config.cluster_config['quorum']['nodes'].insert(0, config.quorum_status['master'])
                SaveConfiguration()




