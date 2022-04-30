import config
import os
import requests
import json
import random
import string
from src.functions import *


class quorum:

    SaveConfiguration = False
    url = []
    args = {}
    client_ip = ''
    username = ''

    answer_msg = {}
    answer_error = 'wrong api path'
    answer_status = 'error'

    def __init__(self, url, args, client_ip, username):
        self.url = url
        self.args = args
        self.client_ip = client_ip
        self.username = username

    def status(self):
        self.answer_status = 'success'
        self.answer_msg['status'] = 'OK'
        self.answer_msg['quorum_status'] = config.quorum_status
