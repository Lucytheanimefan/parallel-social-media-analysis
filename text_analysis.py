import multiprocessing
from multiprocessing import Pool
import os
import ast,json
import monkey_learn
from monkey_learn import extract_topic
import datetime
from twitter_track import TWITTER_USERS
import time
import numpy as np

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

def text_from_file(file_name):
	file = open(os.path.join(APP_STATIC, file_name), "r")
	lines = file.read()
	return eval(lines)


def pure_text_from_file(file_name):
	file = open(os.path.join(APP_STATIC, file_name), "r")
	lines = file.read()
	return lines

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]

def get_topics():
	pool = Pool()
	unmerged= pool.map(text_from_file,[user+".txt" for user in TWITTER_USERS])
	res = [item for sublist in unmerged for item in sublist]
	#print split_list(res,len(res)/25)
	pool2 = Pool()
	res2= pool2.map(extract_topic, split_list(res,len(res)/25))
	#print res2
	return res2

def seq_topics():
	data = [text_from_file(file+'.txt') for file in TWITTER_USERS]
	res = [monkey_learn.extract_topic(dat) for dat in data]
	return res

def funSquare(num):
    return num ** 2


if __name__ == '__main__':
	start = time.time()
	print len(get_topics())
	end = time.time()
	print "Parallel: "
	print (end-start)

    

	#pool = multiprocessing.Pool()
	#results = pool.map(funSquare, range(10))
	#print(results)
