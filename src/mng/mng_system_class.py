import json

from src.mng.mng_class import mng
import config
import time
import os
from datetime import datetime



class system(mng):

    Timeout_Loop_Cluster_Task_Processor = 1
    Timeout_Loop_Local_Task_Processor = 1
    Timeout_Loop_Cluster_Task_Status = 1

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

    def Loop_Cluster_Task_Status(self):
        if 'quorum' in config.cluster_config:
            if os.uname()[1] != config.quorum_status['master']:
                time.sleep(10)
                return 0
        if 'cluster_tasks' not in config.modules_data:
            return 0

        i = 0
        while i < len(config.modules_data['cluster_tasks']):
            task = config.modules_data['cluster_tasks'][i]
            if task['status'] in ['waiting', 'processing']:
                answer = self.SendToNode(task['node'], 'system/localtaskstatus', {'id': task['id']})
                if answer['status'] == 'success':
                    config.modules_data['cluster_tasks'][i]['status'] = answer['msg']['status']
                    config.modules_data['cluster_tasks'][i]['duration'] = answer['msg']['duration']
                    config.modules_data['cluster_tasks'][i]['end'] = answer['msg']['end']

            i = i + 1

    def Loop_Local_Task_Processor(self):
        if len(config.local_tasks) > 0:
            i = 0
            while i < len(config.local_tasks):

                if config.local_tasks[i]['status'] == 'transfer':
                    config.local_tasks[i]['status'] = 'processing'
                    config.local_tasks[i]['duration'] = 0

                if config.local_tasks[i]['status'] == 'processing':
                    config.local_tasks[i]['duration'] = config.local_tasks[i]['duration'] + 10

                if config.local_tasks[i]['duration'] == 100:
                    now = datetime.now()
                    config.local_tasks[i]['end'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.local_tasks[i]['status'] = 'success'




                i = i + 1



    def localtaskadd(self):
        if 'task' in self.args:
            task = json.loads(self.args['task'])
            config.local_tasks.append(task)

            config.logger.name = 'SYSTEM'
            config.logger.info('Add local task: ' + task['id'])
            config.logger.debug('Add local task: ' + str(task))
            self.answer_status = 'success'
            self.answer_msg = ''
            self.answer_error = ''

    def localtaskstatus(self):
        if 'id' in self.args:
            if len(config.local_tasks) > 0:
                i = 0
                while i < len(config.local_tasks):
                    task = config.local_tasks[i]
                    if task['id'] == self.args['id']:
                        self.answer_status = 'success'
                        self.answer_msg = task
                        self.answer_error = ''
                        return 0
                    i = i +1

        self.answer_status = 'error'
        self.answer_msg = {}
        self.answer_error = 'Task not found'