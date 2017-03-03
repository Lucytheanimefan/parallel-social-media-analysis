import multiprocessing
import os
import ast

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

def text_from_file(file_name):
	file = open(os.path.join(APP_STATIC, file_name), "r")
	lines = file.read()
	return ast.literal_eval(lines)


if __name__ == '__main__':
	print len(text_from_file("NYT.txt"))
