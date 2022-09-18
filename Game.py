from logging import exception
import pygame
import sys
from enum import Enum
import numpy as np
import pygame_menu


board_size = (8, 8)
grid_size = (70, 70)
font_size = 64
score_pos_black = (100, 60)
score_pos_white = (924, 60)


class ChessState(Enum):
    BLACK = 0
    WHITE = 1
    VALID = 2
    EMPTY = 3
    def __int__(self):
        return self.value

class GameMode(Enum):
    P1VSP2 = 0
    P1VSCOM = 1
    MENU = 2
    def __int__(self):
        return self.value


scores = {ChessState.BLACK:2, ChessState.WHITE:2}

chess_status = np.full(board_size, ChessState.EMPTY)
curren_chess_color = ChessState.BLACK
is_finish = False
curren_game_mode = GameMode.MENU
def init_game():
    global curren_chess_color
    global scores
    chess_status[::] = ChessState.EMPTY
    chess_status[board_size[0]//2-1][board_size[1]//2-1] = ChessState.WHITE
    chess_status[board_size[0]//2-1][board_size[1]//2] = ChessState.BLACK
    chess_status[board_size[0]//2][board_size[1]//2-1] = ChessState.BLACK
    chess_status[board_size[0]//2][board_size[1]//2] = ChessState.WHITE
    curren_chess_color = ChessState.BLACK
    scores = {ChessState.BLACK:2, ChessState.WHITE:2}

chess_state_img_map = None
screen = None
board_rect = None
finish_img = None 
black_info_text = None
black_text_rect = None
white_info_text =None
white_text_rect = None
bg_img = None
text_font = None
menu = None
def init():
    global chess_state_img_map, screen, board_rect, finish_img, black_info_text, black_text_rect\
        ,white_info_text, white_text_rect, bg_img, text_font, menu
    pygame.init()
    screen = pygame.display.set_mode([1024, 768], depth = 32)
    board_rect = (234, 143, 555, 555)
    pygame.display.set_caption("Reversi")
    bg_img = pygame.image.load("image/s_background.png").convert()
    black_img = pygame.image.load("image/s_chess_black.png").convert_alpha()
    white_img = pygame.image.load("image/s_chess_white.png").convert_alpha()
    valid_img = pygame.image.load("image/s_chess_valid.png").convert_alpha()
    finish_img = pygame.image.load("image/dialog2.png").convert_alpha()
    screen.blit(bg_img, (0, 0))
    mytheme = pygame_menu.themes.THEME_DARK.copy()
    # myimage = pygame_menu.baseimage.BaseImage(
    #     image_path='dialog2.png',
    #     drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL
    # )

    #mytheme.background_color = myimage
    mytheme.background_color=(40, 41, 35, 200)
    mytheme = mytheme.set_background_color_opacity(0.7)
    text_font = pygame.font.Font('font/云峰静龙行书.ttf', 32)
    mytheme.widget_font = text_font
    #mytheme.title = False
    #menu = pygame_menu.Menu('Welcome', 400, 300, theme=pygame_menu.themes.THEME_DARK)
    menu = pygame_menu.Menu('Menu', 400, 300, theme=mytheme)

    menu.add.button('P1 vs. P2', start_game, GameMode.P1VSP2)
    menu.add.button('P1 vs. Com', start_game, GameMode.P1VSCOM)
    menu.add.button('Quit', pygame_menu.events.EXIT)

    black_info_text = text_font.render("黑",True,(0,0,0))
    black_text_rect =black_info_text.get_rect() 
    black_text_rect.center = score_pos_black

    white_info_text = text_font.render("白",True,(0,0,0))
    white_text_rect =white_info_text.get_rect() 
    white_text_rect.center = score_pos_white


    chess_state_img_map = {ChessState.BLACK: black_img,
                        ChessState.WHITE: white_img,
                        ChessState.VALID: valid_img}

def show_background():
    screen.blit(bg_img, (0, 0))

def update_chess_img_to_screen():
    for x in range(board_size[0]):
        for y in range(board_size[1]):
            if chess_status[x][y] != ChessState.EMPTY:
                #screen.set_clip(board_rect[0]+y*70, board_rect[1]+x*70, 70, 70)
                screen.blit(chess_state_img_map[chess_status[x][y]], (board_rect[0]+y*grid_size[0], board_rect[1]+x*grid_size[1]))

blink_rect = None
def update_info():
    screen.blit(black_info_text,black_text_rect)
    text = text_font.render("{}".format(scores[ChessState.BLACK]),True,(0,0,0))
    textRect =text.get_rect() 
    textRect.center = (score_pos_black[0], score_pos_black[1] + 80)
    screen.blit(text,textRect)
    screen.blit(white_info_text,white_text_rect)
    text = text_font.render("{}".format(scores[ChessState.WHITE]),True,(0,0,0))
    textRect =text.get_rect() 
    textRect.center = (score_pos_white[0], score_pos_white[1] + 80)
    screen.blit(text,textRect)
    blink_rect = black_text_rect if curren_chess_color == ChessState.BLACK else white_text_rect
    pygame.draw.rect(screen, (50, 50, 50), blink_rect, 2)

finish_text_rect = None
test_flag = False
def check_show_finish():
    global is_finish
    global finish_text_rect
    #if len(valid_path_map) == 0 or scores[ChessState.BLACK] == 0 or scores[ChessState.WHITE] == 0:
    if test_flag:
        face = pygame.Surface((1024,768), pygame.SRCALPHA, 32)
        face.fill((200, 200, 200, 200))
        screen.blit(face, (0, 0))
        screen.blit(finish_img, (310, 220))
        text = text_font.render("{}胜".format('黑' if scores[ChessState.BLACK] >= scores[ChessState.WHITE]else '白'),True,(30,30,30))
        finish_text_rect =text.get_rect() 
        finish_text_rect.center = (510, 390)
        screen.blit(text,finish_text_rect)
        is_finish = True

def update_board():
    #change chess
    show_background()
    if curren_game_mode == GameMode.P1VSP2 or curren_game_mode == GameMode.P1VSCOM:  
        update_chess_img_to_screen()
        update_info()
        check_show_finish()

    

def get_reversed_color():
    #return int(curren_chess_color) ^ 1
    return ChessState.WHITE if curren_chess_color == ChessState.BLACK else ChessState.BLACK


def flip_chess(x, y):
    reverse_color = get_reversed_color()
    for d in valid_path_map[str(np.array([x,y]))].values():
        for p in d:
            chess_status[(*p,)] = curren_chess_color
            scores[curren_chess_color] +=1
            scores[reverse_color] -=1
            

def process_mouse(x_pos, y_pos):
    global curren_chess_color
    x = y_pos//grid_size[0]
    y = x_pos//grid_size[1]
    if chess_status[x][y] == ChessState.VALID:
        chess_status[x][y] = curren_chess_color
        scores[curren_chess_color] += 1
        flip_chess(x, y)
        curren_chess_color = get_reversed_color()

        clear_valid_state()
        update_valid_state()
        update_board()


def clear_valid_state():
    for x in range(board_size[0]):
        for y in range(board_size[1]):
            if chess_status[x][y] == ChessState.VALID:
                chess_status[x][y] = ChessState.EMPTY

def check_pos_valid(x, y):
    return x >= 0 and x < board_size[0] and y >= 0 and y < board_size[1]

valid_path_map = {}
def update_valid_state():
    reverse_color = get_reversed_color()
    directs = [np.array([0, 1]),
    np.array([0, -1]),
    np.array([1, 0]),
    np.array([-1, 0]),
    np.array([-1, -1]),
    np.array([-1, 1]),
    np.array([1, -1]),
    np.array([1, 1])]
    
    global valid_path_map
    valid_path_map.clear()
    for x in range(board_size[0]):
        for y in range(board_size[1]):
            if (x == 0 and y ==0) or (x == 0 and y ==board_size[0]) or (x == board_size[0]-1 and y ==0) or (x == board_size[0]-1 and y ==board_size[1] - 1):
                continue
            if chess_status[x][y] == reverse_color:
                if x == 4 and y == 4:
                    a = x
                for d in directs:
                    coordinate = np.array([x, y])
                    coordinate_new = coordinate + d
                    if not check_pos_valid(*(coordinate - d)) or (chess_status[(*(coordinate - d), )] != ChessState.EMPTY and chess_status[(*(coordinate - d), )] != ChessState.VALID):
                        continue
                    if str(coordinate - d) not in valid_path_map:
                        valid_path_map[str(coordinate - d)] = {}
                    if str(d) not in valid_path_map[str(coordinate - d)]:
                        valid_path_map[str(coordinate - d)][str(d)] = []   
                    valid_path_map[str(coordinate - d)][str(d)].append(coordinate)
                    while check_pos_valid(*coordinate_new):
                        if chess_status[(*coordinate_new,)] == ChessState.EMPTY or chess_status[(*coordinate_new,)] == ChessState.VALID:
                            del valid_path_map[str(coordinate - d)][str(d)]
                            break
                        if chess_status[(*coordinate_new,)] == curren_chess_color:
                            chess_status[(*(coordinate - d), )] = ChessState.VALID
                            break
                        valid_path_map[str(coordinate - d)][str(d)].append(coordinate_new.tolist())
                        coordinate_new += d
    for k in list(valid_path_map):
        if valid_path_map[k] == {}:
            del valid_path_map[k]

def process_event(events):
    global is_finish
    global test_flag
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP:
            if not is_finish and event.pos[0] > board_rect[0] and event.pos[0] < board_rect[0] + board_rect[2]\
                and event.pos[1] > board_rect[1] and event.pos[1] < board_rect[1] + board_rect[3]:
                process_mouse(event.pos[0] - board_rect[0], event.pos[1] - board_rect[1])
            if is_finish:
                if event.pos[0] > finish_text_rect.left and  event.pos[0] < finish_text_rect.left + finish_text_rect.width\
                    and event.pos[1] > finish_text_rect.top and  event.pos[1] < finish_text_rect.top + finish_text_rect.height:
                    # init_game()
                    is_finish = False
                    test_flag = False
                    # clear_valid_state()
                    # update_valid_state()
                    # update_board()
                    show_background()
                    #pygame.event.clear()
                    return_menu()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                test_flag = True
                update_board()

menu_flag = True
def return_menu():
    global menu_flag, curren_game_mode
    curren_game_mode = GameMode.MENU
    menu_flag = True
    menu.enable()

def run():
    global count
    clock = pygame.time.Clock()
    while True:
        events = pygame.event.get()
        update_board()
        if menu_flag and menu.is_enabled():
            menu.update(events)
            try:
                menu.draw(screen)
            except RuntimeError as e:
                ...
        process_event(events)
        pygame.display.update()
        clock.tick(20)


def start_game(mode):
    global menu_flag, curren_game_mode
    if mode == GameMode.P1VSCOM:
        ...
    elif mode == GameMode.P1VSP2:
        menu_flag = False
        curren_game_mode = GameMode.P1VSP2
        init_game()
        update_chess_img_to_screen()
        update_valid_state()
        update_board()
        menu.close()
        menu.disable()
        
        
init()
run()





