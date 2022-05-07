import json

from src.mng.mng_class import mng
import config
import time
import os
from datetime import datetime



class system(mng):

    Timeout_Loop_Cluster_Task_Processor = 1
    Timeout_Loop_Local_Task_Processor = 1

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
                config.logger.name = 'SYSTEM'
                config.logger.error('Send task. Node: ' + task['node'] + ' Task' + str(task))

                answer = self.SendToNode(task['node'], 'system/localtaskadd', {'task': json.dumps(task)})
                if answer['status'] == 'success':
                    config.modules_data['cluster_tasks'][i]['status'] = 'waiting'
                    now = datetime.now()
                    config.modules_data['cluster_tasks'][i]['start'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.logger.name = 'SYSTEM'
                    config.logger.info('Send task success. id: ' + task['id'] + ' Node: ' + task['node'])

                if answer['status'] != 'success':
                    config.modules_data['cluster_tasks'][i]['status'] = 'error'
                    now = datetime.now()
                    config.modules_data['cluster_tasks'][i]['start'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.modules_data['cluster_tasks'][i]['end'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.modules_data['cluster_tasks'][i]['duration'] = 0
                    config.modules_data['cluster_tasks'][i]['log'] = task['node'] + ' :' + answer['error']
                    config.logger.name = 'SYSTEM'
                    config.logger.error('Send task error. id: ' + task['id'] + ' Node: ' + task['node'] + ' :' + answer['error'])
            i = i + 1

    def Loop_Local_Task_Processor(self):
        if len(config.local_tasks) > 0:
            print(config.local_tasks)




    def localtaskadd(self):
        if 'task' in self.args:
            config.logger.name = 'SYSTEM'
            config.logger.debug('Add local task: ' + str(task))
            task = json.loads(self.args['task'])
            config.local_tasks.append(task)
            config.logger.name = 'SYSTEM'
            config.logger.info('Add local task: ' + task['id'])
            self.answer_status = 'success'
            self.answer_msg = ''
            self.answer_error = ''
