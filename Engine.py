from random import randint

class Engine:
	def __init__(self):
		from MapMakers import RandomMapMaker

		#create random map
		randomMapMaker = RandomMapMaker(20, 20)
		randomMapMaker.generateRandomMap()
		map = randomMapMaker.getMap()

		#create new player
		getPlayerStartCoords = randomMapMaker.getPlayerStartCoords()
		player = Player(getPlayerStartCoords[0], getPlayerStartCoords[1])
		
		#create game
		self.game = Game(player, map)
		
	def _vTileWalkable(self, x, y):
		map = self.game.getMap()
		return x >= 0 and x < map.getW() and y >= 0 and y < map.getH() and map.getTile(x, y).getProp('walkable')
		
	def _vEntityMove(self, entity, adj):
		x, y = entity.getX(), entity.getY()
		return {
			'up' : self._vTileWalkable(x, y - 1),
			'down' : self._vTileWalkable(x, y + 1),
			'left' : self._vTileWalkable(x - 1, y),
			'right' : self._vTileWalkable(x + 1, y)
		}[adj]

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

class Map:
	def __init__(self, w, h):
		self.w = w
		self.h = h
		self.tiles = []
		for i in range(w * h): self.tiles.append(MapTileGenerator().createTile(MapTile.T_NONE))
		
	def setTile(self, x, y, tile): self.tiles[(y * self.w) + x] = tile
	def getTile(self, x, y): return self.tiles[(y * self.w) + x]
	
	def getW(self): return self.w
	def getH(self): return self.h

class MapTile:
	T_NONE 	= 'none'
	T_FLOOR = 'floor'
	T_HWALL = 'hwall'
	T_VWALL = 'vwall'
	T_XWALL = 'xwall'
	T_DOOR 	= 'door'

	def __init__(self, type, props):
		self.type = type
		self.props = props
		
	def getType(self): return self.type
	def getProp(self, k): return self.props[k]

class MapTileGenerator:
	def createTile(self, type):
		if type == MapTile.T_NONE:
			return MapTile(type, {'walkable': 0, 'opacity': 1})
		if type == MapTile.T_FLOOR:
			return MapTile(type, {'walkable': 1, 'opacity': 0})
		if (MapTile.T_HWALL, MapTile.T_VWALL, MapTile.T_XWALL).count(type) > 0:
			return MapTile(type, {'walkable': 0, 'opacity': 1})
		if type == MapTile.T_DOOR:
			return MapTile(type, {'walkable': 1, 'opacity': 0, 'open': 1})

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
	def __init__(self, player, map):
		self.player = player
		self.map = map
		
	def getPlayer(self): return self.player
	def getMap(self): return self.map
