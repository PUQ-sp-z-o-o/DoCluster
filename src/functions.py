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



