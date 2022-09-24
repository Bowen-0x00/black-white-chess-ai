
from enum import Enum
class ChessStateEnum(Enum):
    BLACK = 0
    WHITE = 1
    VALID = 2
    EMPTY = 3

    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value

        return member
    def __int__(self):
        return self.value

def chess_to_char(c):
    if c == ChessStateEnum.BLACK:
        return u'\u25CF'
    elif c == ChessStateEnum.WHITE:
        return u'\u25CB'
    else: 
        return u'\u2B1A'
    
def print_board(chess_state):
    for x in range(8):
        print("")
        for y in range(8):
            print(" {}".format(chess_to_char(chess_state[x][y])), end="")