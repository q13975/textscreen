from textscreen import ScreenMethod, TextWindow, TextPad
import time
import sys
import random 

'''
tw = TextWindow(20,20,10,10)

tw.clearScreen()

for i in range(1, 20):
	tw.write('test line {}'.format(i), i, 1, [33])

tw.flush()

time.sleep(1)

for i in range(5,35,5):
	tw.clearScreen()
	tw.moveWindow(i,i)
	time.sleep(1)

'''

tp = TextPad(1024, 80, 20, 20, 10, 20)

ScreenMethod.cursorOff()
ScreenMethod.echoOff()

ScreenMethod.clearScreen()
#tp.disableLineWrap()

for i in range(1,10):
	tp.write('this {}'.format(i), 0, 1, [33])
	tp.print(' is a way too long test line', 0, 0, [37])
for i in range(10,20):
	tp.write('test line {} is another long long long long example'.format(i), i, 5, [34])
for i in range(20,40):
	tp.write('line {} is for 35 example'.format(i), i, 3, [35])

tp.flush()

time.sleep(1)

tp.paginate(5)
tp.page.setCurrentPage(2)

tp.flush()

for _ in range(5):
	tp.clearWindow()
	x = random.randrange(1,10)
	y = random.randrange(1,20)
	tp.moveWindow(x,y)
	time.sleep(1)

'''
for i in range(20, 40, 5):
	tp.clearWindow()
	tp.resizeWindow(i, i)
	time.sleep(1)
'''

tp.enableFullScreen()
tp.page.setCurrentPage(1)
for _ in range(3):
	tp.clearWindow()
	x = random.randrange(1,10)
	y = random.randrange(1,10)
	tp.movePad(x,y)
	time.sleep(1)

ScreenMethod.flushInput()
