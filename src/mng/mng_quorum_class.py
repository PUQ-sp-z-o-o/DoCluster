import time
import config
import requests
import json
class quorum:
    SaveConfiguration = False
    url = []
    args = {}
    client_ip = ''
    mng_port = 3030
    answer_msg = {}
    answer_error = 'wrong api path'
    answer_status = 'error'

    def __init__(self, mng_port, url, args, client_ip):
        self.url = url
        self.args = args
        self.mng_port = mng_port
        self.client_ip = client_ip
        self.answer_msg = {}


    def Scheduler_QuorumStatus(self):
        while True:
            if 'quorum' in config.cluster_config:
                config.quorum_status['nodes'] = config.cluster_config['quorum']
                i = 0
                while i < len(config.cluster_config['quorum']):
                    try:
                        send = requests.post(url='http://' + config.cluster_config['quorum'][i]['node'] + ':' + str(self.mng_port) + '/mng/quorum/status', data={},
                                             timeout=2)
                    except requests.Timeout:
                        config.quorum_status['nodes'][i]['status'] = 'offline'
                        config.quorum_status['nodes'][i]['error'] = 'network problem: Timeout'
                        continue
                    except requests.ConnectionError:
                        config.quorum_status['nodes'][i]['status'] = 'offline'
                        config.quorum_status['nodes'][i]['error'] = 'network problem: ConnectionError'
                        continue

                    try:
                        answer = json.loads(send.text)
                    except ValueError as e:
                        config.quorum_status['nodes'][i]['status'] = 'offline'
                        config.quorum_status['nodes'][i]['error'] = str(e)
                    else:
                        config.quorum_status['nodes'][i]['status'] = 'online'
                        config.quorum_status['nodes'][i]['config_version'] = answer['msg']['config_version']
                    i=+1
                config.logger.name = 'QUORUM'
                config.logger.debug(str(config.quorum_status))
                time.sleep(5)

                #config.logger.name = 'SYSTEM'
                #config.logger.info('Not start schedulers: cluster not created')
                #config.logger.name = 'QUORUM'
                #config.logger.debug('Scheduler_QuorumStatus in')

    def status(self):
        self.answer_status = 'OK'
        self.answer_msg = {'config_version': config.cluster_config['version']}
        self.answer_error = ''
        #config.logger.name = 'SYSTEM'
        #config.logger.d(self.client_ip  + 'WWWWWWWWWWWWWWWWWWWWWWWWWWWW')

