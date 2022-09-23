import random
import math
from ChessState import ChessState
import time
import multiprocessing
from multiprocessing import  Process
import threading
from ThreadWithCallback import ThreadWithCallback
from KeepAliveMultiProcess import KeepAliveMultiprocessing
random.seed(4)
class Node():
    def __init__(self, state, action):
        self.state = state   #player  |   chess_state  |  scores  |  
        self.action = action #from which action
        self.children = []
        self.parent = None
        self.n = 0           #numbers of be searched      
        self.q = 0           #value
        self.visited = False
def chess_to_char(c):
    if c == ChessState.BLACK:
        return u'\u25CF'
    elif c == ChessState.WHITE:
        return u'\u25CB'
    else: 
        return u'\u2B1A'
    
def print_board(chess_state):
    for x in range(8):
        print("")
        for y in range(8):
            print(" {}".format(chess_to_char(chess_state[x][y])), end="")
class UCT():
    iretation_times = 100
    c = 2
    time_out = 1

    def __init__(self, do_action, check_finish, color):
        self.do_action = do_action      #do action return state
        self.check_finish = check_finish
        self.color = color
        self.v0 = None
        self.keep_alive_multiprocessing = None

    def is_terminal(self, s):
        return self.check_finish(s)

    def do_random_action(self, s, unvisited = False):
        actions = s.get_actions()
        if unvisited:
            actions = [a for a in actions if a.expanded == False]
        a = actions[random.randint(0, len(actions)-1)] #从动作列表中选择一个动作
        s = self.do_action(s, a.action)  
        s.get_actions()                      #执行动作返回状态
        return a, s
    def thread_callback(self, t):
        self.time_map['select'] = t['select'] if t['select'] > self.time_map['select'] else self.time_map['select']
        self.time_map['simulate'] = t['simulate'] if t['simulate'] > self.time_map['simulate'] else self.time_map['simulate']
        self.time_map['back_propagate'] = t['back_propagate'] if t['back_propagate'] > self.time_map['back_propagate'] else self.time_map['back_propagate']
    def multi_processor_search(self, s0):
        self.v0 = Node(s0, None)
        actions = s0.get_actions()
        self.v0.n = len(actions)
        #process_list = []
        self.time_map = {'select': 0, 'simulate': 0, 'back_propagate': 0}
        start_time = time.process_time()
        if not self.keep_alive_multiprocessing:
            self.keep_alive_multiprocessing = KeepAliveMultiprocessing(self.search, self.success_callback)
            self.keep_alive_multiprocessing.run()

        for a in s0.actions:
            s = self.do_action(s0, a.action)  
            v = Node(s, a)
            v.parent = self.v0
            self.keep_alive_multiprocessing.q.put(v)
            #self.v0.children.append(v)
            #pool.apply_async(self.search, (v,), callback=self.success_callback, error_callback=self.error_callback)
            #p = ThreadWithCallback(target=self.search,args=(v,), callback=self.thread_callback)
            #p = Process(target=self.search, args=(v,))
            #process_list.append(p)
            #p.start()
        
        #for p in process_list:
        #    p.join()
        #pool.close()
        #pool.join()
        count = 0
        while True:
            if not self.keep_alive_multiprocessing.q_return.empty():
                v = self.keep_alive_multiprocessing.q_return.get()
                self.v0.children.append(v)
                count += 1
            if count == len(actions):
                break
            # if len(self.v0.children) == len(actions):
            #     break
        end_time = time.process_time()
        print('actual time: ', end_time-start_time)
        v1, a = self.UCB1(self.v0)
        print('curren_chess_color: ', v1.state.curren_chess_color)

        return a, self.time_map
    def search(self, v0):
        i = 0
        start_time = time.process_time()
        time_map = {'select': 0, 'simulate': 0, 'back_propagate': 0}
        #v0 = Node(s0, None)
        while i < self.iretation_times:
            t1 = time.process_time()
            v1 = self.select(v0)
            t = time.process_time()
            time_map['select'] += t - t1
            t1 = t
            st = self.simulate(v1.state)
            t = time.process_time()
            time_map['simulate'] += t - t1
            t1 = t
            self.back_propagate(v1, st)
            t = time.process_time()
            time_map['back_propagate'] += t - t1

            i += 1

            if time.process_time() > self.time_out + start_time:
                print('time out, iterate times: {}'.format(i))
                break

        # v1, a = self.UCB1(v0)
        # print('curren_chess_color: ', v1.state.curren_chess_color)
        # print_board(v1.state.chess_status)
        # return a
        return v0

    def is_has_unexpended_child(self, v):
        actions = v.state.get_actions()
        for a in actions:
            if a.expanded == False:
                return True
        return False

    def select(self, v0):
        v = v0
        while not self.is_terminal(v.state):          #非叶子节点
            if self.is_has_unexpended_child(v):  #有未扩展节点
                #print("has unexpanded")
                return self.expand(v)           #有则扩展节点
            else:
                v, _ = self.UCB1(v)      #没有则找UCB最大的往下继续
                #print("UCB1")
        return v
    def simulate(self, s0):
        s = s0
        while not self.is_terminal(s):
            _,s = self.do_random_action(s, False)       #执行随机动作
        return s

    def back_propagate(self, v, st):
        while v != None:
            v.n += 1
            v.q = v.q + self.get_q_by_player(st, v.state)
            v = v.parent

    def expand(self, v):
        a, s = self.do_random_action(v.state, True)  #执行随机未访问过的动作
        a.expanded = True
        v_next = Node(s, a)
        v_next.parent = v
        if not v.children:
            v.children = []
        v.children.append(v_next)
        return v_next

    def get_q_by_player(self, st, state):
        q = self.value(st)
        if state.curren_chess_color == ChessState.BLACK:
            return -q
        else:
            return q

    def value(self, st):
        if self.color == ChessState.BLACK:
            return st.scores[ChessState.BLACK] - st.scores[ChessState.WHITE]
        else:
            return st.scores[ChessState.WHITE] - st.scores[ChessState.BLACK]
    def UCB(self, v, v1):
        return v1.q / v1.n + self.c * math.sqrt(2*math.log(v.n)/ v1.n)

    def UCB1(self, v):
        v_next = max(v.children, key=lambda x: self.UCB(v, x))
        return v_next, v_next.action

    def success_callback(self, v):
        v.parent = self.v0
        self.v0.children.append(v)
        ...


    def error_callback(self, e):
        ...
def multi_processor_search(s0, uct):
    global v0
    v0 = Node(s0, None)
    actions = s0.get_actions()
    v0.n = len(actions)
    
    #process_list = []
    pool = multiprocessing.Pool()

    for a in s0.actions:
        s = uct.do_action(s0, a.action)  
        v = Node(s, a)
        v.parent = v0
        #v0.children.append(v)
        pool.apply_async(uct.search, (v,), callback=self.success_callback, error_callback = self.error_callback)
        #p = threading.Thread(target=self.search,args=(v,))
        #p = Process(target=wrapper, args=(v,))
        #process_list.append(p)
        #p.start()
    
    # for p in process_list:
    #     p.join()
    pool.close()
    pool.join()
    v1, a = uct.UCB1(v0)
    print('curren_chess_color: ', v1.state.curren_chess_color)
