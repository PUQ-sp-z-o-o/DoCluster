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

