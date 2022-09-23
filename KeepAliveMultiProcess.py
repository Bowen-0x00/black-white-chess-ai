from ast import arg
import multiprocessing

class KeepAliveMultiprocessing():

    def __init__(self, target, callback, *args):
        self.q = multiprocessing.Queue()
        self.q_return = multiprocessing.Queue()
        self.cpu_count = multiprocessing.cpu_count()
        self.target = target
        self.args = args
        self.callback = callback

    def run(self):
        for i in range(self.cpu_count):
            p = multiprocessing.Process(target=self.loop, args = (self.q,))
            p.daemon = True
            p.start()

    def loop(self, q):
        while True:
            if not q.empty():
                v = q.get()
                self.q_return.put(self.target(v))
               
