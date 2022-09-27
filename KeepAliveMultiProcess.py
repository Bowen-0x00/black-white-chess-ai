from ast import arg
import multiprocessing
import time

class KeepAliveMultiprocessing():

    def __init__(self, target, callback, num = 1, *args):
        self.q = multiprocessing.Queue()
        self.q_return = multiprocessing.Queue()
        #self.q_param = multiprocessing.Queue()
        self.cpu_count = multiprocessing.cpu_count()
        self.target = target
        #self.setparam = setparam
        self.args = args
        self.callback = callback
        self.running = multiprocessing.Manager().Value(int, 1)
        self.num = num

    def run(self):
        print('KeepAliveMultiprocessing num: ', self.num)
        for i in range(self.cpu_count//self.num):
            p = multiprocessing.Process(target=self.loop, args = (self.q, ), name = ''.format('Reversi: {}'.format(str(i))))
            p.daemon = True
            p.start()

    def loop(self, q):
        #while self.running.value == 1:
        while True:
            if not q.empty():
                v = q.get()
                self.q_return.put(self.target(v))
            time.sleep(0.01)
            # if not q_param.empty():                         Use Manager for global variable.  Also can be use change v1
            #     temp = []
            #     flag = False
            #     while not q_param.empty():
            #         p = q_param.get()
            #         temp.append(p)

            #         if p[0] == i:
            #             flag = True
            #             self.setparam(p[1:])
            #             break 
            #     for t in temp[:-1 if flag else 0]:
            #         q_param.put(t)    
    def terminate(self):
        for p in self.process_list:
            p.terminate()

               
