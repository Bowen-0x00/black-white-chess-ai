

import numpy as np

class Action():
    action = None
    expanded = False

    def __init__(self, action):
        self.action = action

class ReversiState():


    def __init__(self, curren_chess_color, chess_status, scores, valid_path_map):
        self.curren_chess_color = curren_chess_color
        self.chess_status = chess_status
        self.scores = scores
        self.valid_path_map = valid_path_map
        #player  |   chess_state  |  scores  |  
        self.actions = []

    def get_actions(self):
        if len(self.actions) > 0:
            return self.actions
        actions = list(self.valid_path_map.keys())
        actions = [eval(a) for a in actions]
        for a in actions:
            self.actions.append(Action(a))
        return self.actions

    