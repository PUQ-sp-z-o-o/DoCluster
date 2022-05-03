from src.api.api_class import api
from src.functions import *

import config

import os
import requests
import json
import random
import string
from src.functions import *


class quorum(api):

    def status(self):
        self.answer_status = 'success'
        self.answer_msg = config.quorum_status
        self.answer_error = ''
