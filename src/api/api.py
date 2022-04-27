#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from src.api.DoClusterApi_class import ClastercpApi
import config
import importlib
from src.functions import *


def ApiStart(url, args, client_ip):
    ClientApi = ClastercpApi(url, args, client_ip)

    if ClientApi.token_status == False:
        return ClientApi.answer()

    if 'cluster' not in config.cluster_config:
        if len(url) >= 2 and url[0] == 'cluster' and url[1] in ['create', 'join']:
            config.logger.info(ClientApi.client_ip + ' (' + ClientApi.username + ') ' + 'create or join cluster')
        else:
            ClientApi.answer_status = 'error'
            ClientApi.answer_error = 'Cluster not created'
            config.logger.debug(ClientApi.client_ip + ' (' + ClientApi.username + ') ' + 'cluster not created')
            return ClientApi.answer()

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
                return ClientApi.answer()
            del api_class
        else:
            ClientApi.answer_msg = {}
            ClientApi.answer_status = 'error'
            ClientApi.answer_error = 'Wrong API path'
            config.logger.error(ClientApi.client_ip + ' (' + ClientApi.username + ') ' + 'wrong api path')
            return ClientApi.answer()

    r = ClientApi.answer()
    del ClientApi
    return r
