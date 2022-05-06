from src.mng.mng_class import mng
from src.functions import *
import psutil
from psutil._common import bytes2human

import time
import subprocess
import config
import hashlib
import random
import string

class cluster(mng):

    Timeout_Loop_NodesStatus = config.nodes_timeout

    def join(self):

        if 'cluster' not in config.cluster_config:
            config.logger.name = 'MNG'
            config.logger.error(self.client_ip + 'Join to cluster: cluster not created on connecting node')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'cluster not created on connecting node'
            return False

        if config.quorum_status['master'] != os.uname()[1]:
            config.logger.name = 'MNG'
            config.logger.error(self.client_ip + ' not manager master node')
            self.answer_status = 'error'
            self.answer_msg = {'master':  config.quorum_status['master']}
            self.answer_error = 'not manager master node'
            return False

        if 'cluster_username' not in self.args and 'cluster_password' not in self.args and 'node' not in self.args:
            config.logger.name = 'MNG'
            config.logger.error(self.client_ip + ' Join to cluster: missing data')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'missing data'
            return False

        answer = self.SendToNode(self.args['node'], '', {})
        if answer['error'] != 'no hash value':
            config.logger.name = 'MNG'
            config.logger.error(self.client_ip + ' echo test failed, node: ' + self.args['node'] + 'not available')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'echo test failed, node: ' + self.args['node'] + 'not available'
            return False

        if self.args['cluster_username'] not in config.cluster_config['systems']['users']:
            config.logger.name = 'MNG'
            config.logger.error(self.client_ip + ' Join to cluster: username not found')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'username not found'
            return False

        cluster_password = self.args['cluster_password']
        if hashlib.md5(cluster_password.encode("utf-8")).hexdigest() != \
                config.cluster_config['systems']['users'][self.args['cluster_username']]['password']:
            config.logger.name = 'MNG'
            config.logger.error(self.client_ip + ' Join to cluster: password is wrong')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'password is wrong'
            return False

        if self.args['node'] in config.cluster_config['cluster']['nodes']:
            config.logger.name = 'MNG'
            config.logger.error(self.client_ip + ' Join to cluster: a node with the same hostname is already in the cluster')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'a node with the same hostname is already in the cluster'
            return False

        config.cluster_config['cluster']['nodes'][self.args['node']] = {
            'machine': self.args['machine'],
            'API_key': ''.join(random.choice(string.ascii_lowercase) for i in range(30)),
            'MNG_IP': self.client_ip
        }
        config.cluster_config['quorum']['nodes'].append(self.args['node'])

        SaveConfiguration()
        config.logger.name = 'MNG'
        config.logger.info(self.client_ip + 'Join to cluster:' + self.args['node'])
        self.answer_status = 'success'
        self.answer_msg = config.cluster_config
        self.answer_error = ''
        return True

    def Loop_NodesStatus(self):
        if 'cluster' not in config.cluster_config:
            time.sleep(1)
            return 0

        if 'quorum' in config.cluster_config:
            if os.uname()[1] != config.quorum_status['master']:
                time.sleep(1)
                return 0

        node_online = 0
        node_offline = 0
        for node in config.cluster_config['cluster']['nodes']:
            # Обработать наоборот!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if node not in config.cluster_status['nodes']:
                config.cluster_status['nodes'][node] = {}

            url = 'cluster/nodestatus'
            data = {}
            answer = self.SendToNode(node, url, data)
            config.cluster_status['nodes'][node] = answer['msg']
            config.cluster_status['nodes'][node]['status'] = answer['status']

            if answer['status'] == 'success':
                node_online = node_online + 1
            if answer['status'] == 'offline':
                node_offline = node_offline + 1

        '''Обрабатываем ошибки нодов и заганяем их в список'''
        config.cluster_status['errors'].clear()
        config.cluster_status['status'] = 'OK'
        if node_offline > 0:
            config.cluster_status['status'] = 'WARNING'
            config.cluster_status['errors'].append(str(node_offline) + ' nodes are not online')

        for node in config.cluster_status['nodes']:
            if 'config_version' in config.cluster_status['nodes'][node]:
                if config.cluster_config['version'] != config.cluster_status['nodes'][node]['config_version']:
                    config.cluster_status['errors'].append(node + ' node does not have current configuration')
                    # update config on remote nod
                    url = 'cluster/configupdate'
                    data = {'config': json.dumps(config.cluster_config)}
                    answer = self.SendToNode(node, url, data)
                    if answer['status'] == 'success':
                        config.logger.name = 'CLUSTER'
                        config.logger.info('Successful configuration update in node: ' + node)
                    else:
                        config.logger.name = 'CLUSTER'
                        config.logger.error('Problem updating configuration on node: ' + node + ' error:' + answer['error'])




    def nodestatus(self):
        self.answer_msg['config_version'] = config.cluster_config['version']
        self.answer_msg['cpu_percent'] = psutil.cpu_percent()
        self.answer_msg['memory_percent'] = psutil.virtual_memory().percent
        self.answer_msg['memory_available'] = bytes2human(psutil.virtual_memory().available)
        self.answer_msg['memory_used'] = bytes2human(psutil.virtual_memory().used)
        self.answer_msg['memory_total'] = bytes2human(psutil.virtual_memory().total)
        self.answer_msg['errors'] = []
        self.answer_status = 'success'
        self.answer_error = ''

    def configupdate(self):
        config.cluster_config = json.loads(self.args['config'])
        SaveConfiguration()
        self.answer_msg = {}
        self.answer_status = 'success'
        self.answer_error = ''


    def config(self):
        if len(self.url) >= 3:
            if self.url[2] == 'get':
                self.answer_status = 'success'
                self.answer_msg = {'config': config.cluster_config}
                self.answer_error = ''
