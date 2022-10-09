from multiprocessing.managers import BaseManager
import random
import math
from ChessStateEnum import ChessStateEnum
import time
import multiprocessing
from KeepAliveMultiProcess import KeepAliveMultiprocessing
from ExpertSystem import ExpertSystem

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
class UCTParam():
    def __init__(self, i, t, c):
        self.iretation_times = i
        self.time_out = t
        self.c = c

class UCT():
    iretation_times = 100
    c = 2
    time_out = 1

    def __init__(self, reversi, color):
        self.reversi = reversi
        self.do_action = reversi.do_action      #do action return state
        self.color = color
        self.v0 = None
        self.keep_alive_multiprocessing = None
        self.param = multiprocessing.Manager().Namespace()
        self.param.iretation_times = 100
        self.param.time_out = 1
        self.param.c = 3
        self.num = 1
        self.is_expert = False

    def is_terminal(self, s):
        return self.reversi.check_finish(s)

    def do_random_action(self, s, unvisited = False):
        actions = s.get_actions()
        if unvisited:
            actions = [a for a in actions if a.expanded == False]
        if len(actions) > 0:
            if self.is_expert:
                expert = ExpertSystem()
                actions_choose, _ = expert.choose_action(s, self.reversi, self.color) ## 小心删光了       
                if actions_choose != []:
                    actions = actions_choose   
            a = actions[random.randint(0, len(actions)-1)] #从动作列表中选择一个动作
            s = self.reversi.do_action(s, a.action)  
        else:
            a = None
            s = self.reversi.do_action(s, None)  
        s.get_actions()                      #执行动作返回状态
        return a, s
    def thread_callback(self, t):
        self.time_map['select'] = t['select'] if t['select'] > self.time_map['select'] else self.time_map['select']
        self.time_map['simulate'] = t['simulate'] if t['simulate'] > self.time_map['simulate'] else self.time_map['simulate']
        self.time_map['back_propagate'] = t['back_propagate'] if t['back_propagate'] > self.time_map['back_propagate'] else self.time_map['back_propagate']
    
    def set_param(self, param):
        # for i in range(multiprocessing.cpu_count()):
        #     self.keep_alive_multiprocessing.q_param.put([i, t, iretation_times, c])
        self.param.time_out = param.time_out
        self.param.iretation_times = param.iretation_times
        self.param.c = param.c

    # def setparam_callback(self, l):
    #     self.time_out.value = l[0]
    #     self.iretation_times.value = l[1]
    #     self.c.value = l[2]

    def search(self, s0):
        expert = ExpertSystem()
        if self.is_expert:
            actions, flag = expert.choose_action(s0, self.reversi, self.color, debug=True)
            if flag:
                if len(actions) == 1:
                    return actions[0], {'select': 0, 'simulate': 0, 'back_propagate': 0}
                else:
                    s0.actions = actions
                    return self.multi_processor_search(s0)
        return self.multi_processor_search(s0)

    def multi_processor_search(self, s0):
        self.v0 = Node(s0, None)
        actions = s0.get_actions()
        self.v0.n = len(actions)
        #process_list = []
        self.time_map = {'select': 0, 'simulate': 0, 'back_propagate': 0}
        start_time = time.process_time()
        if not self.keep_alive_multiprocessing:
            self.keep_alive_multiprocessing = KeepAliveMultiprocessing(self._search, self.success_callback, self.num)
            self.keep_alive_multiprocessing.run()
        
        for a in s0.actions:
            s = self.reversi.do_action(s0, a.action)  
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
                v, t = self.keep_alive_multiprocessing.q_return.get()
                self.v0.children.append(v)
                self.time_map['select'] = t['select'] if t['select'] > self.time_map['select'] else self.time_map['select']
                self.time_map['simulate'] = t['simulate'] if t['simulate'] > self.time_map['simulate'] else self.time_map['simulate']
                self.time_map['back_propagate'] = t['back_propagate'] if t['back_propagate'] > self.time_map['back_propagate'] else self.time_map['back_propagate']
                count += 1
            #print('count: {}, len(actions): {}'.format(count, len(actions)))
            if count == len(actions):
                break
            # if len(self.v0.children) == len(actions):
            #     break
        end_time = time.process_time()
        print('multiprocess actual time: ', end_time-start_time)
        v1, a = self.UCB1(self.v0)

        return a, self.time_map

    def _search(self, v0):
        i = 0
        start_time = time.process_time()
        time_map = {'select': 0, 'simulate': 0, 'back_propagate': 0}
        #v0 = Node(s0, None)
        while i < self.param.iretation_times:
            v1 = self.select(v0)
            st = self.simulate(v1.state)
            self.back_propagate(v1, st)
            i += 1

            if end_time > self.param.time_out + start_time:
                print('time out: {}, iterate times: {}.  actual: {}'.format(self.param.time_out, i, end_time-start_time))
                break

        # v1, a = self.UCB1(v0)
        # print('curren_chess_color: ', v1.state.curren_chess_color)
        # print_board(v1.state.chess_status)
        # return a
        #print('i: ', i)
        return v0, time_map

    def is_has_unexpended_child(self, v):
        actions = v.state.get_actions()
        if len(actions) == 0:
            return True
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
        if a != None:
            a.expanded = True
        v_next = Node(s, a)
        v_next.parent = v
        if not v.children:
            v.children = []
        v.children.append(v_next)
        return v_next

    def get_q_by_player(self, st, state):
        q = self.value(st)
        if state.curren_chess_color == self.color:
            return -q
        else:
            return q

    def value(self, st):
        if self.color == ChessStateEnum.BLACK:
            return st.scores[ChessStateEnum.BLACK]**2 - st.scores[ChessStateEnum.WHITE] ** 2
        else:
            return st.scores[ChessStateEnum.WHITE]**2 - st.scores[ChessStateEnum.BLACK] ** 2
    def UCB(self, v, v1):
        return v1.q / v1.n + self.param.c * math.sqrt(2*math.log(v.n)/ v1.n)

    def UCB1(self, v):
        v_next = max(v.children, key=lambda x: self.UCB(v, x))
        return v_next, v_next.action

    def success_callback(self, v):
        v.parent = self.v0
        self.v0.children.append(v)



    def error_callback(self, e):
        ...

