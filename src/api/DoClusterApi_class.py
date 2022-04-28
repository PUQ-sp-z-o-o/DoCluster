import config
import json
import datetime
import calendar
import hashlib
import random
import string
import os

class DoClustercpApi:

    config.logger.name = 'API'
    access_tokens = config.access_tokens
    token_timeout = config.token_timeout
    user_token = ''
    user_token_server = {}
    token_status = False
    url = ''
    args = {}
    client_ip = ''
    answer_msg = {}
    answer_error = ''
    answer_status = ''
    username = ''
    password = ''

    def __init__(self, url, args, client_ip):
        self.url = url
        self.args = args
        self.client_ip = client_ip

        if args == {}:
            self.user_token = ''
        else:
            if 'access_token' in args.keys():
                self.user_token = args['access_token']
            else:
                self.user_token = ''
            if 'username' in args.keys():
                self.username = args['username']
            if 'password' in args.keys():
                self.password = args['password']

        self.user_token_server = config.access_tokens.get(self.user_token, '')

        if self.CheckToken():
            if len(self.url) == 1 and self.url[0] == 'logout':
                self.__logout()

            if len(self.url) == 1 and self.url[0] == 'tokens':
                self.__tokens()
        else:
            if len(self.url) == 1 and self.url[0] == 'login':
                self.__login()

        if len(self.url) == 1 and self.url[0] not in ['logout', 'login', 'tokens']:
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = 'Wrong API path'
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'wrong api path')

        config.logger.debug(
            self.client_ip + ' (' + self.username + ') ' + 'URL: ' + str(self.url) + ' POST: ' + str(self.args))

    def CheckToken(self):
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        '''Delete invalid tokens'''
        if len(config.access_tokens) > 0:
            for key in list(config.access_tokens):
                if config.access_tokens[key]['expiration'] < utc_time:
                    del config.access_tokens[key]

        self.answer_status = 'false'

        if not self.user_token_server:
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'wrong token')
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = 'Token not found, please log in.'
            return False
        if self.user_token_server == '':
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'wrong token')
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = 'Token not found, please log in.'
            return False
        if self.user_token_server['ip'] != self.client_ip:
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'wrong token')
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = 'The token is not important for this IP address, please log in.'
            return False
        if self.user_token_server['expiration'] < utc_time:
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'wrong token')
            self.answer_msg = {}
            self.answer_status = 'error'
            self.answer_error = 'Token expired please log in.'
            return False
        self.user_token_server['expiration'] = utc_time + self.token_timeout
        config.access_tokens[self.user_token]['expiration'] = utc_time + self.token_timeout
        self.username = self.user_token_server['username']
        config.logger.debug(self.client_ip + ' (' + self.username + ') ' + 'success token')
        self.answer_status = 'success'
        self.token_status = True
        return True

    def __login(self):
        self.answer_status = 'false'

        if self.username not in config.cluster_config['systems']['users']:
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'wrong login or password')
            self.answer_msg = {}
            self.answer_error = 'Username not found, please log in.'
            return False

        if config.cluster_config['systems']['users'][self.username]['password'] != hashlib.md5(self.password.encode("utf-8")).hexdigest():
            config.logger.error(self.client_ip + ' (' + self.username + ') ' + 'wrong login or password')
            self.answer_msg = {}
            self.answer_error = 'Wrong password.'
            return False

        config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'login success')
        self.answer_status = "success"
        self.answer_error = ''
        self.answer_msg = {"access_token": self.__WriteToken()}

    def __logout(self):
        config.access_tokens[self.user_token]['expiration'] = 0
        config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'logout success')
        self.answer_status = "success"
        self.answer_error = ''
        self.answer_msg = ''
        return 0

    def __tokens(self):
        self.answer_status = "success"
        self.answer_error = ''
        self.answer_msg['tokens'] = config.access_tokens
        return 0

    def __WriteToken(self):
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        self.user_token = ''.join(random.choice(string.ascii_uppercase) for i in range(60))
        config.access_tokens[self.user_token] = {
            "username": self.username,
            "ip": self.client_ip,
            "expiration": utc_time + self.token_timeout
        }
        return self.user_token

    def ManagementNode(self):
        if 'cluster' not in config.cluster_config:
            return True
        for node in config.cluster_config['cluster']['quorum']:
            if node['node'] == os.uname()[1]:
                return True
        return False

    def Answer(self):
        answer = {
            'msg': self.answer_msg,
            'status': self.answer_status,
            'error': self.answer_error
        }
        return json.dumps(answer, indent=1)
