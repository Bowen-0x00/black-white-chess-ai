import os

if __name__ == '__main__':
    for i in range(300):
        os.system('python Game.py GREEDY_MAXSCORE UCT 2 100 2 2 100 8')
    for i in range(300):
        os.system('python Game.py GREEDY_MINPOS UCT 2 100 2 2 100 8')    
