from src.mng.mng_class import mng
import config
import time
import os
from datetime import datetime



class system(mng):

    Timeout_Loop_Cluster_Task_Processor = 1

    def Loop_Cluster_Task_Processor(self):
        if 'quorum' in config.cluster_config:
            if os.uname()[1] != config.quorum_status['master']:
                time.sleep(10)
                return 0
        if 'cluster_tasks' not in config.modules_data:
            return 0

        for task in config.modules_data['cluster_tasks']:
            if task['status'] == 'transfer':
                answer = self.SendToNode(task['node'], 'system/localtaskadd', {'task': task})
                if answer['status'] == 'success':
                    task['status'] = 'waiting'
                    now = datetime.now()
                    task['start'] = now.strftime("%d-%m-%Y %H:%M:%S")

                if answer['error'] == 'offline':
                    task['status'] = 'error'
                    now = datetime.now()
                    task['start'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    task['end'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    task['duration'] = 0
                    task['log'] = task['node'] + ' :' + answer['error']


