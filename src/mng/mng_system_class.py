from src.mng.mng_class import mng
import config
import time
import os


class system(mng):

    Timeout_Cluster_Task_Processor = 1

    def Loop_Cluster_Task_Processor(self):
        if 'quorum' in config.cluster_config:
            if os.uname()[1] != config.quorum_status['master']:
                time.sleep(10)
                return 0
