import random
import math
from ChessState import ChessState
class Node():
    def __init__(self, state, action):
        self.state = state   #player  |   chess_state  |  scores  |  
        self.action = action #from which action
        self.children = None
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

    def __init__(self, do_action, check_finish):
        self.do_action = do_action      #do action return state
        self.check_finish = check_finish

    def is_terminal(self, s):
        return self.check_finish(s)

    def do_random_action(self, s):
        actions = list(s.valid_path_map.keys())
        actions = [eval(a) for a in actions]
        a = actions[random.randint(0, len(actions)-1)] #从动作列表中选择一个动作
        s = self.do_action(s, a)                        #执行动作返回状态
        return a, s

    def search(self, s0):
        i = self.iretation_times
        v0 = Node(s0, None)
        while i > 0:
            v1 = self.select(v0)
            st = self.simulate(v1.state)
            self.back_propagate(v1, st)
            i = i - 1

        v1, a = self.UCB1(v0)
        print('curren_chess_color: ', v1.state.curren_chess_color)
        print_board(v1.state.chess_status)
        return a

    def is_has_unvisited_child(self, v):
        return v.children == None or len([i for i in v.children if i.visited == False]) > 0

    def select(self, v0):
        v = v0
        while not self.is_terminal(v.state):          #非叶子节点
            if self.is_has_unvisited_child(v):  #有未扩展节点
                v.visited = True
                return self.expand(v)           #有则扩展节点
            else:
                v, _ = self.UCB1(v)      #没有则找UCB最大的往下继续

    def simulate(self, s0):
        s = s0
        while not self.is_terminal(s):
            _,s = self.do_random_action(s)       #执行随机动作
        return s

    def back_propagate(self, v, st):
        while v != None:
            v.n += 1
            v.q = v.q + self.get_q_by_player(st, v.state)
            v = v.parent

    def expand(self, v):
        if len(v.state.valid_path_map) == 0:
            x = v
        a, s = self.do_random_action(v.state)
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
        return st.scores[ChessState.BLACK] - st.scores[ChessState.WHITE]

    def UCB(self, v, v1):
        return v1.q / v1.n + self.c * math.sqrt(2*math.log(v.n)/ v1.n)

    def UCB1(self, v):
        v_next = max(v.children, key=lambda x: self.UCB(v, x))
        return v_next, v_next.action