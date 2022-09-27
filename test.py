import os

if __name__ == '__main__':
    for i in range(10):
        print('start {}th simulation'.format(i))
        os.system('python Game.py UCT_EXPERT GREEDY_MAXSCORE 1 100 2 1 100 2')
