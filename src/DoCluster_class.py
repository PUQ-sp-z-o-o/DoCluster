import config
import os
import json
import threading
import datetime
import calendar
import hashlib
import random
import string
import importlib
import re
from flask import Flask, request


class DoClusterMng:

    api_port = 3033
    api_access_tokens = {}

    mng_port = 3030

    def __init__(self):
        config.logger.name = 'SYSTEM'
        config.logger.info('*********************************')
        config.logger.info('*                               *')
        config.logger.info('* Start DoCluster system        *')
        config.logger.info('* Development by Ruslan Polovyi *')
        config.logger.info('* email: ruslan.polovyi@puq.pl  *')
        config.logger.info('*                               *')
        config.logger.info('*********************************')

        self.ReadConfiguration()
        #self.SaveConfiguration()
        self.MngSchedulersStart()

    '''Read cluster configuration from file in format JSON'''
    def ReadConfiguration(self):
        config.logger.name = 'SYSTEM'
        if not os.path.isdir('config'):
            os.mkdir('config')

        if not os.access('config/docluster.conf', os.F_OK):
            f = open('config/docluster.conf', 'w+')
            json.dump(config.default_config, f, indent=1)
            f.close()

        with open('config/docluster.conf') as json_file:
            config.cluster_config = json.load(json_file)
            json_file.close()
        config.logger.info('Read configuration version: ' + str(config.cluster_config['version']))
        config.logger.debug('Read configuration: ' + str(config.cluster_config))

    '''Save cluster configuration to file in format JSON'''
    def SaveConfiguration(self):
        config.logger.name = 'SYSTEM'
        f = open('config/docluster.conf', 'w+')
        json.dump(config.cluster_config, f, indent=1)
        config.logger.info('Save configuration version: ' + str(config.cluster_config['version']))
        config.logger.debug('Save configuration: ' + str(config.cluster_config))
        f.close()

    '''API interface for clients'''
    def ApiStartWeb(self):
        config.logger.name = 'SYSTEM'
        api = Flask(__name__)
        api.debug = True

        @api.route('/api/', defaults={'path': ''}, methods=['GET', 'POST'])
        @api.route('/api/<path:path>', methods=['GET', 'POST'])
        def api_get_dir(path):
            args = {}
            if request.method == 'POST':
                args = request.form.to_dict()
            client_ip = request.remote_addr
            url = list(filter(None, path.split('/')))
            return self.ApiRequestProcessor(url, args, client_ip)

        def api_web():
            api.run(host='0.0.0.0', port=self.api_port, use_reloader=False)

        config.logger.info('Start API service. Port: ' + str(self.api_port))
        api_t = threading.Thread(target=api_web, daemon=False)
        api_t.start()

    '''API interface for cluster'''
    def MngStartWeb(self):
        config.logger.name = 'SYSTEM'
        mng = Flask(__name__)
        mng.debug = True

        @mng.route('/mng/', defaults={'path': ''}, methods=['GET', 'POST'])
        @mng.route('/mng/<path:path>', methods=['GET', 'POST'])
        def mng_get_dir(path):
            args = {}
            if request.method == 'POST':
                args = request.form.to_dict()
            client_ip = request.remote_addr
            url = list(filter(None, path.split('/')))
            return self.MngRequestProcessor(url, args, client_ip)

        def mng_web():
            mng.run(host='0.0.0.0', port=self.mng_port, use_reloader=False)

        config.logger.info('Start MNG service. Port: ' + str(self.mng_port))
        mng_t = threading.Thread(target=mng_web, daemon=False)
        mng_t.start()

    ''' The function is responsible for processing requests from the nodes MNG and returns a response. '''
    def MngRequestProcessor(self, url, args, client_ip):

        if len(url) >= 2:
            if os.access('src/mng/mng_' + url[0] + '_class.py', os.F_OK):
                mng_module = importlib.import_module('src.mng.mng_' + url[0] + '_class')
                mng_class = getattr(mng_module, url[0])
                mng_instance = mng_class(self.mng_port, url, args, client_ip)

                if url[1] in dir(mng_instance):
                    getattr(mng_instance, url[1])()
                    if mng_instance.SaveConfiguration:
                        self.SaveConfiguration()
                    return self.MngAnswer(mng_instance.answer_msg, mng_instance.answer_status, mng_instance.answer_error)

        '''If nothing matches, we return an error that the path is not correct.'''
        return self.ApiAnswer('', 'error', 'wrong api path')



    ''' The function is responsible for processing requests from the client API and returns a response. '''
    def ApiRequestProcessor(self, url, args, client_ip):
        config.logger.name = 'API'
        config.logger.debug('IP: ' + client_ip + ' URL: ' + str(url) + ' POST: ' + str(args))

        '''Loging and create valid access token'''
        if len(url) == 1:
            if url[0] == 'login':
                if 'username' in args and 'password' in args:
                    if self.ApiLogin(args['username'], args['password']):
                        config.logger.info('IP: ' + client_ip + ' username: ' + args['username'] + ' login success')
                        return self.ApiAnswer({'access_token': self.ApiWriteToken(args['username'], client_ip)},
                                              'success',
                                              '')
                    else:
                        config.logger.error('IP: ' + client_ip + ' username: ' + args['username'] + ' access denied')
                        return self.ApiAnswer('', 'error', 'access denied')

        '''Check Token'''
        if 'access_token' not in args:
            return self.ApiAnswer('', 'error', 'wrong token')
        if 'access_token' in args:
            if not self.ApiCheckToken(args['access_token'], client_ip):
                config.logger.error('IP: ' + client_ip + ' wrong token')
                return self.ApiAnswer('', 'error', 'wrong token')

        '''Logout'''
        if len(url) == 1:
            if url[0] == 'logout':
                username = self.ApiLogout(args['access_token'])
                config.logger.info('IP: ' + client_ip + ' username: ' + username + ' logout success')
                return self.ApiAnswer('', 'success', '')

        '''If cluster not created'''
        if 'cluster' not in config.cluster_config:
            if len(url) >= 2 and url[0] in ['cluster'] and url[1] in ['create', 'join']:
                config.logger.info(
                    'IP: ' + client_ip + ' (' + self.ApiGetUser(args['access_token']) + ')' + 'create or join cluster')
            else:
                config.logger.debug(
                    'IP: ' + client_ip + ' (' + self.ApiGetUser(args['access_token']) + ')' + 'cluster not created')
                return self.ApiAnswer('', 'error', 'cluster not created')

        '''Main api process'''
        if len(url) >= 2:
            if os.access('src/api/api_' + url[0] + '_class.py', os.F_OK):
                api_module = importlib.import_module('src.api.api_' + url[0] + '_class')
                api_class = getattr(api_module, url[0])
                api_instance = api_class(url, args, client_ip, self.ApiGetUser(args['access_token']))

                if url[1] in dir(api_instance):
                    getattr(api_instance, url[1])()
                    if api_instance.SaveConfiguration:
                        self.SaveConfiguration()
                    return self.ApiAnswer(api_instance.answer_msg, api_instance.answer_status, api_instance.answer_error)

        '''If nothing matches, we return an error that the path is not correct.'''
        return self.ApiAnswer('', 'error', 'wrong api path')

    '''Login API client'''
    def ApiLogin(self, username, password):
        if username not in config.cluster_config['systems']['users']:
            return False
        if config.cluster_config['systems']['users'][username]['password'] != hashlib.md5(password.encode("utf-8")).hexdigest():
            return False
        return True

    def ApiLogout(self, access_token):
        self.api_access_tokens[access_token]['expiration'] = 0
        return self.api_access_tokens[access_token]['username']

    def ApiWriteToken(self, username, client_ip):
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        user_token = ''.join(random.choice(string.ascii_uppercase) for i in range(60))
        self.api_access_tokens[user_token] = {
            "username": username,
            "ip": client_ip,
            "expiration": utc_time + config.token_timeout
        }
        return user_token

    def ApiGetUser(self, access_token):
        return self.api_access_tokens[access_token]['username']

    def ApiCheckToken(self, access_token, client_ip):
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        '''Delete invalid tokens'''
        if len(self.api_access_tokens) > 0:
            for key in list(self.api_access_tokens):
                if self.api_access_tokens[key]['expiration'] < utc_time:
                    del self.api_access_tokens[key]

        if len(self.api_access_tokens) == 0:
            return False

        if access_token in self.api_access_tokens:
            if self.api_access_tokens[access_token]['ip'] != client_ip:
                return False
            else:
                self.api_access_tokens[access_token]['expiration'] = utc_time + config.token_timeout
                return True
        return False

    '''Answer for API clients'''
    def ApiAnswer(self, msg, status, error):
        config.logger.name = 'API'
        if msg == '':
            msg = {}
        answer = {
            'msg': msg,
            'status': status,
            'error': error
        }
        config.logger.debug('ApiAnswer:' + str(answer))
        return json.dumps(answer, indent=1)

    '''Answer for MNG clients'''
    def MngAnswer(self, msg, status, error):
        config.logger.name = 'MNG'
        if msg == '':
            msg = {}
        answer = {
            'msg': msg,
            'status': status,
            'error': error
        }
        config.logger.debug('MngAnswer:' + str(answer))
        return json.dumps(answer, indent=1)

    '''Start Scheduler for all nodes'''
    def MngSchedulersStart(self):
        files = os.listdir('src/mng')
        for file in files:
            result = re.split(r'_', file)
            if result[0] == 'mng' and result[2] == 'class.py':
                self.MngSchedulerStart(result[1])

    '''Start Scheduler all per class'''
    def MngSchedulerStart(self, scheduler):
        mng_module = importlib.import_module('src.mng.mng_' + scheduler + '_class')
        mng_class = getattr(mng_module, scheduler)
        mng_instance = mng_class(self.mng_port, [], {}, '')

        for metchod in dir(mng_instance):
            temp = re.split(r'_', metchod)
            if temp[0] == 'Scheduler':
                config.logger.name = 'SYSTEM'
                config.logger.info('Start Scheduler: ' + scheduler + '/' + metchod)
                threading.Thread(target=getattr(mng_instance, metchod), args=()).start()

'''
        if ClientApi.token_status == False:
            return ClientApi.Answer()

        if 'cluster' not in config.cluster_config:
            if len(url) >= 2 and url[0] == 'cluster' and url[1] in ['create', 'join']:
                config.logger.info(ClientApi.client_ip + ' (' + ClientApi.username + ') ' + 'create or join cluster')
            else:
                ClientApi.answer_status = 'error'
                ClientApi.answer_error = 'Cluster not created'
                config.logger.debug(ClientApi.client_ip + ' (' + ClientApi.username + ') ' + 'cluster not created')
                return ClientApi.Answer()

        if not ClientApi.ManagementNode():
            ClientApi.answer_msg = {}
            ClientApi.answer_status = 'error'
            ClientApi.answer_error = 'not management node'
            config.logger.error(ClientApi.client_ip + ' (' + ClientApi.username + ') ' + 'not management node')
            return ClientApi.Answer()

        if len(url) >= 2:
            if os.access('src/api/api_' + url[0] + '_class.py', os.F_OK):
                api_module = importlib.import_module('src.api.api_' + url[0] + '_class')
                api_class = getattr(api_module, url[0])
                api_instance = api_class(url, args, client_ip, ClientApi.username)

                if url[1] in dir(api_instance):
                    getattr(api_instance, url[1])()

                    ClientApi.answer_msg = api_instance.answer_msg
                    ClientApi.answer_error = api_instance.answer_error
                    ClientApi.answer_status = api_instance.answer_status
                    if api_instance.SaveConfiguration:
                        SaveConfiguration()
                else:
                    ClientApi.answer_msg = {}
                    ClientApi.answer_status = 'error'
                    ClientApi.answer_error = 'Wrong API path'
                    config.logger.error(ClientApi.client_ip + ' (' + ClientApi.username + ') ' + 'wrong api path')
                    return ClientApi.Answer()
                del api_class
            else:
                ClientApi.answer_msg = {}
                ClientApi.answer_status = 'error'
                ClientApi.answer_error = 'Wrong API path'
                config.logger.error(ClientApi.client_ip + ' (' + ClientApi.username + ') ' + 'wrong api path')
                return ClientApi.Answer()

        r = ClientApi.Answer()
        del ClientApi
        return r
    '''




'''
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

                try:
                    answer = json.loads(send.text)
                except ValueError as e:
                    config.cluster_nodes_status[key]['status'] = 'offline'
                    config.cluster_nodes_status[key]['error'] = str(e)
                else:
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
'''
'''
    def ReadClusterTasks():
        try:
            os.mkdir('config')
        except Exception as e:
            print(e)
        if not os.access('config/docluster.tasks', os.F_OK):
            f = open('config/docluster.tasks', 'w+')
            json.dump(config.cluster_tasks, f, indent=1)
            f.close()

        with open('config/docluster.tasks') as json_file:
            config.cluster_tasks = json.load(json_file)
            json_file.close()
'''