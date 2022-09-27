from enum import Enum
class StrategyEnum(Enum):
    UCT = 0
    GREEDY_MAXSCORE = 1
    GREEDY_MINPOS = 2
    HUMAN = 3
    UCT_EXPERT = 4


    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value

        return member
    def __int__(self):
        return self.value