import os

if __name__ == '__main__':
    start = 202
    for i in range(100):
        os.system('python Game.py UCT UCT 3 100 2 {} 1 100 2'.format(start + i))
        
