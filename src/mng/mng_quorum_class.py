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

                config.quorum_status['nodes'] = copy.deepcopy(config.cluster_config['quorum'])
                i = 0
                while i < len(config.cluster_config['quorum']):
                    try:
                        send = requests.post(url='http://' + config.cluster_config['quorum'][i]['node'] + ':' + str(self.mng_port) + '/mng/quorum/status', data={},
                                             timeout=2)
                    except requests.Timeout:
                        config.quorum_status['nodes'][i]['status'] = 'offline'
                        config.quorum_status['nodes'][i]['error'] = 'network problem: Timeout'
                        i = i + 1
                        continue
                    except requests.ConnectionError:
                        config.quorum_status['nodes'][i]['status'] = 'offline'
                        config.quorum_status['nodes'][i]['error'] = 'network problem: ConnectionError'
                        i = i + 1
                        continue

                    try:
                        answer = json.loads(send.text)
                    except ValueError as e:
                        config.quorum_status['nodes'][i]['status'] = 'offline'
                        config.quorum_status['nodes'][i]['error'] = str(e)
                    else:
                        config.quorum_status['nodes'][i]['status'] = 'online'
                        config.quorum_status['nodes'][i]['config_version'] = answer['msg']['config_version']
                        config.quorum_status['nodes'][i]['error'] = ''
                    i = i + 1

                i = 0
                offline = 0
                while i < len(config.quorum_status['nodes']):
                    if config.quorum_status['nodes'][i]['status'] == 'offline':
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
                    if config.quorum_status['nodes'][i]['main'] and config.quorum_status['nodes'][i]['status'] == 'online':
                        config.quorum_status['master'] = config.quorum_status['nodes'][i]['node']
                        break
                    else:
                        if config.quorum_status['nodes'][i]['status'] == 'online':
                            config.quorum_status['master'] = config.quorum_status['nodes'][i]['node']
                            break
                    i = i + 1






                config.logger.name = 'QUORUM'
                config.logger.debug(str(config.quorum_status))
                time.sleep(1)

    def status(self):
        self.answer_status = 'OK'
        self.answer_msg = {'config_version': config.cluster_config['version']}
        self.answer_error = ''
