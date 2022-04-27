import ipaddress
import re
import json
import config

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
    with open('config/docluster.conf') as json_file:
        config.cluster_config = json.load(json_file)
        json_file.close()

def SaveConfiguration():
    f = open('config/docluster.conf', 'w+')
    json.dump(config.cluster_config, f, indent=1)
    f.close()

