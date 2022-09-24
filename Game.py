from logging import exception
from tkinter import Menu
from unittest import main
import pygame
import sys
from enum import Enum
import pygame_menu
from ChessStateEnum import ChessStateEnum, print_board
from MonteCarloSearch import UCT
from StrategyEnum import StrategyEnum
from ThreadWithCallback import ThreadWithCallback
from Reversi import Reversi
import time
from Player import Player


uct = None
game = None

class GameMode(Enum):
    P1VSP2 = 0
    P1VSCOM = 1
    COM1VSCOM2 = 2
    MENU = 3
    FINISH = 4

class CurrentColor():
    color = ChessStateEnum.BLACK

class Board():
    scores = {ChessStateEnum.BLACK:2, ChessStateEnum.WHITE:2}

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
        self.circle_img = pygame.image.load("image/circle2.png").convert_alpha()
        self.icon_img = pygame.image.load("image/icon.png").convert_alpha()
        pygame.display.set_icon(self.icon_img)
        #self.screen.blit(self.bg_img, (0, 0))

        #mytheme.title = False
        #menu = pygame_menu.Menu('Welcome', 400, 300, theme=pygame_menu.themes.THEME_DARK)

        self.text_font = pygame.font.Font('font/云峰静龙行书.ttf', 48)
        self.text_font_16 = pygame.font.SysFont('STSong', 16) 
        self.text_font_32 = pygame.font.SysFont('STSong', 32) 
        self.black_info_text = self.text_font.render("黑",True,(0,0,0))
        self.black_text_rect = self.black_info_text.get_rect() 
        self.black_text_rect.center = self.score_pos_black

        self.white_info_text = self.text_font.render("白",True,(0,0,0))
        self.white_text_rect = self.white_info_text.get_rect() 
        self.white_text_rect.center = self.score_pos_white


        self.chess_state_img_map = {ChessStateEnum.BLACK: self.black_img,
                            ChessStateEnum.WHITE: self.white_img,
                            ChessStateEnum.VALID: self.valid_img}
        self.finish_text_rect = None

    def show_background(self):
        self.screen.blit(self.bg_img, (0, 0))

    def update_chess_img_to_screen(self, chess_status):
        for x in range(self.board_size[0]):
            for y in range(self.board_size[1]):
                if chess_status[x][y] != ChessStateEnum.EMPTY:
                    #screen.set_clip(board_rect[0]+y*70, board_rect[1]+x*70, 70, 70)
                    self.screen.blit(self.chess_state_img_map[chess_status[x][y]], (self.board_rect[0]+y*self.grid_size[0], self.board_rect[1]+x*self.grid_size[1]))

    def update_info(self, scores, curren_chess_color, curren_game_mode, com_thinking, com_color, time_map):
        self.screen.blit(self.black_info_text, self.black_text_rect)
        text = self.text_font.render("{}".format(scores[ChessStateEnum.BLACK]),True,(0,0,0))
        textRect =text.get_rect() 
        textRect.center = (self.score_pos_black[0], self.score_pos_black[1] + 80)
        self.screen.blit(text,textRect)
        self.screen.blit(self.white_info_text, self.white_text_rect)
        text = self.text_font.render("{}".format(scores[ChessStateEnum.WHITE]),True,(0,0,0))
        textRect =text.get_rect() 
        textRect.center = (self.score_pos_white[0], self.score_pos_white[1] + 80)
        self.screen.blit(text,textRect)
        rect = self.circle_img.get_rect()
        rect.center = self.black_text_rect.center if curren_chess_color == ChessStateEnum.BLACK else self.white_text_rect.center
        # pygame.draw.rect(self.screen, (50, 50, 50), blink_rect, 2)
        self.screen.blit(self.circle_img, rect)
        if curren_game_mode == GameMode.P1VSCOM:
            text = self.text_font_32.render("Status: {}".format('Thinking...' if com_thinking else "Done"),True,(0,0,0))
            textRect =text.get_rect()
            pos = self.score_pos_white if com_color == ChessStateEnum.WHITE else self.score_pos_black
            textRect.bottomleft = (40, pos[1] + 80 + 80)
            self.screen.blit(text,textRect)



            y = pos[1] + 240
            if time_map and not com_thinking:
                text = self.text_font_32.render("Time:",True,(0,0,0))
                textRect =text.get_rect()
                textRect.bottomleft = (40, y)
                y += 40
                self.screen.blit(text,textRect)
                for t in time_map:
                    text = self.text_font_16.render("{}: {:.2f}".format(t, time_map[t]),True,(0,0,0))
                    textRect =text.get_rect()
                    textRect.bottomright = (self.board_rect[0] - 40, y)
                    y += 40
                    self.screen.blit(text,textRect)
            

    def show_finish(self, scores):
        face = pygame.Surface((1024,768), pygame.SRCALPHA, 32)
        face.fill((200, 200, 200, 200))
        self.screen.blit(face, (0, 0))
        self.screen.blit(self.finish_img, (310, 220))
        text = self.text_font.render("{}胜".format('黑' if scores[ChessStateEnum.BLACK] >= scores[ChessStateEnum.WHITE]else '白'),True,(30,30,30))
        finish_text_rect =text.get_rect() 
        finish_text_rect.center = (510, 390)
        self.screen.blit(text,finish_text_rect)
        return finish_text_rect
 
class Game():
    def __init__(self) -> None:
        self.board = Board()
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
        self.widget_font = pygame.font.Font('font/云峰静龙行书.ttf', 32)
        #mytheme.widget_font = self.widget_font
        self.menu = {}
        main_menu = pygame_menu.Menu('Main Menu', 450, 300, theme=mytheme)

        main_menu.add.button('P1 vs. P2', self.menu_callback_start_game, GameMode.P1VSP2)
        #self.main_menu.add.button('', self.menu_callback_start_game, GameMode.P1VSCOM)
        main_menu.add.button('P1 vs. Com', self.show_menu, 'COM1')
    
        main_menu.add.button('COM1 vs. COM2', self.show_menu, 'COM1COM2')
        main_menu.add.button('Quit', pygame_menu.events.EXIT)
        main_menu.flag = True
        main_menu.parent = None

        self.time_out = 1
        self.iretation_times = 100
        self.c = 2
        com1menu = pygame_menu.Menu('P1 VS. COM Menu', 450, 500, theme=mytheme)
        com1menu.add.button('Start', self.menu_callback_start_game, GameMode.P1VSCOM)
        self.com_color = ChessStateEnum.BLACK
        com1menu.add.selector('COM1 color:', [('Black', ChessStateEnum.BLACK), ('White', ChessStateEnum.WHITE)], default=int(self.com_color), 
                  onchange = self.com1menu_callback_setcolor)
        com1menu.add.dropselect(
            title='COM1\'s tactic',
            items=[('1', 0),
                ('2', 1)],
                font_size=32,
                selection_option_font_size=20)
        com1menu.add.range_slider('Time out', self.time_out, (0.5, 60), 0.5,
                      value_format=lambda x: str(int(x*2)/2), onchange=self.set_timeout)
        com1menu.add.range_slider('Iterations', self.iretation_times, (10, 100), 1,
                value_format=lambda x: str(int(x)), onchange=self.set_iteration)
        com1menu.add.range_slider('c', self.c, (1, 100), 1,
            value_format=lambda x: str(int(x)), onchange=self.set_c)
        com1menu.parent = 'MAIN'
        com1menu.flag = False
        com1menu.disable()
        com1com2menu = pygame_menu.Menu('COM1 VS. COM2', 450, 400, theme=mytheme)
        com1com2menu.add.button('Start', self.menu_callback_start_game, GameMode.COM1VSCOM2)
        com1com2menu.add.dropselect(
            title='COM1\'s tactic',
            items=[('1', 0),
                ('2', 1)],
                font_size=32,
                selection_option_font_size=20)
        com1com2menu.add.dropselect(
            title='COM2\'s tactic',
            items=[('1', 0),
                ('2', 1)],
                font_size=32,
                selection_option_font_size=20)
        com1com2menu.parent = 'MAIN'
        com1com2menu.flag = False
        com1com2menu.disable()
        self.menu['MAIN'] = main_menu
        self.menu['COM1'] = com1menu
        self.menu['COM1COM2'] = com1com2menu
        self.current_menu = None
        self.com_thinking = False
        self.time_map = None
        
        self.reversi = Reversi(self.board.board_size)
        self.players = [None, None]


    def set_timeout(self, t):
        self.time_out = t
        if uct:
            uct.setparam(self.time_out, self.iretation_times, self.c)
            print('time_out: ', self.time_out)

    def set_iteration(self, i):
        self.iretation_times = i
        if uct:
            uct.setparam(self.time_out, self.iretation_times, self.c)
    def set_c(self, c):
        self.c = c
        if uct:
            uct.setparam(self.time_out, self.iretation_times, self.c)

    def show_menu(self, key):
        for m in self.menu:
            self.menu[m].flag = False
            self.menu[m].disable()
        self.current_menu = None
        if key:
            self.menu[key].flag = True
            self.menu[key].enable()
            self.current_menu = self.menu[key]

    def com1menu_callback_setcolor(self, a, color):
        self.com_color = color
        #self.menu_callback_start_game(GameMode.P1VSCOM)


    def check_show_finish(self):
        if self.reversi.check_finish(self.reversi.state):
        #if self.test_flag:
            self.reversi.is_finish = True
            self.curren_game_mode = GameMode.FINISH

    
    def update_board(self):
        self.board.show_background()
        if self.curren_game_mode == GameMode.P1VSP2 or self.curren_game_mode == GameMode.P1VSCOM or self.curren_game_mode == GameMode.FINISH or self.curren_game_mode == GameMode.COM1VSCOM2:  
            self.board.update_chess_img_to_screen(self.reversi.state.chess_status)
            self.board.update_info(self.reversi.state.scores, self.reversi.state.curren_chess_color, self.curren_game_mode, self.com_thinking, self.com_color, self.time_map)  
            self.check_show_finish()

            
        if self.curren_game_mode == GameMode.FINISH:
            self.finish_text_rect = self.board.show_finish(self.reversi.state.scores)

        if self.current_menu != None:
            pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
        elif self.curren_game_mode == GameMode.P1VSP2 or self.curren_game_mode == GameMode.P1VSCOM:
            pygame.mouse.set_cursor((0,0), self.board.black_img if self.reversi.state.curren_chess_color == ChessStateEnum.BLACK else self.board.white_img)
    def process_chess_mouse_event(self, x_pos, y_pos):
        if self.curren_game_mode == GameMode.P1VSCOM and self.reversi.state.curren_chess_color == self.com_color:
            return
        board = self.board
        x = y_pos//board.grid_size[0]
        y = x_pos//board.grid_size[1]
        if self.reversi.state.chess_status[x][y] == ChessStateEnum.VALID:
            self.reversi.state = self.reversi.do_action(self.reversi.state, (x,y))
            # if not self.reversi.check_finish(self.reversi.state):
            #     self.com_do_action()

    def com_do_action_callback(self, arg):
        self.com_thinking = False
        #self.check_show_finish()
            #self.update_board()
    def com_do_action(self):
        if self.curren_game_mode == GameMode.P1VSCOM and self.reversi.state.curren_chess_color == self.com_color:
            self.com_thinking = True
            def target():
                start_time = time.process_time()
                a, self.time_map = uct.multi_processor_search(self.reversi.state)
                print('actual time: ', time.process_time() - start_time)
                self.reversi.state = self.reversi.do_action(self.reversi.state, a.action)
            #t = threading.Thread(target=target, args=(self, ))
            t = ThreadWithCallback(target=target, args=(), callback=self.com_do_action_callback, callback_args=())
            t.start()
    def dispatch(self):
        def target():
            while True:
                if self.reversi.check_finish(self.reversi.state):
                    break
                for p in self.players:
                    if p.color == self.reversi.state.curren_chess_color:
                        s = p.do()
                        if p.strategy_enum != StrategyEnum.HUMAN: self.reversi.state = s
            print('dispatch finish')
        t = ThreadWithCallback(target=target, args=())
        t.start()

    def process_event(self, events):
        board_rect = self.board.board_rect
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if  (self.curren_game_mode == GameMode.P1VSP2 or self.curren_game_mode == GameMode.P1VSCOM)\
                    and len([m for m in self.menu if  self.menu[m].flag == True]) == 0\
                    and event.pos[0] > board_rect[0] and event.pos[0] < board_rect[0] + board_rect[2]\
                    and event.pos[1] > board_rect[1] and event.pos[1] < board_rect[1] + board_rect[3]:
                    self.process_chess_mouse_event(event.pos[0] - board_rect[0], event.pos[1] - board_rect[1])
                if self.reversi.is_finish:
                    if event.pos[0] > self.finish_text_rect.left and  event.pos[0] < self.finish_text_rect.left + self.finish_text_rect.width\
                        and event.pos[1] > self.finish_text_rect.top and  event.pos[1] < self.finish_text_rect.top + self.finish_text_rect.height:
                        # init_game()
                        self.reversi.is_finish = False
                        self.test_flag = False
                        # clear_valid_state()
                        # update_valid_state()
                        # update_board()
                        self.board.show_background()
                        #pygame.event.clear()
                        self.curren_game_mode = GameMode.MENU
                        self.show_menu('MAIN')
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.test_flag = True
                    self.update_board()
                elif event.key == pygame.K_z:
                    ...
                    #s_new = self.reversi.do_action(self.reversi.state, (3, 2))
                    
                    #print(self.reversi.state.valid_path_map)
                    #print(len(self.reversi.state.valid_path_map))
                    #a = uct.search(self.reversi.state)
                    #print(a)
                    #print(s_new.curren_chess_color)
                    print_board(self.reversi.state.chess_status)
                elif event.key == pygame.K_ESCAPE:
                    if self.curren_game_mode == GameMode.P1VSP2:
                        if self.menu['MAIN'].flag:
                            self.show_menu(None)
                        else:
                            self.show_menu('MAIN')
                    elif self.curren_game_mode == GameMode.P1VSCOM:
                        if self.menu['COM1'].flag:
                            self.show_menu(None)
                        else:
                            self.show_menu('COM1')
                    elif self.curren_game_mode == GameMode.COM1VSCOM2:
                        if self.menu['COM1COM2'].flag:
                            self.show_menu(None)
                        else:
                            self.show_menu('COM1COM2')
                    elif self.curren_game_mode == GameMode.MENU:
                        menu = [self.menu[m] for m in self.menu if self.menu[m].flag == True][0]
                        self.show_menu(menu.parent)
    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            
            self.update_board()
            for m in self.menu:
                if self.menu[m].flag and self.menu[m].is_enabled():
                    events = pygame.event.get()
                    self.menu[m].update(events)
                    try:
                        self.menu[m].draw(self.board.screen)
                    except RuntimeError as e:
                        ...
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                menu = [self.menu[m] for m in self.menu if self.menu[m].flag == True][0]
                                self.show_menu(menu.parent)
            if self.curren_game_mode != GameMode.MENU:
                events = pygame.event.get()
                self.process_event(events)
            pygame.display.update()
            clock.tick(60)
    def debug_init_state(self):
        board = [
        [0, 0, 0, 2, 0, 2, 0, 2],
        [0, 0, 0, 1, 1, 1, 1, 2],
        [0, 0, 0, 0, 0, 1, 1, 2],
        [0, 1, 1, 0, 1, 2, 1, 1],
        [0, 1, 0, 1, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 0, 0],
        [0, 2, 0, 1, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 0, 0, 0]
        ]
        def get_chess_state_from_int(x):
            if x == 0: return ChessStateEnum.BLACK
            elif x == 1: return ChessStateEnum.WHITE
            else: return ChessStateEnum.EMPTY
        for x in range(8):
            for y in range(8):
                self.reversi.state.chess_status[x][y] = get_chess_state_from_int(board[x][y])
        # self.reversi.state.chess_status[::] = ChessStateEnum.EMPTY
        # self.reversi.state.chess_status[0][0:8] = [ChessStateEnum.BLACK, ChessStateEnum.BLACK, ChessStateEnum.EMPTY]
        # self.reversi.state.chess_status[3][2:5] = ChessStateEnum.WHITE
        # self.reversi.state.chess_status[2][2:5] = ChessStateEnum.WHITE
        # self.reversi.state.chess_status[1][4] = ChessStateEnum.WHITE
        # self.reversi.state.chess_status[0][4] = ChessStateEnum.WHITE
        # self.reversi.state.chess_status[5][3] = ChessStateEnum.BLACK
        self.reversi.state.scores = {ChessStateEnum.BLACK:36, ChessStateEnum.WHITE:20}

    def menu_callback_start_game(self, mode):
        global uct
        if mode != GameMode.MENU and mode != GameMode.FINISH:
            if mode == GameMode.P1VSCOM:
                self.curren_game_mode = GameMode.P1VSCOM
                #uct = UCT(self.reversi.do_action, self.reversi.check_finish, self.com_color)
                # uct.time_out = self.time_out 
                # uct.iretation_times = self.iretation_times
                # uct.c = self.c
                self.players[0] = Player(StrategyEnum.UCT, self.com_color, self.reversi)
                self.players[1] = Player(StrategyEnum.HUMAN, self.reversi.get_reversed_color(self.com_color), self.reversi)
            elif mode == GameMode.P1VSP2:
                self.curren_game_mode = GameMode.P1VSP2
                self.players[0] = Player(StrategyEnum.HUMAN, ChessStateEnum.BLACK, self.reversi)
                self.players[1] = Player(StrategyEnum.HUMAN, ChessStateEnum.WHITE, self.reversi)
            elif mode == GameMode.COM1VSCOM2:
                self.curren_game_mode = GameMode.COM1VSCOM2
                self.players[0] = Player(StrategyEnum.UCT, ChessStateEnum.BLACK, self.reversi)
                self.players[1] = Player(StrategyEnum.GREEDY_MAXSCORE, ChessStateEnum.WHITE, self.reversi)
            #self.menu_flag = False
            self.reversi.init_game_state()
            #self.debug_init_state()
            #update_chess_img_to_screen()
            self.reversi.update_valid_state(self.reversi.state)
            self.dispatch()
            self.update_board()
            self.show_menu(None)

            #self.com_do_action()




if __name__=="__main__":
    
    game = Game()
    game.run()    





