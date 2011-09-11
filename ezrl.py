from libtcodpy import *

#					#
#	Input Processor	#
#					#
class InputProcessor:
	def __init__(self):
		self.inputToCommand = {
			ord('x')	: 'sys exit',
			KEY_UP		: 'p move up',
			KEY_DOWN	: 'p move down',
			KEY_LEFT	: 'p move left',
			KEY_RIGHT	: 'p move right'
		}
		
	def fetchCommands(self):
		actions = []

		key = console_wait_for_keypress(True)
		
		if key.c != 0: keycode = key.c #printable char
		else: keycode = key.vk #physical key
			
		try: actions.append(self.inputToCommand[keycode]) 
		except KeyError: None

		return actions

#						#
#	Engine / Gamestate	#
#						#
class MapTile:
	def __init__(self, type):
		self.type = type
		
	def getType(self): return self.type

class Map:
	def __init__(self, w, h):
		self.w = w
		self.h = h
		self.tiles = []
		for i in range(w * h):
			self.tiles.append(MapTile('floor'))
		
	def setTile(self, x, y, tile): self.tiles[(y * self.w) + x] = tile
	def getTile(self, x, y): return self.tiles[(y * self.w) + x]
	
	def getW(self): return self.w
	def getH(self): return self.h

class Player:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.steps = 0
		
	def getY(self): return self.y
	def setY(self, y): self.y = y	
	def incY(self): self.y += 1
	def decY(self): self.y -= 1
	
	def getX(self): return self.x		
	def setX(self, x): self.x = x
	def incX(self): self.x += 1
	def decX(self): self.x -= 1

	def getSteps(self): return self.steps
	def incSteps(self): self.steps += 1

class Game:
	def __init__(self):
		self.player = Player(0, 0)
		self.map = Map(10, 10)
		
	def getPlayer(self): return self.player
	def getMap(self): return self.map

class Engine:
	def __init__(self):
		self.game = Game()
		
	def _vEntityMove(self, entity, adj):
		if adj == 'up': return entity.getY() > 0
		if adj == 'down': return entity.getY() < self.game.getMap().getH() - 1
		if adj == 'left': return entity.getX() > 0
		if adj == 'right': return entity.getX() < self.game.getMap().getW() - 1

	def _verifyEntityCommand(self, entity, verb, adj):
		if verb == 'move': return self._vEntityMove(entity, adj)
		return 0
		
	def _cEntityMove(self, entity, adj):
		if adj == 'up': entity.decY()
		if adj == 'down': entity.incY()
		if adj == 'left': entity.decX()
		if adj == 'right': entity.incX()
		entity.incSteps()

	def _processEntityCommand(self, entity, verb, adj):
		if (not self._verifyEntityCommand(entity, verb, adj)): return
		if verb == 'move': self._cEntityMove(entity, adj)
		
	def _processSysCommand(self, verb):
		if verb == 'exit': exit()

	def processCommands(self, commands):
		for c in commands:
			a = c.split()
			noun, verb = a[0], a[1]
			if (len(a) == 3):
				adj = a[2]
			else:
				adj = None
			
			if noun == 'sys': self._processSysCommand(verb)
			if noun == 'p': self._processEntityCommand(self.game.getPlayer(), verb, adj)

	def getGame(self): return self.game

#								#
#	Display Manager / Console	#
#								#
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
			'floor' : ConsoleItem('.', white)
		}
		
		self.console = Console(self.C_HEIGHT, self.C_WIDTH, self.C_TITLE)
		
	def _mapTileConsoleItem(self, mapTile):
		return self.mapTileTypeToConsoleItem[mapTile.getType()]
		
	def _playerConsoleItem(self, player):
		return ConsoleItem('@', white)
		
	def _statusConsoleItem(self, player):
		s = 'X:[' + str(player.getX()) + ']Y:[' + str(player.getY()) + ']Steps:[' + str(player.getSteps()) + ']'

		return ConsoleItem(s, Color(128, 128, 128))

	def draw(self, game):
		player = game.getPlayer()
		map = game.getMap()

		#draw status
		self.console.putConsoleString(self.statusOffset[0], self.statusOffset[1], self._statusConsoleItem(player))
		
		#draw map
		for y in range(map.getH()):
			for x in range(map.getW()):
				self.console.putConsoleChar(self.mapOffset[0] + x, self.mapOffset[1] + y, self._mapTileConsoleItem(map.getTile(x, y)))

		#draw player
		self.console.putConsoleChar(self.mapOffset[0] + player.getX(), self.mapOffset[1] + player.getY(), self._playerConsoleItem(player))
		
		self.console.flush()

#				#
#	Controller	#
#				#
class Controller:
	def __init__(self):
		self.displayManager = DisplayManager()
		self.engine = Engine()
		self.inputProcessor = InputProcessor()

	def go(self):
		while(True):
			self.displayManager.draw(self.engine.getGame())
			self.engine.processCommands(self.inputProcessor.fetchCommands())

Controller().go()