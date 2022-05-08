import copy
import json
from multiprocessing import Process, Pipe

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
                time.sleep(5)
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
                time.sleep(5)
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
                    config.modules_data['cluster_tasks'][i]['process_id'] = answer['msg']['process_id']
                    config.modules_data['cluster_tasks'][i]['log'] = answer['msg']['log']

                if answer['status'] != 'success':
                    config.modules_data['cluster_tasks'][i]['status'] = 'error'
                    now = datetime.now()
                    config.modules_data['cluster_tasks'][i]['end'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.modules_data['cluster_tasks'][i]['log'] = config.modules_data['cluster_tasks'][i]['log'] +  answer['error']
            i = i + 1

    def Loop_Local_Task_Processor(self):
        self.TaskCleaner()
        if len(config.local_tasks) > 0:
            i = 0
            while i < len(config.local_tasks):
                if config.local_tasks[i]['id'] not in config.local_tasks_pipe:
                    config.local_tasks_pipe[config.local_tasks[i]['id']] = {}
                    config.local_tasks_pipe[config.local_tasks[i]['id']]['send'] = False

                if config.local_tasks[i]['status'] == 'waiting' and not config.local_tasks[i]['queue']:
                    config.local_tasks[i]['status'] = 'processing'
                    config.local_tasks[i]['duration'] = 0

                # Проверка очереди и стартуем если очередь пуста
                if config.local_tasks[i]['status'] == 'waiting':
                    k = 0
                    start = True
                    while k < len(config.local_tasks):
                        if config.local_tasks[k]['module'] == config.local_tasks[i]['module'] and \
                                config.local_tasks[k]['method'] == config.local_tasks[i]['method'] and \
                                config.local_tasks[k]['queue'] == config.local_tasks[i]['queue'] and \
                                config.local_tasks[k]['status'] == 'processing':
                            start = False
                        k = k + 1

                    if start:
                        config.local_tasks[i]['status'] = 'processing'
                ##################

                if config.local_tasks[i]['duration'] == '10':
                    now = datetime.now()
                    config.local_tasks[i]['end'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.local_tasks[i]['status'] = 'success'

                if config.local_tasks[i]['status'] == 'processing':
                    if 'process' not in config.local_tasks_pipe[config.local_tasks[i]['id']]:

                        config.local_tasks_pipe[config.local_tasks[i]['id']]['parent_conn'],  config.local_tasks_pipe[config.local_tasks[i]['id']]['child_conn'] = Pipe()
                        p = Process(name=config.local_tasks[i]['id'] ,target=self.TaskProcess, args=(config.local_tasks_pipe[config.local_tasks[i]['id']]['child_conn'],))
                        config.local_tasks_pipe[config.local_tasks[i]['id']]['process'] = p
                        p.start()
                        config.local_tasks[i]['process_id'] = str(p.pid)

                    else:
                        t = config.local_tasks_pipe[config.local_tasks[i]['id']]['parent_conn']
                        config.local_tasks[i]['duration'] = t.recv()
                i = i + 1

    def TaskProcess(self, conn):
        i = 0
        while i < 11:
            conn.send(str(i))
            #conn.close()
            time.sleep(1)
            i = i + 1

    def localtaskadd(self):
        if 'task' in self.args:
            task = json.loads(self.args['task'])
            task['status'] = 'waiting'
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

                        if task['status'] == 'success':
                            config.local_tasks_pipe[task['id']]['send'] = True
                        return 0
                    i = i + 1


        self.answer_status = 'error'
        self.answer_msg = {}
        self.answer_error = 'Task not found'

    def TaskCleaner(self):
        tmp = copy.deepcopy(config.local_tasks)
        i = 0
        while i < len(tmp):
            if tmp[i]['id'] in config.local_tasks_pipe:
                if config.local_tasks_pipe[tmp[i]['id']]['send']:
                    config.local_tasks.pop(i)
                    del config.local_tasks_pipe[tmp[i]['id']]
            i = i + 1
        config.local_tasks = copy.deepcopy(tmp)
        print(str(config.local_tasks))
