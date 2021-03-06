import os
from src.functions import *
from src.mng.mng_class import mng
import config

import time
import requests
import json
import copy


class quorum(mng):

    Timeout_Loop_QuorumStatus = config.mng_nodes_timeout

    def Loop_QuorumStatus(self):
        if 'quorum' in config.cluster_config:
            if os.uname()[1] not in config.cluster_config['quorum']['nodes']:
                time.sleep(10)
                return 0
        '''The process polls the quorum nodes.'''
        if 'quorum' in config.cluster_config:
            # Херня с запихиванием актуальных данных о статусе нод а также добавление или удаление новых или старых нод
            quorum_nodes = []
            for node in config.cluster_config['quorum']['nodes']:
                yes = False
                for node_a in config.quorum_status['nodes']:
                    if node_a['node'] == node:
                        quorum_nodes.append(node_a)
                        yes = True
                if not yes:
                    quorum_nodes.append({'node': node})

            config.quorum_status['nodes'] = copy.deepcopy(quorum_nodes)

            url = 'quorum/status'
            data = {}
            i = 0
            while i < len(config.quorum_status['nodes']):
                answer = self.SendToNode(config.quorum_status['nodes'][i]['node'], url, data)
                config.quorum_status['nodes'][i]['status'] = answer['status']
                config.quorum_status['nodes'][i]['error'] = answer['error']

                if answer['error'] == '':
                    config.quorum_status['nodes'][i] = {**config.quorum_status['nodes'][i], **answer['msg']}
                i = i + 1

            self.QuorumSyncConfig()
            time.sleep(1)
            self.QuorumSyncModulesData()
            time.sleep(1)
            self.QuorumMaster()
            config.logger.name = 'QUORUM'
            config.logger.debug(str(config.quorum_status))

    def status(self):
        self.answer_msg['config_version'] = config.cluster_config['version']
        self.answer_msg['modules_data_version'] = config.modules_data['version']
        self.answer_msg['errors'] = []
        self.answer_status = 'success'
        self.answer_error = ''

    def QuorumMaster(self):
        i = 0
        online = 0
        offline = 0
        while i < len(config.quorum_status['nodes']):
            if config.quorum_status['nodes'][i]['status'] == 'offline':
                offline = offline + 1
            else:
                online = online + 1
            i = i + 1

        # Обработка ошибок кворума и запихнуть в список
        config.quorum_status['errors'].clear()
        if offline == 0:
            config.quorum_status['status'] = 'OK'
        else:
            config.quorum_status['status'] = 'WARNING'
            config.quorum_status['errors'].append(str(offline) + ' MNG nodes are not online')

        i = 0
        while i < len(config.quorum_status['nodes']):
            if config.quorum_status['nodes'][i]['status'] in 'success':
                config.quorum_status['master'] = config.quorum_status['nodes'][i]['node']
                # Для того чтоб изменить порядок мастеров
                if i != 0 and config.quorum_status['master'] == os.uname()[1]:
                    config.cluster_config['quorum']['nodes'].remove(config.quorum_status['master'])
                    config.cluster_config['quorum']['nodes'].insert(0, config.quorum_status['master'])
                    config.logger.name = 'QUORUM'
                    config.logger.info('Set new Master ' + config.quorum_status['master'])
                    SaveConfiguration()
                break
            i = i + 1

    def QuorumSyncConfig(self):
        i = 0
        config_v_tmp = 0
        node_config_v_tmp = ''
        while i < len(config.quorum_status['nodes']):
            if config.quorum_status['nodes'][i]['status'] == 'success':
                if config_v_tmp < config.quorum_status['nodes'][i]['config_version']:
                    config_v_tmp = config.quorum_status['nodes'][i]['config_version']
                    node_config_v_tmp = config.quorum_status['nodes'][i]['node']
            i = i + 1

        if config_v_tmp > config.cluster_config['version']:
            url = 'cluster/config/get'
            data = {}
            answer = self.SendToNode(node_config_v_tmp, url, data)

            if answer['status'] == 'success':
                config.cluster_config = copy.deepcopy(answer['msg'])
                config.logger.name = 'QUORUM'
                config.logger.info('Get new config from: ' + node_config_v_tmp + ' version: ' + str(config_v_tmp))
                #Для того чтоб не изменял мастер версию ПЕРЕДЕЛАТЬ!!!!!!!!!!!!!!!#SaveConfiguration()
                f = open('config/docluster.conf', 'w+')
                json.dump(config.cluster_config, f, indent=1)
                config.logger.info('Save configuration version: ' + str(config.cluster_config['version']))
                config.logger.debug('Save configuration: ' + str(config.cluster_config))
                f.close()

    def QuorumSyncModulesData(self):
        i = 0
        config_v_tmp = 0
        node_config_v_tmp = ''
        while i < len(config.quorum_status['nodes']):
            if config.quorum_status['nodes'][i]['status'] == 'success':
                if config_v_tmp < config.quorum_status['nodes'][i]['modules_data_version']:
                    config_v_tmp = config.quorum_status['nodes'][i]['modules_data_version']
                    node_config_v_tmp = config.quorum_status['nodes'][i]['node']
            i = i + 1

        if config_v_tmp > config.modules_data['version']:
            url = 'cluster/modulesdata/get'
            data = {}
            answer = self.SendToNode(node_config_v_tmp, url, data)

            if answer['status'] == 'success':
                config.modules_data = copy.deepcopy(answer['msg'])
                config.logger.name = 'QUORUM'
                config.logger.info('Get new modules data from: ' + node_config_v_tmp + ' version: ' + str(config_v_tmp))
                SaveModulesData()



