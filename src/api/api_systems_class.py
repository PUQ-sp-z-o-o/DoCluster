import config
import os
import json
import random
import string
import hashlib
from src.functions import *


class systems:

    SaveConfiguration = False
    url = []
    args = {}
    client_ip = ''

    answer_msg = {}
    answer_error = 'wrong api path'
    answer_status = 'error'
    username = ''

    def __init__(self, url, args, client_ip, username):
        self.url = url
        self.args = args
        self.client_ip = client_ip
        self.username = username
        self.answer_msg = {}

    '''
    System User Manager. Create, edit, delete, display
    '''
    def users(self):
        if len(self.url) != 3:
            return 0
        if self.url[2] not in ['get', 'set', 'add', 'delete']:
            return 0

        '''Get user per username or all if username not defined'''
        if self.url[2] == 'get':
            if 'username' in self.args:
                if self.args['username'] not in config.cluster_config['systems']['users']:
                    self.answer_status = 'error'
                    self.answer_error = 'username not found'
                    return 0
                self.answer_msg[self.args['username']] = config.cluster_config['systems']['users'][self.args['username']]
                self.answer_status = 'success'
                self.answer_error = ''
            else:
                self.answer_msg = config.cluster_config['systems']['users']
                self.answer_status = 'success'
                self.answer_error = ''

        '''Add new user'''
        if self.url[2] == 'add':
            if 'username' not in self.args or 'password' not in self.args:
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0
            if self.args['username'] == '' or self.args['password'] == '':
                self.answer_status = 'error'
                self.answer_error = 'username and password must not be empty'
                return 0
            if self.args['username'] in config.cluster_config['systems']['users']:
                self.answer_status = 'error'
                self.answer_error = 'user already exists'
                return 0

            pass_tmp = self.args['password']
            config.cluster_config['systems']['users'][self.args['username']] = {"password": hashlib.md5(pass_tmp.encode("utf-8")).hexdigest()}
            self.SaveConfiguration = True
            self.answer_msg[self.args['username']] = config.cluster_config['systems']['users'][self.args['username']]
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'created user: ' + self.args['username'])

        '''Delete user'''
        if self.url[2] == 'delete':
            if 'username' not in self.args:
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0
            if self.args['username'] not in config.cluster_config['systems']['users']:
                self.answer_status = 'error'
                self.answer_error = 'user does not exist'
                return 0
            if self.args['username'] in config.cluster_config['systems']['users'] and len(config.cluster_config['systems']['users']) == 1:
                self.answer_status = 'error'
                self.answer_error = 'Can not delete last user'
                return 0

            del config.cluster_config['systems']['users'][self.args['username']]
            self.SaveConfiguration = True
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'delete user: ' + self.args['username'])

        '''Update user'''
        if self.url[2] == 'set':
            if 'username' not in self.args:
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0
            if self.args['username'] not in config.cluster_config['systems']['users']:
                self.answer_status = 'error'
                self.answer_error = 'user does not exist'
                return 0
            if 'password' in self.args:
                if self.args['password'] != '':
                    pass_tmp = self.args['password']
                    config.cluster_config['systems']['users'][self.args['username']]['password'] = hashlib.md5(pass_tmp.encode("utf-8")).hexdigest()

            if 'email' in self.args:
                config.cluster_config['systems']['users'][self.args['username']]['email'] = self.args['email']

            self.SaveConfiguration = True
            self.answer_msg[self.args['username']] = config.cluster_config['systems']['users'][self.args['username']]
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'Update user: ' + self.args['username'])

    '''
    System HOSTS file Manager. 
    Add, delete, display records on system hosts file
    '''
    def hosts(self):
        '''Ddd'''
        if self.url[2] == 'set':
            if 'ip' not in self.args or 'hostname' not in self.args:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0

            if not is_valid_ip(self.args['ip']) or not is_valid_hostname(self.args['hostname']):
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'wrong IP or hostname format'
                return 0

            if 'hosts' not in config.cluster_config['systems']:
                config.cluster_config['systems']['hosts'] = {}

            if self.args['ip'] not in config.cluster_config['systems']['hosts']:
                config.cluster_config['systems']['hosts'][self.args['ip']] = []

            if self.args['hostname'] in config.cluster_config['systems']['hosts'][self.args['ip']]:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'hostname already added'
                return 0

            self.SaveConfiguration = True
            config.cluster_config['systems']['hosts'][self.args['ip']].append(self.args['hostname'])
            self.answer_msg[self.args['ip']] = config.cluster_config['systems']['hosts'][self.args['ip']]
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'Added in hosts: ' + self.args['ip'] + ':' + self.args['hostname'])
        '''Get'''
        if self.url[2] == 'get':
            self.answer_msg = config.cluster_config['systems']['hosts']
            self.answer_status = 'success'
            self.answer_error = ''
        '''Delete'''
        if self.url[2] == 'delete':
            if 'ip' not in self.args or 'hostname' not in self.args:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0

            if not is_valid_ip(self.args['ip']) or not is_valid_hostname(self.args['hostname']):
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'wrong IP or hostname format'
                return 0

            if self.args['ip'] not in config.cluster_config['systems']['hosts']:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'ip not definite in hosts'
                return 0

            if self.args['hostname'] not in config.cluster_config['systems']['hosts'][self.args['ip']]:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'hostname not definite in hosts'
                return 0

            self.SaveConfiguration = True
            config.cluster_config['systems']['hosts'][self.args['ip']].remove(self.args['hostname'])

            if len(config.cluster_config['systems']['hosts'][self.args['ip']]) == 0:
                del(config.cluster_config['systems']['hosts'][self.args['ip']])
            self.answer_msg = {}
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'Delete in hosts: ' + self.args['ip'] + ':' + self.args['hostname'])
