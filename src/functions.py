import ipaddress
import re
import json
import config
import os


def is_valid_ip(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def is_valid_hostname(hostname: object) -> object:
    if len(hostname) == 0:
        return False
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        return False
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def ReadConfiguration():
    try:
        os.mkdir('config')
    except Exception as e:
        print(e)
    if not os.access('config/docluster.conf', os.F_OK):
        f = open('config/docluster.conf', 'w+')
        json.dump(config.default_config, f, indent=1)
        f.close()

    with open('config/docluster.conf') as json_file:
        config.cluster_config = json.load(json_file)
        json_file.close()


def SaveConfiguration():
    config.cluster_config['version'] = config.cluster_config['version'] + 1
    f = open('config/docluster.conf', 'w+')
    json.dump(config.cluster_config, f, indent=1)
    config.logger.info('SaveConfiguration version: ' + str(config.cluster_config['version']))
    config.logger.debug('SaveConfiguration: ' + str(config.cluster_config))
    f.close()


def ReadClusterTasks():
    try:
        os.mkdir('config')
    except Exception as e:
        print(e)
    if not os.access('config/docluster.tasks', os.F_OK):
        f = open('config/docluster.tasks', 'w+')
        json.dump(config.cluster_tasks, f, indent=1)
        f.close()

    with open('config/docluster.tasks') as json_file:
        config.cluster_tasks = json.load(json_file)
        json_file.close()
