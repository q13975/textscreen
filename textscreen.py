''' Full screen rich text manipulation on Linux terminal
'''
import os, sys, syslog, termios, struct, math

class ReadStream(object):
	''' Set stream(stdin) for read in nocanonical mode and get key input 
	without waiting for line feed

	Example:
	with ReadStream(6, 1, 0) as kb:
		while True:
			key = kb.read()
			r = struct.unpack('B' * len(key), key)
			if len(key) == 1 and r[0] = 27:		#ESCAPE
				break
			if key == ReadStream.ESCAPE:		#ESCAPE
				break
	'''

	# key sequence(byte string), raw data of a key stroke
	KEY_ESCAPE = b'\x1b'
	KEY_TABLE = b'\t'
	KEY_ENTER = b'\n'
	KEY_BACKSPACE = b'\x7f'
	KEY_UP = b'\x1b[A'
	KEY_DOWN = b'\x1b[B'
	KEY_RIGHT = b'\x1b[C'
	KEY_LEFT = b'\x1b[D'
	KEY_HOME = b'\x1b[H'
	KEY_END = b'\x1b[F'
	KEY_INSERT = b'\x1b[2~'
	KEY_DELETE = b'\x1b[3~'
	KEY_PAGEUP = b'\x1b[5~'
	KEY_PAGEDOWN = b'\x1b[6~'
	KEY_F1 = b'\x1bOP'
	KEY_F2 = b'\x1bOQ'
	KEY_F3 = b'\x1bOR'
	KEY_F4 = b'\x1bOS'
	KEY_F5 = b'\x1b[15~'
	KEY_F6 = b'\x1b[17~'
	KEY_F7 = b'\x1b[18~'
	KEY_F8 = b'\x1b[19~'
	KEY_F9 = b'\x1b[20~'
	KEY_F10 = b'\x1b[21~'
	KEY_F11 = b'\x1b[23~'
	KEY_F12 = b'\x1b[24~'
	KEY_ALT_ESCAPE = b'\x1b\x1b'
	KEY_ALT_UP = b'\x1b[1;3A'
	KEY_ALT_DOWN = b'\x1b[1;3B'
	KEY_ALT_RIGHT = b'\x1b[1;3C'
	KEY_ALT_LEFT = b'\x1b[1;3D'
	KEY_ALT_HOME = b'\x1b[1;3H'
	KEY_ALT_END = b'\x1b[1;3F'
	KEY_ALT_INSERT = b'\x1b[2;3~'
	KEY_ALT_DELETE = b'\x1b[3;3~'
	KEY_ALT_PAGEUP = b'\x1b[5;3~'
	KEY_ALT_PAGEDOWN = b'\x1b[6;3~'
	KEY_ALT_F1 = b'\x1b[1;3P'
	KEY_ALT_F2 = b'\x1b[1;3Q'
	KEY_ALT_F3 = b'\x1b[1;3R'
	KEY_ALT_F4 = b'\x1b[1;3S'
	KEY_CTRL_UP = b'\x1b[1;5A'
	KEY_CTRL_DOWN = b'\x1b[1;5B'
	KEY_CTRL_RIGHT = b'\x1b[1;5C'
	KEY_CTRL_LEFT = b'\x1b[1;5D'
	KEY_CTRL_HOME = b'\x1b[1;5H'
	KEY_CTRL_END = b'\x1b[1;5F'
	KEY_CTRL_DELETE = b'\x1b[3;5~'
	KEY_CTRL_PAGEUP = b'\x1b[5;5~'
	KEY_CTRL_PAGEDOWN = b'\x1b[6;5~'
	KEY_CTRL_F1 = b'\x1b[1;5P'
	KEY_CTRL_F2 = b'\x1b[1;5Q'
	KEY_CTRL_F3 = b'\x1b[1;5R'
	KEY_CTRL_F4 = b'\x1b[1;5S'
	KEY_SHIFT_UP = b'\x1b[1;2A'
	KEY_SHIFT_DOWN = b'\x1b[1;2B'
	KEY_SHIFT_RIGHT = b'\x1b[1;2C'
	KEY_SHIFT_LEFT = b'\x1b[1;2D'
	KEY_SHIFT_DELETE = b'\x1b[3;2~'
	KEY_SHIFT_F1 = b'\x1b[1;2P'
	KEY_SHIFT_F2 = b'\x1b[1;2Q'
	KEY_SHIFT_F3 = b'\x1b[1;2R'
	KEY_SHIFT_F4 = b'\x1b[1;2S'

	def __init__(self, read_size=6, vmin=1, vtime=0, stream=None):
		''' set stream(stdin) for read in noncanonical mode, no echo, 
		Suggested:
			- VMIN = 1, VTIME = 0	for getch in blocking mode
			- VMIN = 0, VTIME = 1	for getch in nonblocking mode
		Default: option 1 of suggested
			read_size = 6 is good for read() keyin 
			stream = sys.stdin 
		Return: key sequence, for example b'\x1bOP' when F1 is pressed
		- In noncanonical mode, input is available immediately (without
		the user having to type a line-delimiter character), no input
		processing is performed, and line editing is disabled. 
		- VTIME tenths of a second elapses between bytes
		- VMIN the minimum number of characters to be received
			- VMIN = 0 and VTIME = 0 (polling read)
				if data is available, read returns immediately,
				with the lesser of the number of bytes 
				available, or the number of bytes requested. If
				no data is available, returns 0
			- VMIN > 0 and VTIME = 0 (blocking read)
				read blocks until MIN bytes are available, and
				returns up to the number of bytes requested
			- VMIN = 0 and VTIME > 0 (read with timeout)
				VTIME specifies the limit for a timer in tenths
				of a second. 
				The timer is started when read is called. read
				returns either when at least one byte of data 
				is available, or when the timer expires, read 
				returns 0. If data is already available at the 
				time of the call to read, the call behaves as 
				though the data was received immediately after 
				the call. 
			- VMIN > 0 and VTIME > 0 (read with interbyte timeout)
				VTIME specifies the limit for a timer in tenths
				of a second. 
				Once an initial byte of input becomes available,
				the timer is restarted after each further byte
				is received. read returns when any of the 
				following conditions is met:
				- VMIN bytes have been received
				- The interbyte timer expires
				- The number of bytes requested by read has 
				  been received. (Some may not support this)
		'''
		self.read_size = read_size
		self.stream = stream if isinstance(stream, int) else (stream.fileno() if hasattr(stream, 'fileno') else sys.stdin.fileno())
		self.saved = termios.tcgetattr(self.stream)
		self.attrs = termios.tcgetattr(self.stream)
		self.attrs[3] = self.attrs[3] & ~termios.ICANON & ~termios.ECHO
		self.attrs[6][termios.VMIN] = vmin	
		self.attrs[6][termios.VTIME] = vtime
		termios.tcsetattr(self.stream, termios.TCSANOW, self.attrs)

	def __enter__(self):
		return(self)

	def __exit__(self, type, value, traceback):
		termios.tcsetattr(self.stream, termios.TCSAFLUSH, self.saved)

	def read(self):
		''' return a byte string, ie. b'\x1b[A' when UP key is pressed
		'''
		key = os.read(self.stream, self.read_size)
		return(key)

class Pagination(object):
	def __init__(self, items_per_page, total_items=0):
		self._items_per_page = items_per_page if items_per_page and items_per_page > 0 else 1
		self._total_items = total_items if total_items and total_items > 0 else 0
		self._current_page = 1
		self._total_pages = math.ceil(self._total_items / self._items_per_page)

	def setCurrentPage(self, page):
		''' set current page to 'page'
		'''
		if page and page > 0 and (not self._total_items or page <= self._total_pages):
			self._current_page = page
			return(True)
		else:
			return(False)	

	def setItemsPerPage(self, items_per_page, reset_current_page=True):
		''' change items_per_page
		'''
		if not items_per_page or items_per_page < 1:
			return(False)
		self._items_per_page = items_per_page
		self._total_pages = math.ceil(self._total_items / self._items_per_page)
		self._current_page = 1 if reset_current_page or self._current_page < self._total_pages else self._current_page
		return(True)

	def setTotalItems(self, total_items, reset_current_page=False):
		''' change total_items
		'''
		if not total_items or total_items < 1:
			return(False)
		self._total_items = total_items
		self._total_pages = math.ceil(self._total_items / self._items_per_page)
		self._current_page = 1 if reset_current_page or self._current_page < self._total_pages else self._current_page
		return(True)

	def totalItems(self):
		return(self._total_items)

	def itemsPerPage(self):
		return(self._items_per_page)

	def totalPages(self):
		return(self._total_pages)

	def currentPage(self):
		''' get current page number
		'''
		return(self._current_page)

	def nextPage(self):
		''' get next page number
		Return: current page + 1 or 0 if there is no next page
		Attenttion: always return currentPage + 1 if total_items == 0
		'''
		return(self._current_page + 1 if not self._total_items or self._current_page < self._total_pages else 0)

	def previousPage(self):
		''' Get previous page number
		Return: self._current_page - 1 or 0 if no previous page
		'''
		return(self._currentPage - 1)

	def firstPage(self):
		''' Return the first page number, now always 1
		'''
		return(1)

	def lastPage(self):
		''' Calculate last page 
		Attention: if total_items == 0, self._total_pages = 0 
		'''
		return(self._total_pages)

	def pageItems(self):
		''' get a list of [begin_item_number, end_item_number]
		'''
		begin = (self._current_page - 1) * self._items_per_page + 1
		end = (begin + self._items_per_page - 1) if self._current_page < self._total_page or not self._total_items else self._total_items 
		return([begin, end])

class ScreenMethod(object):
	''' Full screen and rich text (color + position) manipulation
	'''

	''' Query cursor position
	'''
	QUERY_CURSOR_POSITION = '\x1b[6n'	# Report <ESC>[{ROW};{COLUMN}R

	''' Terminal Setup
	'''
	RESET_DEVICE = '\x1bc'
	ENABLE_LINE_WRAP = '\x1b[7h'
	DISABLE_LINE_WRAP = '\x1b[7l'
	DEFAULT_FONT = '\x1b('
	ALTERNATE_FONT = '\x1b)'
	CURSOR_HOME = '\x1b[H'
	CURSOR_UP = '\x1b[A'
	CURSOR_DOWN = '\x1b[B'
	CURSOR_FORWARD = '\x1b[C'		
	CURSOR_BACKWARD = '\x1b[D'
	SAVE_CURSOR = '\x1b[s'
	UNSAVE_CURSOR = '\x1b[u'
	SAVE_CURSOR_ATTRS = '\x1b7'
	RESTORE_CURSOR_ATTRS = '\x1b8'
	SCROLL_SCREEN = '\x1b[r'
	SCROLL_DOWN = '\x1bD'
	SCROLL_UP = '\x1bM'
	SET_TAB = '\x1bH'
	CLEAR_TAB = '\x1b[g'
	CLEAR_ALL_TABS = '\x1b[3g'
	ERASE_END_OF_LINE = '\x1b[K'
	ERASE_START_OF_LINE = '\x1b[1K'
	ERASE_LINE = '\x1b[2K'
	ERASE_DOWN = '\x1b[J'
	ERASE_UP = '\x1b[1J'
	ERASE_SCREEN = '\x1b[2J'
	PRINT_SCREEN = '\x1b[i'
	PRINT_LINE = '\x1b[1i'
	STOP_PRINT_LOG = '\x1b[4i'
	START_PRINT_LOG = '\x1b[5i'

	''' cursor and screen
	'''
	CURSOR_ON = '\x1b[?25h'
	CURSOR_OFF = '\x1b[?25l'
	CURSOR_BLINK_ON = '\x1b[?12h'
	CURSOR_BLINK_OFF = '\x1b[?12l'
	SAVE_SCREEN = '\x1b[?47h'
	RESTORE_SCREEN = '\x1b[?47l'
	
	''' positional variables are expected
	for example:
		var_CURSOR_AT.format(r,c)
	which will move the cursor to postion (r,c)
	'''
	var_CURSOR_HOME = '\x1b[{};{}H'		# (row, column) expected
	var_CURSOR_UP = '\x1b[{}A'		# (row) expected
	var_CURSOR_DOWN = '\x1b[{}B' 		# (row) expected
	var_CURSOR_FORWARD = '\x1b[{}C' 	# (column) expected
	var_CURSOR_BACKWARD = '\x1b[{}D' 	# (column) expected
	var_CURSOR_AT = '\x1b[{};{}f' 		# (row, column) expected
	var_SCROLL_SCREEN = '\x1b[{};{}r' 	# (row, column) expected
	var_SET_ATTRS = '\x1b[{}m'		# expects color(list(attrs))

	''' Display Attributes
		<ESC>[{attr1};...;{attrn}m
	'''
	RESET_ATTRS = '\x1b[0m'		#reset attributes to default

	'''
	The following lists standard attributes:
		0 	Reset all attributes
		1	Bright
		2	Dim
		4	Undersore
		5	Blink
		7	Reverse
		8	Hidden

			Foreground Colors
		30	Black
		31	Red
		32	Green
		33	Yellow
		34	Blue
		35	Magenta
		36	Cyan
		37	White

			Background Colors
		40	Black
		41	Red
		42	Green
		43	Yellow
		44	Blue
		45	Magenta
		46	Cyan
		47	White

	The following may not at all terminals
		39	Default text color (foreground
		49	Default background color
	'''
	ATTR_RESET = 0
	ATTR_BRIGHT = 1
	ATTR_DIM = 2
	ATTR_UNDERSCORE = 4
	ATTR_BLINK = 5
	ATTR_REVERSE = 7
	ATTR_HIDDEN = 8
	FG_BLACK = 30
	FG_RED = 31
	FG_GREEN = 32
	FG_YELLOW = 33
	FG_BLUE = 34
	FG_MAGENTA = 35
	FG_CYAN = 36
	FG_WHITE = 37
	FG_RESET = 39
	BG_BLACK = 40
	BG_RED = 41
	BG_GREEN = 42
	BG_YELLOW = 43
	BG_BLUE = 44
	BG_MAGENTA = 45
	BG_CYAN = 46
	BG_WHITE = 47
	BG_RESET = 49
	
	@staticmethod
	def getSize():
		''' get screen size, refer to 'stty size'
			return: (row, column)

		Example:
			row, column = ScreenMethod.getSize()
		'''
		'''
		# Another approach --- use fcntl.ioctl method
		import fcntl
		rc = struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234'))
		return([int(rc[0]), int(rc[1])])
		'''
		rc = os.get_terminal_size(sys.stdout.fileno())
		return(rc.lines, rc.columns)

	@staticmethod
	def cursorOn():
		''' show cursor refer to 'setterm -cursor on'
		'''
		sys.stdout.write(ScreenMethod.CURSOR_ON)
		sys.stdout.flush()

	@staticmethod
	def cursorOff():
		''' hide cursor refer to 'setterm -cursor off'
		'''
		sys.stdout.write(ScreenMethod.CURSOR_OFF)
		sys.stdout.flush()

	@staticmethod
	def saveScreen():
		''' save current screen content for restoreScreen
		'''
		sys.stdout.write(ScreenMethod.SAVE_SCREEN)
		sys.stdout.flush()

	@staticmethod
	def restoreScreen():
		''' restore screen to the last saved one by saveScreen
		'''
		sys.stdout.write(ScreenMethod.RESTORE_SCREEN)
		sys.stdout.flush()

	@staticmethod
	def getTermAttrs():
		''' Get terminal output attributes,  refer to 'stty -g'
		'''
		return(termios.tcgetattr(sys.stdout.fileno()))

	@staticmethod
	def setTermAttrs(attrs):
		''' Set terminal output attributes
		'''
		if attrs:
			termios.tcsetattr(sys.stdout.fileno(), termios.TCSANOW, attrs)

	@staticmethod
	def echoOn():
		''' Enable echo when key in, refer to 'stty echo'
		'''
		attrs = ScreenMethod.getTermAttrs()
		attrs[3] |= termios.ECHO
		ScreenMethod.setTermAttrs(attrs)

	@staticmethod
	def echoOff():
		''' disable echo when key in, refer to 'stty -echo'
		'''
		attrs = ScreenMethod.getTermAttrs()
		attrs[3] &= ~termios.ECHO
		ScreenMethod.setTermAttrs(attrs)

	@staticmethod
	def flushInput():
		''' clear input buffer, wipe out all keyin's 
		'''
		termios.tcflush(sys.stdin, termios.TCIFLUSH)

	@staticmethod
	def clearScreen():
		''' clear screen
		'''
		sys.stdout.write(ScreenMethod.ERASE_SCREEN + ScreenMethod.CURSOR_HOME)
		sys.stdout.flush()

	@staticmethod
	def resetDevice():
		''' Reset all terminal settings to default
		'''
		sys.stdout.write(ScreenMethod.RESET_DEVICE)
		sys.stdout.flush()

	@staticmethod
	def enableLineWrap():
		''' Text wraps to next line if longer than the length of the display area
		'''
		sys.stdout.write(ScreenMethod.ENABLE_LINE_WRAP)
		sys.stdout.flush()

	@staticmethod
	def disableLineWrap():
		''' Disable line wrapping
		'''
		sys.stdout.write(ScreenMethod.DISABLE_LINE_WRAP)
		sys.stdout.flush()

	@staticmethod
	def setDefaultFont():
		''' Set the default font
		'''
		sys.stdout.write(ScreenMethod.DEFAULT_FONT)
		sys.stdout.flush()

	@staticmethod
	def setAlternateFont():
		''' Set the alternate font
		'''
		sys.stdout.write(ScreenMethod.ALTERNATE_FONT)
		sys.stdout.flush()

	@staticmethod
	def cursorHome(row=None, column=None):
		''' Set the cursor position where subsequent text will begin. 
		'''
		sys.stdout.write(ScreenMethod.var_CURSOR_HOME.format(row, column) if row and column else ScreenMethod.CURSOR_HOME)
		sys.stdout.flush()

	@staticmethod
	def cursorUp(count=1):
		''' Move the cursor up by count rows
		'''
		sys.stdout.write(ScreenMethod.var_CURSOR_UP.format(count))
		sys.stdout.flush()
		
	@staticmethod
	def cursorDown(count=1):
		''' Move the cursor down by count rows
		'''
		sys.stdout.write(ScreenMethod.var_CURSOR_DOWN.format(count))
		sys.stdout.flush()
		
	@staticmethod
	def cursorForward(count=1):
		''' Move the cursor forward by count columns
		'''
		sys.stdout.write(ScreenMethod.var_CURSOR_FORWARD.format(count))
		sys.stdout.flush()
		
	@staticmethod
	def cursorBackward(count=1):
		''' Move the cursor backward by count columns
		'''
		sys.stdout.write(ScreenMethod.var_CURSOR_BACKWARD.format(count))
		sys.stdout.flush()
		
	@staticmethod
	def moveCursor(row, column):
		''' Move cursor 
		'''
		if row and column:
			sys.stdout.write(ScreenMethod.var_CURSOR_AT.format(row, column))
			sys.stdout.flush()

	@staticmethod
	def saveCursor():
		''' Save current cursor position
		'''
		sys.stdout.write(ScreenMethod.SAVE_CURSOR)
		sys.stdout.flush()

	@staticmethod
	def restoreCursor():
		''' Restores cursor position after a save cursor
		'''
		sys.stdout.write(ScreenMethod.UNSAVE_CURSOR)
		sys.stdout.flush()

	@staticmethod
	def saveCursorAttrs():
		''' Save current cursor position and attributes
		'''
		sys.stdout.write(ScreenMethod.SAVE_CURSOR_ATTRS)
		sys.stdout.flush()

	@staticmethod
	def restoreCursorAttrs():
		''' Restores cursor position and attributes after a save cursor
		'''
		sys.stdout.write(ScreenMethod.RESTORE_CURSOR_ATTRS)
		sys.stdout.flush()

	@staticmethod
	def scrollScreen(row_start=None, row_end=None):
		''' Enable scrolling from row {start} to row {end}
		'''
		if row_start and row_end:
			sys.stdout.write(ScreenMethod.var_SCROLL_SCREEN.format(row_start, row_end))
		else:
			sys.stdout.write(ScreenMethod.SCROLL_SCREEN)
		sys.stdout.flush()

	@staticmethod
	def scrollDown():
		''' Scroll display down one line
		'''
		sys.stdout.write(ScreenMethod.SCROLL_DOWN)
		sys.stdout.flush()

	@staticmethod
	def scrollUp():
		''' Scroll display up one line
		'''
		sys.stdout.write(ScreenMethod.SCROLL_UP)
		sys.stdout.flush()

	@staticmethod
	def setTab():
		''' Sets a tab at the current position
		'''
		sys.stdout.write(ScreenMethod.SET_TAB)
		sys.stdout.flush()

	@staticmethod
	def clearTab():
		''' Clears tab at the current position
		'''
		sys.stdout.write(ScreenMethod.CLEAR_TAB)
		sys.stdout.flush()

	@staticmethod
	def clearAllTabs():
		''' Clears all tabs
		'''
		sys.stdout.write(ScreenMethod.CLEAR_ALL_TABS)
		sys.stdout.flush()

	@staticmethod
	def eraseEndOfLine():
		''' Erases from the current cursor position to the end of the current line
		'''
		sys.stdout.write(ScreenMethod.ERASE_END_OF_LINE)
		sys.stdout.flush()

	@staticmethod
	def eraseStartOfLine():
		''' Erases from the current cursor position to the start of the current line
		'''
		sys.stdout.write(ScreenMethod.START_END_OF_LINE)
		sys.stdout.flush()

	@staticmethod
	def eraseLine():
		''' Erases from the current line
		'''
		sys.stdout.write(ScreenMethod.ERASE_LINE)
		sys.stdout.flush()

	@staticmethod
	def eraseDown():
		''' Erase the screen from the current line down to the bottom of the screen
		'''
		sys.stdout.write(ScreenMethod.ERASE_DOWN)
		sys.stdout.flush()

	@staticmethod
	def eraseUp():
		''' Erase the screen from the current line up to the top of the screen
		'''
		sys.stdout.write(ScreenMethod.ERASE_UP)
		sys.stdout.flush()

	@staticmethod
	def eraseScreen():
		''' Erase the screen with background color and moves the cursor to home
		'''
		sys.stdout.write(ScreenMethod.ERASE_SCREEN)
		sys.stdout.flush()

	@staticmethod
	def write(text):
		''' Write text to stdout, need to flush to force print
		'''
		sys.stdout.write(text)

	@staticmethod
	def print(text):
		''' Write text with line feed, need to flush to force print
		'''
		sys.stdout.write(text + '\n')
	
	@staticmethod
	def flush():
		''' flush the stdout buffer 
		'''
		sys.stdout.flush()

	@staticmethod
	def deviceCode():
		''' 	Get device code

		Query Device Code	<ESC>[c
		Report Device Code	<ESC>[?{code};{code}c

			'\x1b[?1;0c' 	VT101
			'\x1b[?1;2c' 	VT100	with AVO

			I got '\x1b[?62;c'

			ACC 	type
			62	vt220
			63	vt320

		Example:
			code = ScreenMethod.deviceCode()
		Return: device code string or '' if fails
		'''
		ret = ''
		with ReadStream(20, 4, 0) as stream:
			for _ in range(3):	# try 3 times
				termios.tcflush(sys.stdin, termios.TCIFLUSH)
				os.write(sys.stdout.fileno(), b'\x1b[c')
				key = stream.read()
				if key[:3] == b'\x1b[?' and key[-1:] == b'c':
					ret = key[3:-1].decode()
					break
		return(ret)
		
	@staticmethod
	def deviceStatus():
		'''	Get device status

		Query Device Status:
			<ESC>[5n
		Report:
			<ESC>[0n	Device Ok
			<ESC>[1n 	Device busy, try later
			<ESC>[2n 	Device busy, will send DSR when ready
			<ESC>[3n 	Device Failure	
			<ESC>[4n 	Device Failure, will send DSR when ready

		Example:
			status = ScreenMethod.deviceStatus()
		Return:	
			status code or '' if it fails
		'''
		ret = ''
		with ReadStream(6, 4, 0) as stream:
			for _ in range(3):	# try 3 times
				termios.tcflush(sys.stdin, termios.TCIFLUSH)
				os.write(sys.stdout.fileno(), b'\x1b[5n')
				key = stream.read()	
				if key[:2] == b'\x1b[' and key[-1:] == b'n':
					ret = key[2:-1].decode()
					break
		return(ret)
		
	@staticmethod
	def cursorPosition():
		''' Get current cursor position on screen

		Query Cursor Position	<ESC>[6n
		Report Cursor Position	<ESC>[{ROW};{COLUMN}R
		
		Return: [row, column] or [None, None] if fails
		Example: row, column = ScreenMethod.cursorPosition()
		'''
		ret = [None, None]
		with ReadStream(10, 6, 0) as stream:
			for _ in range(3):	# try 3 times
				termios.tcflush(sys.stdin, termios.TCIFLUSH)
				os.write(sys.stdout.fileno(), b'\x1b[6n')
				key = stream.read()	# expects b'\x1b[xx;xxR'
				if key[:2] == b'\x1b[' and key[-1:] == b'R' and ';' in key.decode():
					ret = map(int, key[2:-1].decode().split(';'))
					break
		return(ret)

	@staticmethod
	def getKey(blocking=True):
		''' get key without waiting for line feed
		Input:
			It will run in blocking mode if 'blocking' is True, or
			it will run in non-blocking mode if otherwise
		Return: an integer 
		-	for ordinary character, ie 'a', it will return ord('a')
		-	key stroke like KEY_F1(b'\x1bOP'), it will return as
			(((0x1b << 8) + ord('O')) << 8) + ord('P')

		Example:
			key = ScreenMethod.getKey()
			if key == 0x1b:
				print('ESCAPE is pressed')
		'''
		mode = [6, 1, 0] if blocking else [6, 0, 1]
		with ReadStream(*mode) as kb:
			key = kb.read()
			n = len(key)
			r = struct.unpack('B' * n, key)
			x = 0
			for i in range(n):
				x <<= 8
				x += int(r[i])
		return(x)

class RichText(object):
	''' a text structure to hold the raw text and its attributes and
	its relative position 
	Since we keep attrs and position seperately, we can manipulate and 
	change the postion on the fly.

	Example:
		text = str(RichText('test in color', [33], 2, 5))
	or
		text = RichText('test in color', [33], 2, 5).pack()
	or 
		rt = RichText('test in color', [33])
		text = rt.pack(2, 5)
	All will give you the same result
	'''
	def __init__(self, text, attrs=[], row=0, column=0, reserv_setting=True):
		self.text = text
		self.attrs = attrs
		self.row = row
		self.column = column	
		self.reserv_setting = reserv_setting	# preserv setting if set
		''' Define attributes for use in _factory_format
			A rich text will be formatted as:
			{ self._save_setting }{ self._attrs }{ self._position }{ self._text }{ self._restore_setting }
		'''	
		self._save_setting = ''
		self._attrs = ''
		self._position = ''
		self._text = '{}'
		self._restore_setting = ''
		# define a string format for variable (row, column), refer to
		# _factory_format
		self._fmt = ''

	def _factory_attrs(self, attrs=None):
		''' Factory text attrs
		Return:	'' if attrs is empty
		'''
		attrs = self.attrs if attrs == None else attrs
		self._attrs = ScreenMethod.var_SET_ATTRS.format(';'.join(str(x) for x in attrs)) if attrs else ''

	def _factory_position(self, row=None, column=None, text=None):
		''' Factory text position
		Return: '' if text or row or column is empty
		'''
		row = self.row if row == None else row
		column = self.column if column == None else column
		text = self.text if text == None else text
		self._position = ScreenMethod.var_CURSOR_AT if row and column and text else ''

	def _factory_reserv_setting(self):
		''' Factory self._save_setting
		Return: '' if not self.reserv_setting or (not self._attrs and 
		not self._position)
		Dependency: make sure to run it after self._factory_attrs and 
		self._factory_position
		'''
		self._save_setting = ScreenMethod.SAVE_CURSOR_ATTRS if self.reserv_setting and self._position else ''
		self._restore_setting = '' if not self.reserv_setting else (ScreenMethod.RESTORE_CURSOR_ATTRS if self._save_setting else (ScreenMethod.RESET_ATTRS if self._attrs else ''))

	def _factory_format(self, row=None, column=None, text=None, attrs=None):
		''' Factory string format using '{}{}{}{}{}'.format(
				SAVE_CURSOR_ATTRS,
				TEXT_ATTRS,
				VAR_CURSOR_AT,
				text,
				RESTORE_CURSOR_ATTRS
			)
		where:
		-	var_CURSOR_AT('\x1b[{};{}f') expects (row, column)
		-	fill {text} with '{}' and expects real 'text'
		Output:
		- 	save the result into self._fmt, which is a string 
			format, which expects (row, column, text):
				self._fmt.format(row, column, text)	
		-	call self.out(row, column) to get the ultimate richText
		'''
		self._factory_attrs(attrs)
		self._factory_position(row, column, text)
		self._factory_reserv_setting()
		self._fmt = '{}{}{}{}{}'.format(
			self._save_setting, 
			self._attrs,
			self._position,
			'{}',
			self._restore_setting
		)

	def __str__(self):
		''' Generate rich text at preset position and attrs
		    str(RichText(...)) could produce what you expect
		'''
		return(self.pack())

	def pack(self, row=None, column=None, text=None, attrs=None):
		''' Generate rich text for (text, attrs, row, column) 
		-	Pack it at new position (row, column) at any time
		-	Run self._factory_format first so that new attrs 
			can also be used
		-	Pack it with new text with the same or different
			attrs and/or position
		Example: RichText(text, attrs, row0, column0).pack(row1, column1)
		which will generate a rich text in new position (row1, column1) instead
		and move the text on screen 
		'''
		self._factory_format(row, column, text, attrs)
		row = self.row if row == None else row
		column = self.column if column == None else column
		text = self.text if text == None else text
		return(self._fmt.format(row, column, text) if row and column else self._fmt.format(text))

class TextScreen(object):
	''' A text screen which supports line by line print, no positional 
	text is supported, please use TextPad or TextWindow if otherwise

	Example:
		ts = TextScreen()
		ScreenMethod.echoOff()	# do it after TextScreen()
		ScreenMethod.cursorOff()
		ts.print("line 1 in color", [33])
		ts.print("line 2 in color", [37])
		...
		ts.flush()
	'''

	TEXT_ROWS = 8192		# rows to display

	def __init__(self):
		self.rows = 0		# screen size
		self.columns = 0
		self.buffer = {}	# { row : coloredText, ... }
		self.currentRow = 1	# current row for input
		self.beginRow = 1	# where to start display, pad begins
		self.depth = self.TEXT_ROWS	# rows to display, pad depth
		self.setSize()			
		self.newScreen()
		self._savedTerm = ScreenMethod.getTermAttrs()
		self._savedCursor = ScreenMethod.cursorPosition()
		ScreenMethod.saveScreen()

	def __del__(self):
		ScreenMethod.cursorOn()			# restore cursor 
		ScreenMethod.setTermAttrs(self._savedTerm)	# restore term
		ScreenMethod.restoreScreen()
		ScreenMethod.moveCursor(*self._savedCursor)

	def setSize(self):
		self.rows, self.columns = ScreenMethod.getSize()

	def resized(self, update=True):
		rows, columns = ScreenMethod.getSize()
		if rows != self.rows or columns != self.columns:
			if update:
				self.rows = rows
				self.columns = columns
			return(True)
		else:	
			return(False)

	def newScreen(self):
		''' clear screen buffer
		'''
		self.buffer = {}
		self.beginRow = 1
		self.currentRow = 1

	def isEmpty(self):
		''' check if buffer is empty
		'''
		return(False if self.buffer else True)

	def setStartRow(self, row=None):
		''' Start from which row to display
		'''
		self.beginRow = row if row and row > 0 else 1

	def setDisplayDepth(self, depth=None):
		''' Set how many rows to display 
		'''
		self.depth = depth if depth and depth > 0 else self.TEXT_ROWS

	def newLine(self):
		''' Set self.currentRow to next line
		'''
		if self.currentRow not in self.buffer:
			self.buffer[self.currentRow] = ''
		self.currentRow += 1

	def write(self, text, attrs=None, reserv_setting=True):
		''' Write text to screen buffer, either plain or colored text
		'''
		rt = str(RichText(text, attrs, 0, 0, reserv_setting))
		if self.currentRow in self.buffer:
			self.buffer[self.currentRow] += rt
		else:
			self.buffer[self.currentRow] = rt

	def print(self, text, attrs=None, reserv_setting=True):
		''' Write text to screen buffer and new line
		'''
		self.write(text, attrs, reserv_setting)
		self.newLine()

	def flush(self):
		''' Clear the screen and print content (self.buffer) to screen
		'''
		ScreenMethod.clearScreen()
		# make sure it won't go beyond display area or screen
		lastRow = self.beginRow + min(self.depth, self.rows) - 1	
		for l in sorted(filter(lambda x: x >= self.beginRow and x <= lastRow, self.buffer.keys())):
			sys.stdout.write(self.buffer[l] + ('\n' if l < lastRow else ''))
		sys.stdout.flush()
			
class TextWindow(object):
	''' A text window, which reflects a physical area of a screen, which 
	can't go beyond the screen from any corner. 
	--- Line auto wrap is disabled at all time, which means it will be cut
	silently if a text goes beyond the boundary of the window
	Attention: no '\n' supported in the text, use self.newLine instead

	Example:
		tw = TextWindow(5, 5, 30, 50)
		ScreenMethod.echoOff()	# do it after TextScreen()
		ScreenMethod.cursorOff()
		ScreenMethod.clearScreen()
		tw.write('line 1 in color', 5, 1, [33])
		tw.write('line 1 in color', 8, 2, [34])
		tw.flush()
		tw.moveWindow(10,10)
	'''

	def __init__(self, rows=None, columns=None, beginRow=None, beginColumn=None):
		self.screen = TextScreen()
		self.rows = self.screen.rows	# window size
		self.columns = self.screen.columns
		self.beginRow = 1	# top left corner on screen
		self.beginColumn = 1
		self.cursorRow = 1	# cursor position in window
		self.cursorColumn = 1
		self.savedCursorRow = 1	# saved cursor position in window
		self.savedCursorColumn = 1
		self.buffer = []	# Output buffer, list of RichText 
		self.newWindow(rows, columns, beginRow, beginColumn)

	def setSize(self, rows, columns):
		''' Attention: please set window size before window position. 
		If current window position doesnt' work out to fit the screen, 
		the window will be moved to the top left corner. 
		'''
		if not rows or not columns or rows < 1 or columns < 1 or rows > self.screen.rows or columns > self.screen.columns:
			syslog.syslog(syslog.LOG_INFO, 'TextWindow.setSize out of screen')
			return(False)
		if self.rows == rows and self.columns == columns:
			return(True)	# no change at all
		self.newBuffer()
		self.rows = rows
		self.columns = columns
		if not self.setPos(self.beginRow, self.beginColumn):
			syslog.syslog(syslog.LOG_INFO, 'TextWindow.setSize.setPos out of screen')
			self.setPos(1,1)	# move to the top left corner 
		return(True)
	
	def setPos(self, beginRow, beginColumn):
		''' Attention: please set window size before window position. It
		will do health check against the defined window size
		'''
		if not beginRow or not beginColumn or beginRow < 1 or beginColumn < 1 or beginRow + self.rows - 1 > self.screen.rows or beginColumn + self.columns - 1 > self.screen.columns:
			syslog.syslog(syslog.LOG_INFO, 'TextWindow.setPos out of screen')
			return(False)
		self.beginRow = beginRow
		self.beginColumn = beginColumn
		return(True)

	def cursorHome(self):
		''' Move cursor to top left corner of the window
		'''
		self.cursorRow = 1	
		self.cursorColumn = 1

	def newLine(self):
		''' Move cursor to the 1st column of next line
		'''
		self.cursorRow += 1
		self.cursorColumn = 1

	def moveCursor(self, row=0, column=0, n=0, line_feed=False):
		''' move cursor to the desired position
		(row, column) is the starting point to write a text, 
		which is n characters in length
		if line_feed is set, it will new a line at the end
		'''
		if row and row > 0 and row <= self.rows:
			self.cursorRow = row 
		if column and column > 0 and column <= self.columns:
			self.cursorColumn = column 
		if n:
			self.cursorColumn += n
		if self.cursorColumn < 1:
			self.cursorColumn = 1
		if self.cursorColumn > self.columns or line_feed:
			self.newLine()

	def saveCursor(self):
		''' save current cursor position
		'''
		self.savedCursorRow = self.cursorRow
		self.savedCursorColumn = self.cursorColumn

	def restoreCursor(self):
		''' restore cursor to previouly saved position
		'''
		self.cursorRow = self.savedCursorRow
		self.cursorColumn = self.savedCursorColumn

	def newBuffer(self):
		''' New window display buffer and clear old data
		'''
		self.buffer = []
		self.cursorHome()

	def newWindow(self, rows=None, columns=None, beginRow=None, beginColumn=None):
		''' New or change the window size and/or position
		'''
		return(True if self.setSize(rows, columns) and self.setPos(beginRow, beginColumn) else False)

	def moveWindow(self, beginRow=None, beginColumn=None):
		''' Move a window
		'''
		if self.setPos(beginRow, beginColumn):
			self.flush()	
		else:
			syslog.syslog(syslog.LOG_INFO, 'TextWindow.moveWindow out of screen')

	def clearWindow(self):
		''' Clear the display window
		'''
		if not self.screen.resized() or (self.beginRow <= self.screen.rows and self.beginColumn <= self.screen.columns):
			text = ' ' * min(self.columns, self.screen.columns - self.beginColumn + 1)
			attrs = [ ScreenMethod.ATTR_RESET ]
			endRow = self.beginRow - 1 + min(self.rows, self.screen.rows - self.beginRow + 1)
			row = self.beginRow
			while row <= endRow:
				sys.stdout.write(str(RichText(text, attrs, row, self.beginColumn)))
				row += 1	
			sys.stdout.flush()

	def write(self, text, row=0, column=0, attrs=[], line_feed=False):
		''' write text to RichText to display in the window later
		- no auto line wrap supported, text is cut if out of boundary
		- \n or \r or other speical terminal control characters or 
		sequence is prohibited in the text
		- (row, column) is the relative position in the window
		- (0,0) means writing to current cursor position
		- (0,1) means writing to 1st column of current cursor row
		- if line_feed is set, it will new a line at the end
		'''
		# Calculate the relative position(rrow, rcolumn) on screen
		rrow = row if row and row > 0 else self.cursorRow
		rcolumn = column if column and column > 0 else self.cursorColumn
		if rrow > self.rows or rcolumn > self.columns:
			syslog.syslog(syslog.LOG_INFO, 'TextWindow.write out of window')
			return(False)	# out of window
		width = min(len(text), self.columns - rcolumn + 1)
		self.moveCursor(rrow, rcolumn, width, line_feed)
		self.buffer.append(RichText(text[0:width], attrs, rrow, rcolumn))
		return(True)

	def print(self, text, row=0, column=0, attrs=[]):
		''' write with line_feed
		'''
		return(self.write(text, row, column, attrs, True))

	def flush(self):
		''' display content (RichText) on screen
		'''
		if self.screen.resized() and (self.beginRow + self.rows - 1 > self.screen.rows or self.beginColumn + self.columns - 1 > self.screen.columns):
			# Do nothing if window is out of screen
			syslog.syslog(syslog.LOG_INFO, 'TextWindow.flush out of screen')
		else:
			for rt in self.buffer:
				sys.stdout.write(rt.pack(self.beginRow + rt.row - 1, self.beginColumn + rt.column - 1))
			sys.stdout.flush()

class TextPad(object):
	''' Textpad which can be bigger than physical screen
	Attention: no '\n' supported in the text, use self.newLine instead

	It supports paginated display as well

	Example:
		tp = TextPad(1024, 100, 30, 50)
		ScreenMethod.echoOff()	# do it after TextPad()
		ScreenMethod.cursorOff()
		ScreenMethod.clearScreen()
		tp.write('line 1 in color', 2, 1, [33])
		tp.write('line 2 in color', 8, 2, [34])
		tp.flush()
		tp.clearWindow()
		tp.moveWindow(10,10)
		tp.clearWindow()
		tp.movePad(5,5)

		tp.paginate()		# paginate per window rows
		tp.paginate(10)		# 10 items per page
		tp.page.setCurrentpage(2)	# display page 2, need flush it
	'''

	# default pad size 
	PAD_ROWS = 8192
	PAD_COLUMNS = 512

	def __init__(self, rows=0, columns=0, win_rows=0, win_columns=0, win_begin_row=1, win_begin_column=1, display_begin_row=1, display_begin_column=1):
		self.window = TextWindow(win_rows, win_columns, win_begin_row, win_begin_column) 			# Text window to display
		self.rows = 0 		# pad size 
		self.columns = 0
		self.cursorRow = 1	#cursor position
		self.cursorColumn = 1
		self.savedCursorRow = 1	# saved cursor position in window
		self.savedCursorColumn = 1
		self.beginRow = 1	# where in the pad to start to display
		self.beginColumn = 1
		self.page = None	# not enabled by default
		self._max_rows = 0	# this is for pagination purpose
		self._items_per_page = None	# for pagination purpose
		self.lineWrap = True	# default line autowrap enabled
		self.buffer = []	# pad content, list of RichText
		self.fullScreen = False
		self.newPad(rows, columns)
		self.setDisplayPos(display_begin_row, display_begin_column)

	def enableFullScreen(self):
		''' use full screen all the time
		'''
		self.fullScreen = True

	def disableFullScreen(self):
		''' use fix sized screen
		'''
		self.fullScreen = False

	def cursorHome(self):
		''' Set cursor to the top left corner of the pad
		'''
		self.cursorRow = 1	
		self.cursorColumn = 1

	def newLine(self):
		''' set cursor to the 1st column of next line
		'''
		self.cursorRow += 1
		self.cursorColumn = 1

	def moveCursor(self, row=0, column=0, n=0, line_feed=False):
		''' move cursor to the desired position
		(row, column) is the starting point to write a text, 
		which is n characters in length
		if line_feed is set, it will new a line at the end
		'''
		if row and row > 0 and row <= self.rows:
			self.cursorRow = row 
		if column and column > 0 and column <= self.columns:
			self.cursorColumn = column 
		if n:
			self.cursorColumn += n
		if self.cursorColumn < 1:
			self.cursorColumn = 1
		if self.cursorColumn > self.columns or line_feed:
			self.newLine()

	def saveCursor(self):
		''' Save current cursor position
		'''
		self.savedCursorRow = self.cursorRow
		self.savedCursorColumn = self.cursorColumn

	def restoreCursor(self):
		''' Restore cursor position to previously saved one
		'''
		self.cursorRow = self.savedCursorRow
		self.cursorColumn = self.savedCursorColumn

	def enableLineWrap(self):
		''' Enable auto line wrap
		'''
		self.lineWrap = True	

	def disableLineWrap(self):
		''' Disable auto line wrap
		'''
		self.lineWrap = False	

	def newPad(self, rows, columns):
		''' if pad size is not defined, use default size
		'''
		self.rows = rows if rows and rows > 0 else self.PAD_ROWS
		self.columns = columns if columns and columns > 0 else self.PAD_COLUMNS
		self.newContent()

	def setDisplayPos(self, row=1, column=1):
		''' from which starting point in the pad to display
		'''
		self.beginRow = row if row and row > 0 and row <= self.rows else 1
		self.beginColumn = column if column and column > 0 and column <= self.columns else 1
		if self.page:	# if pagination is enabled
			self.page.setTotalItems(self._max_rows - self.beginRow + 1)

	def clearWindow(self):
		''' Clear the pad display window
		'''
		if self.fullScreen:
			ScreenMethod.clearScreen()
		else:	
			self.window.clearWindow()

	def newContent(self):
		''' New pad content and clear old data
		'''
		self.buffer = []
		self._max_rows = 0
		self.cursorHome()
		self.window.newBuffer()
		self.clearWindow()

	def movePad(self, row, column):
		''' Move pad display area
		to show different area/content of pad to the display window
		'''
		self.setDisplayPos(row, column)	
		self.flush()

	def moveWindow(self, beginRow=None, beginColumn=None):
		''' Move pad's display window, content remains the same
		'''
		self.window.moveWindow(beginRow, beginColumn)

	def resizeWindow(self, rows=None, columns=None):
		''' Resize pad's display window, content remains the same
		'''
		if self.window.setSize(rows, columns):
			if self.page and not self._items_per_page:
				self.page.setItemsPerPage(self.window.rows)
			self.flush()	
		else:
			syslog.syslog(syslog.LOG_INFO, 'TextPad.resizeWindow out of screen')

	def write(self, text, row=0, column=0, attrs=[], line_feed=False):
		''' Write text to pad, no \n and/or \r is expected
		(row, column) is relative position in pad
		(0,0) means writing to current cursor position
		(0,1) means writing to 1st column of current cursor row
		if line_feed is set, it will new a line at the end
		'''
		rrow = row if row and row > 0 else self.cursorRow
		rcolumn = column if column and column > 0 else self.cursorColumn
		if rrow > self.rows or rcolumn > self.columns:
			syslog.syslog(syslog.LOG_INFO, 'TextPad.write out of pad')
			return(False)
		self._updateMaxRows(rrow)
		tl = len(text)
		l = min(tl, self.columns - rcolumn + 1)
		self.buffer.append(RichText(text[0:l], attrs, rrow, rcolumn))
		self.moveCursor(rrow, rcolumn, l, line_feed)
		if self.lineWrap and tl > l:
			self.write(text[l:], 0, 0, attrs)
		return(True)

	def print(self, text, row=0, column=0, attrs=[]):
		''' write with line_feed
		'''
		return(self.write(text, row, column, attrs, True))

	def flush(self):
		''' Refresh the content to the display window for display
		'''
		if self.fullScreen:
			# check and update the window size if necessary
			self.window.setSize(*ScreenMethod.getSize())
		self.window.newBuffer()
		for rt in self.buffer:
			self._writeWindowBuffer(rt)
		self.window.flush()

	def _writeWindowBuffer(self, rt):
		''' write RichText to window's buffer, inrternal use only
		'''
		delta = (self.page._current_page - 1) * self.page._items_per_page if self.page else 0
		if not rt or rt.row < self.beginRow + delta or (self.page and rt.row >= self.beginRow + delta + self.page._items_per_page): 	# no show
			return
		row = rt.row - self.beginRow - delta + 1
		if rt.column >= self.beginColumn:
			column = rt.column - self.beginColumn + 1 
			text = rt.text
			self.window.write(text, row, column, rt.attrs)
		elif len(rt.text) + rt.column > self.beginColumn:
			column = 1
			s = self.beginColumn - rt.column
			text = rt.text[s:]
			self.window.write(text, row, column, rt.attrs)

	def _updateMaxRows(self, row):
		''' keep a record of the maximum row number used, this 
		is for pagination purpose
		'''
		if row > self._max_rows:
			self._max_rows = row
			if self.page:	# if pagination is enabled
				self.page.setTotalItems(self._max_rows - self.beginRow + 1)

	def paginate(self, items_per_page=None):
		if items_per_page and items_per_page > 0:
			self._items_per_page = items_per_page
		ipp = self._items_per_page if self._items_per_page else self.window.rows 
		total_items = self._max_rows - self.beginRow + 1
		self.page = Pagination(ipp, total_items)
