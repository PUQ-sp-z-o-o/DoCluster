#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import os
import json


api_url = "http://192.168.129.82:3033/api/"
api_login = 'admin'
api_apss = 'admin'
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
    if answer_token['status'] == 'false':
        print("Not authorized")
        print("Login request to " + api_url)
        send_login = requests.post(url=api_url+'login/', data={"username": api_login, "password": api_apss})
        answer_login = json.loads(send_login.text)
        print(send_login.text)
        if answer_login['status'] == 'success':
            access_token = answer_login['msg']['access_token']
            f = open('access_token.tmp', 'w+')
            f.write(access_token)
            f.close()
            print("Authorization was successful to " + api_url)
        else:
            print("Failed login to " + api_url)
            print("Error: " + answer_login['error'])


def logout():
    send_logout = requests.post(url=api_url + 'logout', data={"access_token": access_token})
    answer_logout = json.loads(send_logout.text)
    if answer_logout['status'] == 'success':
        print("Logout " + api_url)
    else:
        print("Error: " + answer_logout['error'])


def send(path, data):
    data['access_token'] = access_token
    send = requests.post(url=api_url + path, data=data)
    print(send.text)
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
        'cluster_ip': '192.168.129.82',
    }
    send(path, data)


def cluster_status():
    path = 'cluster/status'
    data = {}
    send(path, data)

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


login()
cluster_management_get()
#cluster_status()
#tokens()
#cluster_create()
#cluster_join()
#systems_hosts_set('1.2.3.1', 'dupa-1')
#systems_hosts_get()
#systems_hosts_delete('1.2.3.1', 'dupa-1')
#systems_users_get()
#systems_users_add('dimon', 'QWEqwe123')
#systems_users_delete('admin')
#systems_users_set('admin', 'QWEqwe123', 'admin@clastercp.com')
#logout()