from math import inf
from ChessStateEnum import ChessStateEnum
from StrategyEnum import StrategyEnum
import time


class Greedy():
    def __init__(self, do_action, strategy, color):
        self.do_action = do_action
        self.color = color
        self.strategy = strategy
    
    def search(self, s0):
        time_map = {}
        actions = s0.get_actions()
        best_a = None
        max_value = float('-inf')
        if self.strategy == StrategyEnum.GREEDY_MAXSCORE:
            value = self.value_maxscore
            key = 'greedy-maxscore' 
        elif self.strategy == StrategyEnum.GREEDY_MINPOS:
            value = self.value_minpos
            key = 'greedy-minpos' 
        start_time = time.process_time()
        
        for a in actions:
            s = self.do_action(s0, a.action)
            
            if value(s) > max_value:
                best_a = a
        
        time_map[key] = time.process_time() - start_time
        return best_a, time_map

    def value_maxscore(self, s):
        value = s.scores[ChessStateEnum.BLACK] - s.scores[ChessStateEnum.WHITE]
        if self.color == ChessStateEnum.WHITE: value = -value
        return value

    def value_minpos(self, s):
        actions = s.get_actions()
        return -len(actions)