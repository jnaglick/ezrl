from libtcodpy import *
from Engine import MapTileType
from datetime import date
from types import StringType, ListType

class DisplayManager:
	def __init__(self):
		#console window width, height, title
		self.C_WIDTH = 97
		self.C_HEIGHT = 64
		self.C_TITLE = 'New Game ' + date.today().strftime('%A %d-%B-%Y')
		
		#map draw distances: how much of the map to draw around the player
		self.M_HORZ_DRAW_DISTANCE = 45
		self.M_VERT_DRAW_DISTANCE = 27
		
		#misc constants
		self.PLAYER_STATUS_MESSAGES_TO_DRAW = 4

		#offsets: where to draw stuff
		self.infoOffset = (3, 1)
		self.playerStatusMessagesOffset = (3, 59)
		self.mapOffset = (3, 3)
		
		self.console = Console(self.C_WIDTH, self.C_HEIGHT, self.C_TITLE)
		self.mapTileToConsoleItem = MapTileToConsoleItem()
			
	def _drawPlayerInfo(self, player):
		s = 'X:[' + str(player.getX()) + '] ' + \
			'Y:[' + str(player.getY()) + '] ' + \
			'Steps:[' + str(player.getSteps()) + ']'
		c = ConsoleItem(s, Color(128, 128, 128))
		self.console.drawConsoleItem(self.infoOffset[0], self.infoOffset[1], c)
		
	def _drawPlayerStatusMessages(self, player):
		c = ConsoleItem(player.getStatusMessages()[-self.PLAYER_STATUS_MESSAGES_TO_DRAW:], Color(128, 128, 128))
		self.console.drawConsoleItem(self.playerStatusMessagesOffset[0], self.playerStatusMessagesOffset[1], c)
		
	def _drawMap(self, map, x_start, x_stop, y_start, y_stop):
		i = 0
		for y in range(y_start, y_stop):
			j = 0
			for x in range(x_start, x_stop):
				c = self.mapTileToConsoleItem.get(map.getTile(x, y))
				if c != None:
					self.console.drawConsoleItem(self.mapOffset[0] + j, self.mapOffset[1] + i, c)
				j += 1
			i += 1

	def _drawPlayer(self, player):
		c = ConsoleItem('@', white)
		self.console.drawConsoleItem(self.mapOffset[0] + self.M_HORZ_DRAW_DISTANCE, \
									 self.mapOffset[1] + self.M_VERT_DRAW_DISTANCE, \
									 c)

	def draw(self, game):
		self.console.clear()
		
		player = game.getPlayer()

		self._drawPlayerInfo(player)
		self._drawPlayerStatusMessages(player)
		self._drawMap(game.getMap(), 
					  player.getX() - self.M_HORZ_DRAW_DISTANCE, 
					  player.getX() + self.M_HORZ_DRAW_DISTANCE+1,
					  player.getY() - self.M_VERT_DRAW_DISTANCE, 
					  player.getY() + self.M_VERT_DRAW_DISTANCE+1)
		self._drawPlayer(player)

		self.console.flush()

class MapTileToConsoleItem:
	def get(self, mapTile):
		consoleItem = None
		if mapTile != None:
			type = mapTile.getType()
			if type == MapTileType.T_FLOOR:   consoleItem = ConsoleItem('.', white)
			elif type == MapTileType.T_HWALL: consoleItem = ConsoleItem('#', Color(188, 188, 188)) # -
			elif type == MapTileType.T_VWALL: consoleItem = ConsoleItem('#', Color(188, 188, 188)) # |
			elif type == MapTileType.T_XWALL: consoleItem = ConsoleItem('#', Color(148, 148, 148)) # +
			elif type == MapTileType.T_HALL:  consoleItem = ConsoleItem('*', Color(188, 188, 188))
			elif type == MapTileType.T_NONE:  consoleItem = ConsoleItem('~', Color(0, 0, 127))
			elif type == MapTileType.T_DOOR:  
				if mapTile.getProp('open') == 1:   consoleItem = ConsoleItem('o', Color(188, 188, 188))
				elif mapTile.getProp('open') == 0: consoleItem = ConsoleItem('x', Color(188, 188, 188))
		return consoleItem

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
		
	def drawConsoleItem(self, x, y, consoleItem):
		if type(consoleItem.getI()) == StringType:
			if len(consoleItem.getI()) == 1:
				self._drawChar(x, y, consoleItem)
			elif len(consoleItem.getI()) > 1:
				self._drawString(x, y, consoleItem)
		elif type(consoleItem.getI()) == ListType:
			self._drawList(x, y, consoleItem)

	def _drawChar(self, x, y, consoleItem):
		console_set_char(self.c, x, y, consoleItem.getI())
		console_set_fore(self.c, x, y, consoleItem.getColor())
		if (consoleItem.getBColor() != None): console_set_back(self.c, x, y, consoleItem.getBColor())
		
	def _drawString(self, x, y, consoleItem):
		console_print_left(self.c, x, y, BKGND_NONE, consoleItem.getI())
		for i in range(0, len(consoleItem.getI())): 
			console_set_fore(self.c, x+i, y, consoleItem.getColor())
		if (consoleItem.getBColor() != None):
			for i in range(0, len(consoleItem.getI())): 
				console_set_back(self.c, x+i, y, consoleItem.getBColor())

	def _drawList(self, x, y, consoleList): # TODO not the most elegant or functional. care later.
		i = 0
		for item in consoleList.getI():
			if len(item) == 1:
				self._drawChar(x, y+i, ConsoleItem(item, consoleList.getColor(), consoleList.getBColor()))
			elif len(item) > 1:
				self._drawString(x, y+i, ConsoleItem(item, consoleList.getColor(), consoleList.getBColor()))
			i += 1
		
	def flush(self):
		console_flush()
		
	def clear(self):
		console_clear(self.c)