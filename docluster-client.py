#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import os
import json
from prettytable import PrettyTable



api_url = "http://192.168.129.198:3033/api/"

#api_url = "http://192.168.129.82:3033/api/"
#api_url = "http://192.168.129.83:3033/api/"
#api_url = "http://192.168.129.84:3033/api/"
api_login = 'admin'
api_pss = 'admin'
access_token = ''


try:
    response = requests.get(api_url)
    print(f'Server available {api_url}')
except:
    print(f'Server not available {api_url} ')
    exit()

if os.access('access_token.tmp', os.F_OK) == False:
    f = open('access_token.tmp', 'w+')
    f.close()

f = open('access_token.tmp')
access_token = f.read()
f.close()


def login():
    global access_token
    send_token = requests.post(url=api_url+'login/', data={"access_token": access_token})
    answer_token = json.loads(send_token.text)
    if answer_token['status'] == 'success':
        print("Authorized on " + api_url)
    if answer_token['status'] == 'error':
        print("Not authorized")
        print("Login request to " + api_url)
        send_login = requests.post(url=api_url+'login/', data={"username": api_login, "password": api_pss})
        answer_login = json.loads(send_login.text)
        #print(send_login.text)
        if answer_login['status'] == 'success':
            access_token = answer_login['msg']['access_token']
            f = open('access_token.tmp', 'w+')
            f.write(access_token)
            f.close()
            print("Authorization was successful to " + api_url)
            return True
        else:
            print("Failed login to " + api_url)
            print("Error: " + answer_login['error'])
            return False


def logout():
    send_logout = requests.post(url=api_url + 'logout', data={"access_token": access_token})
    answer_logout = json.loads(send_logout.text)
    if answer_logout['status'] == 'success':
        print("Logout " + api_url)
        return True
    else:
        print("Error: " + answer_logout['error'])
        return False


def send(path, data):
    data['access_token'] = access_token
    send = requests.post(url=api_url + path, data=data)
    return json.loads(send.text)
############################################################3

def cluster_create():
    path = 'cluster/create'
    data = {}
    send(path, data)

def cluster_join():
    path = 'cluster/join'
    data = {
        'cluster_username': 'admin',
        'cluster_password': 'admin',
        'cluster_ip': '192.168.129.198',
    }
    send(path, data)


def cluster_status():
    path = 'cluster/status'
    data = {}
    return send(path, data)

def quorum_status():
    path = 'quorum/status'
    data = {}
    return send(path, data)

'''Argument is a username, if argument not set return all users'''
def systems_users_get(username=None):
    path = 'systems/users/get'
    if username == None:
        data = {}
    else:
        data = {'username': username}
    send(path, data)

'''Add user'''
def systems_users_add(username,password):
    path = 'systems/users/add'
    data = {
        'username': username,
        'password': password
    }
    send(path, data)

'''Delete user'''
def systems_users_delete(username):
    path = 'systems/users/delete'
    data = {
        'username': username
    }
    send(path, data)

def systems_users_set(username,password,email):
    path = 'systems/users/set'
    data = {
        'username': username,
        'password': password,
        'email': email
    }
    send(path, data)

######################################################

def systems_hosts_set(ip,hostname):
    path = 'systems/hosts/set'
    data = {
        'ip': ip,
        'hostname': hostname,
    }
    send(path, data)

def systems_hosts_delete(ip,hostname):
    path = 'systems/hosts/delete'
    data = {
        'ip': ip,
        'hostname': hostname,
    }
    send(path, data)

def systems_hosts_get():
    path = 'systems/hosts/get'
    data = {}
    send(path, data)


def tokens():
    path = 'tokens'
    data = {}
    send(path, data)


def cluster_management_get():
    path = 'cluster/management/get'
    data = {}
    send(path, data)


#login()
#quorum_status()
#cluster_management_get()
#cluster_status()
#tokens()
#cluster_create()
#cluster_join()
#systems_hosts_set('5.2.3.23', 'dupa-23')
#systems_hosts_get()
#systems_hosts_delete('1.2.3.1', 'dupa-1')
#systems_users_get()
#systems_users_add('dimon', 'QWEqwe123')
#systems_users_delete('admin')
#systems_users_set('admin', 'QWEqwe123', 'admin@clastercp.com')
#logout()

import cmd2
from cmd2 import (Bg, Fg, style,)
import argparse

import cmd2
from cmd2 import (
    CommandSet,
    with_argparser,
    with_category,
    with_default_category,
)



class BasicApp(cmd2.Cmd):

    def __init__(self):

        super().__init__(
            persistent_history_file='cmd2_history.dat',
        )
        self.intro = style('Welcome to DoCluster !', fg=Fg.RED, bg=Bg.WHITE, bold=True) + ' 😀'

        self.prompt = 'DoCluster> '
        self.do_login('_')


    def do_login(self, _):
        if login():
            self.prompt = style(api_login, fg=Fg.BLUE, bold=True) + style('@', fg=Fg.RED, bold=True) + style('DoCluster # ', fg=Fg.GREEN, bold=True)

    def do_logout(self, _):
        if logout():
            self.prompt = 'DoCluster> '


    '''     Quorum      '''
    load_parser = cmd2.Cmd2ArgumentParser()
    load_parser.add_argument('quorum', choices=['status', 'add', 'delete'])
    @with_argparser(load_parser)
    def do_quorum(self, ns: argparse.Namespace):
        if ns.quorum == 'status':
            answer = quorum_status()
            if answer['status'] != 'success':
                print('Answer status: ' + answer['status'])
                print('Answer error: ' + answer['error'])
            else:
                table = PrettyTable()
                table.title = 'DoCluster Quorum'
                table.header = False
                table.add_row(['Quorum status', answer['msg']['quorum_status']['status']])
                table.add_row(['Master nod', answer['msg']['quorum_status']['master']])
                table.add_row(['Quorum errors', str(answer['msg']['quorum_status']['errors'])])
                print(table)

                table = PrettyTable()
                table.field_names = ['Node hostname', 'status', 'Config version', 'Errors']
                for key in answer['msg']['quorum_status']['nodes']:
                    if key['status'] == 'offline':
                        table.add_row([key['node'],key['status'], '---', str(key['error'])])
                    else:
                        table.add_row([key['node'], key['status'], key['config_version'], str(key['error'])])
                print(table)


    '''         Cluster     '''
    load_parser = cmd2.Cmd2ArgumentParser()
    load_parser.add_argument('cluster', choices=['status', 'create', 'join'])
    @with_argparser(load_parser)
    def do_cluster(self, ns: argparse.Namespace):
        if ns.cluster == 'status':
            answer = cluster_status()
            if answer['status'] != 'success':
                print('Answer status: ' + answer['status'])
                print('Answer error: ' + answer['error'])
            else:
                table = PrettyTable()
                table.title = 'DoCluster Cluster'
                table.header = False
                table.add_row(['Cluster status', answer['msg']['status']])
                table.add_row(['Cluster errors', str(answer['msg']['errors'])])
                print(table)

                table = PrettyTable()
                table.field_names = ['Node hostname', 'status', 'CPU', 'RAM', 'RAM total', 'Config version', 'Errors']
                for key in answer['msg']['nodes']:
                    if answer['msg']['nodes'][key]['status'] == 'offline':
                        table.add_row([
                            key,
                            answer['msg']['nodes'][key]['status'],
                            '---',
                            '---',
                            '---',
                            '---',
                            '---',
                        ])
                    else:
                        table.add_row([
                            key,
                            answer['msg']['nodes'][key]['status'],
                            str(answer['msg']['nodes'][key]['cpu_percent']),
                            str(answer['msg']['nodes'][key]['memory_percent']),
                            str(answer['msg']['nodes'][key]['memory_total']),
                            str(answer['msg']['nodes'][key]['config_version']),
                            str(answer['msg']['nodes'][key]['errors'])
                        ])
                print(table)










if __name__ == '__main__':
    app = BasicApp()
    app.cmdloop()