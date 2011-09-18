from libtcodpy import *
from Engine import MapTile
from datetime import date

class DisplayManager:
	def __init__(self):
		self.C_HEIGHT = 64
		self.C_WIDTH = 32
		self.C_TITLE = 'New Game ' + date.today().strftime('%A %d-%B-%Y')
		self.console = Console(self.C_HEIGHT, self.C_WIDTH, self.C_TITLE)
		self.consoleItemGenerator = ConsoleItemGenerator()

		self.statusOffset = (1, 1)		
		self.mapOffset = (3, 3)
		self.M_HORZ_DRAW_DISTANCE = 6
		self.M_VERT_DRAW_DISTANCE = 4
		
	def _mapTileToConsoleItem(self, mapTile):
		return self.consoleItemGenerator.createConsoleItem(mapTile)

	def _playerToConsoleItem(self, player):
		return ConsoleItem('@', white)

	def _statusToConsoleItem(self, player):
		s = 'X:[' + str(player.getX()) + ']Y:[' + str(player.getY()) + ']Steps:[' + str(player.getSteps()) + ']'
		return ConsoleItem(s, Color(128, 128, 128))
		
	def draw(self, game):
		player = game.getPlayer()
		map = game.getMap()

		#draw status
		self.console.putConsoleString(self.statusOffset[0], self.statusOffset[1], self._statusToConsoleItem(player))
		
		#draw map
		i = 0
		for y in range(player.getY()-self.M_VERT_DRAW_DISTANCE, player.getY()+self.M_VERT_DRAW_DISTANCE+1):
			j = 0
			for x in range(player.getX() - self.M_HORZ_DRAW_DISTANCE, player.getX() + self.M_HORZ_DRAW_DISTANCE+1):
				consoleItem = self._mapTileToConsoleItem(map.getTile(x, y))
				if consoleItem != None:
					self.console.putConsoleChar(self.mapOffset[0] + j, self.mapOffset[1] + i, consoleItem)
				j += 1
			i += 1

		#draw player
		self.console.putConsoleChar(self.mapOffset[0] + self.M_HORZ_DRAW_DISTANCE, \
									self.mapOffset[1] + self.M_VERT_DRAW_DISTANCE, \
									self._playerToConsoleItem(player))
		
		self.console.flush()

class ConsoleItem:
	def __init__(self, i, color, bcolor=None):
		self.i = i
		self.color = color
		self.bcolor = bcolor
		
	def getI(self): return self.i
	def getColor(self): return self.color
	def getBColor(self): return self.bcolor
	
class ConsoleItemGenerator:
	def createConsoleItem(self, mapTile):
		consoleItem = None
		type = mapTile.getType()
		if type == MapTile.T_FLOOR:   consoleItem = ConsoleItem('.', white)
		elif type == MapTile.T_HWALL: consoleItem = ConsoleItem('-', Color(188, 188, 188))
		elif type == MapTile.T_VWALL: consoleItem = ConsoleItem('|', Color(188, 188, 188))
		elif type == MapTile.T_XWALL: consoleItem = ConsoleItem('+', Color(188, 188, 188))
		elif type == MapTile.T_NONE:  consoleItem = ConsoleItem('#', blue)
		elif type == MapTile.T_DOOR:  
			if mapTile.getProp('open') == 1:   consoleItem = ConsoleItem('o', Color(188, 188, 188))
			elif mapTile.getProp('open') == 0: consoleItem = ConsoleItem('x', Color(188, 188, 188))
		return consoleItem

class Console:
	def __init__(self, consoleWidth, consoleHeight, consoleTitle):
		self.c = console_init_root(consoleWidth, consoleHeight, consoleTitle, False)
		
	def putConsoleChar(self, x, y, ConsoleItem):
		console_set_char(self.c, x, y, ConsoleItem.getI())
		console_set_fore(self.c, x, y, ConsoleItem.getColor())
		if (ConsoleItem.getBColor() != None): console_set_back(self.c, x, y, ConsoleItem.getBColor())
		
	def putConsoleString(self, x, y, ConsoleItem):
		console_print_left(self.c, x, y, BKGND_NONE, ConsoleItem.getI())
		for i in range(0, len(ConsoleItem.getI())): 
			console_set_fore(self.c, x+i, y, ConsoleItem.getColor())
		if (ConsoleItem.getBColor() != None):
			for i in range(0, len(ConsoleItem.getI())): 
				console_set_back(self.c, x+i, y, ConsoleItem.getBColor())
		
	def flush(self):
		console_flush()