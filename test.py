import os

if __name__ == '__main__':
    for i in range(30):
        print('start {}th simulation'.format(i))
        os.system('python Game.py UCT UCT 1 100 2 1 100 0')
    for i in range(30):
        print('start {}th simulation'.format(i))
        os.system('python Game.py UCT UCT 1 100 2 1 100 20')
    for i in range(30):
        print('start {}th simulation'.format(i))
        os.system('python Game.py UCT UCT 1 100 2 3 100 2')
