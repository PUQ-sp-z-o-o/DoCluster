import time
import config


class cluster:

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

    def Scheduler2_QuorumStatuscluster(self):
        while True:
            config.logger.name = 'CLUSTER'
            time.sleep(1)
            config.logger.debug('Scheduler_QuorumStatuscluster in')
            print('Scheduler_QuorumStatuscluster in')

    def Scheduler2_QuorumStatuscluster2(self):
        while True:
            config.logger.name = 'CLUSTER'
            time.sleep(1)
            config.logger.debug('Scheduler_QuorumStatuscluster2 in')
            print('Scheduler_QuorumStatuscluster2 in')