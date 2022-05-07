from src.mng.mng_class import mng
import config
import time
import os


class system(mng):

    Timeout_Loop_MasterTaskStatus = 1

    def Loop_MasterTaskStatus(self):
        if 'quorum' in config.cluster_config:
            if os.uname()[1] != config.quorum_status['master']:
                time.sleep(10)
                return 0
