from src.api.api_class import api
from src.functions import *
import config
import os
import json
import random
import string
import hashlib
import threading
from src.functions import *
import ctypes


class system(api):

    '''
    System User Manager. Create, edit, delete, display
    '''
    def users(self):
        if len(self.url) != 3:
            return 0
        if self.url[2] not in ['get', 'set', 'add', 'delete']:
            return 0

        '''
        Get user per username or all if username not defined
        '''
        if self.url[2] == 'get':
            if 'username' in self.args:
                if self.args['username'] not in config.cluster_config['system']['users']:
                    self.answer_status = 'error'
                    self.answer_error = 'username not found'
                    return 0
                self.answer_msg[self.args['username']] = config.cluster_config['system']['users'][self.args['username']]
                self.answer_status = 'success'
                self.answer_error = ''
            else:
                self.answer_msg = config.cluster_config['system']['users']
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
            if self.args['username'] in config.cluster_config['system']['users']:
                self.answer_status = 'error'
                self.answer_error = 'user already exists'
                return 0

            pass_tmp = self.args['password']
            config.cluster_config['system']['users'][self.args['username']] = {"password": hashlib.md5(pass_tmp.encode("utf-8")).hexdigest()}
            SaveConfiguration()
            self.answer_msg[self.args['username']] = config.cluster_config['system']['users'][self.args['username']]
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'created user: ' + self.args['username'])

        '''Delete user'''
        if self.url[2] == 'delete':
            if 'username' not in self.args:
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0
            if self.args['username'] not in config.cluster_config['system']['users']:
                self.answer_status = 'error'
                self.answer_error = 'user does not exist'
                return 0
            if self.args['username'] in config.cluster_config['system']['users'] and len(config.cluster_config['system']['users']) == 1:
                self.answer_status = 'error'
                self.answer_error = 'Can not delete last user'
                return 0

            del config.cluster_config['system']['users'][self.args['username']]
            SaveConfiguration()
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'delete user: ' + self.args['username'])

        '''Update user'''
        if self.url[2] == 'set':
            if 'username' not in self.args:
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0
            if self.args['username'] not in config.cluster_config['system']['users']:
                self.answer_status = 'error'
                self.answer_error = 'user does not exist'
                return 0

            if 'email' in self.args:
                if not is_valid_email(self.args['email']):
                    self.answer_status = 'error'
                    self.answer_error = 'wrong email format'
                    return 0

            if 'password' in self.args:
                if self.args['password'] != '':
                    pass_tmp = self.args['password']
                    config.cluster_config['system']['users'][self.args['username']]['password'] = hashlib.md5(pass_tmp.encode("utf-8")).hexdigest()

            if 'email' in self.args:
                config.cluster_config['system']['users'][self.args['username']]['email'] = self.args['email']

            SaveConfiguration()
            self.answer_msg[self.args['username']] = config.cluster_config['system']['users'][self.args['username']]
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'Update user: ' + self.args['username'])

    '''
    System HOSTS file Manager. 
    Add, delete, display records on system hosts file
    '''
    def hosts(self):
        '''Ddd'''
        if self.url[2] == 'add':
            if 'hosts' not in config.cluster_config['system']:
                config.cluster_config['system']['hosts'] = {}

            if self.args['ip'] not in config.cluster_config['system']['hosts']:
                config.cluster_config['system']['hosts'][self.args['ip']] = []

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

            if self.args['hostname'] in config.cluster_config['system']['hosts'][self.args['ip']]:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'hostname already added'
                return 0

            config.cluster_config['system']['hosts'][self.args['ip']].append(self.args['hostname'])
            self.answer_msg[self.args['ip']] = config.cluster_config['system']['hosts'][self.args['ip']]
            SaveConfiguration()
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'Added in hosts: ' + self.args['ip'] + ':' + self.args['hostname'])
        '''Get'''
        if self.url[2] == 'get':
            if 'hosts' not in config.cluster_config['system']:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'there is nothing to output'
                return 0

            if 'ip' in self.args:
                if not is_valid_ip(self.args['ip']):
                    self.answer_msg = {}
                    self.answer_status = 'error'
                    self.answer_error = 'wrong IP or hostname format'
                    return 0

            if 'hostname' in self.args:
                if not is_valid_hostname(self.args['hostname']):
                    self.answer_msg = {}
                    self.answer_status = 'error'
                    self.answer_error = 'wrong IP or hostname format'
                    return 0

            if 'ip' not in self.args and 'hostname' not in self.args:
                self.answer_msg = config.cluster_config['system']['hosts']
                self.answer_status = 'success'
                self.answer_error = ''
                return 0

            if 'ip' in self.args and 'hostname' not in self.args:
                if self.args['ip'] not in config.cluster_config['system']['hosts']:
                    self.answer_msg = {}
                    self.answer_status = 'error'
                    self.answer_error = 'IP or hostname not found'
                    return 0
                self.answer_msg[self.args['ip']] = config.cluster_config['system']['hosts'][self.args['ip']]
                self.answer_status = 'success'
                self.answer_error = ''
                return 0

            if 'ip' not in self.args and 'hostname' in self.args:
                for ip in config.cluster_config['system']['hosts']:
                    for hostname in config.cluster_config['system']['hosts'][ip]:
                        if hostname == self.args['hostname']:
                            self.answer_msg[ip] = [hostname]
                if len(self.answer_msg) == 0:
                    self.answer_msg = {}
                    self.answer_status = 'error'
                    self.answer_error = 'IP or hostname not found'
                    return 0
                self.answer_status = 'success'
                self.answer_error = ''
                return 0


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

            if self.args['ip'] not in config.cluster_config['system']['hosts']:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'ip not definite in hosts'
                return 0

            if self.args['hostname'] not in config.cluster_config['system']['hosts'][self.args['ip']]:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'hostname not definite in hosts'
                return 0

            config.cluster_config['system']['hosts'][self.args['ip']].remove(self.args['hostname'])
            if len(config.cluster_config['system']['hosts'][self.args['ip']]) == 0:
                del(config.cluster_config['system']['hosts'][self.args['ip']])
            SaveConfiguration()
            self.answer_msg = {}
            self.answer_status = 'success'
            self.answer_error = ''
            config.logger.info(self.client_ip + ' (' + self.username + ') ' + 'Delete in hosts: ' + self.args['ip'] + ':' + self.args['hostname'])

    '''
    GET SAVE and READ cluster configuration
    '''
    def config(self):

        if self.url[2] == 'get':
            self.answer_status = 'success'
            self.answer_msg = config.cluster_config
            self.answer_error = ''

        if self.url[2] == 'save':
            SaveConfiguration()
            self.answer_status = 'success'
            self.answer_msg = config.cluster_config
            self.answer_error = ''

        if self.url[2] == 'read':
            ReadConfiguration()
            self.answer_status = 'success'
            self.answer_msg = config.cluster_config
            self.answer_error = ''

    def loops(self):
        self.answer_msg.clear()
        if self.url[2] == 'get':
            threads = [t for t in config.schedulers.values()]
            for thread in threads:
                self.answer_msg[thread['loop'].name] = {}
                if thread['loop'].is_alive():
                    self.answer_msg[thread['loop'].name]['isAlive'] = True
                    self.answer_msg[thread['loop'].name]['counter'] = config.schedulers[thread['loop'].name]['counter']
                    self.answer_msg[thread['loop'].name]['ident'] = str(thread['loop'].ident)
                    self.answer_msg[thread['loop'].name]['native_id'] = str(thread['loop'].native_id)
                    self.answer_msg[thread['loop'].name]['timeout'] = config.schedulers[thread['loop'].name]['timeout']
                else:
                    self.answer_msg[thread['loop'].name]['isAlive'] = False
            self.answer_status = 'success'
            self.answer_error = ''
            return 0


        '''
        if self.url[2] == 'stop':
            if 'name' not in self.args:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'data not submitted'
                return 0

            if self.args['name'] not in config.schedulers:
                self.answer_msg = {}
                self.answer_status = 'error'
                self.answer_error = 'Loop not found'
                return 0

            threads = [t for t in config.schedulers.values()]
            for thread in threads:
                if thread['loop'].name == self.args['name']:
                    self.answer_msg[thread['loop'].name] = {}
                    if thread['loop'].isAlive():
                        print(str(config.schedulers))
                        exc = ctypes.py_object(SystemExit)
                        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread['loop'].ident), exc)
                        print(str(config.schedulers))
                        thread['loop'].join()
                        exit()
                        thread['loop'].start()
                        self.answer_msg = {}
                        self.answer_status = 'success'
                        self.answer_error = ''
                        return 0
        '''

