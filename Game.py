from logging import exception
import pygame
import sys
from enum import Enum
import numpy as np
import pygame_menu


class ChessState(Enum):
    BLACK = 0
    WHITE = 1
    VALID = 2
    EMPTY = 3

class GameMode(Enum):
    P1VSP2 = 0
    P1VSCOM = 1
    MENU = 2

class Board():
    scores = {ChessState.BLACK:2, ChessState.WHITE:2}

    def __init__(self) -> None:
        self.board_size = (8, 8)
        self.grid_size = (70, 70)
        self.font_size = 64
        self.score_pos_black = (100, 60)
        self.score_pos_white = (924, 60)

        pygame.init()
        self.screen = pygame.display.set_mode([1024, 768], depth = 32)
        self.board_rect = (234, 143, 555, 555)
        pygame.display.set_caption("Reversi")
        self.bg_img = pygame.image.load("image/s_background.png").convert()
        self.black_img = pygame.image.load("image/s_chess_black.png").convert_alpha()
        self.white_img = pygame.image.load("image/s_chess_white.png").convert_alpha()
        self.valid_img = pygame.image.load("image/s_chess_valid.png").convert_alpha()
        self.finish_img = pygame.image.load("image/dialog2.png").convert_alpha()
        self.screen.blit(self.bg_img, (0, 0))

        #mytheme.title = False
        #menu = pygame_menu.Menu('Welcome', 400, 300, theme=pygame_menu.themes.THEME_DARK)

        self.text_font = pygame.font.Font('font/云峰静龙行书.ttf', 48)
        self.black_info_text = self.text_font.render("黑",True,(0,0,0))
        self.black_text_rect = self.black_info_text.get_rect() 
        self.black_text_rect.center = self.score_pos_black

        self.white_info_text = self.text_font.render("白",True,(0,0,0))
        self.white_text_rect = self.white_info_text.get_rect() 
        self.white_text_rect.center = self.score_pos_white


        self.chess_state_img_map = {ChessState.BLACK: self.black_img,
                            ChessState.WHITE: self.white_img,
                            ChessState.VALID: self.valid_img}
        self.finish_text_rect = None

    def show_background(self):
        self.screen.blit(self.bg_img, (0, 0))

    def update_chess_img_to_screen(self, chess_status):
        for x in range(self.board_size[0]):
            for y in range(self.board_size[1]):
                if chess_status[x][y] != ChessState.EMPTY:
                    #screen.set_clip(board_rect[0]+y*70, board_rect[1]+x*70, 70, 70)
                    self.screen.blit(self.chess_state_img_map[chess_status[x][y]], (self.board_rect[0]+y*self.grid_size[0], self.board_rect[1]+x*self.grid_size[1]))

    def update_info(self, scores, curren_chess_color):
        self.screen.blit(self.black_info_text, self.black_text_rect)
        text = self.text_font.render("{}".format(scores[ChessState.BLACK]),True,(0,0,0))
        textRect =text.get_rect() 
        textRect.center = (self.score_pos_black[0], self.score_pos_black[1] + 80)
        self.screen.blit(text,textRect)
        self.screen.blit(self.white_info_text, self.white_text_rect)
        text = self.text_font.render("{}".format(scores[ChessState.WHITE]),True,(0,0,0))
        textRect =text.get_rect() 
        textRect.center = (self.score_pos_white[0], self.score_pos_white[1] + 80)
        self.screen.blit(text,textRect)
        blink_rect = self.black_text_rect if curren_chess_color == ChessState.BLACK else self.white_text_rect
        pygame.draw.rect(self.screen, (50, 50, 50), blink_rect, 2)

    def show_finish(self, scores):
        face = pygame.Surface((1024,768), pygame.SRCALPHA, 32)
        face.fill((200, 200, 200, 200))
        self.screen.blit(face, (0, 0))
        self.screen.blit(self.finish_img, (310, 220))
        text = self.text_font.render("{}胜".format('黑' if scores[ChessState.BLACK] >= scores[ChessState.WHITE]else '白'),True,(30,30,30))
        finish_text_rect =text.get_rect() 
        finish_text_rect.center = (510, 390)
        self.screen.blit(text,finish_text_rect)
        return finish_text_rect

 


class Game():
    def __init__(self) -> None:
        self.board = Board()
        self.scores = {ChessState.BLACK:2, ChessState.WHITE:2}
        self.chess_status = np.full(self.board.board_size, ChessState.EMPTY)
        self.curren_chess_color = ChessState.BLACK
        self.is_finish = False
        self.curren_game_mode = GameMode.MENU
        self.test_flag = False

        mytheme = pygame_menu.themes.THEME_DARK.copy()
        # myimage = pygame_menu.baseimage.BaseImage(
        #     image_path='dialog2.png',
        #     drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL
        # )

        #mytheme.background_color = myimage
        mytheme.background_color=(40, 41, 35, 200)
        mytheme = mytheme.set_background_color_opacity(0.7)
        self.text_font = pygame.font.Font('font/云峰静龙行书.ttf', 32)
        mytheme.widget_font = self.text_font
        self.menu = pygame_menu.Menu('Menu', 400, 300, theme=mytheme)

        self.menu.add.button('P1 vs. P2', self.menu_callback_start_game, GameMode.P1VSP2)
        self.menu.add.button('P1 vs. Com', self.menu_callback_start_game, GameMode.P1VSCOM)
        self.menu.add.button('Quit', pygame_menu.events.EXIT)
        self.menu_flag = True
        self.valid_path_map = {}

    def init_game(self):
        self.chess_status[::] = ChessState.EMPTY
        self.chess_status[self.board.board_size[0]//2-1][self.board.board_size[1]//2-1] = ChessState.WHITE
        self.chess_status[self.board.board_size[0]//2-1][self.board.board_size[1]//2] = ChessState.BLACK
        self.chess_status[self.board.board_size[0]//2][self.board.board_size[1]//2-1] = ChessState.BLACK
        self.chess_status[self.board.board_size[0]//2][self.board.board_size[1]//2] = ChessState.WHITE
        self.curren_chess_color = ChessState.BLACK
        self.scores = {ChessState.BLACK:2, ChessState.WHITE:2}

    def get_reversed_color(self):
        #return int(curren_chess_color) ^ 1
        return ChessState.WHITE if self.curren_chess_color == ChessState.BLACK else ChessState.BLACK

    def check_show_finish(self):
        #if len(self.valid_path_map) == 0 or self.scores[ChessState.BLACK] == 0 or self.scores[ChessState.WHITE] == 0:
        if self.test_flag:
            self.is_finish = True
            self.finish_text_rect = self.board.show_finish(self.scores)

    def check_pos_valid(self, x, y):
        board_size = self.board.board_size
        return x >= 0 and x < board_size[0] and y >= 0 and y < board_size[1]

    def clear_valid_state(self):
        board_size = self.board.board_size
        for x in range(board_size[0]):
            for y in range(board_size[1]):
                if self.chess_status[x][y] == ChessState.VALID:
                    self.chess_status[x][y] = ChessState.EMPTY

    def update_valid_state(self):
        reverse_color = self.get_reversed_color()
        directs = [np.array([0, 1]),
        np.array([0, -1]),
        np.array([1, 0]),
        np.array([-1, 0]),
        np.array([-1, -1]),
        np.array([-1, 1]),
        np.array([1, -1]),
        np.array([1, 1])]
        
        valid_path_map = self.valid_path_map
        self.valid_path_map.clear()
        board_size = self.board.board_size
        for x in range(board_size[0]):
            for y in range(board_size[1]):
                if (x == 0 and y ==0) or (x == 0 and y ==board_size[0]) or (x == board_size[0]-1 and y ==0) or (x == board_size[0]-1 and y ==board_size[1] - 1):
                    continue
                if self.chess_status[x][y] == reverse_color:
                    for d in directs:
                        coordinate = np.array([x, y])
                        coordinate_new = coordinate + d
                        if not self.check_pos_valid(*(coordinate - d)) or (self.chess_status[(*(coordinate - d), )] != ChessState.EMPTY and self.chess_status[(*(coordinate - d), )] != ChessState.VALID):
                            continue
                        if str(coordinate - d) not in valid_path_map:
                            valid_path_map[str(coordinate - d)] = {}
                        if str(d) not in valid_path_map[str(coordinate - d)]:
                            valid_path_map[str(coordinate - d)][str(d)] = []   
                        valid_path_map[str(coordinate - d)][str(d)].append(coordinate)
                        while self.check_pos_valid(*coordinate_new):
                            if self.chess_status[(*coordinate_new,)] == ChessState.EMPTY or self.chess_status[(*coordinate_new,)] == ChessState.VALID:
                                del valid_path_map[str(coordinate - d)][str(d)]
                                break
                            if self.chess_status[(*coordinate_new,)] == self.curren_chess_color:
                                self.chess_status[(*(coordinate - d), )] = ChessState.VALID
                                break
                            valid_path_map[str(coordinate - d)][str(d)].append(coordinate_new.tolist())
                            coordinate_new += d
        for k in list(valid_path_map):
            if valid_path_map[k] == {}:
                del valid_path_map[k]

    def flip_chess(self, x, y):
        reverse_color = self.get_reversed_color()
        for d in self.valid_path_map[str(np.array([x,y]))].values():
            for p in d:
                self.chess_status[(*p,)] = self.curren_chess_color
                self.scores[self.curren_chess_color] +=1
                self.scores[reverse_color] -=1  


    def update_board(self):
        self.board.show_background()
        if self.curren_game_mode == GameMode.P1VSP2 or self.curren_game_mode == GameMode.P1VSCOM:  
            self.board.update_chess_img_to_screen(self.chess_status)
            self.board.update_info(self.scores, self.curren_chess_color)  
            self.check_show_finish()

         
    def process_chess_mouse_event(self, x_pos, y_pos):
        board = self.board
        x = y_pos//board.grid_size[0]
        y = x_pos//board.grid_size[1]
        if self.chess_status[x][y] == ChessState.VALID:
            self.chess_status[x][y] = self.curren_chess_color
            self.scores[self.curren_chess_color] += 1
            self.flip_chess(x, y)
            self.curren_chess_color = self.get_reversed_color()

            self.clear_valid_state()
            self.update_valid_state()
            self.update_board()

    def return_menu(self):
        self.curren_game_mode = GameMode.MENU
        self.menu_flag = True
        self.menu.enable()

    def process_event(self, events):
        board_rect = self.board.board_rect
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if not self.is_finish and event.pos[0] > board_rect[0] and event.pos[0] < board_rect[0] + board_rect[2]\
                    and event.pos[1] > board_rect[1] and event.pos[1] < board_rect[1] + board_rect[3]:
                    self.process_chess_mouse_event(event.pos[0] - board_rect[0], event.pos[1] - board_rect[1])
                if self.is_finish:
                    if event.pos[0] > self.finish_text_rect.left and  event.pos[0] < self.finish_text_rect.left + self.finish_text_rect.width\
                        and event.pos[1] > self.finish_text_rect.top and  event.pos[1] < self.finish_text_rect.top + self.finish_text_rect.height:
                        # init_game()
                        self.is_finish = False
                        self.test_flag = False
                        # clear_valid_state()
                        # update_valid_state()
                        # update_board()
                        self.board.show_background()
                        #pygame.event.clear()
                        self.return_menu()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.test_flag = True
                    self.update_board()


    def run(self):
        clock = pygame.time.Clock()
        while True:
            events = pygame.event.get()
            self.update_board()
            if self.menu_flag and self.menu.is_enabled():
                self.menu.update(events)
                try:
                    self.menu.draw(self.board.screen)
                except RuntimeError as e:
                    ...
            self.process_event(events)
            pygame.display.update()
            clock.tick(20)

    def menu_callback_start_game(self, mode):
        if mode == GameMode.P1VSCOM:
            ...
        elif mode == GameMode.P1VSP2:
            self.menu_flag = False
            self.curren_game_mode = GameMode.P1VSP2
            self.init_game()
            #update_chess_img_to_screen()
            self.update_valid_state()
            self.update_board()
            self.menu.close()
            self.menu.disable()




if __name__=="__main__":
    game = Game()
    game.run()    





