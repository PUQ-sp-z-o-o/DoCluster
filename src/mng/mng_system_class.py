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

        i = 0
        while i < len(config.modules_data['cluster_tasks']):
            task = config.modules_data['cluster_tasks'][i]
            if task['status'] == 'transfer':
                answer = self.SendToNode(task['node'], 'system/localtaskadd', {'task': task})
                if answer['status'] == 'success':
                    config.modules_data['cluster_tasks'][i]['status'] = 'waiting'
                    now = datetime.now()
                    config.modules_data['cluster_tasks'][i]['start'] = now.strftime("%d-%m-%Y %H:%M:%S")

                if answer['error'] == 'offline':
                    config.modules_data['cluster_tasks'][i]['status'] = 'error'
                    now = datetime.now()
                    config.modules_data['cluster_tasks'][i]['start'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.modules_data['cluster_tasks'][i]['end'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.modules_data['cluster_tasks'][i]['duration'] = 0
                    config.modules_data['cluster_tasks'][i]['log'] = task['node'] + ' :' + answer['error']


