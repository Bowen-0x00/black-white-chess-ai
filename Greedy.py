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
        start_time = time.process_time()
        for a in actions:
            s = self.do_action(s0, a.action)
            if self.strategy == StrategyEnum.GREEDY_MAXSCORE:
                if self.value_maxscore(s) > max_value:
                    best_a = a
            elif self.strategy == StrategyEnum.GREEDY_MINPOS:
                ...
        time_map['greedy'] = time.process_time() - start_time
        return best_a, time_map

    def value_maxscore(self, s):
        value = s.scores[ChessStateEnum.BLACK] - s.scores[ChessStateEnum.WHITE]
        if self.color == ChessStateEnum.WHITE: value = -value
        return value