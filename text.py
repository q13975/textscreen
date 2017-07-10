from textscreen import ScreenMethod, TextScreen
import time

class myScreen(TextScreen):
	def __init__(self):
		TextScreen.__init__(self)
		self.initScreen()

	def initScreen(self):
		ScreenMethod.echoOff()
		ScreenMethod.cursorOff()
		ScreenMethod.clearScreen()


myscr = myScreen()
myscr.setDisplayDepth(50)

for i in range(0, int(myscr.rows/2)):
	myscr.print('this is a test line {}'.format(i), [33])
for i in range(int(myscr.rows/2), myscr.rows):
	myscr.print('this is a way too long test line {}'.format(i))

myscr.flush()

while True:
	key = ScreenMethod.getKey()
	if key == 0x1b or key == ord('q') or key == ord('Q'):
		break
