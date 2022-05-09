import copy
import json
from multiprocessing import Process
#from subprocess import Popen, STDOUT, check_call
import subprocess
from src.mng.mng_class import mng
import config
import time
import os
import calendar
from datetime import datetime
import pymemcache
import importlib



class system(mng):

    Timeout_Loop_Cluster_Task_Processor = 1
    Timeout_Loop_Cluster_Task_Status = 1
    Timeout_Loop_Local_Task_Processor = 1
    '''Мастер обрабатывает локальные таски и отправляет нодам'''
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
                config.logger.info('Send task. Node: ' + task['node'] + ' Task: ' + task['id'])
                config.logger.debug('Send task. Node: ' + task['node'] + ' Task: ' + str(task))

                answer = self.SendToNode(task['node'], 'system/localtaskadd', {'task': json.dumps(task)})
                if answer['status'] == 'success':
                    config.logger.name = 'SYSTEM'
                    config.logger.info('Send task success. Node: ' + task['node'] + ' Task: ' + task['id'])

                    config.modules_data['cluster_tasks'][i]['status'] = 'waiting'
                    now = datetime.now()
                    config.modules_data['cluster_tasks'][i]['start'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.logger.name = 'SYSTEM'
                    config.logger.info('Send task success. id: ' + task['id'] + ' Node: ' + task['node'])

                if answer['status'] != 'success':
                    config.logger.name = 'SYSTEM'
                    config.logger.error('Send task error. Node: ' + task['node'] + ' Task: ' + task['id'])

                    config.modules_data['cluster_tasks'][i]['status'] = 'error'
                    now = datetime.now()
                    config.modules_data['cluster_tasks'][i]['start'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.modules_data['cluster_tasks'][i]['end'] = now.strftime("%d-%m-%Y %H:%M:%S")
                    config.modules_data['cluster_tasks'][i]['duration'] = 0
                    config.modules_data['cluster_tasks'][i]['log'] = task['node'] + ' :' + answer['error']
                    config.logger.name = 'SYSTEM'
                    config.logger.error('Send task error. id: ' + task['id'] + ' Node: ' + task['node'] + ' :' + answer['error'])
            i = i + 1
    '''Мастер обрабатывает статусы тасков на нодах'''
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
                    config.modules_data['cluster_tasks'][i]['log'] = config.modules_data['cluster_tasks'][i]['log'] + answer['error']
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

                if config.local_tasks[i]['status'] == 'processing':
                    if 'process' not in config.local_tasks_pipe[config.local_tasks[i]['id']]:

                        name = config.local_tasks[i]['id']
                        memcache = pymemcache.Client(('localhost', 11211))
                        memcache.set(name + '_log', '')
                        memcache.set(name + '_status', 'processing')

                        p = Process(name=config.local_tasks[i]['id'], target=self.TaskProcess,
                                    args=([config.local_tasks[i]],))

                        config.local_tasks_pipe[config.local_tasks[i]['id']]['process'] = p
                        p.start()
                        config.local_tasks[i]['process_id'] = str(p.pid)

                        config.logger.name = 'SYSTEM'
                        config.logger.info('Start task. process_id: ' + config.local_tasks[i]['process_id'] + ' Task: ' + name)
                        config.logger.debug('Start task. process_id: ' + config.local_tasks[i]['process_id'] + ' Task: ' + str(config.local_tasks[i]))

                        date = datetime.utcnow()
                        utc_time = calendar.timegm(date.utctimetuple())
                        config.local_tasks_pipe[config.local_tasks[i]['id']]['start'] = utc_time

                    else:
                        name = config.local_tasks[i]['id']
                        memcache = pymemcache.Client(('localhost', 11211))
                        config.local_tasks[i]['log'] = str(memcache.get(name + '_log').decode())
                        config.local_tasks[i]['status'] = str(memcache.get(name + '_status').decode())

                        date = datetime.utcnow()
                        utc_time = calendar.timegm(date.utctimetuple())
                        config.local_tasks[i]['duration'] = str(utc_time - config.local_tasks_pipe[config.local_tasks[i]['id']]['start'])

                        if config.local_tasks[i]['status'] in ['success', 'error']:
                            now = datetime.now()
                            config.local_tasks[i]['end'] = now.strftime("%d-%m-%Y %H:%M:%S")

                i = i + 1

    def TaskProcess(self, task):
        id = task[0]['id']
        user = task[0]['user']
        module = task[0]['module']
        method = task[0]['method']
        description = task[0]['description']

        memcache = pymemcache.Client(('localhost', 11211))
        log = 'Task: ' + id + '\n'
        log += 'Module: ' + module + '\n'
        log += 'Method: ' + method + '\n'
        log += 'Description: ' + description + '\n'
        log += 'User: ' + user + '\n'
        log += '-------------------------------------\n'
        memcache.set(id + '_log', log)
        #######
        status = 'processing'
        if os.access('src/mng/mng_' + module + '_class.py', os.F_OK):
            mng_module = importlib.import_module('src.mng.mng_' + module + '_class')
            mng_class = getattr(mng_module, module)
            mng_instance = mng_class([], {}, '')

            if method in dir(mng_instance):
                task = getattr(mng_instance, method)(id, task[0]['arg'], log)
                status = task['status']
                log = task['log']
                memcache.set(id + '_log', log)
            else:
                status = 'error'
                log += 'Error: Method not found!' '\n'
        else:
            status = 'error'
            log += 'Error: Module not found!' '\n'
        time.sleep(1)
        memcache.set(id + '_log', log)
        time.sleep(1)
        memcache.set(id + '_status', status)

    def TaskCleaner(self):
        tmp = copy.deepcopy(config.local_tasks)
        i = 0
        while i < len(tmp):
            if tmp[i]['id'] in config.local_tasks_pipe:
                if config.local_tasks_pipe[tmp[i]['id']]['send']:
                    config.local_tasks.pop(i)
                    del config.local_tasks_pipe[tmp[i]['id']]
            i = i + 1


    ''' MNG '''
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


    '''    Tsks   '''
    def hostsset(self, id, args, log):
        memcache = pymemcache.Client(('localhost', 11211))
        status = 'success'

        result = subprocess.Popen("echo 127.0.0.1 localhost > /etc/hosts.test", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = result.communicate()
        if result.returncode != 0:
            status = 'error'
            log += error.decode() + '\n'

        for arg in args:
            for hostname in args[arg]:
                result = subprocess.Popen("echo " + str(arg) + " " + hostname + " >> /etc/hosts.test", shell=True,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = result.communicate()
                if result.returncode != 0:
                    status = 'error'
                    log += error.decode() + '\n'

                memcache.set(id + '_log', log)



        memcache.set(id + '_log', log)
        return {'log': log, 'status': status}
