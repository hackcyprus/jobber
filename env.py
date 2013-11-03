"""
env.py
~~~~~~

Sets up the path to include the `jobber` directory.

"""
import sys, os

def path_setup():
    path = os.path.abspath(os.path.dirname(__file__))
    src = '/'
    for token in path.split('/'):
        src += token + '/'
        if token == 'jobber': break
    sys.path.insert(0, src)