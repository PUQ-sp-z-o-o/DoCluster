import time
import config
import hashlib
import random
import string


class mng:
    SaveConfiguration = False
    url = []
    args = {}
    client_ip = ''
    mng_port = 3030
    answer_msg = {}
    answer_error = 'wrong api path'
    answer_status = 'error'

    def __init__(self, mng_port, url, args, client_ip):
        self.url = url
        self.args = args
        self.client_ip = client_ip
        self.mng_port = mng_port
        self.answer_msg = {}
