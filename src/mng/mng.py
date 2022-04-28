import config
import hashlib
import random
import string
from src.functions import *

def MngJoin(args, client_ip):
    if 'cluster' not in config.cluster_config:
        config.logger.error(client_ip + 'Join to cluster: cluster not created on connecting node')
        return {'status': 'error', 'error': 'cluster not created on connecting node'}

    if 'cluster_username' not in args and 'cluster_password' not in args and 'node' not in args:
        config.logger.error(client_ip + 'Join to cluster: missing data')
        return {'status': 'error', 'error': 'missing data'}

    if args['cluster_username'] not in config.cluster_config['systems']['users']:
        config.logger.error(client_ip + 'Join to cluster: username not found')
        return {'status': 'error', 'error': 'username not found'}

    cluster_password = args['cluster_password']
    if hashlib.md5(cluster_password.encode("utf-8")).hexdigest() != config.cluster_config['systems']['users'][args['cluster_username']]['password']:
        config.logger.error(client_ip + 'Join to cluster: password is wrong')
        return {'status': 'error', 'error': 'password is wrong'}

    if args['node'] in config.cluster_config['cluster']['nodes']:
        config.logger.error(client_ip + 'Join to cluster: a node with the same hostname is already in the cluster')
        return {'status': 'error', 'error': 'a node with the same hostname is already in the cluster'}

    config.cluster_config['cluster']['nodes'][args['node']] = {
        'machine': args['machine'],
        'API_key': ''.join(random.choice(string.ascii_lowercase) for i in range(30)),
    }
    SaveConfiguration()

    config.logger.info(client_ip + 'Join to cluster:' + args['node'])
    return {'status': 'success', 'error': '', 'msg': config.cluster_config}
