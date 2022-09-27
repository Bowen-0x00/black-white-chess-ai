import os

if __name__ == '__main__':
    for i in range(40):
        print('start {}th simulation'.format(i))
        os.system('python Game.py UCT_EXPERT UCT_EXPERT 3 100 2 1 100 2')
