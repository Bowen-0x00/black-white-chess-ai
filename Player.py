from StrategyEnum import StrategyEnum
from Greedy import Greedy
from MonteCarloSearch import UCT

class Player():

    def __init__(self, strategy_enum, color, reversi):
        self.color = color
        self.strategy_enum = strategy_enum
        self.reversi = reversi
        if strategy_enum == StrategyEnum.GREEDY_MAXSCORE or strategy_enum == StrategyEnum.GREEDY_MINPOS:
            self.strategy = Greedy(reversi.do_action, strategy_enum, self.color)
        elif strategy_enum == StrategyEnum.HUMAN:
            pass
        elif strategy_enum == StrategyEnum.UCT:
            self.strategy = UCT(reversi.do_action, reversi.check_finish, self.color)

    def do(self):
        if self.strategy_enum != StrategyEnum.HUMAN:
            a, _ = self.strategy.search(self.reversi.state)
            return self.reversi.do_action(self.reversi.state, a.action)
        else:
            while self.color == self.reversi.state.curren_chess_color and not self.reversi.is_finish:
                pass 
            return None