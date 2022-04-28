import logging

import config
import time
import json
import requests

class DoClusterMng:

    def NodsStatusCheck(self):
        while True:
            time.sleep(1)
            config.logger.name = 'NodsStatusCheck'
            config.logger.debug(str(config.cluster_nodes_status))
            for key in config.cluster_config['cluster']['nodes']:
                config.cluster_nodes_status[key] = {}
                try:
                    send = requests.post(url='http://' + key + ':3030/mng/', data={'command': 'node_status'}, timeout=2)
                except requests.Timeout:
                    config.cluster_nodes_status[key]['status'] = 'offline'
                    config.cluster_nodes_status[key]['error'] = 'network problem: Timeout'
                    continue
                except requests.ConnectionError:
                    config.cluster_nodes_status[key]['status'] = 'offline'
                    config.cluster_nodes_status[key]['error'] = 'network problem: ConnectionError'
                    continue

                answer = json.loads(send.text)
                config.cluster_nodes_status[key]['status'] = 'online'
                config.cluster_nodes_status[key]['config_version'] = answer['config_version']


    def NodeStatus(self):
        config.logger.name = 'NodeStatus'
        NodeStatus = {'status': 'OK', 'config_version': config.cluster_config['version']}
        return json.dumps(NodeStatus, indent=1)

    def quorum(self):
        while True:
            time.sleep(5)
            config.logger.name = 'quorum'
            if 'cluster' not in config.cluster_config:
                config.cluster_quorum['status'] = 'critical'
                config.cluster_quorum['error'] = 'cluster not created'
                config.logger.debug('cluster not created')

            if len(config.cluster_config['cluster']['quorum']) == 1:
                config.cluster_quorum['master'] = config.cluster_config['cluster']['quorum'][0]['node']
                config.cluster_quorum['status'] = 'warning'
                config.cluster_quorum['error'] = 'Quorum consists of one node'
                config.logger.info('quorum consists of one node')

            config.logger.debug(str(config.cluster_quorum))

    def MngStart(self, args, client_ip):
        config.logger.name = 'MNG'
        config.logger.debug(client_ip + ' answer: ' + str(args))
        if 'command' in args:
            if args['command'] == 'node_status':
                return self.NodeStatus()

        return client_ip


