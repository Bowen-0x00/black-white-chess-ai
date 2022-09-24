from math import inf
from ChessStateEnum import ChessStateEnum
from StrategyEnum import StrategyEnum
import sys


class Greedy():
    def __init__(self, do_action, strategy, color):
        self.do_action = do_action
        self.color = color
        self.strategy = strategy
    
    def search(self, s0):
        actions = s0.get_actions()
        best_a = None
        max_value = float('-inf')
        for a in actions:
            s = self.do_action(s0, a.action)
            if self.strategy == StrategyEnum.GREEDY_MAXSCORE:
                if self.value_maxscore(s) > max_value:
                    best_a = a
            elif self.strategy == StrategyEnum.GREEDY_MINPOS:
                ...
        return best_a, None

    def value_maxscore(self, s):
        value = s.scores[ChessStateEnum.BLACK] - s.scores[ChessStateEnum.WHITE]
        if self.color == ChessStateEnum.WHITE: value = -value
        return value