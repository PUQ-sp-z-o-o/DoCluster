import config
import time


class DoClusterMng:

    ttt = 1
    #def __init__(self):
    #    print('Start ')

    def quorum(self):
        while True:
            time.sleep(5)
            config.logger.name = 'quorum'
            if 'cluster' not in config.cluster_config:
                config.cluster_quorum['status'] = 'critical'
                config.cluster_quorum['error'] = 'cluster not created'
                config.logger.debug('cluster not created')

            if len(config.cluster_config['cluster']['quorum']) == 1:
                config.cluster_quorum['master'] = config.cluster_config['cluster']['quorum'][0]['node']
                config.cluster_quorum['status'] = 'warning'
                config.cluster_quorum['error'] = 'Quorum consists of one node'
                config.logger.info('quorum consists of one node')

            config.logger.debug(str(config.cluster_quorum))


