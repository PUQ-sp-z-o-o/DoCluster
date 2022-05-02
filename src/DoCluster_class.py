import config
from src.functions import *
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

        ReadConfiguration()
        #self.SaveConfiguration()
        #self.MngSchedulersStart()

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
            server_ip = request.host.split(':')[0]
            url = list(filter(None, path.split('/')))
            return self.ApiRequestProcessor(url, args, client_ip, server_ip)

        def api_web():
            api.run(host='0.0.0.0', port=config.api_port, use_reloader=False)

        config.logger.info('Start API service. Port: ' + str(config.api_port))
        threading.Thread(target=api_web, daemon=False).start()

    ''' The function is responsible for processing requests from the client API and returns a response. '''
    def ApiRequestProcessor(self, url, args, client_ip, server_ip):
        config.logger.name = 'API'
        config.logger.debug(client_ip + ' URL: ' + str(url) + ' POST: ' + str(args))

        '''Loging and create valid access token'''
        if len(url) == 1:
            if url[0] == 'login':
                if 'username' in args and 'password' in args:
                    if self.ApiLogin(args['username'], args['password']):
                        config.logger.info(client_ip + ' username: ' + args['username'] + ' login success')
                        return self.ApiAnswer({'access_token': self.ApiWriteToken(args['username'], client_ip)},
                                              'success',
                                              '')
                    else:
                        config.logger.error(client_ip + ' username: ' + args['username'] + ' access denied')
                        return self.ApiAnswer('', 'error', 'access denied')

        '''Check Token'''
        if 'access_token' not in args:
            return self.ApiAnswer('', 'error', 'wrong token')
        if 'access_token' in args:
            if not self.ApiCheckToken(args['access_token'], client_ip):
                config.logger.error(client_ip + ' wrong token')
                return self.ApiAnswer('', 'error', 'wrong token')

        '''Logout'''
        if len(url) == 1:
            if url[0] == 'logout':
                username = self.ApiLogout(args['access_token'])
                config.logger.info(client_ip + ' username: ' + username + ' logout success')
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

        '''If not manager master node'''
        #if config.quorum_status['master'] != os.uname()[1]:
        #    return self.ApiAnswer({'master':  config.quorum_status['master']}, 'error', 'not manager master node')

        '''Main api process'''
        if len(url) >= 2:
            if os.access('src/api/api_' + url[0] + '_class.py', os.F_OK):
                api_module = importlib.import_module('src.api.api_' + url[0] + '_class')
                api_class = getattr(api_module, url[0])
                api_instance = api_class(url, args, client_ip, self.ApiGetUser(args['access_token']), server_ip)

                if url[1] in dir(api_instance):
                    getattr(api_instance, url[1])()
                    return self.ApiAnswer(api_instance.answer_msg, api_instance.answer_status, api_instance.answer_error)

        '''If nothing matches, we return an error that the path is not correct.'''
        return self.ApiAnswer('', 'error', 'wrong api path')

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
        threading.Thread(target=mng_web, daemon=False).start()
        #mng_t = threading.Thread(target=mng_web, daemon=False)
        #mng_t.start()

    ''' The function is responsible for processing requests from the nodes MNG and returns a response. '''
    def MngRequestProcessor(self, url, args, client_ip):
        config.logger.name = 'MNG'
        config.logger.debug(client_ip + ' URL: ' + str(url) + ' POST: ' + str(args))

        if 'hash' not in args:
            config.logger.name = 'MNG'
            config.logger.warning(client_ip + ' no hash value')
            return self.ApiAnswer('', 'error', 'no hash value')

        local_hash = client_ip + \
                            config.cluster_config['cluster']['nodes'][os.uname()[1]]['MNG_IP'] + \
                            config.cluster_config['cluster']['nodes'][os.uname()[1]]['API_key']
        local_hash = hashlib.md5(local_hash.encode("utf-8")).hexdigest()

        config.logger.name = 'MNG'
        config.logger.debug(client_ip + ' Local hash: ' + local_hash)
        config.logger.debug(client_ip + ' Remote hash: ' + args['hash'])

        if 'cluster' in url and 'join' in url:
            if url[0] == 'cluster' and url[1] == 'join':
                local_hash = ''

        if args['hash'] != local_hash:
            config.logger.name = 'MNG'
            config.logger.warning(client_ip + ' The hash does not match')
            return self.ApiAnswer('', 'error', 'the hash does not match')

        if len(url) >= 2:
            if os.access('src/mng/mng_' + url[0] + '_class.py', os.F_OK):
                mng_module = importlib.import_module('src.mng.mng_' + url[0] + '_class')
                mng_class = getattr(mng_module, url[0])
                mng_instance = mng_class(self.mng_port, url, args, client_ip)

                if url[1] in dir(mng_instance):
                    getattr(mng_instance, url[1])()
                    return self.MngAnswer(mng_instance.answer_msg, mng_instance.answer_status, mng_instance.answer_error)

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
        config.api_access_tokens[access_token]['expiration'] = 0
        return config.api_access_tokens[access_token]['username']

    def ApiWriteToken(self, username, client_ip):
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        user_token = ''.join(random.choice(string.ascii_uppercase) for i in range(60))
        config.api_access_tokens[user_token] = {
            "username": username,
            "ip": client_ip,
            "expiration": utc_time + config.token_timeout
        }
        return user_token

    def ApiGetUser(self, access_token):
        return config.api_access_tokens[access_token]['username']

    def ApiCheckToken(self, access_token, client_ip):
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        '''Delete invalid tokens'''
        if len(config.api_access_tokens) > 0:
            for key in list(config.api_access_tokens):
                if config.api_access_tokens[key]['expiration'] < utc_time:
                    del config.api_access_tokens[key]

        if len(config.api_access_tokens) == 0:
            return False

        if access_token in config.api_access_tokens:
            if config.api_access_tokens[access_token]['ip'] != client_ip:
                return False
            else:
                config.api_access_tokens[access_token]['expiration'] = utc_time + config.token_timeout
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
            if len(result) == 3:
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

