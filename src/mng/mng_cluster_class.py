from src.mng.mng_class import mng
from src.functions import *

import time
import config
import hashlib
import random
import string

class cluster(mng):

    def join(self):
        if 'cluster' not in config.cluster_config:
            config.logger.error(self.client_ip + 'Join to cluster: cluster not created on connecting node')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'cluster not created on connecting node'
            return False

        if 'cluster_username' not in self.args and 'cluster_password' not in self.args and 'node' not in self.args:
            config.logger.error(self.client_ip + ' Join to cluster: missing data')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'missing data'
            return False

        if self.args['cluster_username'] not in config.cluster_config['systems']['users']:
            config.logger.error(self.client_ip + ' Join to cluster: username not found')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'username not found'
            return False

        cluster_password = self.args['cluster_password']
        if hashlib.md5(cluster_password.encode("utf-8")).hexdigest() != \
                config.cluster_config['systems']['users'][self.args['cluster_username']]['password']:
            config.logger.error(self.client_ip + ' Join to cluster: password is wrong')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'password is wrong'
            return False

        if self.args['node'] in config.cluster_config['cluster']['nodes']:
            config.logger.error(self.client_ip + ' Join to cluster: a node with the same hostname is already in the cluster')
            self.answer_status = 'error'
            self.answer_msg = {}
            self.answer_error = 'a node with the same hostname is already in the cluster'
            return False

        config.cluster_config['cluster']['nodes'][self.args['node']] = {
            'machine': self.args['machine'],
            'API_key': ''.join(random.choice(string.ascii_lowercase) for i in range(30)),
        }
        config.cluster_config['quorum'].append({'node': self.args['node'], 'main': False})

        self.SaveConfiguration = True
        config.logger.info(self.client_ip + 'Join to cluster:' + self.args['node'])
        self.answer_status = 'success'
        self.answer_msg = config.cluster_config
        self.answer_error = ''
        return True
