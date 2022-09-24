from ast import arg
import multiprocessing

class KeepAliveMultiprocessing():

    def __init__(self, target, callback, *args):
        self.q = multiprocessing.Queue()
        self.q_return = multiprocessing.Queue()
        #self.q_param = multiprocessing.Queue()
        self.cpu_count = multiprocessing.cpu_count()
        self.target = target
        #self.setparam = setparam
        self.args = args
        self.callback = callback

    def run(self):
        for i in range(self.cpu_count):
            p = multiprocessing.Process(target=self.loop, args = (self.q, ), name = ''.format('Reversi: {}'.format(str(i))))
            p.daemon = True
            p.start()

    def loop(self, q):
        while True:
            if not q.empty():
                v = q.get()
                self.q_return.put(self.target(v))
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

               
