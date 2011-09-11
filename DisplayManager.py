from libtcodpy import *
from Engine import MapTile

class ConsoleItem:
	def __init__(self, i, color, bcolor=None):
		self.i = i
		self.color = color
		self.bcolor = bcolor
		
	def getI(self): return self.i
	def getColor(self): return self.color
	def getBColor(self): return self.bcolor

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

class DisplayManager:
	def __init__(self):
		self.C_HEIGHT = 64
		self.C_WIDTH = 32
		self.C_TITLE = 'New Game Sept-10-2011'
		self.mapOffset = (3, 3)
		self.statusOffset = (2, 20)
		
		self.mapTileTypeToConsoleItem = {
			MapTile.T_FLOOR : ConsoleItem('.', white),
			MapTile.T_HWALL : ConsoleItem('-', Color(188, 188, 188)),
			MapTile.T_VWALL : ConsoleItem('|', Color(188, 188, 188)),
			MapTile.T_XWALL : ConsoleItem('+', Color(188, 188, 188)),
			MapTile.T_NONE	: None
		}
		
		self.console = Console(self.C_HEIGHT, self.C_WIDTH, self.C_TITLE)
		
	def _mapTileTypeToConsoleItem(self, mapTileType):
		return self.mapTileTypeToConsoleItem[mapTileType]
		
	def _mapTileToConsoleItem(self, mapTile):
		if mapTile.getType() == MapTile.T_DOOR:
			if mapTile.getProp('open') == 1: return ConsoleItem('o', Color(188, 188, 188))
			if mapTile.getProp('open') == 0: return ConsoleItem('x', Color(188, 188, 188))
		
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
		for y in range(map.getH()):
			for x in range(map.getW()):
				mapTile = map.getTile(x, y)
				try:
					consoleItem = self._mapTileTypeToConsoleItem(mapTile.getType())
				except KeyError:
					consoleItem = self._mapTileToConsoleItem(mapTile)
				if consoleItem != None:
					self.console.putConsoleChar(self.mapOffset[0] + x, self.mapOffset[1] + y, consoleItem)

		#draw player
		self.console.putConsoleChar(self.mapOffset[0] + player.getX(), self.mapOffset[1] + player.getY(), self._playerToConsoleItem(player))
		
		self.console.flush()
