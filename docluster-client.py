#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import requests
import cmd2
import os
import json
import sys
from prettytable import PrettyTable
from cmd2 import (
    Bg,
    Fg,
    style,
)

api_url = "http://192.168.129.198:3033/api/"
#api_url = "http://192.168.129.82:3033/api/"
#api_url = "http://192.168.129.83:3033/api/"
#api_url = "http://192.168.129.84:3033/api/"
api_username = 'admin'
api_password = 'admin'
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
        send_login = requests.post(url=api_url+'login/', data={"username": api_username, "password": api_password})
        answer_login = json.loads(send_login.text)
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
    answer = {}
    try:
        send = requests.post(url=api_url + path, data=data, timeout=5)
        try:
            send_answer = json.loads(send.text)
        except ValueError as e:
            answer['status'] = 'critical'
            answer['error'] = 'answer problem: ' + str(e)
            answer['msg'] = {}
        else:
            answer = send_answer
    except requests.Timeout:
        answer['status'] = 'offline'
        answer['error'] = 'network problem: Timeout'
        answer['msg'] = {}
    except requests.ConnectionError:
        answer['status'] = 'offline'
        answer['error'] = 'network problem: ConnectionError'
        answer['msg'] = {}

    if answer['status'] != 'success':
        print('Answer status: ' + answer['status'])
        print('Answer error: ' + str(answer['error']))

    return answer
############################################################3

def cluster_create():
    path = 'cluster/create'
    data = {}
    return send(path, data)

def cluster_join(ip, username, password):
    path = 'cluster/join'
    data = {
        'cluster_username': username,
        'cluster_password': password,
        'cluster_ip': ip
    }
    return send(path, data)


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
    return send(path, data)

'''Add user'''
def systems_users_add(username,password):
    path = 'systems/users/add'
    data = {
        'username': username,
        'password': password
    }
    return send(path, data)

'''Delete user'''
def systems_users_delete(username):
    path = 'systems/users/delete'
    data = {
        'username': username
    }
    return send(path, data)

def systems_users_set(username,password,email):
    path = 'systems/users/set'
    data = {
        'username': username,
        'password': password,
        'email': email
    }
    return send(path, data)

######################################################

def systems_hosts_add(ip, hostname):
    path = 'systems/hosts/add'
    data = {
        'ip': ip,
        'hostname': hostname,
    }
    return send(path, data)

def systems_hosts_delete(ip,hostname):
    path = 'systems/hosts/delete'
    data = {
        'ip': ip,
        'hostname': hostname,
    }
    return send(path, data)

def systems_hosts_get(ip,hostname):
    path = 'systems/hosts/get'
    data = {
        'ip': ip,
        'hostname': hostname,
    }
    return send(path, data)

def tokens():
    path = 'tokens'
    data = {}
    send(path, data)


def cluster_management_get():
    path = 'cluster/management/get'
    data = {}
    send(path, data)

def system_config_get():
    path = 'systems/config/get'
    data = {}
    return send(path, data)

def system_config_save():
    path = 'systems/config/save'
    data = {}
    return send(path, data)

def system_config_read():
    path = 'systems/config/read'
    data = {}
    return send(path, data)

def system_loops_get():
    path = 'systems/loops/get'
    data = {}
    return send(path, data)

def system_loops_stop(name):
    path = 'systems/loops/stop'
    data = {
        'name': name
    }
    return send(path, data)

def system_loops_start(name):
    path = 'systems/loops/start'
    data = {
        'name': name
    }
    return send(path, data)

def system_loops_reload(name):
    path = 'systems/loops/reload'
    data = {
        'name': name
    }
    return send(path, data)


def quorum_nodes_add(node):
    path = 'quorum/nodes/add'
    data = {
        'node': node
    }
    return send(path, data)


def quorum_nodes_delete(node):
    path = 'quorum/nodes/delete'
    data = {
        'node': node
    }
    return send(path, data)


#tokens()
#cluster_management_get()

class DoClusterCLI(cmd2.Cmd):

    def __init__(self):

        super().__init__(
            persistent_history_file='cmd2_history.dat',
        )
        self.intro = style('Welcome to DoCluster !', fg=Fg.RED, bg=Bg.WHITE, bold=True) + ' 😀'

        self.prompt = 'DoCluster> '
        self.do_login('_')

    def do_login(self, _):
        if login():
            self.prompt = style(api_username, fg=Fg.BLUE, bold=True) + style('@', fg=Fg.RED, bold=True) + style('DoCluster # ', fg=Fg.GREEN, bold=True)

    def do_logout(self, _):
        if logout():
            self.prompt = 'DoCluster> '

    ##########               SYSTEMS                  ##################################################################
    system_parser = cmd2.Cmd2ArgumentParser()
    system_subparsers = system_parser.add_subparsers(title='system', help='Managing Cluster System Settings')

    ### users
    parser_system_users = system_subparsers.add_parser('users', help='Management of systems users')
    system_users_subparsers = parser_system_users.add_subparsers(title='users', help='help for 3rd layer of commands')

    def system_users(self, args):
        self.do_help('system users')

    parser_system_users.set_defaults(func=system_users)
    '''users get'''
    parser_system_users_get = system_users_subparsers.add_parser('get', help='List of users')
    parser_system_users_get.add_argument('-u', type=str, help='List data of user')
    parser_system_users_get.add_argument('-all', action='store_true', help='List data of all user')

    def system_users_get(self, ns: argparse.Namespace):
        answer = {}
        if ns.all:
            answer = systems_users_get()

        if not ns.all and ns.u is not None:
            answer = systems_users_get(ns.u)

        if 'status' in answer:
            if answer['status'] == 'success':
                table = PrettyTable()
                table.title = 'Cluster users'
                table.field_names = ['Username', 'md5(password)', 'E-mail']
                for user in answer['msg']:
                    email = '---'
                    if 'email' in answer['msg'][user]:
                        email = answer['msg'][user]['email']
                    table.add_row([user, answer['msg'][user]['password'], email])
                print(table)
        else:
            self.do_help('system users get')

    parser_system_users_get.set_defaults(func=system_users_get)
    '''users set'''
    parser_system_users_set = system_users_subparsers.add_parser('set', help='Edit user')
    parser_system_users_set.add_argument('-u', type=str, help='Username')
    parser_system_users_set.add_argument('-p', type=str, help='Set if you want to change the password')
    parser_system_users_set.add_argument('-e', type=str, help='E-mail')

    def system_users_set(self, ns: argparse.Namespace):
        if ns.u is None:
            self.do_help('system users set')
            return 0

        answer = systems_users_set(ns.u, ns.p, ns.e)
        if answer['status'] == 'success':
            print('User update successfully')

    parser_system_users_set.set_defaults(func=system_users_set)
    '''users add'''
    parser_system_users_add = system_users_subparsers.add_parser('add', help='Add new user')
    parser_system_users_add.add_argument('-u', type=str, help='Username')
    parser_system_users_add.add_argument('-p', type=str, help='Password')

    def system_users_add(self, ns: argparse.Namespace):
        if ns.u is None or ns.p is None:
            self.do_help('system users add')
            return 0
        answer = systems_users_add(ns.u, ns.p)
        if answer['status'] == 'success':
            print('User added successfully')
            if answer['status'] == 'success':
                table = PrettyTable()
                table.title = 'Cluster users'
                table.field_names = ['Username', 'md5(password)']
                for user in answer['msg']:
                    table.add_row([user, answer['msg'][user]['password']])
                print(table)

    parser_system_users_add.set_defaults(func=system_users_add)
    '''users delete'''
    parser_system_users_delete = system_users_subparsers.add_parser('delete', help='Remove user')
    parser_system_users_delete.add_argument('-u', type=str, help='Username')
    parser_system_users_delete.add_argument('-y', action='store_true', help='Deletion confirmation')

    def system_users_delete(self, ns: argparse.Namespace):
        if ns.u is not None and ns.y:
            answer = systems_users_delete(ns.u)
            if answer['status'] == 'success':
                print('User removed successfully')
            return 0
        self.do_help('system users delete')
    parser_system_users_delete.set_defaults(func=system_users_delete)

    ### hosts
    parser_system_hosts = system_subparsers.add_parser('hosts', help='Management of hosts file on all nodes')
    system_hosts_subparsers = parser_system_hosts.add_subparsers(title='hosts', help='help for 3rd layer of commands')

    def system_hosts(self, args):
        self.do_help('system hosts')

    parser_system_hosts.set_defaults(func=system_hosts)
    '''hosts get'''
    parser_system_hosts_get = system_hosts_subparsers.add_parser('get', help='List of hosts')
    parser_system_hosts_get.add_argument('-all', action='store_true', help='List data of all hosts')
    parser_system_hosts_get.add_argument('-hostname', type=str, help='List data per hostname')
    parser_system_hosts_get.add_argument('-ip', type=str, help='List data per IP address')

    def system_hosts_get(self, ns: argparse.Namespace):
        if not ns.all and ns.ip is None and ns.hostname is None:
            self.do_help('system hosts get')
            return 0

        answer = systems_hosts_get(ns.ip, ns.hostname)
        table = PrettyTable()
        table.title = 'Cluster hosts'
        table.field_names = ['IP', 'Hostname']
        for ip in answer['msg']:
            for hostname in answer['msg'][ip]:
                table.add_row([ip, hostname])
        print(table)

    parser_system_hosts_get.set_defaults(func=system_hosts_get)

    '''hosts add'''
    parser_system_hosts_add = system_hosts_subparsers.add_parser('add', help='Add of hosts')
    parser_system_hosts_add.add_argument('-hostname', type=str, help='Hostname')
    parser_system_hosts_add.add_argument('-ip', type=str, help='IP address')

    def system_hosts_add(self, ns: argparse.Namespace):
        if ns.ip is None or ns.hostname is None:
            self.do_help('system hosts add')
            return 0
        answer = systems_hosts_add(ns.ip, ns.hostname)
        if answer['status'] == 'success':
            print('Hostname and IP added successfully')

    parser_system_hosts_add.set_defaults(func=system_hosts_add)

    '''hosts delete'''
    parser_system_hosts_delete = system_hosts_subparsers.add_parser('delete', help='Remove host')
    parser_system_hosts_delete.add_argument('-hostname', type=str, help='Hostname')
    parser_system_hosts_delete.add_argument('-ip', type=str, help='IP address')
    parser_system_hosts_delete.add_argument('-y', action='store_true', help='Deletion confirmation')

    def system_hosts_delete(self, ns: argparse.Namespace):
        if ns.ip is not None and ns.hostname is not None and ns.y:
            answer = systems_hosts_delete(ns.ip, ns.hostname)
            if answer['status'] == 'success':
                print('Host removed successfully')
            return 0
        self.do_help('system hosts delete')
    parser_system_hosts_delete.set_defaults(func=system_hosts_delete)

    ### config
    parser_system_config = system_subparsers.add_parser('config', help='Manual cluster configuration management')
    system_config_subparsers = parser_system_config.add_subparsers(title='config', help='help for 3rd layer of commands')

    def system_config(self, args):
        self.do_help('system config')

    parser_system_config.set_defaults(func=system_config)

    '''config get'''
    parser_system_config_get = system_config_subparsers.add_parser('get', help='List configuration file')

    def system_config_get(self, ns: argparse.Namespace):
        answer = system_config_get()
        if answer['status'] == 'success':
            print(json.dumps(answer['msg'], indent=1))

    parser_system_config_get.set_defaults(func=system_config_get)

    '''config save'''
    parser_system_config_save = system_config_subparsers.add_parser('save', help='Save configuration')

    def system_config_save(self, ns: argparse.Namespace):
        answer = system_config_save()
        if answer['status'] == 'success':
            print('Config save successfully')
            print('Config version: ' + str(answer['msg']['version']))

    parser_system_config_save.set_defaults(func=system_config_save)

    '''config read'''
    parser_system_config_read = system_config_subparsers.add_parser('read', help='Read configuration')

    def system_config_read(self, ns: argparse.Namespace):
        answer = system_config_read()
        if answer['status'] == 'success':
            print('Config read successfully')
            print('Config version: ' + str(answer['msg']['version']))

    parser_system_config_read.set_defaults(func=system_config_read)

    ### Loops
    parser_system_loops = system_subparsers.add_parser('loops', help='Loops management')
    system_config_subparsers = parser_system_loops.add_subparsers(title='loops', help='help for 3rd layer of commands')

    def system_loops(self, args):
        self.do_help('system loops')

    parser_system_loops.set_defaults(func=system_loops)

    '''loops get'''
    parser_system_loops_get = system_config_subparsers.add_parser('get', help='List loops')

    def system_loops_get(self, ns: argparse.Namespace):
        answer = system_loops_get()
        if answer['status'] == 'success':
            #print(json.dumps(answer['msg'], indent=1))
            table = PrettyTable()
            table.field_names = ['Name', 'Status', 'id', 'native_id', 'Timeout', 'Counter']

            for loop in answer['msg']:
                id = '---'
                native_id = '---'
                timeout = '---'
                if 'ident' in answer['msg'][loop]:
                    id = answer['msg'][loop]['ident']
                    native_id = answer['msg'][loop]['native_id']
                    timeout = str(answer['msg'][loop]['timeout'])
                    counter = str(answer['msg'][loop]['counter'])
                table.add_row([loop, answer['msg'][loop]['isAlive'], id,  native_id, timeout, counter])
            print(table)

    parser_system_loops_get.set_defaults(func=system_loops_get)

    #'''loop reload'''
    #parser_system_loops_reload = system_config_subparsers.add_parser('reload', help='Reload loop')

    #def system_loops_reload(self, ns: argparse.Namespace):
    #    answer = system_config_save()
        #if answer['status'] == 'success':
        #    print('Config save successfully')
        #    print('Config version: ' + str(answer['msg']['version']))

    #parser_system_loops_reload.set_defaults(func=system_loops_reload)

    #'''loop stop'''
    #parser_system_loops_stop = system_config_subparsers.add_parser('stop', help='Stop loop')
    #parser_system_loops_stop.add_argument('-n', type=str, help='Name')
    #def system_loops_stop(self, ns: argparse.Namespace):
    #    if ns.n is None:
    #        self.do_help('system loops stop')
    #        return 0

    #    answer = system_loops_stop(ns.n)
    #    if answer['status'] == 'success':
    #        print('Loop: ' + ns.n + ' stopped successfully')

    #parser_system_loops_stop.set_defaults(func=system_loops_stop)

    #'''loop start'''
    #parser_system_loops_start = system_config_subparsers.add_parser('start', help='Start loop')

    #def system_loops_start(self, ns: argparse.Namespace):
    #    answer = system_config_save()
    #    #if answer['status'] == 'success':
    #    #    print('Config save successfully')
    #    #    print('Config version: ' + str(answer['msg']['version']))

    #parser_system_loops_start.set_defaults(func=system_loops_start)

    '''system'''
    @cmd2.with_argparser(system_parser)
    def do_system(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('system')
    ####################################################################################################################

    ##########               CLUSTER                  ##################################################################
    cluster_parser = cmd2.Cmd2ArgumentParser()


    cluster_subparsers = cluster_parser.add_subparsers(title='cluster', help='Cluster Managing')
    '''cluster status'''
    parser_cluster_status = cluster_subparsers.add_parser('status', help='Status of all nodes in cluster')

    def cluster_status(self, args):

        answer = cluster_status()
        if answer['status'] == 'success':
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

    parser_cluster_status.set_defaults(func=cluster_status)

    '''cluster create'''
    parser_cluster_create = cluster_subparsers.add_parser('create', help='Create cluster')

    def cluster_create(self, args):
        answer = cluster_create()
        if answer['status'] == 'success':
            print('Create cluster successfully')

    parser_cluster_create.set_defaults(func=cluster_create)


    '''cluster join'''
    parser_cluster_join = cluster_subparsers.add_parser('join', help='Join to cluster')
    parser_cluster_join.add_argument('-hostname', type=str, help='Hostname or IP cluster master node')
    parser_cluster_join.add_argument('-u', type=str, help='Username cluster master node')
    parser_cluster_join.add_argument('-p', type=str, help='Password cluster master node')

    def cluster_join(self, ns: argparse.Namespace):
        if ns.hostname is None or ns.u is None or ns.p is None:
            self.do_help('cluster join')
            return 0
        answer = cluster_join(ns.hostname, ns.u, ns.p)
        if answer['status'] == 'success':
            print('Join to cluster successfully')

    parser_cluster_join.set_defaults(func=cluster_join)

    @cmd2.with_argparser(cluster_parser)
    def do_cluster(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('cluster')
    ####################################################################################################################

    ##########               QUORUM                   ##################################################################
    quorum_parser = cmd2.Cmd2ArgumentParser()
    quorum_subparsers = quorum_parser.add_subparsers(title='quorum', help='Quorum Managing')

    '''quorum status'''
    parser_quorum_status = quorum_subparsers.add_parser('status', help='Status of all MNG nodes in quorum')

    def quorum_status(self, args):
        answer = quorum_status()
        if answer['status'] == 'success':
            table = PrettyTable()
            table.title = 'DoCluster Quorum'
            table.header = False
            table.add_row(['Quorum status', answer['msg']['status']])
            table.add_row(['Master nod', answer['msg']['master']])
            table.add_row(['Quorum errors', str(answer['msg']['errors'])])
            print(table)

            table = PrettyTable()
            table.field_names = ['Node hostname', 'status', 'Config version', 'Errors']
            for key in answer['msg']['nodes']:
                if key['status'] == 'offline':
                    table.add_row([key['node'], key['status'], '---', str(key['error'])])
                else:
                    table.add_row([key['node'], key['status'], key['config_version'], str(key['error'])])
            print(table)

    parser_quorum_status.set_defaults(func=quorum_status)

    ### nodes

    parser_quorum_nodes = quorum_subparsers.add_parser('nodes', help='Managing nodes in a quorum')
    quorum_nodes_subparsers = parser_quorum_nodes.add_subparsers(title='nodes', help='help for 3rd layer of commands')

    def quorum_nodes(self, args):
        self.do_help('quorum nodes')

    parser_quorum_nodes.set_defaults(func=quorum_nodes)

    '''nodes add'''
    parser_quorum_nodes_add = quorum_nodes_subparsers.add_parser('add', help='Add node to quorum')
    parser_quorum_nodes_add.add_argument('-hostname', type=str, help='Hostname of node')

    def quorum_nodes_add(self, ns: argparse.Namespace):
        if ns.hostname is None:
            self.do_help('quorum nodes add')
            return 0
        answer = quorum_nodes_add(ns.hostname)
        if answer['status'] == 'success':
            print('Node successfully added to quorum')

    parser_quorum_nodes_add.set_defaults(func=quorum_nodes_add)

    '''nodes delete'''
    parser_quorum_nodes_delete = quorum_nodes_subparsers.add_parser('delete', help='Delete node from quorum')
    parser_quorum_nodes_delete.add_argument('-hostname', type=str, help='Hostname of node')

    def quorum_nodes_delete(self, ns: argparse.Namespace):
        if ns.hostname is None:
            self.do_help('quorum nodes delete')
            return 0
        answer = quorum_nodes_delete(ns.hostname)
        if answer['status'] == 'success':
            print('Node successfully removed from quorum')

    parser_quorum_nodes_delete.set_defaults(func=quorum_nodes_delete)


    @cmd2.with_argparser(quorum_parser)
    def do_quorum(self, args):
        func = getattr(args, 'func', None)
        if func is not None:
            func(self, args)
        else:
            self.do_help('quorum')
    ####################################################################################################################

if __name__ == '__main__':
    app = DoClusterCLI()
    sys.exit(app.cmdloop())