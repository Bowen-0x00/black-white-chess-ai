import numpy as np
from ChessStateEnum import ChessStateEnum
import copy

class ExpertSystem():
    def choose_action(self, state, reversi, color, debug = False, cut_nouse = False, stable_count = False):
        h, w = reversi.board_size
        actions = copy.deepcopy(state.get_actions())
        #actions = state.actions
        reverse_color = reversi.get_reversed_color(color)
        chess_status = state.chess_status
        corner_list = []
        for idx, a in enumerate(state.actions):
            if list(a.action) == [0, 0] or list(a.action) == [0, w-1] or list(a.action) == [h-1, 0] or list(a.action) == [h-1, w-1]:
                if debug:
                    print('select corner')
                corner_list.append(a)
        if len(corner_list) > 0:
            return corner_list, True
        if cut_nouse:
            for idx, a in enumerate(state.actions):
                stable, _ = self.find_stable(chess_status, reverse_color)
                directions = [np.array([0, 1]),np.array([0, -1]),np.array([1, 0]),np.array([-1, 0]),np.array([-1, -1]),np.array([-1, 1]),np.array([1, -1]),np.array([1, 1])]
                for d in directions:
                    if reversi.check_pos_valid(*(a.action + d)):
                        if stable[(*(a.action + d),)] == 1:
                            #print('del reverse stable')
                            if a in actions:
                                actions.remove(a)
        if stable_count:
            max_n = 0
            max_a = None
            for idx, a in enumerate(actions):
                s = reversi.do_action()
                stable, n = self.find_stable(s.chess_status, color)
                if n > max_n:
                   max_a = a 
            return [max_a], False
        if len(actions) == 0:
            actions = state.actions
        return actions, False

                    
    def find_stable(self, board, color):
        stable = np.zeros((8, 8))
        corners = [np.array([0, 0]),np.array([0, 7]),np.array([7, 0]),np.array([7, 7])]   
        directions_list = np.array([[np.array([0, 1]),np.array([1, 0]),np.array([1, 1])],
                [np.array([0, -1]),np.array([1, 0]),np.array([1, -1])],
                [np.array([0, 1]),np.array([-1, 0]),np.array([-1, 1])],
                [np.array([0, -1]),np.array([-1, 0]),np.array([-1, -1])]])
        # for x in range(8):
        for idx, c in enumerate(corners):
            if board[(*c,)] == color:
                stable[(*c,)] = 1
                directions = directions_list[idx]
                count = 0
                for d in directions[0:2]:
                    pos_next = c + d
                    for i in range(7):
                        if board[(*pos_next,)] == color:
                            stable[(*pos_next,)] = 1
                        else:
                            break
                        pos_next += d
        for j in range(3): 
            corners[0] += (1,1)   
            corners[1] += (1,-1)
            corners[2] += (-1,1)
            corners[3] += (-1,-1)
            for idx, c in enumerate(corners):
                if board[(*c,)] == 1:
                    directions = directions_list[idx]
                    count = 0
                    for d in directions:
                        if stable[(*(c - d),)] != 1:
                            count= 0
                            break
                        count += 1
                    if count == 3:
                        stable[(*c,)] = 1
                        for d in directions[0:2]:
                            pos_next = c + d
                            for i in range(7):
                                if board[(*pos_next,)] == color:
                                    stable[(*pos_next,)] = 1
                                else:
                                    break
                                pos_next += d 
        return stable, np.sum(stable)          