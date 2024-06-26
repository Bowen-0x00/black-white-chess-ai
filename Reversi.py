from ReversiState import ReversiState
from ChessStateEnum import ChessStateEnum
import numpy as np
import copy
import multiprocessing
from MonteCarloSearch import Node, UCT

class Reversi():
    def __init__(self, board_size):
        self.board_size = board_size
        scores = {ChessStateEnum.BLACK:2, ChessStateEnum.WHITE:2}
        chess_status = np.full(self.board_size, ChessStateEnum.EMPTY)
        curren_chess_color = ChessStateEnum.BLACK
        self.is_finish = False
        valid_path_map = {}
        self.state = ReversiState(curren_chess_color, chess_status, scores, valid_path_map)
        self.invalid_count = {ChessStateEnum.BLACK:0, ChessStateEnum.WHITE:0}
        
    def init_game_state(self):
        self.is_finish = False
        self.state.valid_path_map = {}
        self.invalid_count = {ChessStateEnum.BLACK:0, ChessStateEnum.WHITE:0}
        self.state.curren_chess_color = ChessStateEnum.BLACK
        self.state.chess_status[::] = ChessStateEnum.EMPTY

        self.state.chess_status[self.board_size[0]//2-1][self.board_size[1]//2-1] = ChessStateEnum.WHITE
        self.state.chess_status[self.board_size[0]//2-1][self.board_size[1]//2] = ChessStateEnum.BLACK
        self.state.chess_status[self.board_size[0]//2][self.board_size[1]//2-1] = ChessStateEnum.BLACK
        self.state.chess_status[self.board_size[0]//2][self.board_size[1]//2] = ChessStateEnum.WHITE
        self.state.curren_chess_color = ChessStateEnum.BLACK
        self.state.scores = {ChessStateEnum.BLACK:2, ChessStateEnum.WHITE:2}

    def get_reversed_color(self, curren_chess_color):
        return ChessStateEnum.WHITE if curren_chess_color == ChessStateEnum.BLACK else ChessStateEnum.BLACK


    def check_finish(self, s):
        if self.invalid_count[ChessStateEnum.BLACK] >= 1 and self.invalid_count[ChessStateEnum.WHITE] >= 1:
            return True
        ret = s.scores[ChessStateEnum.BLACK] == 0 or s.scores[ChessStateEnum.WHITE] == 0 or s.scores[ChessStateEnum.BLACK] + s.scores[ChessStateEnum.WHITE] == self.board_size[0] * self.board_size[1] 
        return ret
    
    def check_pos_valid(self, x, y):
        board_size = self.board_size
        return x >= 0 and x < board_size[0] and y >= 0 and y < board_size[1]

    def clear_valid_state(self, s):
        board_size = self.board_size
        for x in range(board_size[0]):
            for y in range(board_size[1]):
                if s.chess_status[x][y] == ChessStateEnum.VALID:
                    s.chess_status[x][y] = ChessStateEnum.EMPTY

    def update_valid_state(self, s):
        reverse_color = self.get_reversed_color(s.curren_chess_color)
        directs = [np.array([0, 1]),np.array([0, -1]),np.array([1, 0]),np.array([-1, 0]),np.array([-1, -1]),np.array([-1, 1]),np.array([1, -1]),np.array([1, 1])]
        
        s.valid_path_map.clear()
        board_size = self.board_size
        for x in range(board_size[0]):
            for y in range(board_size[1]):
                if (x == 0 and y ==0) or (x == 0 and y ==board_size[0]) or (x == board_size[0]-1 and y ==0) or (x == board_size[0]-1 and y ==board_size[1] - 1):
                    continue
                if s.chess_status[x][y] == reverse_color:
                    if x==4 and y==4:
                        aa =x
                    for d in directs:
                        coordinate = np.array([x, y])
                        coordinate_new = coordinate + d
                        if not self.check_pos_valid(*(coordinate_new)):
                            continue

                        if not self.check_pos_valid(*(coordinate - d)) or (s.chess_status[(*(coordinate - d), )] != ChessStateEnum.EMPTY and s.chess_status[(*(coordinate - d), )] != ChessStateEnum.VALID):
                            continue
                        if str(list(coordinate - d)) not in s.valid_path_map:
                            s.valid_path_map[str(list(coordinate - d))] = {}
                        if str(list(d)) not in s.valid_path_map[str(list(coordinate - d))]:
                            s.valid_path_map[str(list(coordinate - d))][str(list(d))] = []   
                        s.valid_path_map[str(list(coordinate - d))][str(list(d))].append(coordinate)
                        while True:
                            if self.check_pos_valid(*coordinate_new):
                                if s.chess_status[(*coordinate_new,)] == ChessStateEnum.EMPTY or s.chess_status[(*coordinate_new,)] == ChessStateEnum.VALID:
                                    del s.valid_path_map[str(list(coordinate - d))][str(list(d))]
                                    break
                                if s.chess_status[(*coordinate_new,)] == s.curren_chess_color:
                                    s.chess_status[(*(coordinate - d), )] = ChessStateEnum.VALID
                                    break
                                s.valid_path_map[str(list(coordinate - d))][str(list(d))].append(coordinate_new.tolist())
                            
                                coordinate_new += d
                            else:
                                del s.valid_path_map[str(list(coordinate - d))][str(list(d))]
                                break
        for k in list(s.valid_path_map):
            if s.valid_path_map[k] == {}:
                del s.valid_path_map[k]   
        

    def flip_chess(self, s, a):
        if a == None:
            return
        x, y = a
        s.chess_status[x][y] = s.curren_chess_color
        s.scores[s.curren_chess_color] += 1
        reverse_color = self.get_reversed_color(s.curren_chess_color)
        for d in s.valid_path_map[str(list(np.array([x,y])))].values():
            for p in d:
                s.chess_status[(*p,)] = s.curren_chess_color
                s.scores[s.curren_chess_color] +=1
                s.scores[reverse_color] -=1  

    def do_action(self, s, a):
        s_new = copy.deepcopy(s)
        if a == None:
            self.invalid_count[s.curren_chess_color] += 1
        else:
            self.invalid_count[s.curren_chess_color] = 0
        self.flip_chess(s_new, a)
        s_new.curren_chess_color = self.get_reversed_color(s_new.curren_chess_color)
        self.clear_valid_state(s_new)
        self.update_valid_state(s_new)
        s_new.actions = []
        return s_new

