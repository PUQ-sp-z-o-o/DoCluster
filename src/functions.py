import ipaddress
import re
import json
import config
import os
import time
import random
import string


def is_valid_ip(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def is_valid_email(email):
    return re.search(r'[\w.-]+@[\w.-]+.\w+', email)


def is_valid_hostname(hostname: object) -> object:
    if len(hostname) == 0:
        return False
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        return False
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))



'''Read cluster configuration from file in format JSON'''
def ReadConfiguration():
    config.logger.name = 'SYSTEM'
    if not os.path.isdir('config'):
        os.mkdir('config')

    if not os.access('config/docluster.conf', os.F_OK):
        f = open('config/docluster.conf', 'w+')
        json.dump(config.default_config, f, indent=1)
        f.close()

    with open('config/docluster.conf') as json_file:
        config.cluster_config = json.load(json_file)
        json_file.close()
    config.logger.info('Read configuration version: ' + str(config.cluster_config['version']))
    config.logger.debug('Read configuration: ' + str(config.cluster_config))


'''Save cluster configuration to file in format JSON'''
def SaveConfiguration():
    config.logger.name = 'SYSTEM'
    if config.quorum_status['master'] == os.uname()[1]:
        config.cluster_config['version'] = config.cluster_config['version'] + 1

    f = open('config/docluster.conf', 'w+')
    json.dump(config.cluster_config, f, indent=1)
    config.logger.info('Save configuration version: ' + str(config.cluster_config['version']))
    config.logger.debug('Save configuration: ' + str(config.cluster_config))
    f.close()


def ReadModulesData():
    config.logger.name = 'SYSTEM'
    if not os.path.isdir('config'):
        os.mkdir('config')

    if not os.access('config/modules_data.conf', os.F_OK):
        f = open('config/modules_data.conf', 'w+')
        json.dump(config.default_modules_data, f, indent=1)
        f.close()

    with open('config/modules_data.conf') as json_file:
        config.modules_data = json.load(json_file)
        json_file.close()
    config.logger.info('Read modules_data version: ' + str(config.modules_data['version']))
    config.logger.debug('Read modules_data: ' + str(config.modules_data))


def SaveModulesData():
    config.logger.name = 'SYSTEM'
    if config.quorum_status['master'] == os.uname()[1]:
        config.modules_data['version'] = config.modules_data['version'] + 1

    f = open('config/modules_data.conf', 'w+')
    json.dump(config.modules_data, f, indent=1)
    config.logger.info('Save modules_data version: ' + str(config.modules_data['version']))
    config.logger.debug('Save modules_data: ' + str(config.modules_data))
    f.close()


def AddTask(node, user, description, module, method, arg, queue):
    if 'cluster_tasks' not in config.modules_data:
        config.modules_data['cluster_tasks'] = []
    # 'status': "transfer | waiting | processing | success | error",
    task = {
        'id': ''.join(random.choice(string.ascii_lowercase) for i in range(30)),
        'node': node,
        'user': user,
        'description': description,
        'module': module,
        'method': method,
        'arg': arg,
        'queue': queue,
        'status': "transfer",
        'process_id': '',
        'start': '',
        'end': '',
        'duration': '',
        'log': ''
    }
    config.modules_data['cluster_tasks'].append(task)
    SaveModulesData()
    config.logger.name = 'SYSTEM'
    config.logger.info('Add task: '+ str(task['id']))
    config.logger.debug('Add task: ' + str(task))

    return 0


