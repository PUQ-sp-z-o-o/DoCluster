import config
import os
import requests
import json
import random
import string
from src.functions import *


class api:

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
